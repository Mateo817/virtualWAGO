"""Deterministic raw-I/O backend, Python >=3.11, standard library only.

The JSON protocol, offsets, identities, watchdog and restart policy are OUR
research contracts. No WAGO library, kernel driver or CODESYS runtime is loaded.
Manufacturer data codecs are explicitly bounded; unknown states fail closed.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
from typing import Any
from .catalog import Catalog
from .contracts import ContractError, Unsupported, canonical, uint, exact_keys, hexbytes

VERSION = "0.2.0"
# Compatibility view; Rail resolves its own validated catalog rather than
# trusting mutations of this exported dictionary.
MODELS = {key: (m["article"], m["input_bytes"], m["output_bytes"])
          for key, m in Catalog().model_specs.items()}
MAX_IMAGE = 4096

def encode_ai466_standard(current_uA: int) -> int:
    """Normal range ONLY, no diagnosis generation.

    Manufacturer manual v1.4.0, pp.27-28: bits B3..B14, 4mA=0,
    12mA=0x4000, 20mA=0x7ff8. Floor quantization between table points is
    a MODEL ASSUMPTION, not a measured ADC transition characteristic.
    """
    uint(current_uA, "current_uA", 20000)
    if current_uA < 4000:
        raise Unsupported("under-range/wire-break threshold not modeled; inject raw bytes")
    count = min(4095, (current_uA - 4000) * 4096 // 16000)
    return count << 3

def decode_ao550_standard_word(raw_word: int) -> int:
    """Decode one standard 750-550 output word into model millivolts.

    WAGO manual v1.1.0, table points 0x0000=0 V, 0x1000=1.25 V,
    0x4000=5 V, 0x7000=8.75 V and 0x7fff=10 V. Bits B0..B2 are ignored.
    Piecewise linear interpolation rounded to nearest millivolt is an explicit
    model assumption between documented points; special /000-200 and register
    modes are excluded.
    """
    if type(raw_word) is not int or not 0 <= raw_word <= 0xFFFF:
        raise ContractError("raw_word: expected an unsigned 16-bit integer")
    if raw_word > 0x7FFF:
        raise Unsupported("750-550 standard normal output words stop at 0x7fff")
    code = raw_word & 0x7FF8
    anchors = ((0x0000, 0), (0x1000, 1250), (0x2000, 2500),
               (0x3000, 3750), (0x4000, 5000), (0x5000, 6250),
               (0x6000, 7500), (0x7000, 8750), (0x7FF8, 10000))
    for (low_word, low_mV), (high_word, high_mV) in zip(anchors, anchors[1:]):
        if code <= high_word:
            return low_mV + ((code - low_word) * (high_mV - low_mV)
                             + (high_word - low_word) // 2) // (high_word - low_word)
    return 10_000

def decode_pwm677_frq(data: bytes) -> tuple[int, int, int, int]:
    """Bounded PWM Frq OUTPUT decoder, not register-communication emulation.

    Manufacturer manual v1.0.0, pp.33,38-40: four 3-byte groups C,L,H;
    enable is pair-wise in C0/C2, frequency words are channel-wise.
    RegCom, other modes and unverified reserved-bit behavior are rejected.
    No status byte is invented by this helper.
    """
    if type(data) is not bytes or len(data) != 12:
        raise ContractError("PWM output must be exactly 12 bytes")
    controls = [data[i] for i in (0, 3, 6, 9)]
    if any(c & 0x80 for c in controls):
        raise Unsupported("RegCom path requires verified register protocol; not modeled")
    if controls[1] or controls[3] or controls[0] & ~1 or controls[2] & ~1:
        raise Unsupported("nonzero unmodeled PWM control bits")
    values = [int.from_bytes(data[i+1:i+3], "little") for i in (0, 3, 6, 9)]
    if any(v > 20000 for v in values):
        raise Unsupported("PWM Frq range exceeds 20kHz")
    return tuple(v if controls[(i // 2) * 2] & 1 else 0
                 for i, v in enumerate(values))

class Rail:
    """One instance, one caller/writer, atomic operations at explicit cycles.

    Raw bytes never prove a manufacturer's module-identification protocol.
    Bus loss/presence/watchdog affect effective outputs, NOT command history.
    After invalidation a NEW complete output frame is needed to rearm.
    """
    def __init__(self, config: dict[str, Any], *, catalog: Catalog | None = None):
        self.catalog = Catalog() if catalog is None else catalog
        if not isinstance(self.catalog, Catalog):
            raise ContractError("validated Catalog required")
        self.catalog_hash = self.catalog.sha256
        exact_keys(config, {"schema", "purpose", "input_size", "output_size",
                            "watchdog_ns", "modules"}, "config")
        if type(config["schema"]) is not int or config["schema"] != 1:
            raise ContractError("schema must be integer 1")
        if config["purpose"] != "research-layout-not-target-mapping":
            raise ContractError("research purpose marker required")
        self.ni = uint(config["input_size"], "input_size", MAX_IMAGE)
        self.no = uint(config["output_size"], "output_size", MAX_IMAGE)
        self.watchdog = uint(config["watchdog_ns"], "watchdog_ns")
        if self.watchdog == 0:
            raise ContractError("watchdog_ns must be positive")
        if type(config["modules"]) is not list or not 1 <= len(config["modules"]) <= 64:
            raise ContractError("1..64 modules required")
        occupied = {"input_offset": set(), "output_offset": set()}
        self.modules: dict[str, dict[str, Any]] = {}
        for module in config["modules"]:
            exact_keys(module, {"id", "model", "input_offset", "output_offset"}, "module")
            ident = module["id"]
            if (type(ident) is not str or re.fullmatch(r"[A-Za-z0-9_-]{1,40}", ident) is None
                    or ident in self.modules):
                raise ContractError("module id invalid or duplicate")
            spec = self.catalog.model(module["model"])
            article, size_i, size_o = spec["article"], spec["input_bytes"], spec["output_bytes"]
            for key, length, total in (("input_offset", size_i, self.ni),
                                        ("output_offset", size_o, self.no)):
                off = uint(module[key], key, MAX_IMAGE)
                if off + length > total:
                    raise ContractError(f"{ident}: {key} exceeds image")
                span = set(range(off, off + length))
                if span & occupied[key]:
                    raise ContractError(f"{ident}: overlapping {key}")
                occupied[key] |= span
            self.modules[ident] = dict(module, article=article, input_bytes=size_i,
                                       output_bytes=size_o, kbus_uid=None,
                                       input_mask=spec["input_mask"], output_mask=spec["output_mask"])
        self.covered_outputs = occupied["output_offset"]
        self.config = copy.deepcopy(config)
        self.config_hash = hashlib.sha256(canonical(config)).hexdigest()
        self.reset()

    def reset(self) -> None:
        """Research cold reset: zero transient data, no retained PLC state exists."""
        self.state = {
            "time_ns": 0, "cycle": 0, "running": False, "bus_ok": True,
            "armed": False, "last_write_ns": None,
            "command_hex": "00" * self.no,
            "input_hex": "00" * self.ni,
            "physical": {k: "00" * m["input_bytes"] for k, m in self.modules.items()},
            "present": {k: True for k in self.modules},
            "frozen": {k: False for k in self.modules},
            "quality": "UNSAMPLED",
        }

    def enumerate(self) -> list[dict[str, Any]]:
        return [dict(m, present=self.state["present"][k],
                     identity_scope="research-metadata-not-WAGO-enumeration")
                for k, m in self.modules.items()]

    def _module(self, module_id: str) -> dict[str, Any]:
        if type(module_id) is not str or module_id not in self.modules:
            raise ContractError("unknown module id")
        return self.modules[module_id]

    def _bus_valid(self) -> bool:
        return self.state["bus_ok"] and all(self.state["present"].values())

    def _expire(self) -> None:
        last = self.state["last_write_ns"]
        if (not self.state["running"] or not self._bus_valid() or
                last is None or self.state["time_ns"] - last >= self.watchdog):
            self.state["armed"] = False

    def run(self, running: bool) -> None:
        if type(running) is not bool:
            raise ContractError("running must be bool")
        self.state["running"] = running
        if not running:
            self.state["armed"] = False

    def set_input(self, module_id: str, data_hex: str) -> None:
        m = self._module(module_id)
        if not m["input_bytes"]:
            raise ContractError("output-only module has no input")
        data = hexbytes(data_hex, m["input_bytes"], "input")
        self._validate_bits(m, data, "input")
        self.state["physical"][module_id] = data.hex()

    @staticmethod
    def _validate_bits(module, data: bytes, direction: str) -> None:
        mask = module[direction + "_mask"]
        if mask is not None and int.from_bytes(data, "little") & ~mask:
            raise Unsupported("nonzero bits outside the model's digital channels")

    def fault(self, kind: str, active: bool, module_id: str | None = None) -> None:
        if type(active) is not bool:
            raise ContractError("active must be bool")
        if kind == "bus_lost":
            if module_id is not None:
                raise ContractError("bus fault must not name module")
            self.state["bus_ok"] = not active
        elif kind in ("missing", "freeze"):
            m = self._module(module_id)
            if kind == "freeze" and not m["input_bytes"]:
                raise ContractError("cannot freeze an output-only module")
            self.state["present" if kind == "missing" else "frozen"][module_id] = (
                not active if kind == "missing" else active)
        else:
            raise Unsupported("unknown fault: inject documented raw diagnostics separately")
        self._expire()

    def advance(self, dt_ns: int) -> dict[str, Any]:
        """Advance OUR clock only. No host/PLC/license time is modified."""
        uint(dt_ns, "dt_ns")
        if self.state["time_ns"] + dt_ns > 2**63-1:
            raise ContractError("virtual clock overflow")
        self.state["time_ns"] += dt_ns
        self._expire()
        return self.observe()

    def cycle(self, outputs_hex: str | None = None) -> dict[str, Any]:
        # Validate the COMPLETE transaction before touching any state.
        out = None if outputs_hex is None else hexbytes(outputs_hex, self.no, "outputs")
        if out is not None and any(v and i not in self.covered_outputs
                                   for i, v in enumerate(out)):
            raise Unsupported("nonzero output in unmapped research-layout gap")
        if out is not None:
            for m in self.modules.values():
                off, size = m["output_offset"], m["output_bytes"]
                self._validate_bits(m, out[off:off+size], "output")
        if self.state["cycle"] == 2**63-1:
            raise ContractError("cycle counter overflow")
        self._expire()
        if out is not None:
            self.state["command_hex"] = out.hex()
            self.state["last_write_ns"] = self.state["time_ns"]
            self.state["armed"] = self.state["running"] and self._bus_valid()
        image = bytearray.fromhex(self.state["input_hex"])
        if self._bus_valid():
            for k, m in self.modules.items():
                n, off = m["input_bytes"], m["input_offset"]
                if n and not self.state["frozen"][k]:
                    image[off:off+n] = bytes.fromhex(self.state["physical"][k])
        self.state["input_hex"] = image.hex()
        self.state["quality"] = ("BUS_FAULT" if not self._bus_valid() else
                                  "FROZEN" if any(self.state["frozen"].values()) else "GOOD")
        self.state["cycle"] += 1
        return self.observe()

    def observe(self) -> dict[str, Any]:
        s = self.state
        return {"time_ns": s["time_ns"], "cycle": s["cycle"],
                "input_hex": s["input_hex"], "input_quality": s["quality"],
                "command_hex": s["command_hex"],
                "effective_hex": s["command_hex"] if s["armed"] else "00" * self.no,
                "armed": s["armed"], "running": s["running"],
                "bus_ok": self._bus_valid(), "config_sha256": self.config_hash,
                "catalog_sha256": self.catalog_hash,
                "evidence_scope": "standalone-model-NOT-original-runtime"}

    def snapshot(self) -> dict[str, Any]:
        return {"format": 2, "model_version": VERSION, "config_sha256": self.config_hash,
                "catalog_sha256": self.catalog_hash,
                "state": copy.deepcopy(self.state)}

    def restore(self, snapshot: dict[str, Any]) -> None:
        """Strict local-model restore; NEVER a PLC or license snapshot."""
        exact_keys(snapshot, {"format", "model_version", "config_sha256", "catalog_sha256", "state"}, "snapshot")
        if (type(snapshot["format"]) is not int or snapshot["format"] != 2 or
                snapshot["model_version"] != VERSION or
                snapshot["config_sha256"] != self.config_hash or
                snapshot["catalog_sha256"] != self.catalog_hash):
            raise ContractError("snapshot format/model/config/catalog mismatch")
        s = snapshot["state"]
        exact_keys(s, set(self.state), "snapshot.state")
        for k in ("time_ns", "cycle"):
            uint(s[k], k)
        for k in ("running", "bus_ok", "armed"):
            if type(s[k]) is not bool:
                raise ContractError(f"{k}: bool required")
        if s["last_write_ns"] is not None:
            uint(s["last_write_ns"], "last_write_ns", s["time_ns"])
        hexbytes(s["command_hex"], self.no, "command_hex")
        hexbytes(s["input_hex"], self.ni, "input_hex")
        for key in ("physical", "present", "frozen"):
            exact_keys(s[key], set(self.modules), key)
        for k, m in self.modules.items():
            physical = hexbytes(s["physical"][k], m["input_bytes"], "physical")
            self._validate_bits(m, physical, "input")
            input_image = bytes.fromhex(s["input_hex"])
            off, size = m["input_offset"], m["input_bytes"]
            self._validate_bits(m, input_image[off:off+size], "input")
            output_image = bytes.fromhex(s["command_hex"])
            off, size = m["output_offset"], m["output_bytes"]
            self._validate_bits(m, output_image[off:off+size], "output")
            if type(s["present"][k]) is not bool or type(s["frozen"][k]) is not bool:
                raise ContractError("present/frozen: bool required")
            if s["frozen"][k] and not m["input_bytes"]:
                raise ContractError("invalid output freeze")
        if s["quality"] not in ("UNSAMPLED", "BUS_FAULT", "FROZEN", "GOOD"):
            raise ContractError("unknown quality")
        command = bytes.fromhex(s["command_hex"])
        if any(v and i not in self.covered_outputs for i, v in enumerate(command)):
            raise ContractError("snapshot contains unmapped nonzero output")
        valid_armed = (s["running"] and s["bus_ok"] and all(s["present"].values())
                       and s["last_write_ns"] is not None and
                       s["time_ns"] - s["last_write_ns"] < self.watchdog)
        if s["armed"] and not valid_armed:
            raise ContractError("inconsistent armed snapshot")
        self.state = copy.deepcopy(s)
