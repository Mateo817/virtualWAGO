#!/bin/sh
# Run only inside an already verified isolated mount/net/IPC/PID namespace,
# with fresh tmpfs /run, hidden host endpoints and an externally bounded child.
# This starts a real private message bus, not an LED service or API substitute.
set -eu
umask 077
[ "$#" -ge 2 ] || exit 64
bus_config=$1
shift
[ -f "$bus_config" ] && [ ! -L "$bus_config" ]
[ ! -e /run/dbus ] && [ ! -L /run/dbus ]
mkdir /run/dbus
bus_pid=
child_pid=
cleanup() {
  trap - EXIT INT TERM
  if [ -n "$child_pid" ]; then
    kill -TERM "$child_pid" 2>/dev/null || true
    wait "$child_pid" 2>/dev/null || true
  fi
  if [ -n "$bus_pid" ]; then
    kill -TERM "$bus_pid" 2>/dev/null || true
    wait "$bus_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT
trap 'exit 143' TERM
trap 'exit 130' INT
unset DBUS_SESSION_BUS_ADDRESS DBUS_STARTER_ADDRESS DBUS_STARTER_BUS_TYPE
DBUS_SYSTEM_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
export DBUS_SYSTEM_BUS_ADDRESS
/usr/bin/dbus-daemon --config-file="$bus_config" --nofork --nopidfile \
  --nosyslog --print-address=3 3>/run/dbus/address \
  >/run/dbus/daemon.log 2>&1 &
bus_pid=$!
ready=0
while [ "$ready" -lt 5 ]; do
  kill -0 "$bus_pid" 2>/dev/null || { cat /run/dbus/daemon.log >&2; exit 70; }
  if [ -s /run/dbus/address ] && [ -S /run/dbus/system_bus_socket ]; then
    break
  fi
  ready=$((ready + 1))
  # The bound FW31 BusyBox sleep accepts only integral seconds.
  sleep 1
done
[ "$ready" -lt 5 ] || exit 70
printf 'PRIVATE_DBUS_READY no_activation_config=1\n'
set +e
"$@" &
child_pid=$!
wait "$child_pid"
child_status=$?
child_pid=
set -e
exit "$child_status"
