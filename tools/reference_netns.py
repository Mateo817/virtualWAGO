#!/usr/bin/env python3
"""Render or use a narrowly allowlisted, per-process IPv4 egress namespace.

The default invocation only validates the private policy and prints a plan. It
does not create namespaces, configure networking, or open network sockets.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import os
from pathlib import Path
import selectors
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Any, Sequence


ALLOWED_POLICY_KEYS = {"allowed_reference_ipv4", "protected_ipv4"}
LOCAL_POLICY_SCHEMA = "virtualwago-local-authorization/1"
LOCAL_POLICY_METADATA_KEYS = {
    "schema", "nature", "issued_date", "protected_access", "private_network_default",
    "local_development_infrastructure", "credentials_file", "password_change_allowed",
    "reference_read_only_inventory_authorized", "plc_gateway_software_installation",
    "requires_separate_scoped_authorization", "hardware_in_ci", "reference_identity_observed",
    "physical_actuator_isolation_observed", "target_policy_enforced_and_tested", "reference_model",
    "reference_firmware", "reference_runtime", "reference_ssh_host_key_fingerprint", "open_tasks",
}
ALLOWED_TCP_PORTS = {22, 80, 443}
RFC1918 = tuple(ipaddress.ip_network(x) for x in ("10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"))
NFT_TABLE = "reference_guard"


class PolicyError(ValueError):
    """The private target policy is invalid or unsafe to interpret."""


def _ipv4_list(value: Any, field: str) -> list[ipaddress.IPv4Address]:
    if not isinstance(value, list) or not value:
        raise PolicyError(f"{field} must be a non-empty JSON array of exact IPv4 addresses")
    result: list[ipaddress.IPv4Address] = []
    for item in value:
        if not isinstance(item, str) or item != item.strip():
            raise PolicyError(f"{field} entries must be canonical IPv4 address strings")
        try:
            address = ipaddress.ip_address(item)
        except ValueError as exc:
            raise PolicyError(f"{field} contains a hostname, subnet, or invalid address") from exc
        if not isinstance(address, ipaddress.IPv4Address):
            raise PolicyError(f"{field} must contain IPv4 only")
        if str(address) != item:
            raise PolicyError(f"{field} entries must use canonical IPv4 spelling")
        if field == "allowed_reference_ipv4" and not any(address in network for network in RFC1918):
            raise PolicyError(f"{field} entries must be RFC1918 owner-local IPv4 addresses")
        if address.is_unspecified or address.is_multicast or address.is_loopback or address.is_link_local:
            raise PolicyError(f"{field} contains a non-unicast local/special-purpose address")
        result.append(address)
    if len(set(result)) != len(result):
        raise PolicyError(f"{field} contains duplicate addresses")
    return result


def load_policy(path: str | os.PathLike[str]) -> dict[str, list[str]]:
    """Load either the minimal test schema or the known private authorization schema."""
    policy_path = Path(path)
    try:
        raw = policy_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise PolicyError(f"cannot read local target policy {policy_path}: {exc.strerror or exc}") from exc
    try:
        data = json.loads(raw, object_pairs_hook=_unique_json_object)
    except PolicyError:
        raise
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise PolicyError("target policy must be valid UTF-8 JSON") from exc
    if not isinstance(data, dict):
        raise PolicyError("target policy must be a JSON object")
    keys = set(data)
    if keys == ALLOWED_POLICY_KEYS:
        pass
    elif keys == ALLOWED_POLICY_KEYS | LOCAL_POLICY_METADATA_KEYS:
        _validate_local_authorization_metadata(data)
    else:
        raise PolicyError("target policy has an unsupported schema or unexpected/missing fields")
    allowed = _ipv4_list(data["allowed_reference_ipv4"], "allowed_reference_ipv4")
    protected = _ipv4_list(data["protected_ipv4"], "protected_ipv4")
    overlap = set(allowed) & set(protected)
    if overlap:
        raise PolicyError("allowed_reference_ipv4 overlaps protected_ipv4")
    return {
        "allowed_reference_ipv4": [str(x) for x in allowed],
        "protected_ipv4": [str(x) for x in protected],
    }


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise PolicyError(f"target policy contains duplicate JSON key: {key}")
        result[key] = value
    return result


def _validate_local_authorization_metadata(data: dict[str, Any]) -> None:
    """Validate known context fields, without treating them as added network grants."""
    if data.get("schema") != LOCAL_POLICY_SCHEMA:
        raise PolicyError("unsupported local authorization schema")
    required_literals = {
        "nature": "OWNER_INSTRUCTION_ONLY_NOT_AN_ENFORCED_NETWORK_CONTROL",
        "protected_access": "DENY_ALL_INCLUDING_READ_ONLY_DISCOVERY_AND_TRANSITIVE_ACCESS",
        "private_network_default": "DENY_EXCEPT_EXPLICITLY_AUTHORIZED_REFERENCE_TARGET",
    }
    for field, expected in required_literals.items():
        if data.get(field) != expected:
            raise PolicyError(f"local authorization has unexpected {field}")
    for field in ("issued_date", "local_development_infrastructure", "credentials_file"):
        if not isinstance(data.get(field), str) or not data[field]:
            raise PolicyError(f"local authorization {field} must be a non-empty string")
    bool_fields = (
        "password_change_allowed", "reference_read_only_inventory_authorized", "hardware_in_ci",
        "reference_identity_observed", "physical_actuator_isolation_observed",
        "target_policy_enforced_and_tested",
    )
    if any(type(data.get(field)) is not bool for field in bool_fields):
        raise PolicyError("local authorization boolean metadata has an invalid type")
    if data["password_change_allowed"] or data["hardware_in_ci"]:
        raise PolicyError("local authorization metadata conflicts with the guard's operating limits")
    install = data.get("plc_gateway_software_installation")
    if (not isinstance(install, dict)
            or set(install) != {"authorized_on_reference_only", "requires"}
            or type(install.get("authorized_on_reference_only")) is not bool
            or not isinstance(install.get("requires"), list)
            or any(not isinstance(item, str) for item in install["requires"])):
        raise PolicyError("local authorization PLC installation metadata is malformed")
    separate = data.get("requires_separate_scoped_authorization")
    if not isinstance(separate, list) or any(not isinstance(item, str) for item in separate):
        raise PolicyError("local authorization separate-approval metadata is malformed")
    for field in ("reference_model", "reference_firmware", "reference_runtime",
                  "reference_ssh_host_key_fingerprint"):
        if data.get(field) is not None and not isinstance(data[field], str):
            raise PolicyError(f"local authorization {field} must be a string or null")
    if not isinstance(data.get("open_tasks"), list) or any(
            not isinstance(item, str) for item in data["open_tasks"]):
        raise PolicyError("local authorization open_tasks must be a string array")


def _verify_namespace_context(outer: dict[str, Any]) -> None:
    """Require namespaces distinct from the launching process and a single ID map."""
    try:
        current_netns = os.stat("/proc/self/ns/net").st_ino
        current_userns = os.stat("/proc/self/ns/user").st_ino
        uid_map = Path("/proc/self/uid_map").read_text(encoding="ascii").split()
        gid_map = Path("/proc/self/gid_map").read_text(encoding="ascii").split()
    except OSError as exc:
        raise RuntimeError(f"cannot verify namespace context: {exc.strerror or exc}") from exc
    try:
        outer_netns = int(outer["netns_inode"])
        outer_userns = int(outer["userns_inode"])
        outer_uid = int(outer["uid"])
        outer_gid = int(outer["gid"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError("launcher did not provide valid namespace context") from exc
    if current_netns == outer_netns or current_userns == outer_userns:
        raise RuntimeError("internal worker requires network and user namespaces distinct from its launcher")
    if uid_map != ["0", str(outer_uid), "1"]:
        raise RuntimeError("worker user namespace must map only namespace root to its launcher UID")
    if gid_map != ["0", str(outer_gid), "1"]:
        raise RuntimeError("worker user namespace must map only namespace root to its launcher GID")


def validate_ports(ports: Sequence[int]) -> list[int]:
    if len(set(ports)) != len(ports):
        raise PolicyError("TCP port list contains duplicates")
    if any(port not in ALLOWED_TCP_PORTS for port in ports):
        raise PolicyError("only explicitly selected TCP ports 22, 80, and 443 are supported")
    return sorted(ports)


def nft_rules(policy: dict[str, list[str]], ports: Sequence[int]) -> str:
    """Return an nftables table scoped to the fresh network namespace."""
    ports = validate_ports(ports)
    lines = [
        f"table inet {NFT_TABLE} {{",
        "  chain output {",
        "    type filter hook output priority 0; policy drop;",
        "    counter comment \"guard_observed_egress\"",
    ]
    if ports:
        port_expr = ", ".join(str(p) for p in ports)
        for address in policy["allowed_reference_ipv4"]:
            lines.append(f"    ip daddr {address} tcp dport {{ {port_expr} }} accept")
    lines.extend(["  }", "}", ""])
    return "\n".join(lines)


def plan(policy: dict[str, list[str]], ports: Sequence[int], include_targets: bool = False) -> dict[str, Any]:
    ports = validate_ports(ports)
    return {
        "status": "PLAN_ONLY",
        "setup_performed": False,
        "network_access_attempted": False,
        "namespace": "new unshared user + network namespace",
        "target_policy": "local exact IPv4 allowlist; protected entries are never emitted as permits",
        "allowed_reference_ipv4_count": len(policy["allowed_reference_ipv4"]),
        "protected_ipv4_count": len(policy["protected_ipv4"]),
        "target_values_shown": include_targets,
        "allowed_tcp_ports": ports,
        "slirp4netns": "--configure --disable-host-loopback",
        "egress_default": "drop",
        "nftables": nft_rules(policy, ports) if include_targets else None,
        "nftables_summary": "default drop; selected TCP ports to exact allowed targets only",
        "evidence": "NOT_RUN: plan rendering does not establish kernel isolation",
    }


def _command(name: str) -> str:
    trusted_paths = {
        "nft": (Path("/usr/sbin/nft"), Path("/sbin/nft")),
        "ip": (Path("/usr/sbin/ip"), Path("/sbin/ip")),
        "unshare": (Path("/usr/bin/unshare"), Path("/bin/unshare")),
        "slirp4netns": (Path("/usr/bin/slirp4netns"), Path("/usr/sbin/slirp4netns")),
        "setpriv": (Path("/usr/bin/setpriv"), Path("/bin/setpriv")),
    }
    for trusted in trusted_paths.get(name, ()):
        if trusted.is_file() and os.access(trusted, os.X_OK):
            return str(trusted)
    path = shutil.which(name)
    if not path:
        raise RuntimeError(f"required command not found: {name}")
    return path


def _terminate_group(proc: subprocess.Popen[bytes]) -> None:
    """Stop a helper and descendants created in its private process group."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


def _run_nft(rules: str) -> None:
    result = subprocess.run([_command("nft"), "-f", "-"], input=rules, text=True,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"namespace nftables setup failed: {result.stderr.strip()}")


def _bring_loopback_up() -> None:
    result = subprocess.run([_command("ip"), "link", "set", "lo", "up"],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"could not bring namespace loopback up: {result.stderr.strip()}")


def _self_test() -> None:
    """Prove a loopback TCP connect is dropped by this namespace's output hook."""
    # A local listener makes the test meaningful: without the guard connect()
    # would succeed. No TEST-NET or real device address is contacted.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", 0))
    server.listen(1)
    port = server.getsockname()[1]
    reached = threading.Event()

    def accept_once() -> None:
        server.settimeout(0.7)
        try:
            connection, _ = server.accept()
        except (TimeoutError, socket.timeout):
            return
        reached.set()
        connection.close()

    listener = threading.Thread(target=accept_once, daemon=True)
    listener.start()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(0.2)
    try:
        try:
            client.connect(("127.0.0.1", port))
        except (TimeoutError, socket.timeout, OSError):
            pass
        else:
            raise RuntimeError("self-test FAIL: loopback listener was reachable")
    finally:
        client.close()
        listener.join(timeout=1.0)
        server.close()
    if reached.is_set():
        raise RuntimeError("self-test FAIL: loopback TCP reached the local listener")

    result = subprocess.run([_command("nft"), "-j", "list", "chain", "inet", NFT_TABLE, "output"],
                            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if result.returncode:
        raise RuntimeError(f"self-test cannot inspect nft counter: {result.stderr.strip()}")
    try:
        payload = json.loads(result.stdout)
        counters = [item.get("rule", {}).get("expr", []) for item in payload.get("nftables", [])]
        observed = any(
            expr.get("counter", {}).get("packets", 0) >= 1
            for row in counters for expr in row if isinstance(expr, dict)
        )
    except (json.JSONDecodeError, TypeError, AttributeError) as exc:
        raise RuntimeError("self-test could not parse nftables counter evidence") from exc
    if not observed:
        raise RuntimeError("self-test FAIL: no output-hook packet counter increment was observed")
    print(json.dumps({
        "status": "PASS",
        "scope": "local loopback TCP denied by nftables output hook",
        "listener_reached": False,
        "kernel_counter_incremented": True,
        "protected_target_contacted": False,
        "external_destination_contacted": False,
    }, sort_keys=True))


def _namespace_worker(args: argparse.Namespace) -> int:
    try:
        control = os.fdopen(args.control_fd, "r", encoding="ascii")
        try:
            try:
                outer_context = json.loads(control.readline())
            except (json.JSONDecodeError, UnicodeError) as exc:
                raise RuntimeError("launcher namespace context is missing or invalid") from exc
            _verify_namespace_context(outer_context)
            # Install the default-drop hook while the fresh namespace still has no
            # configured link. Only then tell the parent it may start slirp4netns.
            policy = load_policy(args.policy)
            _run_nft(nft_rules(policy, args.port))
            _bring_loopback_up()
            print(f"READY {os.getpid()}", flush=True)
            go = control.readline().strip()
        finally:
            control.close()
        if go != "GO":
            raise RuntimeError("parent did not authorize network configuration")
        if args.self_test:
            _self_test()
            return 0
        command = ["setpriv", "--bounding-set=-all", "--inh-caps=-all", "--ambient-caps=-all",
                   "--no-new-privs", "--", *args.command]
        os.execv(_command("setpriv"), command)
    except Exception as exc:
        print(f"reference_netns: {exc}", file=sys.stderr, flush=True)
        return 2
    return 0


def execute(policy_path: str, ports: Sequence[int], command: Sequence[str] | None,
            self_test: bool = False) -> int:
    """Run a command under the guard, or run its local kernel-drop self-test."""
    if not self_test and not command:
        raise PolicyError("execution requires a command after -- or --self-test")
    validate_ports(ports)
    # Validate before invoking unshare; the worker re-reads the policy from its
    # local path immediately before installing the guard.
    load_policy(policy_path)
    unshare = _command("unshare")
    slirp = _command("slirp4netns")
    worker = str(Path(__file__).resolve())
    outer_context = {
        "netns_inode": os.stat("/proc/self/ns/net").st_ino,
        "userns_inode": os.stat("/proc/self/ns/user").st_ino,
        "uid": os.getuid(),
        "gid": os.getgid(),
    }
    control_read, control_write = os.pipe()
    ns_command = [unshare, "--user", "--map-root-user", "--net", "--fork", sys.executable,
                  worker, "--_worker", "--control-fd", str(control_read), "--policy",
                  str(Path(policy_path).resolve())]
    for port in ports:
        ns_command.extend(["--allow-tcp-port", str(port)])
    if self_test:
        ns_command.append("--self-test")
    else:
        ns_command.extend(["--", *(command or [])])

    try:
        ns = subprocess.Popen(ns_command, stdout=subprocess.PIPE, stderr=None, bufsize=0,
                              start_new_session=True, close_fds=True, pass_fds=(control_read,))
    except Exception:
        os.close(control_read)
        os.close(control_write)
        raise
    os.close(control_read)
    slirp_process: subprocess.Popen[bytes] | None = None
    ready_read: int | None = None
    ready_write: int | None = None
    try:
        os.write(control_write, json.dumps(outer_context, separators=(",", ":")).encode("ascii") + b"\n")
        selector = selectors.DefaultSelector()
        selector.register(ns.stdout, selectors.EVENT_READ)
        ready_buffer = bytearray()
        deadline = time.monotonic() + 15
        while b"\n" not in ready_buffer:
            remaining = deadline - time.monotonic()
            if remaining <= 0 or not selector.select(remaining):
                raise RuntimeError("namespace guard did not become ready")
            chunk = os.read(ns.stdout.fileno(), 4096)
            if not chunk:
                raise RuntimeError(f"namespace guard exited before readiness (status {ns.poll()})")
            ready_buffer.extend(chunk)
        ready_line, _, trailing = ready_buffer.partition(b"\n")
        parts = ready_line.decode("ascii", errors="replace").split()
        if len(parts) != 2 or parts[0] != "READY" or not parts[1].isdigit():
            raise RuntimeError("namespace worker returned an invalid readiness message")
        worker_pid = parts[1]
        if not self_test:
            print(f"reference_netns: guarded namespace ready; slirp target PID {worker_pid}", file=sys.stderr)
        ready_read, ready_write = os.pipe()
        slirp_process = subprocess.Popen(
            [slirp, "--configure", "--disable-host-loopback", "--ready-fd", str(ready_write),
             worker_pid, "tap0"],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=None,
            start_new_session=True, close_fds=True, pass_fds=(ready_write,),
        )
        os.close(ready_write)
        ready_write = None
        ready_selector = selectors.DefaultSelector()
        ready_selector.register(ready_read, selectors.EVENT_READ)
        if not ready_selector.select(15):
            raise RuntimeError("slirp4netns did not report configured networking")
        if not os.read(ready_read, 1):
            raise RuntimeError(f"slirp4netns exited before network readiness (status {slirp_process.poll()})")
        os.close(ready_read)
        ready_read = None
        os.write(control_write, b"GO\n")
        os.close(control_write)
        control_write = -1
        if trailing:
            sys.stdout.buffer.write(trailing)
            sys.stdout.buffer.flush()
        assert ns.stdout is not None
        while True:
            chunk = os.read(ns.stdout.fileno(), 4096)
            if not chunk:
                break
            sys.stdout.buffer.write(chunk)
            sys.stdout.buffer.flush()
        return ns.wait()
    finally:
        for fd in (ready_read, ready_write, control_write):
            if fd is not None and fd >= 0:
                os.close(fd)
        for proc in (slirp_process, ns):
            if proc is not None:
                _terminate_group(proc)
        for proc in (slirp_process, ns):
            if proc is not None:
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    try:
                        os.killpg(proc.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    proc.wait(timeout=2)


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--policy", default="target-policy.local.json",
                        help="private local exact-target policy JSON (default: %(default)s)")
    parser.add_argument("--allow-tcp-port", action="append", type=int, choices=sorted(ALLOWED_TCP_PORTS),
                        dest="port", default=[], metavar="{22,80,443}",
                        help="explicitly permit this TCP port to listed reference IPv4 targets")
    parser.add_argument("--self-test", action="store_true",
                        help="execute the guarded local-loopback drop test; contacts no external target")
    parser.add_argument("--show-targets", action="store_true",
                        help="include private target addresses and complete nftables rules in plan output")
    parser.add_argument("--_worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--control-fd", type=int, help=argparse.SUPPRESS)
    parser.add_argument("command", nargs=argparse.REMAINDER,
                        help="command to run inside the guard after --")
    args = parser.parse_args(argv)
    if args.command and args.command[0] == "--":
        args.command = args.command[1:]
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args._worker:
            return _namespace_worker(args)
        policy = load_policy(args.policy)
        if args.self_test:
            if args.show_targets:
                raise PolicyError("--show-targets is only valid for a read-only plan")
            return execute(args.policy, args.port, None, self_test=True)
        if args.command:
            if args.show_targets:
                raise PolicyError("--show-targets is only valid for a read-only plan")
            return execute(args.policy, args.port, args.command)
        print(json.dumps(plan(policy, args.port, include_targets=args.show_targets), indent=2, sort_keys=True))
        return 0
    except (PolicyError, RuntimeError, OSError) as exc:
        print(f"reference_netns: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
