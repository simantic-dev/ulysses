"""usage: make_gif.py baro.txt out.gif "<caption tag>"  -- animates the real driver samples (from the run) against the peer's world."""
import re, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0] + "/peers")
from bmp585 import world
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, io
from PIL import Image
txt = open(sys.argv[1]).read()
rows = [(int(m[1]) / 1000, int(m[3]) / 100, int(m[2]) / 1000) for m in re.finditer(r"BARO n=\d+ t_ms=(\d+) read=\d+ mC=(-?\d+) Pa=(-?\d+)", txt)]
t = [r[0] for r in rows]; p = [r[1] for r in rows]; T = [r[2] for r in rows]
frames = []
for k in range(2, len(rows) + 1, 2):
    fig, ax = plt.subplots(2, 1, figsize=(7, 4.4), dpi=70, sharex=True)
    ax[0].plot(t, [world(x * 1e6)[1] / 100 for x in t], "-", c="0.7", lw=3, label="peer's world")
    ax[0].plot(t[:k], p[:k], ".", c="C0", ms=4, label="driver output (sim)")
    ax[0].set_ylabel("pressure, hPa"); ax[0].legend(loc="upper right", fontsize=7)
    ax[1].plot(t[:k], T[:k], ".", c="C1", ms=4); ax[1].set_ylabel("temperature, C"); ax[1].set_xlabel("virtual time, s"); ax[1].set_xlim(0, 2.05)
    ax[0].set_title(f"Ulysses CM7 BMP585 driver on simulated H745, sample {k}/{len(rows)}, {sys.argv[3]}", fontsize=8)
    fig.tight_layout(); b = io.BytesIO(); fig.savefig(b, format="png"); plt.close(fig)
    frames.append(Image.open(b).convert("RGB").quantize(colors=64, dither=Image.Dither.NONE))
frames[0].save(sys.argv[2], save_all=True, append_images=frames[1:], duration=[100] * (len(frames) - 1) + [1500], loop=0, optimize=True)
