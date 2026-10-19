"""Versioned model catalog; documentation and runtime evidence stay separate.

The bundled JSON is repository source, not discovered hardware. Sizes and
masks describe our research models. No API derives native bus IDs or offsets.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from .contracts import ContractError, Unsupported, canonical, exact_keys, uint

CATALOG_PATH = Path(__file__).resolve().parents[1] / "config/module-catalog.json"
MODEL_SCOPE = "OWN_RESEARCH_LAYOUT_NOT_NATIVE_MAPPING"
_CODECS = {"digital", "ai466_standard", "ao550_standard", "pwm677_frq"}


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"catalog: duplicate JSON key {key}")
        result[key] = value
    return result


def _text(value, name):
    if type(value) is not str or not value or len(value) > 1024:
        raise ContractError(f"{name}: nonempty bounded string required")


class Catalog:
    """Validated immutable-by-interface metadata and content digest.

    Passing ``data`` is for own research tests/models. It cannot authorize a
    native build; the native generator reads the bundled catalog itself.
    """

    def __init__(self, data: dict | None = None):
        self.bundled = data is None
        if data is None:
            with CATALOG_PATH.open(encoding="utf-8") as stream:
                data = json.load(stream, object_pairs_hook=_unique_object)
        data = copy.deepcopy(data)
        exact_keys(data, {"schema", "revision", "scope", "source_report",
                          "modules", "native_profiles"}, "catalog")
        if type(data["schema"]) is not int or data["schema"] != 1:
            raise ContractError("catalog: schema 1 required")
        if data["scope"] != "OWN_MODULE_CATALOG_NOT_HARDWARE_INVENTORY":
            raise ContractError("catalog: research scope required")
        _text(data["revision"], "revision")
        _text(data["source_report"], "source_report")
        if not re.fullmatch(r"docs/[a-z0-9-]+\.md", data["source_report"]):
            raise ContractError("catalog: invalid source report path")
        if type(data["modules"]) is not list or not 1 <= len(data["modules"]) <= 128:
            raise ContractError("catalog: 1..128 entries required")
        entries, models = {}, {}
        for entry in data["modules"]:
            exact_keys(entry, {"article", "variant", "family", "channels", "sources",
                               "descriptor", "model", "native_evidence",
                               "hardware_evidence", "limits"}, "catalog entry")
            article = entry["article"]
            if type(article) is not str or not re.fullmatch(r"750-[0-9]{3,4}", article):
                raise ContractError("catalog: exact article required")
            if article in entries:
                raise ContractError("catalog: duplicate article")
            if entry["variant"] != "standard":
                raise Unsupported("catalog: variant needs a separate exact schema/contract")
            if type(entry["family"]) is not str or entry["family"] not in {"di", "do", "ai", "ao", "pwm", "serial", "passive"}:
                raise ContractError("catalog: unknown family")
            channels = entry["channels"]
            if channels is None:
                if entry["family"] != "serial":
                    raise ContractError("catalog: channel count required for this family")
            else:
                uint(channels, "channels", 64)
                if (channels == 0) != (entry["family"] == "passive"):
                    raise ContractError("catalog: zero channels only for passive entries")
            sources = entry["sources"]
            if type(sources) is not list or not 1 <= len(sources) <= 10:
                raise ContractError("catalog: bounded source list required")
            for source in sources:
                exact_keys(source, {"url", "kind", "version", "checked_on"}, "source")
                _text(source["url"], "source URL")
                parsed = urlsplit(source["url"])
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise ContractError("catalog: HTTPS source without credentials required")
                if type(source["kind"]) is not str or source["kind"] not in {
                        "manufacturer_product", "manufacturer_manual",
                        "manufacturer_manual_on_mirror"}:
                    raise ContractError("catalog: unknown source kind")
                if source["version"] is not None:
                    _text(source["version"], "source version")
                if type(source["checked_on"]) is not str or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", source["checked_on"]):
                    raise ContractError("catalog: source date required")
            for evidence in (entry["native_evidence"], entry["hardware_evidence"]):
                if evidence is not None and (type(evidence) is not str or
                        not re.fullmatch(r"docs/[a-z0-9-]+\.md", evidence)):
                    raise ContractError("catalog: evidence report path required")
            descriptor = entry["descriptor"]
            if descriptor is not None:
                exact_keys(descriptor, {"device_id", "version", "sha256", "scope"}, "descriptor")
                if descriptor["scope"] != "ENGINEERING_DESCRIPTION_NOT_PHYSICAL_REVISION":
                    raise ContractError("catalog: descriptor scope required")
                _text(descriptor["device_id"], "descriptor id")
                _text(descriptor["version"], "descriptor version")
                if type(descriptor["sha256"]) is not str or not re.fullmatch(r"[0-9a-f]{64}", descriptor["sha256"]):
                    raise ContractError("catalog: descriptor digest required")
            if type(entry["limits"]) is not list or not entry["limits"]:
                raise ContractError("catalog: explicit limits required")
            for limit in entry["limits"]:
                _text(limit, "limit")
            model = entry["model"]
            if model is not None:
                self._validate_model(entry)
                if model["id"] in models:
                    raise ContractError("catalog: duplicate model id")
                models[model["id"]] = dict(model, article=article, family=entry["family"], channels=channels)
            entries[article] = entry
        profiles = data["native_profiles"]
        if type(profiles) is not list or len(profiles) > 16:
            raise ContractError("catalog: bounded native profile list required")
        seen = set()
        for profile in profiles:
            exact_keys(profile, {"name", "c_enum", "modules", "input_bits", "output_bits",
                                 "module_ids", "parameter10", "process_field_type",
                                 "input_offsets_bits", "output_offsets_bits", "scope"}, "native profile")
            if type(profile["name"]) is not str or profile["name"] not in {"digital8", "digital16"} or profile["name"] in seen:
                raise Unsupported("catalog: unknown or duplicate native profile")
            seen.add(profile["name"])
            expected_enum = {"digital8": "VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8",
                             "digital16": "VIRTUAL_ADI_PROFILE_DIGITAL16"}[profile["name"]]
            if profile["c_enum"] != expected_enum or profile["scope"] != "OWN_MODEL_METADATA_BOUND_TO_DESCRIPTORS_NOT_PHYSICAL_BUS":
                raise ContractError("catalog: native profile scope/enum mismatch")
            for key in ("modules", "module_ids", "parameter10", "input_offsets_bits", "output_offsets_bits"):
                if type(profile[key]) is not list or len(profile[key]) != 2:
                    raise ContractError("catalog: native profiles have exactly two records")
            for key in ("input_bits", "output_bits"):
                if uint(profile[key], key, 16) not in (8, 16):
                    raise Unsupported("catalog: native width not implemented")
            for value in profile["module_ids"]:
                uint(value, "native module id", 65535)
            for value in profile["parameter10"] + [profile["process_field_type"]]:
                if value is not None:
                    _text(value, "native parameter")
                    if not re.fullmatch(r"[A-Za-z0-9_]+", value):
                        raise ContractError("catalog: native parameter must be a token")
            for key in ("input_offsets_bits", "output_offsets_bits"):
                for value in profile[key]:
                    uint(value, key, 32)
            for index, article in enumerate(profile["modules"]):
                if type(article) is not str or article not in entries:
                    raise ContractError("catalog: native module reference missing")
                e = entries[article]
                if e["family"] != ("di" if index == 0 else "do") or e["descriptor"] is None:
                    raise ContractError("catalog: native profile requires descriptor-bound DI/DO")
                if e["channels"] != profile["input_bits" if index == 0 else "output_bits"]:
                    raise ContractError("catalog: native width disagrees with module channels")
        self._data, self._entries, self._models = data, entries, models
        self.sha256 = hashlib.sha256(canonical(data)).hexdigest()

    @staticmethod
    def _validate_model(entry):
        model = entry["model"]
        exact_keys(model, {"id", "input_bytes", "output_bytes", "codec", "input_mask",
                           "output_mask", "layout_scope"}, "model")
        if type(model["id"]) is not str or not re.fullmatch(re.escape(entry["article"]) + r"\.[a-z0-9]+", model["id"]):
            raise ContractError("catalog: model id must bind the exact article")
        if type(model["codec"]) is not str or model["codec"] not in _CODECS or model["layout_scope"] != MODEL_SCOPE:
            raise Unsupported("catalog: codec/layout not supported")
        ni, no = (uint(model[k], k, 4096) for k in ("input_bytes", "output_bytes"))
        for direction, size in (("input", ni), ("output", no)):
            mask = model[direction + "_mask"]
            if mask is not None:
                if size > 8 or size == 0:
                    raise ContractError("catalog: invalid mask size")
                uint(mask, direction + " mask", (1 << (8 * size)) - 1)
        if model["codec"] == "digital":
            channels = entry["channels"]
            if entry["family"] not in {"di", "do"} or channels not in {2, 4, 8, 16}:
                raise Unsupported("catalog: digital family/width unsupported")
            expected_size = (channels + 7) // 8
            expected = (expected_size, 0) if entry["family"] == "di" else (0, expected_size)
            if (ni, no) != expected:
                raise ContractError("catalog: digital image size disagrees with channels")
            key = "input_mask" if entry["family"] == "di" else "output_mask"
            other = "output_mask" if entry["family"] == "di" else "input_mask"
            if model[key] != (1 << channels) - 1 or model[other] is not None:
                raise ContractError("catalog: digital channel mask mismatch")
        else:
            expected = {"ai466_standard": ("750-466", "ai", 2, 6, 0),
                        "ao550_standard": ("750-550", "ao", 2, 0, 4),
                        "pwm677_frq": ("750-677", "pwm", 4, 12, 12)}[model["codec"]]
            if (entry["article"], entry["family"], entry["channels"], ni, no) != expected:
                raise Unsupported("catalog: codec belongs to another exact module")
            if model["input_mask"] is not None or model["output_mask"] is not None:
                raise ContractError("catalog: nondigital masks unsupported")

    @property
    def data(self):
        return copy.deepcopy(self._data)

    @property
    def native_profiles(self):
        return copy.deepcopy(self._data["native_profiles"])

    @property
    def model_specs(self):
        return copy.deepcopy(self._models)

    def entries(self):
        return copy.deepcopy(list(self._entries.values()))

    def entry(self, article: str):
        if type(article) is not str or article not in self._entries:
            raise Unsupported("unknown exact module article")
        return copy.deepcopy(self._entries[article])

    def model(self, model_id: str):
        if type(model_id) is not str or model_id not in self._models:
            raise Unsupported("module has no implemented model profile")
        return copy.deepcopy(self._models[model_id])

    def model_for_article(self, article: str):
        entry = self.entry(article)
        if entry["model"] is None:
            raise Unsupported("documentation-only module: no model implemented")
        return self.model(entry["model"]["id"])

    def research_layout(self, articles: list[str], watchdog_ns: int = 100_000_000):
        """Pack our byte models consecutively; NEVER derive native bus offsets.

        The result retains the old explicit-offset schema. Repeated article
        instances are allowed; documentation-only/passive entries are rejected.
        """
        if type(articles) is not list or not 1 <= len(articles) <= 64:
            raise ContractError("research layout requires 1..64 exact articles")
        if uint(watchdog_ns, "watchdog_ns") == 0:
            raise ContractError("watchdog_ns must be positive")
        ni, no, modules = 0, 0, []
        for i, article in enumerate(articles):
            spec = self.model_for_article(article)
            modules.append({"id": f"m{i}", "model": spec["id"],
                            "input_offset": ni, "output_offset": no})
            ni += spec["input_bytes"]
            no += spec["output_bytes"]
        if max(ni, no) > 4096:
            raise ContractError("research layout exceeds model image bound")
        return {"schema": 1, "purpose": "research-layout-not-target-mapping",
                "input_size": ni, "output_size": no,
                "watchdog_ns": watchdog_ns, "modules": modules}
