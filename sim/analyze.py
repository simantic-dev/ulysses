"""Checks the run outputs and, with an output directory, draws the charts.
usage: analyze.py baro.txt boot.txt irq.txt [outdir "<caption tag>"]"""
import re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/peers")
from bmp585 import world

baro, boot, irq = (open(p).read() for p in sys.argv[1:4])
fail = []
def check(ok, msg):
    print(("ok   " if ok else "FAIL ") + msg)
    if not ok: fail.append(msg)

# --- barometer: the real driver's output against what the peer was told
rows = []
for m in re.finditer(r"\[([\d.]+)s\] \(usart3\) BARO n=(\d+) t_ms=(\d+) read=(-?\d+) mC=(-?\d+) Pa=(-?\d+)", baro):
    rows.append((float(m[1]), int(m[2]), int(m[3]), int(m[4]), int(m[5]), int(m[6])))
check("BARO init=0" in baro and "BARO done" in baro, "driver init returned 0 and the loop finished")
check(len(rows) == 100 and all(r[3] == 0 for r in rows), f"100 samples, every read returned 0 ({len(rows)} seen)")
err_pa = [r[5] - world(r[2] * 1000)[1] for r in rows]
err_mc = [r[4] - world(r[2] * 1000)[0] * 1000 for r in rows]
check(max(map(abs, err_pa)) < 12, f"pressure within 12 Pa of the peer's world (max {max(map(abs, err_pa)):.1f} Pa)")
check(max(map(abs, err_mc)) < 60, f"temperature within 60 mC of the peer's world (max {max(map(abs, err_mc)):.1f} mC)")

# --- boot: both cores reach StartDefaultTask, nothing reaches a fault or assert handler
hits = {m[2]: float(m[1]) for m in re.finditer(r"\[([\d.]+)s\] \(TRACE\) (0x[0-9a-f]+) ", boot)}
check("0x08009e14" in hits and "0x0810ad4c" in hits, f"CM7 and CM4 StartDefaultTask reached ({hits.get('0x08009e14')} s, {hits.get('0x0810ad4c')} s)")
check(not (set(hits) - {"0x08009e14", "0x0810ad4c"}), "no Error_Handler, HardFault_Handler or assert handler hit")

if len(sys.argv) > 4:
    import matplotlib; matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    out, tag = sys.argv[4], sys.argv[5]
    t = [r[2] / 1000 for r in rows]
    fig, ax = plt.subplots(3, 1, figsize=(8, 6.4), sharex=True, dpi=90)
    ax[0].plot(t, [r[5] / 100 for r in rows], ".", ms=3, label="driver output")
    ax[0].plot(t, [world(x * 1e6)[1] / 100 for x in t], "-", lw=1, label="peer's world")
    ax[0].set_ylabel("pressure, hPa"); ax[0].legend()
    ax[1].plot(t, [r[4] / 1000 for r in rows], ".", ms=3); ax[1].set_ylabel("temperature, C")
    ax[2].plot(t, err_pa, "-"); ax[2].set_ylabel("driver - world, Pa"); ax[2].set_xlabel("virtual time, s")
    fig.suptitle("BMP585 driver (dev/ivan/baro) reading a scripted peer, " + tag, fontsize=9)
    fig.tight_layout(); fig.savefig(out + "/baro.png"); plt.close(fig)

    ev = [(float(m[1]), m[2]) for m in re.finditer(r"\[([\d.]+)s\] \(IRQ\) enter (\w+)", irq)]
    names = ["SysTick", "PendSV", "IRQ54", "IRQ55"]
    fig, ax = plt.subplots(figsize=(8, 3.6), dpi=90)
    bins = [i * 0.01 for i in range(31)]
    import numpy as np
    for n in names:
        c, _ = np.histogram([e[0] for e in ev if e[1] == n], bins=bins)
        ax.step(bins[:-1], c, where="post", label=n)
    for a, lab, y in (("0x08009e14", "CM7 StartDefaultTask", 55), ("0x0810ad4c", "CM4 StartDefaultTask", 50)):
        ax.axvline(hits[a], color="k", ls=":", lw=1)
        ax.text(0.02, y, f"{lab}, {hits[a] * 1000:.2f} ms", fontsize=7)
    ax.set_xlabel("virtual time, s"); ax.set_ylabel("exception entries per 10 ms"); ax.set_ylim(0, 58); ax.legend(fontsize=7, loc="center right")
    ax.set_title("Unmodified main firmware: exception entries, both cores merged, " + tag, fontsize=9)
    fig.tight_layout(); fig.savefig(out + "/boot_irq.png"); plt.close(fig)
sys.exit(1 if fail else 0)
