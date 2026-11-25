#!/usr/bin/env python3
"""Piano cover course video renderer: chord pill + piano card + lyrics overlay.

Usage: python3 render.py <source.mov> <theme: biru|merah> <out.mp4> [--preview SECONDS]
Overlay frames are drawn with PIL and piped to ffmpeg, which applies the
cinematic grade + frosted-glass blur behind the card.
"""
import json, subprocess, sys, math, os
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, THEME, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
PREVIEW = float(sys.argv[sys.argv.index('--preview') + 1]) if '--preview' in sys.argv else None
FONTS = os.environ.get('FONT_DIR', os.path.join(HERE, 'fonts'))

W, H, FPS = 1080, 1920, 30
DATA = json.load(open(os.path.join(HERE, 'song.json')))
DUR = PREVIEW or DATA['duration']

THEMES = {
    'biru':  dict(accent=(77, 163, 255), accent_dk=(36, 110, 214), pill_text=(8, 28, 58),
                  grade="colorbalance=rs=-0.02:bs=0.035:rm=-0.01:bm=0.015"),
    'merah': dict(accent=(255, 107, 102), accent_dk=(214, 62, 62), pill_text=(58, 10, 12),
                  grade="colorbalance=rs=0.025:bs=-0.01:rm=0.01"),
}
T = THEMES[THEME]
ACC, ACC_DK = T['accent'], T['accent_dk']

def font(w, size):
    return ImageFont.truetype(os.path.join(FONTS, f'Poppins-{w}.ttf'), size)

# ---------------- layout ----------------
CARD_W, CARD_H = 500, 236
CARD_X, CARD_Y = (W - CARD_W) // 2, 652
PILL_CY = 604
LYR_Y, SUB_Y = 978, 1040
SS = 2  # supersample for static art

# ---------------- music helpers ----------------
PC = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'Bb': 10, 'A#': 10, 'B': 11}
QUAL = {'': [0, 4, 7], 'm': [0, 3, 7], '7': [0, 4, 7, 10], 'maj7': [0, 4, 7, 11], 'm7': [0, 3, 7, 10]}
SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
FLAT_KEYS = {'Gm': {10: 'Bb'}}
LOW, HIGH = 53, 76  # F3 .. E5 (14 white keys)

def parse(ch):
    root = ch[:2] if len(ch) > 1 and ch[1] in '#b' else ch[:1]
    return root, ch[len(root):]

def voicing(ch):
    root, q = parse(ch)
    r = PC[root]
    base = 60 + r if r <= 4 else 48 + r
    notes = [base + i for i in QUAL[q]]
    while notes[-1] > HIGH: notes = [n - 12 for n in notes]
    while notes[0] < LOW: notes = [n + 12 for n in notes]
    names = [FLAT_KEYS.get(ch, {}).get(n % 12, SHARP[n % 12]) for n in notes]
    return notes, names

WHITE_PCS = [0, 2, 4, 5, 7, 9, 11]
def keyboard_layout(x0, w):
    whites = [m for m in range(LOW, HIGH + 1) if m % 12 in WHITE_PCS]
    ww = w / len(whites)
    pos = {}
    for i, m in enumerate(whites):
        pos[m] = ('w', x0 + i * ww, ww)
    for m in range(LOW, HIGH + 1):
        if m % 12 not in WHITE_PCS:
            left = pos[m - 1][1]
            bw = ww * 0.6
            pos[m] = ('b', left + ww - bw / 2, bw)
    return pos, ww

# ---------------- static / cached art ----------------
def rr(draw, box, r, **kw):
    draw.rounded_rectangle([round(v) for v in box], radius=round(r), **kw)

@lru_cache(None)
def card_img(ch, nxt):
    s = SS
    im = Image.new('RGBA', (CARD_W * s, CARD_H * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    rr(d, (0, 0, CARD_W * s - 1, CARD_H * s - 1), 20 * s, fill=(18, 16, 20, 120),
       outline=ACC + (150,), width=2 * s)
    f_h = font(500, 17 * s)
    d.text((22 * s, 16 * s), f"Key: {DATA['key']}", font=f_h, fill=ACC + (255,))
    notes, names = voicing(ch) if ch else ([], [])
    if names:
        d.text((CARD_W * s / 2, 16 * s), '  '.join(names), font=font(600, 17 * s),
               fill=(255, 255, 255, 235), anchor='ma')
    if nxt:
        d.text((CARD_W * s - 22 * s, 16 * s), f"Next  {nxt}", font=f_h,
               fill=(255, 255, 255, 200), anchor='ra')
    kx, ky, kw, kh = 22 * s, 46 * s, (CARD_W - 44) * s, 118 * s
    pos, ww = keyboard_layout(kx, kw)
    on = set(notes)
    for m, (t, x, w) in pos.items():
        if t != 'w': continue
        col = ACC + (255,) if m in on else (246, 244, 240, 255)
        rr(d, (x + 1.2 * s, ky, x + w - 1.2 * s, ky + kh), 4 * s, fill=col)
        if m == 60:
            d.text((x + w / 2, ky + kh - 8 * s), 'C4', font=font(400, 10 * s), fill=(150, 150, 150, 255), anchor='md')
    for m, (t, x, w) in pos.items():
        if t != 'b': continue
        col = ACC_DK + (255,) if m in on else (22, 20, 24, 255)
        rr(d, (x, ky, x + w, ky + kh * 0.6), 3 * s, fill=col)
    # note dots under keys
    fd = font(700, 12 * s)
    for m, nm in zip(notes, names):
        t, x, w = pos[m]
        cx, cy, r = x + w / 2, ky + kh + 22 * s, 14 * s
        d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACC + (255,), outline=(255, 255, 255, 90), width=s)
        d.text((cx, cy), nm, font=fd, fill=T['pill_text'] + (255,), anchor='mm')
    return im.resize((CARD_W, CARD_H), Image.LANCZOS)

@lru_cache(None)
def pill_img(ch):
    s = SS
    f = font(600, 46 * s)
    tw = f.getlength(ch)
    pw, ph = tw + 64 * s, 72 * s
    im = Image.new('RGBA', (int(pw + 40 * s), int(ph + 40 * s)), (0, 0, 0, 0))
    glow = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(glow).rounded_rectangle((20 * s, 20 * s, 20 * s + pw, 20 * s + ph), radius=ph / 2, fill=ACC + (110,))
    glow = glow.filter(ImageFilter.GaussianBlur(12 * s))
    im.alpha_composite(glow)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20 * s, 20 * s, 20 * s + pw, 20 * s + ph), radius=ph / 2, fill=ACC + (255,))
    d.text((20 * s + pw / 2, 20 * s + ph / 2 + 2 * s), ch, font=f, fill=T['pill_text'] + (255,), anchor='mm')
    return im.resize((im.width // s, im.height // s), Image.LANCZOS)

def shadowed_text(txt, f, fill, shadow=150, spacing=0):
    if spacing:
        widths = [f.getlength(c) for c in txt]
        tw = sum(widths) + spacing * (len(txt) - 1)
    else:
        tw = f.getlength(txt)
    asc, desc = f.getmetrics()
    pad = 24
    im = Image.new('RGBA', (int(tw + pad * 2), asc + desc + pad * 2), (0, 0, 0, 0))
    def put(dr, col):
        if spacing:
            x = pad
            for c, w in zip(txt, widths):
                dr.text((x, pad), c, font=f, fill=col); x += w + spacing
        else:
            dr.text((pad, pad), txt, font=f, fill=col)
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    put(ImageDraw.Draw(sh), (0, 0, 0, shadow))
    sh = sh.filter(ImageFilter.GaussianBlur(7))
    im.alpha_composite(sh)
    put(ImageDraw.Draw(im), fill)
    return im

@lru_cache(None)
def lyric_imgs(txt):
    f = font(500, 56)
    return shadowed_text(txt, f, (255, 255, 255, 255)), shadowed_text(txt, f, ACC + (255,)), f.getlength(txt)

@lru_cache(None)
def sub_img(txt):
    return shadowed_text(txt, font(400, 30), (255, 255, 255, 175), shadow=120)

@lru_cache(None)
def label_img(txt):
    return shadowed_text(txt, font(400, 30), (255, 255, 255, 215), shadow=120, spacing=12)

@lru_cache(None)
def count_img(n, lit):
    f = font(600, 64)
    col = ACC + (255,) if lit else (255, 255, 255, 90)
    return shadowed_text(str(n), f, col)

@lru_cache(None)
def scrim():
    """Soft dark gradient behind the UI block for legibility."""
    im = Image.new('L', (W // 4, H // 4), 0)
    d = ImageDraw.Draw(im)
    cy, ry, rx = 840 // 4, 330 // 4, 560 // 4
    d.ellipse((W // 8 - rx, cy - ry, W // 8 + rx, cy + ry), fill=80)
    im = im.filter(ImageFilter.GaussianBlur(40 // 4 * 2)).resize((W, H), Image.BILINEAR)
    out = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    out.putalpha(im)
    return out

# ---------------- timeline ----------------
chords = DATA['chords']  # [[t, name], ...]
end_t = DATA['duration']
def chord_at(t):
    idx = -1
    for i, (ct, _) in enumerate(chords):
        if ct <= t: idx = i
    return idx

def ease(x): x = max(0.0, min(1.0, x)); return 1 - (1 - x) ** 3
def ease_back(x):
    x = max(0.0, min(1.0, x)); c = 1.7
    return 1 + (c + 1) * (x - 1) ** 3 + c * (x - 1) ** 2

def place(canvas, im, cx, cy, alpha=1.0, scale=1.0):
    if alpha <= 0.01: return
    if scale != 1.0:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.BICUBIC)
    if alpha < 0.999:
        a = im.getchannel('A').point(lambda v: int(v * alpha))
        im = im.copy(); im.putalpha(a)
    canvas.alpha_composite(im, (int(round(cx - im.width / 2)), int(round(cy - im.height / 2))))

def frame(t):
    cv = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    first = chords[0][0]
    ui_in = ease((t - (first - 0.45)) / 0.5)
    ui_out = 1 - ease((t - (end_t - 1.2)) / 1.0)
    ui_a = ui_in * ui_out
    place(cv, scrim(), W / 2, H / 2, alpha=ui_a)

    # top progress bar
    prog = min(1.0, t / end_t)
    d = ImageDraw.Draw(cv)
    d.rectangle((0, 0, W, 7), fill=(255, 255, 255, 40))
    d.rectangle((0, 0, int(W * prog), 7), fill=ACC + (235,))

    # count-in
    for i, ct in enumerate(DATA['count_in']):
        a = ease((t - (ct - 0.12)) / 0.15) * (1 - ease((t - (first - 0.4)) / 0.25))
        lit = ct <= t < (DATA['count_in'][i + 1] if i + 1 < len(DATA['count_in']) else first)
        pop = 1.0 + 0.18 * (1 - ease((t - ct) / 0.25)) if t >= ct else 1.0
        place(cv, count_img(i + 1, lit), W / 2 + (i - 1.5) * 110, LYR_Y - 6, alpha=a * 0.97 + 0.0, scale=pop)
    if t < first - 0.25:
        place(cv, label_img('SEDIA'), W / 2, SUB_Y + 18, alpha=ease(t / 0.3) * (1 - ease((t - (first - 0.6)) / 0.3)))

    ci = chord_at(t)
    if ci < 0 and t >= first - 0.45: ci = 0
    if ci >= 0 and ui_a > 0:
        ct, ch = chords[ci]
        nxt = chords[ci + 1][1] if ci + 1 < len(chords) else ''
        nt = chords[ci + 1][0] if ci + 1 < len(chords) else end_t
        k = ease((t - ct) / 0.18) if t >= ct else 1.0
        if ci > 0 and k < 1:
            pch, pnx = chords[ci - 1][1], ch
            place(cv, card_img(pch, pnx), W / 2, CARD_Y + CARD_H / 2, alpha=ui_a * (1 - k))
        place(cv, card_img(ch, nxt), W / 2, CARD_Y + CARD_H / 2, alpha=ui_a * (k if ci > 0 else 1))
        # chord progress inside card
        cp = max(0.0, min(1.0, (t - ct) / (nt - ct)))
        bx0, bx1, by = CARD_X + 22, CARD_X + CARD_W - 22, CARD_Y + CARD_H - 14
        d = ImageDraw.Draw(cv)
        d.rounded_rectangle((bx0, by, bx1, by + 4), radius=2, fill=(255, 255, 255, int(55 * ui_a)))
        d.rounded_rectangle((bx0, by, bx0 + max(4, (bx1 - bx0) * cp), by + 4), radius=2, fill=ACC + (int(255 * ui_a),))
        # pill pop
        sc = 0.82 + 0.18 * ease_back((t - ct) / 0.32) if t >= ct else 1.0
        place(cv, pill_img(ch), W / 2, PILL_CY, alpha=ui_a, scale=sc)

    # lyrics
    for ln in DATA['lyrics']:
        s, e = ln['start'], ln['end']
        if not (s - 0.4 <= t <= e + 0.4): continue
        a = ease((t - (s - 0.12)) / 0.35) * (1 - ease((t - e) / 0.35))
        dy = 18 * (1 - ease((t - (s - 0.12)) / 0.45))
        if ln.get('label'):
            place(cv, label_img(ln['text']), W / 2, LYR_Y + dy, alpha=a)
        else:
            white, acc, tw = lyric_imgs(ln['text'])
            ks, ke = ln.get('k', [s, s + (e - s) * 0.8])
            p = max(0.0, min(1.0, (t - ks) / (ke - ks)))
            line = white.copy()
            if p > 0:
                cut = int(24 + tw * p)
                line.paste(acc.crop((0, 0, cut, acc.height)), (0, 0))
            place(cv, line, W / 2, LYR_Y + dy, alpha=a)
        if ln.get('sub'):
            place(cv, sub_img(ln['sub']), W / 2, SUB_Y + dy, alpha=a)
    return cv

# ---------------- ffmpeg ----------------
MASK = OUT + '.mask.png'
_m = Image.new('L', (CARD_W * 4, CARD_H * 4), 0)
ImageDraw.Draw(_m).rounded_rectangle((0, 0, CARD_W * 4 - 1, CARD_H * 4 - 1), radius=80, fill=255)
_m.resize((CARD_W, CARD_H), Image.LANCZOS).save(MASK)
vf = (
    f"[0:v]fps={FPS},scale={W}:{H},setsar=1,format=yuv420p,"
    f"eq=contrast=1.05:saturation=0.96:gamma=1.02,"
    f"curves=master='0/0.025 0.25/0.24 0.75/0.775 1/0.98',{T['grade']},"
    f"split=3[base][g][fr];"
    f"[g]scale=270:480,gblur=sigma=10,scale={W}:{H}[glow];"
    f"[base][glow]blend=all_mode=screen:all_opacity=0.10[b1];"
    f"[fr]crop={CARD_W}:{CARD_H}:{CARD_X}:{CARD_Y},gblur=sigma=14,format=yuva420p[gl0];"
    f"[2:v]format=gray[gm];[gl0][gm]alphamerge,"
    f"fade=t=in:st={chords[0][0] - 0.45:.2f}:d=0.5:alpha=1,fade=t=out:st={end_t - 1.2:.2f}:d=1.0:alpha=1[glass];"
    f"[b1]vignette=angle=PI/5.5:mode=forward,noise=alls=4:allf=t[b2];"
    f"[b2][glass]overlay={CARD_X}:{CARD_Y}[b3];"
    f"[b3][1:v]overlay=0:0:format=auto,format=yuv420p[v]"
)
cmd = ['ffmpeg', '-v', 'error', '-y', '-i', SRC,
       '-f', 'rawvideo', '-pix_fmt', 'rgba', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
       '-loop', '1', '-i', MASK,
       '-filter_complex', vf, '-map', '[v]', '-map', '0:a',
       '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-profile:v', 'high',
       '-c:a', 'aac', '-b:a', '192k', '-t', f'{DUR:.3f}', '-movflags', '+faststart', OUT]
if PREVIEW: cmd[cmd.index('medium')] = 'veryfast'
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
n = int(DUR * FPS)
for i in range(n):
    p.stdin.write(frame(i / FPS).tobytes())
    if i % 300 == 0: print(f'{THEME}: {i}/{n}', flush=True)
p.stdin.close(); p.wait(); os.remove(MASK)
print('done', OUT, p.returncode)
