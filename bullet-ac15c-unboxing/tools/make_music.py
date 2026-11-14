"""Synthesize the musical audio for the edit (no samples, fully procedural):

  mic-check.wav   TTS "Check. Check. One, two, three." run through a small-amp + room chain
  gtr-strum.wav   one open G strum right after the guitar is plugged in
  gtr-tweak.wav   arpeggio while knobs are turned: VOL up -> BASS up -> CHORUS on -> SPEED up
  gtr-try.wav     a short strum pattern ("cuba sikit") with chorus
  jam-mix.wav     phone backing track over Bluetooth + live strummed guitar on top

Guitar = Karplus-Strong strings + a simple body resonance, then an "amp" chain.
Run:  python3 tools/make_music.py   (after `hyperframes tts` wrote assets/voice/raw-am_michael.wav)
"""
import os
import numpy as np
from scipy import signal
from scipy.io import wavfile

SR = 48000
ROOT = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(ROOT, "assets", "music")
os.makedirs(OUT, exist_ok=True)
rng = np.random.default_rng(11)

# ---------------------------------------------------------------- helpers
def sos(kind, f, order=2):
    return signal.butter(order, f, btype=kind, fs=SR, output="sos")


def filt(x, kind, f, order=2):
    return signal.sosfilt(sos(kind, f, order), x, axis=0)


def biquad_peak(x, f0, gain_db, q=0.9):
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / (2 * q)
    b = [1 + al * a, -2 * np.cos(w0), 1 - al * a]
    aa = [1 + al / a, -2 * np.cos(w0), 1 - al / a]
    return signal.lfilter(b, aa, x, axis=0)


def low_shelf(x, f0, gain_db):
    a = 10 ** (gain_db / 40)
    w0 = 2 * np.pi * f0 / SR
    al = np.sin(w0) / 2 * np.sqrt(2)
    c = np.cos(w0)
    b = [a * ((a + 1) - (a - 1) * c + 2 * np.sqrt(a) * al),
         2 * a * ((a - 1) - (a + 1) * c),
         a * ((a + 1) - (a - 1) * c - 2 * np.sqrt(a) * al)]
    aa = [(a + 1) + (a - 1) * c + 2 * np.sqrt(a) * al,
          -2 * ((a - 1) + (a + 1) * c),
          (a + 1) + (a - 1) * c - 2 * np.sqrt(a) * al]
    return signal.lfilter(b, aa, x, axis=0)


def place(buf, x, at):
    i = int(at * SR)
    if i >= len(buf):
        return buf
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += x[:n]
    return buf


def room_ir(dur=1.3, pre=0.018, damp=3.6):
    """small music shop: early reflections off walls/shelves + a soft diffuse tail"""
    n = int(dur * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-damp * t)[:, None] * 0.6
    ir = filt(ir, "low", 3800)
    ir[: int(pre * SR)] = 0
    for (d, g) in ((0.011, 0.55), (0.017, 0.42), (0.023, 0.35), (0.031, 0.3), (0.043, 0.22)):
        ir[int(d * SR), 0] += g
        ir[int((d + 0.003) * SR), 1] += g * 0.9
    ir[0] = 1.0
    return ir


def reverb(x, mix=0.18, **kw):
    ir = room_ir(**kw)
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    wet = np.stack([signal.fftconvolve(x[:, 0], ir[:, 0])[: len(x)],
                    signal.fftconvolve(x[:, 1], ir[:, 1])[: len(x)]], 1)
    wet /= np.max(np.abs(wet)) + 1e-9
    wet *= np.max(np.abs(x))
    return x * (1 - mix) + wet * mix


def chorus(x, depth_ms=2.8, base_ms=14, rate=0.9, mix=0.5):
    """stereo chorus: modulated fractional delay, L/R in quadrature"""
    if x.ndim == 2:
        x = x.mean(1)
    n = len(x)
    t = np.arange(n) / SR
    idx = np.arange(n)
    out = []
    for ph in (0.0, np.pi / 2):
        d = (base_ms + depth_ms * np.sin(2 * np.pi * rate * t + ph)) * SR / 1000
        pos = np.clip(idx - d, 0, n - 1)
        i0 = np.floor(pos).astype(int)
        fr = pos - i0
        i1 = np.minimum(i0 + 1, n - 1)
        wet = x[i0] * (1 - fr) + x[i1] * fr
        out.append(x * (1 - mix) + wet * mix)
    return np.stack(out, 1)


def amp_chain(x, drive=1.4):
    """small acoustic amp: HPF, gentle low-mid scoop, presence, soft clip, 8in-speaker LPF"""
    y = filt(x, "high", 75)
    y = biquad_peak(y, 450, -2.5, 0.8)
    y = biquad_peak(y, 3200, 2.0, 0.9)
    y = np.tanh(y * drive) / np.tanh(drive)
    return filt(y, "low", 7500)


def norm(x, peak_db=-3.0):
    return x / (np.max(np.abs(x)) + 1e-9) * 10 ** (peak_db / 20)


def save(name, x, peak_db=-3.0):
    if x.ndim == 1:
        x = np.stack([x, x], 1)
    x = norm(x, peak_db)
    f = int(0.006 * SR)
    x[:f] *= np.linspace(0, 1, f)[:, None]
    x[-f:] *= np.linspace(1, 0, f)[:, None]
    wavfile.write(os.path.join(OUT, name), SR, (x * 32767).astype(np.int16))
    print(f"{name}: {len(x)/SR:.2f}s")


# ---------------------------------------------------------------- guitar
def ks_string(freq, dur, bright=0.55, decay=0.9965, vel=1.0):
    n = int(dur * SR)
    N = int(round(SR / freq))
    y = np.zeros(n + N + 2)
    burst = rng.uniform(-1, 1, N + 1)
    # pick brightness: one-pole lowpass on the excitation
    burst = signal.lfilter([bright], [1, -(1 - bright)], burst)
    y[: N + 1] = burst * vel
    for s in range(N + 1, len(y), N):
        e = min(s + N, len(y))
        y[s:e] = decay * 0.5 * (y[s - N:e - N] + y[s - N - 1:e - N - 1])
    return y[:n]


BODY = None


def body(x):
    # acoustic body: a few broad resonances
    y = biquad_peak(x, 105, 5, 1.6)
    y = biquad_peak(y, 210, 3, 1.4)
    y = biquad_peak(y, 2600, 2, 1.0)
    return y


CHORDS = {
    "G": [98.00, 123.47, 146.83, 196.00, 246.94, 392.00],
    "D": [None, None, 146.83, 220.00, 293.66, 369.99],
    "Em": [82.41, 123.47, 164.81, 196.00, 246.94, 329.63],
    "C": [None, 130.81, 164.81, 196.00, 261.63, 329.63],
}


def strum(chord, dur=2.0, down=True, vel=1.0, spread=0.014, bright=0.55, mute=False):
    notes = CHORDS[chord]
    order = range(6) if down else range(5, -1, -1)
    out = np.zeros(int((dur + 0.2) * SR))
    k = 0
    for i in order:
        f = notes[i]
        if f is None:
            continue
        d = 0.06 if mute else dur
        s = ks_string(f, d + 0.1, bright=bright, decay=0.9935 if mute else 0.9968,
                      vel=vel * (0.85 + 0.3 * rng.random()))
        if mute:
            s *= np.exp(-np.arange(len(s)) / (0.02 * SR))
        place(out, s, k * spread)
        k += 1
    return body(out)


def arpeggio(chord, start, buf, step=0.19, pattern=(0, 2, 3, 4, 5, 4, 3, 2), vel=0.8):
    notes = [n for n in CHORDS[chord] if n]
    for j, idx in enumerate(pattern):
        f = notes[min(idx, len(notes) - 1)]
        place(buf, body(ks_string(f, 1.6, bright=0.5, vel=vel)), start + j * step)
    return buf


def strum_pattern(chords, bpm, total, start=0.0, vel=1.0):
    """D . D U . U D U  per bar"""
    beat = 60 / bpm
    hits = [(0, True, 1.0), (1, True, 0.8), (1.5, False, 0.6), (2.5, False, 0.6), (3, True, 0.85), (3.5, False, 0.6)]
    out = np.zeros(int(total * SR))
    t = start
    for c in chords:
        for (b, dn, v) in hits:
            at = t + b * beat
            if at < total:
                place(out, strum(c, dur=beat * 2.2, down=dn, vel=v * vel, spread=0.009 if not dn else 0.012), at)
        t += 4 * beat
    return out


# 1) mic check ---------------------------------------------------------------
sr_v, v = wavfile.read(os.path.join(ROOT, "assets", "voice", "raw-am_michael.wav"))
v = v.astype(np.float64)
if v.ndim > 1:
    v = v.mean(1)
v /= np.max(np.abs(v)) + 1e-9
v = signal.resample_poly(v, SR, sr_v)
lead = np.zeros(int(0.25 * SR))
# mic handling: a soft low "thump" + rub just before speaking
th = filt(rng.standard_normal(int(0.12 * SR)), "low", 180, 4) * np.exp(-np.arange(int(0.12 * SR)) / (0.025 * SR)) * 3
place(lead, th, 0.02)
voice = np.concatenate([lead, v, np.zeros(int(0.7 * SR))])
voice = filt(voice, "high", 110)                      # SM58-ish proximity cut
voice = biquad_peak(voice, 4500, 4, 1.2)              # presence bump
voice = amp_chain(voice, drive=1.8)
voice = reverb(voice, mix=0.26)                       # small shop room
save("mic-check.wav", voice, -2)

# 2) first strum after plugging in ------------------------------------------
g = strum("G", dur=2.4, vel=1.0)
g = reverb(amp_chain(g, 1.2), mix=0.3)
save("gtr-strum.wav", g, -3)

# 3) knob tweak demo (3.4 s): vol up @0.1, bass @0.9, chorus @1.7, speed @2.3 --------
D = 3.4
dry = np.zeros(int(D * SR))
arpeggio("G", 0.0, dry, step=0.21, vel=0.85)
arpeggio("Em", 1.68, dry, step=0.21, vel=0.85)
dry = amp_chain(dry, 1.2)
t = np.arange(len(dry)) / SR
vol = np.clip(0.25 + (t - 0.1) / 0.5 * 0.75, 0.25, 1.0)
bass_amt = np.clip((t - 0.9) / 0.4, 0, 1)
ch_amt = np.clip((t - 1.7) / 0.15, 0, 1)
bassy = low_shelf(dry, 180, 7.0)
y = dry * (1 - bass_amt) + bassy * bass_amt
slow = chorus(y, rate=0.7, depth_ms=1.4, mix=0.2)
fast = chorus(y, rate=2.2, depth_ms=1.6, mix=0.22)
sp = np.clip((t - 2.3) / 0.4, 0, 1)[:, None]
wet = slow * (1 - sp) + fast * sp
y2 = np.stack([y, y], 1) * (1 - ch_amt[:, None]) + wet * ch_amt[:, None]
y2 *= vol[:, None]
save("gtr-tweak.wav", reverb(y2, mix=0.28), -3)

# 4) "cuba sikit" strum pattern with chorus (3.4 s) ---------------------------
tr = strum_pattern(["G", "D"], bpm=100, total=3.6)
tr = amp_chain(low_shelf(tr, 180, 3.0), 1.3)
tr = chorus(tr, rate=0.8, depth_ms=1.4, mix=0.16)
save("gtr-try.wav", reverb(tr, mix=0.3), -3)

# 5) phone backing track + live guitar (8.6 s) --------------------------------
BPM = 92
beat = 60 / BPM
T = 8.6
n = int(T * SR)
mixL = np.zeros(n)
drums = np.zeros(n)
bass = np.zeros(n)
keys = np.zeros(n)
prog = ["G", "D", "Em", "C"]
roots = {"G": 49.0, "D": 73.42, "Em": 82.41, "C": 65.41}
for b in range(int(T / beat) + 1):
    at = b * beat
    bar, pos = divmod(b, 4)
    # kick on 1 and 3 (+ an 8th pickup), snare on 2 and 4
    if pos in (0, 2):
        kt = np.arange(int(0.35 * SR)) / SR
        k = np.sin(2 * np.pi * np.cumsum(50 + 90 * np.exp(-kt * 30)) / SR) * np.exp(-kt * 9)
        place(drums, k * 1.0, at)
    if pos in (1, 3):
        st = np.arange(int(0.25 * SR)) / SR
        sn = filt(rng.standard_normal(len(st)), "band", [1200, 7000]) * np.exp(-st * 22) * 0.5
        sn += np.sin(2 * np.pi * 190 * st) * np.exp(-st * 30) * 0.4
        place(drums, sn, at)
    for h in (0, 0.5):
        ht = np.arange(int(0.05 * SR)) / SR
        hh = filt(rng.standard_normal(len(ht)), "high", 7000) * np.exp(-ht * 70) * (0.22 if h else 0.15)
        place(drums, hh, at + h * beat)
    c = prog[bar % 4]
    if pos == 0:
        # bass: root on 1, fifth on the "and" of 2, root on 3
        for (bb, mul, ln) in ((0, 1, 1.4), (1.5, 1.5, 0.45), (2, 1, 1.8)):
            bt = np.arange(int(ln * beat * SR)) / SR
            f = roots[c] * mul
            tone = np.sin(2 * np.pi * f * bt) + 0.3 * np.sin(2 * np.pi * 2 * f * bt)
            tone *= np.minimum(1, bt / 0.01) * np.exp(-bt * 1.4)
            place(bass, tone * 0.7, at + bb * beat)
        # soft electric-piano pad
        kt = np.arange(int(4 * beat * SR)) / SR
        pad = np.zeros(len(kt))
        for f in [x for x in CHORDS[c] if x][-4:]:
            pad += (np.sin(2 * np.pi * f * kt) + 0.25 * np.sin(2 * np.pi * 2 * f * kt)) * np.exp(-kt * 0.9)
        pad *= (1 + 0.15 * np.sin(2 * np.pi * 4.5 * kt))
        place(keys, pad * 0.18, at)
backing = drums * 0.8 + filt(bass, "low", 900) * 0.9 + filt(keys, "low", 3500)
backing = filt(backing, "high", 60)
# it plays through the amp over Bluetooth: slight band-limit + glue
backing = amp_chain(backing * 0.8, 1.1)
live = strum_pattern(prog * 2, bpm=BPM, total=T, start=0.8 + 4 * beat * 0)  # guitar joins after ~0.8 s
live[: int(0.8 * SR)] = 0
live = amp_chain(low_shelf(live, 180, 3.0), 1.3)
live = chorus(live, rate=0.8, depth_ms=1.4, mix=0.14)
mix = np.stack([backing, backing], 1) * 0.75 + live * 0.6
fade = np.ones(n)
fade[-int(1.6 * SR):] = np.linspace(1, 0, int(1.6 * SR)) ** 1.5
mix *= fade[:, None]
save("jam-mix.wav", reverb(mix, mix=0.22), -2)
