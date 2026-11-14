"""Synthesize the ASMR foley + sound effects used by index.html.

All sounds are generated procedurally (no downloaded samples), so the project
stays self-contained. Run:  python3 tools/make_sfx.py
"""
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")
rng = np.random.default_rng(7)


def t(d):
    return np.arange(int(SR * d)) / SR


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return signal.sosfilt(sos, x)


def lp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return signal.sosfilt(signal.butter(order, f, btype="high", fs=SR, output="sos"), x)


def env(n, a, d, curve=4.0):
    """attack seconds, decay seconds (exponential)"""
    e = np.zeros(n)
    na = max(1, int(a * SR))
    e[:na] = np.linspace(0, 1, na)
    rest = n - na
    e[na:] = np.exp(-curve * np.arange(rest) / max(1, int(d * SR)))
    return e


def click(dur=0.03, f_lo=1500, f_hi=7000, decay=0.006, gain=1.0):
    n = int(dur * SR)
    x = rng.standard_normal(n) * env(n, 0.0004, decay, 5)
    return bp(x, f_lo, f_hi) * gain


def place(buf, x, at):
    i = int(at * SR)
    end = min(len(buf), i + len(x))
    buf[i:end] += x[: end - i]
    return buf


def stereo(x, width=0.15):
    # tiny decorrelation for an "in your ears" ASMR feel
    d = int(0.0007 * SR)
    l = x
    r = np.concatenate([np.zeros(d), x[:-d]]) * (1 - width) + x * width
    return np.stack([l, r], axis=1)


def save(name, x, peak_db=-3.0):
    if x.ndim == 1:
        x = stereo(x)
    pk = np.max(np.abs(x)) + 1e-9
    x = x / pk * (10 ** (peak_db / 20))
    # 5 ms fades so nothing clicks at clip edges
    f = int(0.005 * SR)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    wavfile.write(os.path.join(OUT, name), SR, (x * 32767).astype(np.int16))


os.makedirs(OUT, exist_ok=True)

# --- room tone: soft pink-ish air, very quiet bed (20 s) ---------------------
n = int(20.5 * SR)
w = rng.standard_normal((n, 2))
room = np.stack([lp(w[:, 0], 900, 1), lp(w[:, 1], 900, 1)], axis=1)
room += 0.15 * np.stack([hp(w[:, 1], 4000), hp(w[:, 0], 4000)], axis=1)
save("room-tone.wav", room, -20)

# --- packing tape being slit/ripped off (1.1 s) ------------------------------
d = 1.1
n = int(d * SR)
crackle = (rng.random(n) < np.linspace(0.02, 0.09, n)).astype(float) * rng.standard_normal(n)
noise = rng.standard_normal(n) * 0.35
tape = bp(crackle + noise, 900, 6500)
am = 0.6 + 0.4 * np.sin(2 * np.pi * 38 * t(d)) ** 2  # sticky "zip" chatter
tape *= am * env(n, 0.05, 0.95, 1.2)
save("tape-rip.wav", tape, -4)

# --- cardboard flap opening: creak-rustle + soft hollow thump (0.7 s) --------
def flap(seed_shift=0):
    d = 0.7
    n = int(d * SR)
    rust = bp(rng.standard_normal(n), 400, 3200) * env(n, 0.12, 0.35, 3)
    body = lp(rng.standard_normal(n), 220, 4) * env(n, 0.002, 0.12, 6) * 3.5
    thump = np.zeros(n)
    place(thump, body, 0.32)
    tone = np.sin(2 * np.pi * (110 + seed_shift) * t(d)) * env(n, 0.002, 0.15, 6)
    tone2 = np.zeros(n)
    place(tone2, tone[: n - int(0.32 * SR)], 0.32)
    return rust * 0.6 + thump + tone2 * 0.4


save("flap-1.wav", flap(0), -5)
save("flap-2.wav", flap(14), -5)

# --- foam / plastic bag rustle (1.4 s) ---------------------------------------
d = 1.4
n = int(d * SR)
grains = np.zeros(n)
for k in range(140):
    g = bp(rng.standard_normal(int(0.02 * SR)), 2500, 9000) * env(int(0.02 * SR), 0.001, 0.008, 5)
    place(grains, g * rng.uniform(0.2, 1.0), rng.uniform(0, d - 0.03))
grains += bp(rng.standard_normal(n), 1500, 7000) * 0.12
grains *= env(n, 0.2, 1.0, 1.5)
save("rustle.wav", grains, -6)

# --- soft whoosh (0.6 s) -----------------------------------------------------
d = 0.6
n = int(d * SR)
x = rng.standard_normal(n)
out = np.zeros(n)
hop = 512
for i in range(0, n, hop):
    p = i / n
    fc = 300 + 2600 * np.sin(np.pi * p)
    seg = bp(x[max(0, i - 2048): i + hop], fc * 0.7, fc * 1.4)[-hop:]
    out[i: i + len(seg)] = seg[: n - i]
out *= np.sin(np.pi * np.linspace(0, 1, n)) ** 2
save("whoosh.wav", out, -8)

# --- product set down on carpet: soft low thud (0.5 s) -----------------------
d = 0.5
n = int(d * SR)
thud = lp(rng.standard_normal(n), 160, 4) * env(n, 0.003, 0.09, 6) * 4
thud += np.sin(2 * np.pi * 62 * t(d)) * env(n, 0.003, 0.2, 5)
thud += bp(rng.standard_normal(n), 800, 3000) * env(n, 0.001, 0.03, 6) * 0.2
save("thud.wav", thud, -3)

# --- knob detent ticks: 5 tiny clicks (0.45 s) -------------------------------
d = 0.45
buf = np.zeros(int(d * SR))
for k, at in enumerate([0.0, 0.08, 0.15, 0.23, 0.31]):
    place(buf, click(0.025, 2500, 9000, 0.003, 1.0 - k * 0.08), at)
save("knob-ticks.wav", buf, -6)

# single knob click
save("knob-click.wav", click(0.06, 1800, 8000, 0.006), -6)

# --- XLR latch: double metallic click + short ring (0.35 s) ------------------
d = 0.35
buf = np.zeros(int(d * SR))
place(buf, click(0.03, 2000, 9000, 0.004), 0.0)
place(buf, click(0.04, 1500, 7000, 0.005, 1.3), 0.06)
ring = np.sin(2 * np.pi * 3700 * t(0.25)) * env(int(0.25 * SR), 0.0005, 0.05, 6) * 0.25
ring += np.sin(2 * np.pi * 5210 * t(0.25)) * env(int(0.25 * SR), 0.0005, 0.03, 6) * 0.15
place(buf, ring, 0.06)
save("xlr-click.wav", buf, -4)

# --- 1/4" jack plug-in: scrape + seat thunk + tiny amp hum pop (0.7 s) -------
d = 0.7
buf = np.zeros(int(d * SR))
scr = bp(rng.standard_normal(int(0.12 * SR)), 2000, 8000) * np.linspace(0.2, 1, int(0.12 * SR)) * 0.4
place(buf, scr, 0.0)
place(buf, click(0.05, 600, 5000, 0.008, 1.4), 0.12)
hum_t = t(0.45)
hum = (np.sin(2 * np.pi * 50 * hum_t) + 0.5 * np.sin(2 * np.pi * 100 * hum_t) + 0.2 * np.sin(2 * np.pi * 150 * hum_t))
hum *= env(len(hum_t), 0.002, 0.18, 5) * 0.55
place(buf, hum, 0.125)
save("jack-plug.wav", buf, -3)

# --- toggle switch flick (0.2 s) ---------------------------------------------
d = 0.2
buf = np.zeros(int(d * SR))
place(buf, click(0.02, 3000, 10000, 0.002, 0.5), 0.0)
place(buf, click(0.05, 1200, 8000, 0.006, 1.2), 0.018)
place(buf, lp(rng.standard_normal(int(0.04 * SR)), 300) * env(int(0.04 * SR), 0.001, 0.01, 6) * 2, 0.018)
save("toggle.wav", buf, -4)

# --- bluetooth "paired" chime: two soft bell notes (0.9 s) -------------------
d = 0.9
buf = np.zeros(int(d * SR))
for f, at in [(1318.5, 0.0), (1975.5, 0.14)]:
    tt = t(0.7)
    b = (np.sin(2 * np.pi * f * tt) + 0.25 * np.sin(2 * np.pi * f * 2.01 * tt)) * env(len(tt), 0.004, 0.35, 5)
    place(buf, b, at)
save("bt-chime.wav", buf, -10)

# --- UI pop for callouts (0.15 s) --------------------------------------------
d = 0.15
tt = t(d)
f = 900 * np.exp(-tt * 18) + 300
pop = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(tt), 0.002, 0.05, 5)
save("pop.wav", pop, -10)

# --- soft riser into end card (1.2 s) ----------------------------------------
d = 1.2
n = int(d * SR)
x = rng.standard_normal(n)
riser = np.zeros(n)
for i in range(0, n, hop):
    p = i / n
    fc = 400 + 5000 * p ** 2
    seg = bp(x[max(0, i - 2048): i + hop], fc * 0.8, min(fc * 1.3, 20000))[-hop:]
    riser[i: i + len(seg)] = seg[: n - i]
riser *= np.linspace(0, 1, n) ** 2
save("riser.wav", riser, -10)

# --- warm acoustic-ish pad bed (20 s), barely there under the foley ----------
d = 20.5
tt = t(d)
pad = np.zeros_like(tt)
# Cmaj9-ish voicing, slow chorus wobble (nod to the amp's chorus)
for f in [130.81, 196.0, 246.94, 293.66, 329.63]:
    wob = 1 + 0.003 * np.sin(2 * np.pi * 0.35 * tt + f)
    pad += np.sin(2 * np.pi * f * np.cumsum(wob) / SR)
pad = lp(pad, 1200)
fade = np.minimum(1, tt / 2.5) * np.minimum(1, (d - tt) / 2.0)
pad *= fade
save("pad.wav", pad, -6)

print("wrote", sorted(os.listdir(OUT)))
