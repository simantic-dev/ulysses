#!/bin/sh
# Builds sim/build/main.hex (this tree, unmodified) and sim/build/baro.hex (dev/ivan/baro + patch_baro.py).
# Each .hex holds both cores: CM7 in flash bank 1, CM4 in bank 2. Needs arm-none-eabi-gcc, cmake, ninja.
set -e
cd "$(dirname "$0")/.."
W=$PWD
build() { # source-root name
  cmake -S "$1/cfp" -B "sim/build/$2" -G Ninja -DCMAKE_TOOLCHAIN_FILE="$1/cfp/gcc-arm-none-eabi.cmake" -DCMAKE_BUILD_TYPE=Debug >/dev/null
  cmake --build "sim/build/$2" >/dev/null
  arm-none-eabi-objcopy -O ihex "sim/build/$2/CM7/build/ulysses_cm7.elf" "sim/build/$2.cm7.hex"
  arm-none-eabi-objcopy -O ihex "sim/build/$2/CM4/build/ulysses_cm4.elf" "sim/build/$2.cm4.hex"
  { grep -v ':00000001FF' "sim/build/$2.cm7.hex"; cat "sim/build/$2.cm4.hex"; } > "sim/build/$2.hex"
}
mkdir -p sim/build
build "$W/ulysses" main
rm -rf sim/build/src-baro; mkdir -p sim/build/src-baro
git archive origin/dev/ivan/baro ulysses | tar x -C sim/build/src-baro
python3 sim/patch_baro.py "$W/sim/build/src-baro/ulysses"
build "$W/sim/build/src-baro/ulysses" baro
