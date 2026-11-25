"""usage: make_gif.py baro.txt out.gif "<sim version>"
Draws the run's own BARO lines (CM7 BMP585 driver on USART3) against the peer's scripted world. Pillow + ffmpeg only (sim/gifkit.py)."""
import re, sys, os
here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, here); sys.path.insert(0, here + "/peers")
from gifkit import *
from bmp585 import world, altitude_m

txt = open(sys.argv[1]).read()
rows = [(float(m[1]), int(m[2]), int(m[3]) / 1000, int(m[4]), int(m[5]) / 1000, int(m[6])) for m in re.finditer(r"\[([\d.]+)s\] \(usart3\) BARO n=(\d+) t_ms=(\d+) read=(-?\d+) mC=(-?\d+) Pa=(-?\d+)", txt)]
init_t = float(re.search(r"\[([\d.]+)s\] \(usart3\) BARO init=0", txt)[1])
log = [(init_t, "INFO", "BARO init=0")] + [(r[0], "INFO", f"BARO n={r[1]} t_ms={int(r[2]*1000)} read={r[3]} mC={int(r[4]*1000)} Pa={r[5]}") for r in rows]
VER, END = sys.argv[3], 2.2
P = [(r[2], r[5] / 100) for r in rows]
ERR = [(r[2], round(r[5] - world(r[2] * 1e6)[1], 1)) for r in rows]
ALT = [(r[2], 44330.8 * (1 - (r[5] / 101325.0) ** 0.190263)) for r in rows]   # ICAO standard atmosphere, derived from the driver's pressure
PH = [("BMP585 INIT", init_t), ("CLIMB 0-300 m", 0.0), ("HOLD 300 m", 1.0), ("DESCEND", 1.5)]

def cur(series, t):
    r = [v for a, v in series if a <= t]
    return r[-1] if r else None

def draw(c, t):
    c.header("Ulysses flight computer (STM32H745, CM7) reading a BMP585 barometer", "team's BMP585 driver (dev/ivan/baro), unmodified; the sensor is a scripted peer following a climb, hold, descent. Values are the driver's own USART3 output.", t)
    n = len([r for r in rows if r[0] <= t]); p = cur(P, t); r = [x for x in rows if x[0] <= t]
    tw = 196; X = [24 + i * (tw + 12) for i in range(6)]
    c.tile(X[0], 90, tw, 92, "PRESSURE", f"{p:.1f}" if p else "--", "hPa", CYAN)
    c.tile(X[1], 90, tw, 92, "TEMPERATURE", f"{r[-1][4]:.2f}" if r else "--", "C", CYAN)
    c.tile(X[2], 90, tw, 92, "ALTITUDE (DERIVED)", f"{max(0, cur(ALT, t)):.0f}" if r else "--", "m", AMBER)
    c.tile(X[3], 90, tw, 92, "SAMPLES", f"{n}", "of %d" % len(rows), FG)
    c.tile(X[4], 90, tw, 92, "READ STATUS", ("OK" if all(x[3] == 0 for x in r) else "ERROR") if r else "--", f"{sum(x[3] == 0 for x in r)} ok", GREEN)
    e = cur(ERR, t)
    c.tile(X[5], 90, tw, 92, "ERROR VS PEER", f"{e:+.1f}" if e is not None else "--", "Pa", AMBER)
    c.panel(24, 196, 1232, 112, "Driver and scripted world (phases are the peer's stimulus, not a flight)")
    times = [init_t if t >= init_t else None] + [x if t >= x else None for x in (0.0, 1.0, 1.5)]
    ph = 3 if t >= 1.5 else 2 if t >= 1.0 else 1
    c.chain(40, 226, 1200, 70, [x[0] for x in PH], ph if t >= init_t else None, times, [BLUE, GREEN, AMBER, RED], sz=17)
    c.strip(24, 322, 620, 180, P, t, END, 970, 1020, "driver pressure (hPa)", CYAN, "hPa", ticks=5)
    c.strip(24, 512, 620, 170, ERR, t, END, -12, 12, "driver minus peer (Pa)", AMBER, "Pa", ticks=4)
    c.log(656, 322, 600, 360, log, t, "firmware console (CM7, USART3)", sz=14)
    c.footer(VER, SPEED, ".  Error = driver minus the peer at the 20 ms tick; the read lands a little after it, so the sign follows the slope.")

SPEED = 0.15
print("frames", render(draw, END, SPEED, sys.argv[2]))
