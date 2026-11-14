"""Procedural photo-style textures for the box intro (no stock images):
  kraft.png   corrugated cardboard skin (mottling, fibres, faint flute bands, grain)
  inside.png  what you see in the open box: white foam corners + a plastic dust bag
Run: python3 tools/make_textures.py
"""
import os
import numpy as np
from PIL import Image, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "assets", "img")
rng = np.random.default_rng(3)


def smooth_noise(h, w, scale):
    small = rng.random((max(2, h // scale), max(2, w // scale)))
    im = Image.fromarray((small * 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)
    return np.asarray(im).astype(np.float32) / 255


def kraft(w=1200, h=1000):
    base = np.array([196, 152, 102], np.float32)  # kraft brown
    m = 0.55 * smooth_noise(h, w, 180) + 0.3 * smooth_noise(h, w, 60) + 0.15 * smooth_noise(h, w, 15)
    img = base[None, None, :] * (0.86 + 0.22 * m[..., None])
    # flute bands showing through the liner
    x = np.arange(w)
    flute = 0.5 + 0.5 * np.sin(2 * np.pi * x / 9.0)
    img *= (0.985 + 0.02 * flute)[None, :, None]
    # fibres: short dark/light strokes
    fib = Image.new("L", (w, h), 128)
    px = fib.load()
    for _ in range(9000):
        x0, y0 = rng.integers(0, w), rng.integers(0, h)
        ln = rng.integers(4, 16)
        ang = rng.normal(0, 0.5)
        val = int(128 + rng.choice([-1, 1]) * rng.integers(10, 35))
        for k in range(ln):
            xx = int(x0 + k * np.cos(ang)); yy = int(y0 + k * np.sin(ang))
            if 0 <= xx < w and 0 <= yy < h:
                px[xx, yy] = val
    fib = np.asarray(fib.filter(ImageFilter.GaussianBlur(0.6))).astype(np.float32) / 128
    img *= fib[..., None] ** 0.35
    # fine grain
    img *= 1 + rng.normal(0, 0.025, (h, w, 1))
    # scuffs near the edges
    ex = np.minimum(np.arange(w), w - np.arange(w))[None, :] / w
    ey = np.minimum(np.arange(h), h - np.arange(h))[:, None] / h
    edge = np.minimum(ex, ey)
    img *= (0.9 + 0.1 * np.clip(edge * 12, 0, 1))[..., None]
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def inside(w=1200, h=420):
    img = np.zeros((h, w, 3), np.float32) + np.array([40, 30, 22], np.float32)  # dark interior
    # dust bag: soft white plastic with wrinkles
    bag = 0.6 * smooth_noise(h, w, 40) + 0.4 * smooth_noise(h, w, 12)
    wr = np.abs(np.sin(smooth_noise(h, w, 70) * 9)) ** 3
    plastic = np.array([210, 205, 198], np.float32) * (0.55 + 0.35 * bag + 0.25 * wr)[..., None]
    mask = np.zeros((h, w), np.float32)
    mask[int(h * 0.12):int(h * 0.92), int(w * 0.14):int(w * 0.86)] = 1
    mask = np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(25))).astype(np.float32) / 255
    img = img * (1 - mask[..., None]) + plastic * mask[..., None]
    # foam corner blocks
    for x0 in (0.02, 0.86):
        foam = np.array([235, 233, 228], np.float32) * (0.8 + 0.2 * smooth_noise(h, w, 4))[..., None]
        fm = np.zeros((h, w), np.float32)
        fm[int(h * 0.05):int(h * 0.95), int(w * x0):int(w * (x0 + 0.12))] = 1
        fm = np.asarray(Image.fromarray((fm * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))).astype(np.float32) / 255
        img = img * (1 - fm[..., None]) + foam * fm[..., None]
    # light falls off toward the back of the box
    y = np.linspace(0.55, 1.0, h)[:, None, None]
    img *= y
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


os.makedirs(OUT, exist_ok=True)
kraft().save(os.path.join(OUT, "kraft.png"))
inside().save(os.path.join(OUT, "inside.png"))
print("ok")
