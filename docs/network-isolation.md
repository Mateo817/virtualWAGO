# Reference-target network guard

`tools/reference_netns.py` is a per-process Linux egress guard for a future
reference-device session. It is separate from the hardware-free emulator and
does not implement the broader safety contract in [safety.md](safety.md).

The default invocation is read-only: it validates a private policy and prints
a sanitized plan. It does not create a namespace, configure an interface, or
attempt a connection. The private handoff uses the versioned
`virtualwago-local-authorization/1` authorization schema, which includes the
two target arrays below and documented owner/context metadata. The tool checks
that metadata against the known schema, but only `allowed_reference_ipv4`
creates permits. Metadata such as inventory authority or software-install
authority does not widen network access. A minimal two-field policy is accepted
for synthetic tests and generic use. Actual device sessions require the
owner-authorized local policy under [safety.md](safety.md); accepting a minimal
file does not establish authorization. Do not publish the actual local policy.

```json
{
  "allowed_reference_ipv4": ["<owner-local RFC1918 IPv4>"],
  "protected_ipv4": ["<protected RFC1918 IPv4>"]
}
```

Only exact IPv4 addresses are accepted. Hostnames, subnets, IPv6, malformed or
duplicate entries and duplicate JSON keys, non-RFC1918 allowed targets, overlap
between allowed and protected addresses, unsupported schema versions, and
unexpected metadata fields fail closed. Protected addresses are validated and
counted in the plan but never emitted as permits. Plan output omits both target
values and complete nftables rules by default. `--show-targets` reveals the
private values for a local, unshared review; do not capture that output in
public logs or artifacts.

Example plan command:

```sh
python3 tools/reference_netns.py --policy target-policy.local.json \
  --allow-tcp-port 22 --allow-tcp-port 443
```

Use `--show-targets` only when the full local rule text is needed for review.

The execution form places the command in a fresh user and network namespace,
installs an `inet` output chain with default drop, then starts
`slirp4netns --configure --disable-host-loopback`. Its only permits are TCP to
the exact allowlisted addresses and explicitly selected known ports 22, 80,
and 443. With no selected ports, there are no permits. The payload runs through
`setpriv` after dropping its capability bounding, inheritable, and ambient
sets and setting no-new-privileges. Processes are terminated if setup fails.
The internal worker verifies that it is in distinct user and network
namespaces, that the launcher remains outside them, and that namespace root is
mapped only to the launching user and group before invoking nftables. The nft
binary is resolved from trusted system paths before `PATH` lookup.
For example, after reviewing the rendered plan:

```sh
python3 tools/reference_netns.py --policy target-policy.local.json \
  --allow-tcp-port 22 -- ssh -o BatchMode=yes <reviewed-user>@<reviewed-target>
```

Interactive SSH/password prompting is unsupported; use a separately protected
local credential mechanism and noninteractive commands. Do not put passwords,
keys, or private target values in command arguments, shell history, repository
files, or logs. The tool does not verify device
identity, SSH host keys, routes outside the namespace, physical isolation, or
the owner’s approval. Exact IP allowlisting is not sufficient authorization
for a deployment. Commands still see the host filesystem permitted to their
mapped user; this is a network guard, not a general-purpose VM or filesystem
sandbox. slirp4netns remains a host process that mediates namespace traffic.
Host Unix sockets, proxies, and readable client/autostart configurations are
outside this tool's filesystem boundary. Use only reviewed reference commands
without agent forwarding, host socket access, proxies, redirects, or automatic
device clients. Do not launch an original runtime with this guard alone: its
separate filesystem/device/IPC isolation remains an M3/M4 prerequisite.

`--self-test` runs a separate active test after setting up the guard. It creates
a listener on namespace loopback and verifies that a local TCP connection is
dropped and the nftables output counter increments. It contacts no external
address and does not use the private allowed targets. This tests one local
kernel egress path; it does not prove device identity, all routes, all protocol
families, resistance to kernel or helper compromise, or safety of a particular
network. Do not describe isolation as verified until that self-test is actually
run on the intended host and its version/configuration/result are recorded.

## Evidence for this revision

Recorded 2026-10-11 against repository base revision `0bdddbf77d688fd9e1cce7165d718fa6a30efe2c`, with guard source SHA-256 `6690ab0e9ee66abd56adf43e7cf1219e034127114e33eb91a5a9732ef20921f3`. The local `virtualwago-local-authorization/1` policy contained one allowed reference entry and one protected entry; values are omitted:

- Policy parser, metadata validation, duplicate-key rejection, sanitized plan,
  and host-namespace rejection tests: **PASS**, 8 tests. `py_compile` and
  `git diff --check`: **PASS**.
- Kernel self-test: **PASS**. Loopback listener was not reached and the
  namespace nftables output counter incremented. No external or protected
  destination was contacted.
- Guarded `/bin/true` with TCP port 22 explicitly selected: **PASS**, exit 0.
  The command made no network request.
- Capability check: **PASS**. Inside a separate guarded namespace,
  `/usr/sbin/ip link set lo down` was denied (exit 2), confirming the payload
  lacked the namespace network-administration capability.
- Cleanup: **PASS**. No slirp4netns process from either guarded run remained.
- Environment: Python 3.13.5, nftables 1.1.3, slirp4netns 1.2.1 with libslirp
  4.8.0, Linux `6.12.111+deb13-cloud-amd64`.

This is local kernel evidence for the tested guard revision/configuration. It
does not verify a device route or identity and is not evidence of contact with
any hardware. The guard does not alter global firewall or routing rules; its
nftables table is created only after entering the new network namespace.
