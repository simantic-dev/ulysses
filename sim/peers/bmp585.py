"""Bosch BMP585 on I2C1 as UBC Rocket's Ulysses driver (dev/ivan/baro) uses it. Written from that
driver, not checked on a part. No conversion time, no FIFO, no INT pin.

STIMULUS: pressure and temperature follow a scripted altitude profile of virtual time (climb 0 to
300 m in 1 s, hold 0.5 s, descend in 1 s), through the ICAO standard atmosphere. It is what the part
is told the world is doing, not a flight."""
CMD, SOFT_RESET = 0x7E, 0xB6


def altitude_m(t_us):
    t = t_us / 1e6
    if t < 1.0:
        return 300.0 * t
    if t < 1.5:
        return 300.0
    return max(0.0, 300.0 - 300.0 * (t - 1.5))


def world(t_us):
    h = altitude_m(t_us)
    return 25.0 - 0.0065 * h, 101325.0 * (1 - 2.25577e-5 * h) ** 5.25588


class Slave:
    def __init__(self, ctx):
        self.ctx = ctx
        self.ptr = 0
        self.por = True
        self.regs = bytearray(256)

    def on_write(self, data):
        self.ptr = data[0]
        for b in data[1:]:
            if self.ptr == CMD:
                if b == SOFT_RESET:
                    self.por = True
            else:
                self.regs[self.ptr] = b
            self.ptr = (self.ptr + 1) & 0xFF

    def read_reg(self, r):
        c, pa = world(self.ctx.now_us)
        t, p = round(c * 65536) & 0xFFFFFF, round(pa * 64) & 0xFFFFFF
        if r == 0x01:
            return 0x51  # CHIP_ID
        if 0x1D <= r <= 0x1F:
            return (t >> (8 * (r - 0x1D))) & 0xFF
        if 0x20 <= r <= 0x22:
            return (p >> (8 * (r - 0x20))) & 0xFF
        if r == 0x27:  # INT_STATUS: POR, clears on read
            por, self.por = self.por, False
            return 0x10 if por else 0
        if r == 0x28:
            return 0x02  # STATUS: NVM ready
        if r == 0x38:
            return 0x80  # OSR_EFF: ODR valid
        return self.regs[r]

    def on_read(self, count):
        out = bytearray()
        for _ in range(count):
            out.append(self.read_reg(self.ptr))
            self.ptr = (self.ptr + 1) & 0xFF
        return bytes(out)

    def on_finish(self):
        pass
