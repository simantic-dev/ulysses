#!/bin/sh
# Runs the committed Ulysses-FC firmware (sim/fw/*.hex, both cores) on the simulator and checks it:
#  1. main firmware, 0.3 s: both cores reach StartDefaultTask, no fault/assert handler is hit.
#  2. dev/ivan/baro firmware, 2.2 s: BMP585 driver init=0, 100 reads ok, values match the scripted peer.
# Pass = exit 0 (analyze.py prints ok/FAIL per check). Needs SIM (default: sim on PATH) and python3.
set -e
cd "$(dirname "$0")/.."
SIM=${SIM:-sim}
O=$(mktemp -d); trap 'rm -rf "$O"' EXIT
T=""; for a in 0x08009e14 0x0810ad4c 0x08009a84 0x0810ab2c 0x0800af28 0x0810be58 0x08009668 0x0810a878; do T="$T --trace-symbol $a"; done
"$SIM" run --scenario sim/scenario-boot.yaml --timeout 0.3 --trace-interrupts $T > "$O/trace.txt"
grep '(TRACE)' "$O/trace.txt" > "$O/boot.txt" || true
grep '(IRQ)' "$O/trace.txt" > "$O/irq.txt" || true
"$SIM" run --scenario sim/scenario.yaml --timeout 2.2 --ascii --output "$O/baro.txt" >/dev/null
python3 -I sim/analyze.py "$O/baro.txt" "$O/boot.txt" "$O/irq.txt"
