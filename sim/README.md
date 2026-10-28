# Simulating Ulysses

`run.sh` runs both cores of a Debug build on [pyrite](https://github.com/simantic-dev/pyrite)'s
`Ulysses-FC` board: an STM32H745ZI with this board's 24 MHz HSE and a blank SD card on
SDMMC2. Build first, then:

    sim/run.sh --timeout 1

Extra arguments go to `sim run`. The image is one Intel HEX holding both cores, so trace
by address (`--trace-symbol 0x<addr>`, from `arm-none-eabi-nm`), not by name.

The H745 model's dual-core boot (CM4 STOP on WFE, HSEM wake through EXTI line 78,
D2CKRDY, each core's COREID) was checked against a Nucleo-H755ZI-Q
(sim-fixtures `hil-setups/stm/h755zi-dualcore`). Off-chip parts (IMU, baro, radio on
SPI5/SPI6/I2C3/I2C4) are not attached yet.
