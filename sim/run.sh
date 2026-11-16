#!/bin/sh
# usage: sim/run.sh [charts]   Needs sim on PATH and sim/build.sh done. Prints PASS or FAIL.
# Run 1 (main, unmodified): 0.3 s of both cores, trace-symbol on each core's StartDefaultTask and the
#   fault/assert handlers (addresses are those of the Debug build in sim/build.sh), plus exception entries.
# Run 2 (dev/ivan/baro + patch_baro.py): 2.2 s, the BMP585 driver sampled every 20 ms against peers/bmp585.py.
# "charts" also draws sim/screenshots/*.png (needs matplotlib).
set -e
cd "$(dirname "$0")/.."
mkdir -p sim/out
T=""; for a in 0x08009e14 0x0810ad4c 0x08009a84 0x0810ab2c 0x0800af28 0x0810be58 0x08009668 0x0810a878; do T="$T --trace-symbol $a"; done
sim run --scenario sim/scenario-boot.yaml --timeout 0.3 --trace-interrupts $T > sim/out/trace.txt
grep '(TRACE)' sim/out/trace.txt > sim/out/boot.txt
grep '(IRQ)' sim/out/trace.txt > sim/out/irq.txt
sim run --scenario sim/scenario.yaml --timeout 2.2 --ascii --output sim/out/baro.txt >/dev/null
if [ "$1" = charts ]; then
  python3 sim/analyze.py sim/out/baro.txt sim/out/boot.txt sim/out/irq.txt sim/screenshots "$(sim version | head -1), $(date +%F)" && echo PASS || { echo FAIL; exit 1; }
else
  python3 sim/analyze.py sim/out/baro.txt sim/out/boot.txt sim/out/irq.txt && echo PASS || { echo FAIL; exit 1; }
fi
