#!/usr/bin/env python3
"""List, inspect and exercise our module catalog without device access.

Generated layouts are standalone research byte layouts, not native K-Bus maps.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from prototype.catalog import Catalog
from prototype.contracts import ContractError, Unsupported, exact_keys
from prototype.module_models import Analog466, Pwm677
from prototype.module_simulation import ModuleSimulation
from prototype.vio import Rail


def summarize(catalog: Catalog) -> dict:
    entries = catalog.entries()
    return {
        "revision": catalog.data["revision"], "catalog_sha256": catalog.sha256,
        "scope": "OWN_MODULE_CATALOG_NOT_HARDWARE_INVENTORY",
        "entries": [{"article": e["article"], "variant": e["variant"],
                     "family": e["family"], "channels": e["channels"],
                     "standalone_model": None if e["model"] is None else e["model"]["id"],
                     "historical_native_evidence": e["native_evidence"],
                     "this_revision_native_runtime": "NOT_RUN"} for e in entries],
    }


def demo(catalog: Catalog, article: str) -> dict:
    """Preset stimuli and hardware reactions; no PLC decision algorithm."""
    spec = catalog.model_for_article(article)
    result = {"article": article, "model": spec["id"],
              "catalog_sha256": catalog.sha256,
              "scope": "STANDALONE_MODEL_NOT_NATIVE_RUNTIME_OR_ELECTRICAL_TEST"}
    if spec["codec"] == "pwm677_frq":
        pwm = Pwm677()
        # Complete PWM Frq frame; paired enable at C0/C2, no RegCom.
        frame = bytes.fromhex("01e80300d00701000000204e")
        pwm.apply_output_frame(frame)
        result["closed_gate"] = pwm.observe()
        pwm.set_permit(True)
        pwm.start()
        # A single configuration followed by autonomous model-clock advance.
        pwm.advance(1_000_000_000)
        result["configured_frame_hex"] = frame.hex()
        result["after_one_second_without_new_command"] = pwm.observe()
        pwm.set_permit(False)
        result["after_gate_loss"] = pwm.observe()
        return result
    rail = Rail(catalog.research_layout([article]), catalog=catalog)
    result["initial"] = rail.observe()
    if spec["codec"] == "ai466_standard":
        analog = Analog466()
        analog.set_currents_uA([12_000, 20_000])
        rail.set_input("m0", analog.input_bytes().hex())
        result["currents_uA"] = [12_000, 20_000]
        result["sample"] = rail.cycle()
    elif spec["family"] == "di":
        rail.set_input("m0", spec["input_mask"].to_bytes(spec["input_bytes"], "little").hex())
        result["all_channels_high"] = rail.cycle()
    elif spec["family"] == "do":
        rail.run(True)
        frame = spec["output_mask"].to_bytes(spec["output_bytes"], "little").hex()
        result["all_channels_requested"] = rail.cycle(frame)
        rail.run(False)
        result["after_model_stop"] = rail.observe()
    else:
        raise Unsupported("no bounded behavioral demo for this model")
    return result


def dispatch_simulation(simulation: ModuleSimulation, request: dict) -> dict:
    """Own stdin protocol; no network, runtime management or native APIs."""
    if type(request) is not dict or type(request.get("op")) is not str:
        raise ContractError("request requires a string op")
    operation = request["op"]
    fields = {"observe": set(), "run": {"running"},
              "input": {"module", "value"}, "currents": {"module", "uA"},
              "cycle": {"outputs_hex"}, "advance": {"dt_ns"},
              "fault": {"kind", "active", "module"}}
    if operation not in fields:
        raise Unsupported("unknown standalone simulation operation")
    exact_keys(request, fields[operation] | {"op"}, "request")
    if operation == "run":
        simulation.set_running(request["running"])
    elif operation == "input":
        simulation.set_digital_input(request["module"], request["value"])
    elif operation == "currents":
        simulation.set_currents_uA(request["module"], request["uA"])
    elif operation == "cycle":
        return simulation.cycle(request["outputs_hex"])
    elif operation == "advance":
        return simulation.advance(request["dt_ns"])
    elif operation == "fault":
        return simulation.fault(request["kind"], request["active"], request["module"])
    return simulation.observe()


def simulate_session(simulation: ModuleSimulation) -> int:
    """One bounded JSON request/reply per line, identical to the old CLI limit."""
    stream = sys.stdin.buffer
    while True:
        line = stream.readline(65538)
        if not line:
            return 0
        if len(line) > 65536:
            print(json.dumps({"ok": False, "error": "request too large; session closed"}))
            return 2
        try:
            result = dispatch_simulation(simulation, json.loads(line))
            response = {"ok": True, "result": result}
        except (ContractError, ValueError, TypeError) as error:
            response = {"ok": False, "error": str(error), "error_type": type(error).__name__}
        print(json.dumps(response, sort_keys=True, allow_nan=False), flush=True)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list exact articles and separate support/evidence")
    sub.add_parser("validate", help="strictly validate the bundled catalog")
    for command in ("show", "demo"):
        sub.add_parser(command).add_argument("article")
    layout = sub.add_parser("layout", help="emit an own standalone research layout")
    layout.add_argument("articles", nargs="+")
    simulation = sub.add_parser("simulate", help="run mixed own module models over stdin JSON lines")
    simulation.add_argument("articles", nargs="+")
    simulation.add_argument("--watchdog-ns", type=int, default=100_000_000,
                            help="own logical lease duration; not WAGO watchdog semantics")
    args = parser.parse_args(argv)
    try:
        catalog = Catalog()
        if args.command == "simulate":
            return simulate_session(ModuleSimulation(args.articles, args.watchdog_ns))
        if args.command == "list":
            result = summarize(catalog)
        elif args.command == "validate":
            result = {"result": "PASS_FOR_CATALOG_SCHEMA_ONLY", "catalog_sha256": catalog.sha256,
                      "entries": len(catalog.entries()), "standalone_models": len(catalog.model_specs),
                      "native_runtime": "NOT_RUN"}
        elif args.command == "show":
            result = catalog.entry(args.article)
        elif args.command == "layout":
            result = catalog.research_layout(args.articles)
        else:
            result = demo(catalog, args.article)
    except (ContractError, OSError, ValueError, TypeError) as error:
        print(json.dumps({"ok": False, "error": str(error), "error_type": type(error).__name__}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
