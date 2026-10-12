#!/usr/bin/env python3
"""Generate own C ADI profile metadata from the trusted bundled catalog.

This generator intentionally has no external-catalog input. Native profile
metadata remains restricted to the two reviewed own profiles below.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HEADER = ROOT / "tools" / "adi_catalog_profiles.h"
sys.path.insert(0, str(ROOT))

from prototype.catalog import Catalog  # noqa: E402


PROFILE_PINS: dict[str, dict[str, Any]] = {
    "digital8": {
        "c_enum": "VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8",
        "modules": ["750-430", "750-530"],
        "input_bits": 8,
        "output_bits": 8,
        "module_ids": [0x8801, 0x8802],
        "parameter10": ["UUUU8801UUUUUUUU", "UUUU8802UUUUUUUU"],
        "process_field_type": "stdBYTE8bools",
        "input_offsets_bits": [0, 0],
        "output_offsets_bits": [0, 0],
        "scope": "OWN_MODEL_METADATA_BOUND_TO_DESCRIPTORS_NOT_PHYSICAL_BUS",
        "descriptors": {
            "750-430": ("8801_0750043000000000", "2.0.0.14",
                        "26d302678905d2e8f4c7e34880cf830c4ad56361ebd647e6ed82a9e02c81dd91"),
            "750-530": ("8802_0750053000000000", "2.0.0.15",
                        "84b4043d448c44155a36916a1b65a39f20ba0560459d3c0ffac53fba351daa5d"),
        },
    },
    "digital16": {
        "c_enum": "VIRTUAL_ADI_PROFILE_DIGITAL16",
        "modules": ["750-1405", "750-1504"],
        "input_bits": 16,
        "output_bits": 16,
        "module_ids": [0x9001, 0x9002],
        "parameter10": [None, None],
        "process_field_type": None,
        "input_offsets_bits": [0, 16],
        "output_offsets_bits": [0, 0],
        "scope": "OWN_MODEL_METADATA_BOUND_TO_DESCRIPTORS_NOT_PHYSICAL_BUS",
        "descriptors": {
            "750-1405": ("9001_0750140500000000", "2.0.0.14",
                         "2ea6fb96d1db35228450ccd94454f1e51b562a6e1982e416f34eed2feb056273"),
            "750-1504": ("9002_0750150400000000", "2.0.0.14",
                         "207e7d654f98a180b06cb75117e282ac2a85f956cbb5d057113d76846a6dc991"),
        },
    },
}

ENUMS = {
    "digital8": "VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8",
    "digital16": "VIRTUAL_ADI_PROFILE_DIGITAL16",
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate_catalog(catalog: Any) -> list[dict[str, Any]]:
    """Validate strict reviewed native-profile allowlist and descriptor pins."""
    _require(getattr(catalog, "bundled", False) is True,
             "native profile generation requires bundled Catalog()")
    profiles = catalog.native_profiles
    _require(type(profiles) is list, "Catalog.native_profiles must be a list")
    _require(len(profiles) == 2, "only bundled digital8 and digital16 profiles are allowed")
    _require(type(catalog.sha256) is str and len(catalog.sha256) == 64,
             "Catalog.sha256 must be canonical catalog digest")
    modules = catalog.entries()
    _require(type(modules) is list, "Catalog.modules must be a list")
    module_by_article = {m.get("article"): m for m in modules if type(m) is dict}
    _require(len(module_by_article) == len(modules), "duplicate or invalid catalog module")

    seen: set[str] = set()
    normalized: list[dict[str, Any]] = []
    fields = ("name", "c_enum", "modules", "input_bits", "output_bits",
              "module_ids", "parameter10", "process_field_type",
              "input_offsets_bits", "output_offsets_bits", "scope")
    for profile in profiles:
        _require(type(profile) is dict, "native profile must be an object")
        _require(set(profile) == set(fields), "native profile fields differ from reviewed schema")
        name = profile["name"]
        _require(name in PROFILE_PINS and name not in seen,
                 f"unknown or duplicate native profile: {name!r}")
        seen.add(name)
        expected = PROFILE_PINS[name]
        for key, value in expected.items():
            if key == "descriptors":
                continue
            _require(profile[key] == value, f"{name}.{key} differs from reviewed metadata")
        _require(profile["c_enum"] == ENUMS[name], f"{name}: unexpected C enum")
        _require(len(profile["modules"]) == len(profile["module_ids"]) == 2,
                 f"{name}: exactly two ordered terminals required")

        for article, descriptor_pin in expected["descriptors"].items():
            module = module_by_article.get(article)
            _require(module is not None, f"{name}: missing pinned module {article}")
            descriptor = module.get("descriptor")
            _require(type(descriptor) is dict, f"{article}: descriptor metadata missing")
            actual = (descriptor.get("device_id"), descriptor.get("version"),
                      descriptor.get("sha256"))
            _require(actual == descriptor_pin,
                     f"{article}: descriptor does not match known pin")

        in_bits = profile["input_bits"]
        out_bits = profile["output_bits"]
        _require(type(in_bits) is int and type(out_bits) is int,
                 f"{name}: bit sizes must be integers")
        item = dict(profile)
        item["input_bytes"] = (in_bits + 7) // 8
        item["output_bytes"] = (out_bits + 7) // 8
        item["input_mask"] = (1 << in_bits) - 1 if in_bits else 0
        item["output_mask"] = (1 << out_bits) - 1 if out_bits else 0
        item["terminal_count"] = len(profile["modules"])
        normalized.append(item)
    _require(seen == set(PROFILE_PINS), "both reviewed native profiles must be present")
    return sorted(normalized, key=lambda p: (0 if p["name"] == "digital16" else 1))


def _c_u(value: int, width: int = 0) -> str:
    return f"0x{value:0{width}x}u" if width else f"{value}u"


def render_header() -> str:
    catalog = Catalog()
    profiles = validate_catalog(catalog)
    digest = catalog.sha256
    lines = [
        "/* Generated by tools/generate_module_catalog.py; do not edit.",
        f" * Bundled catalog canonical SHA-256: {digest}",
        " * Own research metadata only; no vendor declarations or physical ABI.",
        " */",
        "#ifndef VIRTUALWAGO_ADI_CATALOG_PROFILES_H",
        "#define VIRTUALWAGO_ADI_CATALOG_PROFILES_H",
        "",
        "typedef struct {",
        "  virtual_adi_profile profile;",
        "  uint32_t input_bytes;",
        "  uint32_t output_bytes;",
        "  uint32_t input_bits;",
        "  uint32_t output_bits;",
        "  uint16_t input_mask;",
        "  uint16_t output_mask;",
        "  uint32_t terminal_count;",
        "  uint16_t module_ids[2];",
        "  const char *parameter10[2];",
        "  const char *process_field_type;",
        "  uint32_t input_offsets_bits[2];",
        "  uint32_t output_offsets_bits[2];",
        "} virtual_profile_data;",
        "",
    ]
    for p in profiles:
        ident = p["name"]
        lines.extend([
            f"static const virtual_profile_data profile_{ident} = {{",
            f"    {p['c_enum']},",
            f"    {_c_u(p['input_bytes'])}, {_c_u(p['output_bytes'])},",
            f"    {_c_u(p['input_bits'])}, {_c_u(p['output_bits'])},",
            f"    {_c_u(p['input_mask'], 4)}, {_c_u(p['output_mask'], 4)},",
            f"    {_c_u(p['terminal_count'])},",
            "    {" + ", ".join(_c_u(v, 4) for v in p["module_ids"]) + "},",
            "    {" + ", ".join("NULL" if v is None else f'"{v}"'
                               for v in p["parameter10"]) + "},",
            "    " + ("NULL" if p["process_field_type"] is None
                      else f'"{p["process_field_type"]}"') + ",",
            "    {" + ", ".join(_c_u(v) for v in p["input_offsets_bits"]) + "},",
            "    {" + ", ".join(_c_u(v) for v in p["output_offsets_bits"]) + "}",
            "};",
            "",
        ])
    lines.extend(["#endif", ""])
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="fail if generated header is stale (default)")
    mode.add_argument("--write", action="store_true", help="write the generated header")
    args = parser.parse_args(argv)
    try:
        generated = render_header()
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        parser.error(str(exc))
    if args.write:
        HEADER.write_text(generated, encoding="utf-8")
        return 0
    try:
        current = HEADER.read_text(encoding="utf-8")
    except FileNotFoundError:
        current = ""
    if current != generated:
        print(f"stale generated header: {HEADER.relative_to(ROOT)}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
