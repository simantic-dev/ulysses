#!/bin/sh
# Run both cores of a Debug build on pyrite's Ulysses-FC (STM32H745ZI, 24 MHz HSE,
# SD card on SDMMC2). Extra arguments go to `sim run` (--timeout, --trace-symbol ...).
#   (cd ulysses/cfp && cmake --preset Debug && cmake --build build/Debug)
#   sim/run.sh --timeout 1
set -e
cd "$(dirname "$0")/.."
B=ulysses/cfp/build/Debug
out=$(mktemp -d)
trap 'rm -rf "$out"' EXIT
# One image for both cores: CM7 in flash bank 1, CM4 in bank 2. The CM7 file's
# end-of-file record is dropped so the CM4's records follow it.
arm-none-eabi-objcopy -O ihex "$B/CM7/build/ulysses_cm7.elf" "$out/cm7.hex"
arm-none-eabi-objcopy -O ihex "$B/CM4/build/ulysses_cm4.elf" "$out/cm4.hex"
grep -v ':00000001FF' "$out/cm7.hex" > "$out/ulysses.hex"
cat "$out/cm4.hex" >> "$out/ulysses.hex"
sim Ulysses-FC run --elf "$out/ulysses.hex" "$@"
