"""One JSON request per line over stdin/stdout; no network or device access."""
import argparse
import json
import sys
from .vio import Rail, ContractError, exact_keys

def dispatch(rail, req):
    if type(req) is not dict or type(req.get("op")) is not str:
        raise ContractError("request must be an object with string op")
    op = req["op"]
    specs = {"enumerate": set(), "observe": set(), "reset": set(), "snapshot": set(),
             "run": {"running"}, "advance": {"dt_ns"}, "input": {"module", "hex"},
             "cycle": {"outputs_hex"}, "restore": {"snapshot"},
             "fault": {"kind", "active", "module"}}
    if op not in specs:
        raise ContractError("unknown operation")
    exact_keys(req, specs[op] | {"op"}, "request")
    if op in ("enumerate", "observe", "reset", "snapshot"):
        return getattr(rail, op)()
    if op == "run": return rail.run(req["running"])
    if op == "advance": return rail.advance(req["dt_ns"])
    if op == "input": return rail.set_input(req["module"], req["hex"])
    if op == "cycle": return rail.cycle(req["outputs_hex"])
    if op == "restore": return rail.restore(req["snapshot"])
    return rail.fault(req["kind"], req["active"], req["module"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    try:
        with open(args.config, encoding="utf-8") as f:
            rail = Rail(json.load(f))
    except (OSError, ValueError, TypeError) as e:
        parser.error(str(e))
    while True:
        line = sys.stdin.buffer.readline(65538)
        if not line: break
        if len(line) > 65536:
            print(json.dumps({"ok": False, "error": "request too large; session closed"}))
            return 2
        try:
            req = json.loads(line)
            result = dispatch(rail, req)
            response = {"ok": True, "result": result}
        except (ContractError, ValueError, TypeError) as e:
            response = {"ok": False, "error": str(e), "error_type": type(e).__name__}
        print(json.dumps(response, sort_keys=True, allow_nan=False), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
