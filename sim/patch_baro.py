"""Harness patch for the dev/ivan/baro tree: after io_board_init() in the CM7 main, read the real
BMP585 driver every 20 ms, 100 times, and print each sample on USART3 (the firmware has no console)."""
import sys

main = sys.argv[1] + "/cfp/CM7/Core/Src/main.c"
PRINT = r'''
#include <stdio.h>
#define U3 0x40004800u
#define R(a) (*(volatile uint32_t *)(a))
static void sim_print(const char *s)
{
    *(volatile uint32_t *)0x580244E8u |= 1u << 18; (void)R(0x580244E8u);
    R(U3 + 0x0C) = 64000000u / 115200u; R(U3 + 0x00) = 0x9;
    for (; *s; s++) { while (!(R(U3 + 0x1C) & (1u << 7))) ; R(U3 + 0x28) = (uint8_t)*s; }
}
'''
src = open(main).read()
src = src.replace('#include "ulysses/io/board.h"\n', '#include "ulysses/io/board.h"\n#include "ulysses/dev/bmp585.h"\n' + PRINT, 1)
src = src.replace("  io_board_init();\n", r'''  io_board_init();
  {
    struct dev_bmp585_sample b = {0}; char l[96];
    int i = dev_bmp585_init(&IO_BARO);
    snprintf(l, sizeof l, "BARO init=%d\r\n", i); sim_print(l);
    for (int n = 0; n < 100; n++) {
      uint32_t t0 = HAL_GetTick();
      int r = dev_bmp585_read(&IO_BARO, &b);
      snprintf(l, sizeof l, "BARO n=%d t_ms=%lu read=%d mC=%ld Pa=%ld\r\n", n, (unsigned long)t0, r, (long)(b.temp_c * 1000.0f), (long)b.pressure_pa);
      sim_print(l);
      while (HAL_GetTick() - t0 < 20) ;
    }
    sim_print("BARO done\r\n");
    for (;;) ;
  }
''', 1)
open(main, "w").write(src)
