"""Catalog-backed composition of standalone module signal models.

This is an own research simulation over :class:`prototype.vio.Rail`. It does
not run PLC decisions, identify hardware, or claim native ADI/runtime byte
contracts. Inputs and output reactions are supplied by individual module
models; modules without a bounded behavior model stay explicitly unsupported.
"""
from __future__ import annotations

from typing import Any

from .catalog import Catalog
from .contracts import ContractError, Unsupported, hexbytes, uint
from .module_models import Analog466, Pwm677
from .vio import Rail, decode_pwm677_frq

_MAX_TIME_NS = 2**63 - 1


class ModuleSimulation:
    """Compose a consecutive research layout with per-instance behaviors.

    Instances use stable names ``m0`` ... ``mN`` in the order of ``articles``;
    repeated articles are separate models. The bundled catalog digest is
    surfaced in every observation. A complete output frame is validated in
    full before any model or rail state changes. PWM runs autonomously between
    frame writes and shares the Rail's logical watchdog lease.

    Snapshot/restore is deliberately unsupported: Rail snapshots alone cannot
    capture helper-model phases, pulse counts, and gates as one atomic state.
    """

    def __init__(self, articles: list[str], watchdog_ns: int = 100_000_000):
        self._catalog = Catalog()
        config = self._catalog.research_layout(articles, watchdog_ns)
        self._rail = Rail(config, catalog=self._catalog)
        self._catalog_hash = self._catalog.sha256
        self._watchdog_ns = config["watchdog_ns"]
        self._modules: dict[str, dict[str, Any]] = {}
        self._analog: dict[str, Analog466] = {}
        self._currents_uA: dict[str, tuple[int, int]] = {}
        self._pwm: dict[str, Pwm677] = {}
        self._digital_inputs: dict[str, int] = {}
        self._lease_deadline_ns: int | None = None
        self._cycles = 0

        for module_id, module in self._rail.modules.items():
            article = module["article"]
            spec = self._catalog.model_for_article(article)
            codec = spec["codec"]
            record = {
                "article": article,
                "model": spec["id"],
                "codec": codec,
                "input_offset": module["input_offset"],
                "output_offset": module["output_offset"],
                "input_bytes": module["input_bytes"],
                "output_bytes": module["output_bytes"],
                "input_mask": module["input_mask"],
                "output_mask": module["output_mask"],
            }
            self._modules[module_id] = record
            if codec == "ai466_standard":
                self._analog[module_id] = Analog466()
                self._currents_uA[module_id] = (4000, 4000)
            elif codec == "pwm677_frq":
                self._pwm[module_id] = Pwm677()
            elif codec == "digital" and module["input_bytes"]:
                self._digital_inputs[module_id] = 0

    def _module(self, instance: str) -> dict[str, Any]:
        if type(instance) is not str or instance not in self._modules:
            raise ContractError("unknown module instance")
        return self._modules[instance]

    def set_running(self, running: bool) -> None:
        if type(running) is not bool:
            raise ContractError("running must be bool")
        self._rail.run(running)
        if not running:
            self._lease_deadline_ns = None
            for model in self._pwm.values():
                model.set_permit(False)

    def set_digital_input(self, instance: str, value: int) -> None:
        module = self._module(instance)
        if (module["codec"] != "digital" or not module["input_bytes"]):
            raise Unsupported("instance has no modeled digital input")
        if type(value) is not int or value < 0 or value & ~module["input_mask"]:
            raise ContractError("digital input value exceeds modeled channels")
        # Validation is complete before the rail's physical input is changed.
        data = value.to_bytes(module["input_bytes"], "little")
        self._rail.set_input(instance, data.hex())
        self._digital_inputs[instance] = value

    def set_currents_uA(self, instance: str, currents_uA) -> None:
        self._module(instance)
        if instance not in self._analog:
            raise Unsupported("instance has no modeled 750-466 analog input")
        # Analog466 validates the complete pair before replacing its state.
        self._analog[instance].set_currents_uA(currents_uA)
        self._currents_uA[instance] = tuple(currents_uA)

    def _validate_output_frame(self, outputs_hex: str | None) -> bytes | None:
        if self._cycles >= _MAX_TIME_NS:
            raise ContractError("cycle counter overflow")
        if outputs_hex is None:
            return None
        frame = hexbytes(outputs_hex, self._rail.no, "outputs")
        occupied = self._rail.covered_outputs
        if any(value and offset not in occupied for offset, value in enumerate(frame)):
            raise Unsupported("nonzero output in unmapped research-layout gap")
        for instance, module in self._modules.items():
            size = module["output_bytes"]
            if not size:
                continue
            start = module["output_offset"]
            payload = frame[start:start + size]
            mask = module["output_mask"]
            if mask is not None and int.from_bytes(payload, "little") & ~mask:
                raise Unsupported("nonzero bits outside the model's digital channels")
            if instance in self._pwm:
                # Decode every PWM slice before any output or input mutation.
                decode_pwm677_frq(payload)
        return frame

    def _sync_permit(self, armed: bool) -> None:
        for model in self._pwm.values():
            model.set_permit(armed)
        if not armed:
            self._lease_deadline_ns = None

    def cycle(self, outputs_hex: str | None = None) -> dict[str, Any]:
        # Validate the full output transaction first, including every PWM
        # decoder. Only after this point can helpers or the Rail be mutated.
        frame = self._validate_output_frame(outputs_hex)
        analog_frames = {instance: model.input_bytes()
                         for instance, model in self._analog.items()}

        for instance, data in analog_frames.items():
            self._rail.set_input(instance, data.hex())
        rail_result = self._rail.cycle(None if frame is None else frame.hex())
        self._cycles += 1

        now_ns = rail_result["time_ns"]
        armed = bool(rail_result["armed"])
        self._sync_permit(armed)
        if frame is not None:
            if armed:
                self._lease_deadline_ns = now_ns + self._watchdog_ns
            for instance, model in self._pwm.items():
                module = self._modules[instance]
                start = module["output_offset"]
                payload = frame[start:start + module["output_bytes"]]
                model.apply_output_frame(payload)
                # Every accepted Rail frame is complete. It can rearm a PWM
                # instance only when the Rail itself is running and healthy.
                if armed:
                    model.start()
        return self.observe()

    def advance(self, dt_ns: int) -> dict[str, Any]:
        if type(dt_ns) is not int or dt_ns < 0:
            raise ContractError("dt_ns: expected a nonnegative integer")
        now_ns = self._rail.state["time_ns"]
        if now_ns + dt_ns > _MAX_TIME_NS:
            raise ContractError("logical clock overflow")

        # Integrate PWM only while the current complete-frame lease is valid.
        # At its exact deadline the gate closes, then model time continues with
        # frequency zero. This matches repeated advances at the same boundary.
        active_ns = dt_ns
        if self._lease_deadline_ns is not None:
            active_ns = min(dt_ns, max(0, self._lease_deadline_ns - now_ns))
        if active_ns:
            for model in self._pwm.values():
                model.advance(active_ns)
        remainder_ns = dt_ns - active_ns
        if remainder_ns:
            if self._lease_deadline_ns is not None and active_ns < dt_ns:
                self._sync_permit(False)
            for model in self._pwm.values():
                model.advance(remainder_ns)

        self._rail.advance(dt_ns)
        rail_state = self._rail.observe()
        self._sync_permit(bool(rail_state["armed"]))
        if not rail_state["armed"]:
            self._lease_deadline_ns = None
        return self.observe()

    def fault(self, kind: str, active: bool, instance: str | None = None) -> dict[str, Any]:
        if type(active) is not bool:
            raise ContractError("active must be bool")
        if kind == "bus_lost":
            if instance is not None:
                raise ContractError("bus fault must not name a module instance")
            module_id = None
        elif kind in ("missing", "freeze"):
            if instance is None:
                raise ContractError("module fault requires an instance")
            module = self._module(instance)
            if kind == "freeze" and not module["input_bytes"]:
                raise ContractError("cannot freeze an output-only module")
            module_id = instance
        else:
            raise Unsupported("unknown fault: inject documented raw diagnostics separately")

        self._rail.fault(kind, active, module_id)
        armed = bool(self._rail.observe()["armed"])
        self._sync_permit(armed)
        return self.observe()

    def observe(self) -> dict[str, Any]:
        rail = self._rail.observe()
        input_image = bytes.fromhex(rail["input_hex"])
        command = bytes.fromhex(rail["command_hex"])
        effective = bytes.fromhex(rail["effective_hex"])
        modules: dict[str, dict[str, Any]] = {}
        for instance, module in self._modules.items():
            result: dict[str, Any] = {
                "article": module["article"],
                "model": module["model"],
                "codec": module["codec"],
            }
            if instance in self._analog:
                result["input_status"] = ("GENERATED_OWN_RESEARCH_LAYOUT" if self._cycles
                                           else "NOT_SAMPLED")
                result["currents_uA"] = list(self._currents_uA[instance])
                if self._cycles:
                    offset, size = module["input_offset"], module["input_bytes"]
                    result["input_bytes_hex"] = input_image[offset:offset + size].hex()
            elif instance in self._pwm:
                result["input_status"] = "NOT_GENERATED"
                result["behavior"] = self._pwm[instance].observe()
            elif module["input_bytes"]:
                result["input_status"] = ("DIGITAL_RESEARCH_INPUT" if self._cycles
                                           else "NOT_SAMPLED")
                result["requested_input_value"] = self._digital_inputs[instance]
                if self._cycles:
                    offset, size = module["input_offset"], module["input_bytes"]
                    result["input_bytes_hex"] = input_image[offset:offset + size].hex()
            if module["output_bytes"]:
                offset, size = module["output_offset"], module["output_bytes"]
                result["requested_output_hex"] = command[offset:offset + size].hex()
                result["effective_output_hex"] = effective[offset:offset + size].hex()
            modules[instance] = result
        return {
            "rail": rail,
            "modules": modules,
            "catalog_sha256": self._catalog_hash,
            "scope": "OWN catalog-backed module simulation; no PLC decisions or native runtime claim",
        }

    def snapshot(self):
        raise Unsupported("ModuleSimulation snapshot/restore is not supported as one atomic model state")

    def restore(self, snapshot):
        raise Unsupported("ModuleSimulation snapshot/restore is not supported as one atomic model state")
