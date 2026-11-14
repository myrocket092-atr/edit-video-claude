"""Generates the HyperFrames project files for the 'Setup Home Studio Bajet' edit."""
import json, os, sys

OUT = sys.argv[1]
W, H = 1080, 1920
TOTAL = 41.1
YEL = "#FFD400"

CHECK_SVG = ('<svg viewBox="0 0 24 24" width="34" height="34"><path d="M4 12.5l5 5L20 6.5" '
             'fill="none" stroke="#0b0b0b" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>')

SCENE_CSS = f"""
    #root {{ position: absolute; inset: 0; font-family: Inter, sans-serif; }}
    .lcw {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; }}
    .lc {{ display: flex; align-items: center; gap: 28px; background: #0b0b0b; border-radius: 30px;
           padding: 24px 48px 24px 24px; min-width: 840px; border: 4px solid {YEL};
           box-shadow: 0 18px 50px rgba(0,0,0,.45); }}
    .num {{ width: 150px; height: 150px; border-radius: 24px; background: {YEL}; color: #0b0b0b;
            font-family: 'Archivo Black'; font-size: 80px; display: flex; align-items: center;
            justify-content: center; flex: none; }}
    .cat {{ font-weight: 900; font-size: 30px; letter-spacing: .12em; color: {YEL}; }}
    .name {{ font-family: 'Archivo Black'; font-size: 84px; line-height: 1; color: #fff; margin-top: 10px; }}
    .chipw {{ position: absolute; left: 56px; right: 56px; }}
    .chip {{ display: inline-flex; align-items: center; gap: 20px; background: rgba(11,11,11,.9);
             border-radius: 22px; padding: 16px 32px 16px 16px; font-weight: 700; font-size: 39px;
             color: #fff; box-shadow: 0 10px 30px rgba(0,0,0,.4); }}
    .chip b {{ color: {YEL}; font-weight: 900; }}
    .tick {{ width: 60px; height: 60px; border-radius: 16px; background: {YEL}; display: flex;
             align-items: center; justify-content: center; flex: none; }}
"""


def scene(cid, dur, css, body, script):
    return f"""<template>
  <style>{SCENE_CSS}{css}
  </style>
  <div id="root" data-composition-id="{cid}" data-width="{W}" data-height="{H}" data-duration="{dur}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{script}
    window.__timelines["{cid}"] = tl;
  </script>
</template>
"""


# ---------------------------------------------------------------- products
PRODUCTS = [
    dict(id="p1", start=4.35, dur=5.87, n="01", cat="MIDI CONTROLLER · NEKTAR", name="Nektar SE25",
         card_top=222, card_end=2.0, chips_top=940, chip_at=[2.15, 2.7, 3.25, 3.8], chip_exit=5.6,
         chips=["<b>25 kekunci</b> mini, sensitif velocity",
                "<b>USB plug &amp; play</b> — terus guna",
                "Butang <b>Octave &amp; Transpose</b>",
                "<b>Ringan</b>, muat atas meja kecil"]),
    dict(id="p2", start=10.22, dur=5.68, n="02", cat="AUDIO INTERFACE · M-AUDIO", name="M-Track Solo",
         card_top=336, card_end=1.75, chips_top=940, chip_at=[1.95, 2.5, 3.05, 3.6], chip_exit=5.45,
         chips=["<b>Crystal preamp</b> — vokal jernih",
                "Input <b>XLR/Line + Instrument</b>",
                "<b>Phantom +48V</b> untuk mic condenser",
                "<b>USB-powered</b> · out RCA + headphone"]),
    dict(id="p3", start=15.9, dur=5.1, n="03", cat="DYNAMIC MIC · MISHA", name="MA-990",
         card_top=1071, card_end=2.68, chips_top=1000, chip_at=[2.8, 3.2, 3.6], chip_exit=4.9,
         chips=["<b>Dinamik</b> — kurang tangkap noise bilik",
                "Ada <b>suis ON/OFF</b> pada badan",
                "Sesuai <b>vokal, podcast &amp; live</b>"]),
    dict(id="p4", start=21.0, dur=4.82, n="04", cat="STUDIO HEADPHONE · SUPERLUX", name="HD681",
         card_top=876, card_end=2.08, chips_top=300, chip_at=[0.9, 1.45, 2.0], chip_exit=4.6,
         chips=["Driver <b>50mm</b> — bass padu",
                "<b>Semi-open</b>, selesa pakai lama",
                "Free <b>adapter 6.35mm + pouch</b>"]),
    dict(id="p5", start=25.82, dur=2.51, n="05", cat="INSTRUMENT CABLE · KIRLIN", name="Kabel 3M",
         card_top=1178, card_end=2.48, chips_top=300, chip_at=[0.4, 0.7, 1.0], chip_exit=2.3,
         chips=["Panjang <b>3 meter</b>",
                "Jack <b>6.35mm (1/4\")</b>",
                "Kabel <b>24AWG</b> — signal bersih"]),
]


def product_scene(p):
    cid = p["id"]
    body = []
    body.append(f"""    <div id="{cid}-card" class="lcw clip" data-start="0" data-duration="{p['card_end'] + 0.2:.2f}" data-track-index="0" style="top:{p['card_top']}px">
      <div id="{cid}-card-in" class="lc">
        <div id="{cid}-num" class="num">{p['n']}</div>
        <div><div class="cat" data-var-text="{cid}-cat">{p['cat']}</div><div class="name" data-var-text="{cid}-name">{p['name']}</div></div>
      </div>
    </div>""")
    js = [f"""    tl.fromTo("#{cid}-card-in", {{ opacity: 0, scale: 0.86 }}, {{ opacity: 1, scale: 1, duration: 0.12, ease: "back.out(2)" }}, 0);
    tl.fromTo("#{cid}-num", {{ rotation: -18, scale: 0.6 }}, {{ rotation: 0, scale: 1, duration: 0.35, ease: "back.out(3)" }}, 0.12);
    tl.to("#{cid}-card-in", {{ opacity: 0, y: -24, duration: 0.15, ease: "power2.in" }}, {p['card_end']});"""]
    for i, (txt, at) in enumerate(zip(p["chips"], p["chip_at"])):
        top = p["chips_top"] + i * 100
        eid = f"{cid}-c{i + 1}"
        body.append(f"""    <div id="{eid}" class="chipw clip" data-start="{at}" data-duration="{p['dur'] - at:.2f}" data-track-index="{i + 1}" style="top:{top}px">
      <div id="{eid}-in" class="chip"><span class="tick">{CHECK_SVG}</span><span>{txt}</span></div>
    </div>""")
        js.append(f"""    tl.fromTo("#{eid}-in", {{ opacity: 0, x: -70 }}, {{ opacity: 1, x: 0, duration: 0.24, ease: "power3.out" }}, {at});
    tl.to("#{eid}-in", {{ opacity: 0, x: 40, duration: 0.18, ease: "power2.in" }}, {p['chip_exit'] + i * 0.04:.2f});""")
    return scene(cid, p["dur"], "", "\n".join(body), "\n".join(js))


# ---------------------------------------------------------------- hook
HOOK_CSS = f"""
    .hk {{ position: absolute; left: 0; right: 0; display: flex; flex-direction: column; align-items: center; }}
    .ha1 {{ font-family: 'Archivo Black'; font-size: 88px; color: #fff; line-height: 1.05;
            text-shadow: 0 6px 0 #000, 0 0 30px rgba(0,0,0,.7); }}
    .ha2 {{ font-family: 'Archivo Black'; font-size: 112px; color: #0b0b0b; background: {YEL};
            padding: 6px 34px 14px; border-radius: 22px; margin-top: 18px; line-height: 1.05; }}
    .hb1 {{ width: 880px; text-align: center; font-family: 'Archivo Black'; font-size: 92px; color: #fff;
            background: #0b0b0b; padding: 18px 0 14px; border-radius: 26px 26px 0 0; line-height: 1; }}
    .hb2 {{ width: 880px; text-align: center; font-family: 'Archivo Black'; font-size: 176px; color: #0b0b0b;
            background: {YEL}; padding: 4px 0 16px; border-radius: 0 0 26px 26px; line-height: 1; }}
    .hb3 {{ margin-top: 26px; font-weight: 900; font-size: 46px; color: #fff; background: rgba(11,11,11,.9);
            padding: 14px 34px; border-radius: 999px; letter-spacing: .04em; }}
    .hb3 b {{ color: {YEL}; }}
"""

HOOK_BODY = """    <div id="hook-a" class="hk clip" data-start="0" data-duration="1.3" data-track-index="0" style="top:640px">
      <div id="hook-a1" class="ha1" data-var-text="hook-line-1">NAK REKOD LAGU</div>
      <div id="hook-a2" class="ha2" data-var-text="hook-line-2">DARI RUMAH?</div>
    </div>
    <div id="hook-b" class="hk clip" data-start="1.3" data-duration="3.2" data-track-index="1" style="top:196px">
      <div id="hook-b1" class="hb1" data-var-text="hook-title">HOME STUDIO</div>
      <div id="hook-b2" class="hb2" data-var-text="hook-bajet">BAJET</div>
    </div>
    <div id="hook-c" class="hk clip" data-start="2.2" data-duration="2.3" data-track-index="2" style="top:600px">
      <div id="hook-c1" class="hb3"><b>5 BARANG</b> JE CUKUP ↓</div>
    </div>"""

HOOK_JS = """    tl.fromTo("#hook-a1", { scale: 1.12, y: -10 }, { scale: 1, y: 0, duration: 0.35, ease: "power3.out" }, 0);
    tl.fromTo("#hook-a2", { scale: 1.25, rotation: -4 }, { scale: 1, rotation: -2, duration: 0.4, ease: "back.out(2.5)" }, 0);
    tl.to("#hook-a2", { scale: 1.06, duration: 0.5, ease: "sine.inOut" }, 0.55);
    tl.fromTo("#hook-b1", { y: -40, opacity: 0.4 }, { y: 0, opacity: 1, duration: 0.1, ease: "power2.out" }, 1.3);
    tl.fromTo("#hook-b2", { scale: 1.3 }, { scale: 1, duration: 0.32, ease: "back.out(2.2)" }, 1.3);
    tl.fromTo("#hook-c1", { opacity: 0, y: 30, scale: 0.8 }, { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }, 2.2);
    tl.to("#hook-c1", { y: 10, duration: 0.45, ease: "sine.inOut", yoyo: true, repeat: 3 }, 2.6);
    tl.to("#hook-c1", { opacity: 0, duration: 0.12 }, 4.33);"""

# ---------------------------------------------------------------- progress
PROG_STARTS = [0.0, 5.87, 11.55, 16.65, 21.47, 24.0]
PROG_CSS = f"""
    #prog-wrap {{ position: absolute; top: 182px; left: 0; right: 0; display: flex; justify-content: center; gap: 12px; }}
    .seg {{ width: 150px; height: 10px; border-radius: 6px; background: rgba(255,255,255,.35); overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,.35); }}
    .fill {{ width: 100%; height: 100%; background: {YEL}; transform-origin: 0 50%; }}
"""


def progress_scene():
    segs = "\n".join(f'        <div class="seg"><div id="prog-f{i + 1}" class="fill"></div></div>' for i in range(5))
    body = f"""    <div id="prog" class="clip" data-start="0" data-duration="24" data-track-index="0" data-layout-allow-overlap>
      <div id="prog-wrap">
{segs}
      </div>
    </div>"""
    js = ["    tl.fromTo(\"#prog-wrap\", { opacity: 0, y: -12 }, { opacity: 1, y: 0, duration: 0.25, ease: \"power2.out\" }, 0);"]
    for i in range(5):
        a, b = PROG_STARTS[i], PROG_STARTS[i + 1]
        js.append(f'    tl.fromTo("#prog-f{i + 1}", {{ scaleX: 0 }}, {{ scaleX: 1, duration: {b - a:.2f}, ease: "none" }}, {a});')
    js.append('    tl.to("#prog-wrap", { opacity: 0, duration: 0.2 }, 23.75);')
    return scene("progress", 24, PROG_CSS, body, "\n".join(js))


# ---------------------------------------------------------------- recap
RECAP_ITEMS = ["<b>Nektar SE25</b> · MIDI controller", "<b>M-Track Solo</b> · interface",
               "<b>Misha MA-990</b> · mic dinamik", "<b>Superlux HD681</b> · headphone",
               "<b>Kirlin 3M</b> · kabel"]
RECAP_CSS = f"""
    #recap-card {{ position: absolute; top: 290px; left: 70px; right: 70px; }}
    #recap-in {{ background: rgba(11,11,11,.9); border-radius: 30px; padding: 34px 40px 26px; border: 4px solid {YEL}; }}
    .rt {{ font-family: 'Archivo Black'; font-size: 66px; color: #fff; line-height: 1; margin-bottom: 18px; }}
    .rt span {{ color: {YEL}; }}
    .row {{ display: flex; align-items: center; gap: 22px; font-size: 42px; font-weight: 700; color: #fff; height: 76px; }}
    .row b {{ color: #fff; font-weight: 900; }}
    .box {{ width: 52px; height: 52px; border-radius: 14px; border: 4px solid {YEL}; position: relative; flex: none; }}
    .boxfill {{ position: absolute; inset: 0; background: {YEL}; display: flex; align-items: center; justify-content: center; }}
    #recap-tag {{ position: absolute; top: 880px; left: 0; right: 0; display: flex; justify-content: center; }}
    #recap-tag-in {{ font-family: 'Archivo Black'; font-size: 64px; background: {YEL}; color: #0b0b0b; padding: 12px 40px 18px; border-radius: 20px; }}
"""
RECAP_TICKS = [0.55, 1.0, 1.45, 1.9, 2.35]


def recap_scene():
    rows = "\n".join(
        f'        <div class="row"><div class="box"><div id="rc-b{i + 1}" class="boxfill">{CHECK_SVG}</div></div><span id="rc-t{i + 1}">{t}</span></div>'
        for i, t in enumerate(RECAP_ITEMS))
    body = f"""    <div id="recap-card" class="clip" data-start="0" data-duration="4.92" data-track-index="0">
      <div id="recap-in">
        <div class="rt">5 BARANG = <span>1 STUDIO</span></div>
{rows}
      </div>
    </div>
    <div id="recap-tag" class="clip" data-start="2.9" data-duration="2.02" data-track-index="1">
      <div id="recap-tag-in">SIAP UNTUK REKOD!</div>
    </div>"""
    js = ['    tl.fromTo("#recap-in", { opacity: 0, y: -50, scale: 0.94 }, { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "power3.out" }, 0);']
    for i, at in enumerate(RECAP_TICKS):
        js.append(f'    tl.fromTo("#rc-b{i + 1}", {{ scale: 0, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "back.out(3)" }}, {at});')
        js.append(f'    tl.fromTo("#rc-t{i + 1}", {{ opacity: 0.45 }}, {{ opacity: 1, duration: 0.15 }}, {at});')
    js.append('    tl.fromTo("#recap-tag-in", { opacity: 0, scale: 1.6, rotation: -6 }, { opacity: 1, scale: 1, rotation: -3, duration: 0.25, ease: "back.out(2)" }, 2.9);')
    js.append('    tl.to(["#recap-in", "#recap-tag-in"], { opacity: 0, duration: 0.15, ease: "power2.in" }, 4.72);')
    return scene("recap", 4.92, RECAP_CSS, body, "\n".join(js))


# ---------------------------------------------------------------- CTA
CTA_CSS = f"""
    .cw {{ position: absolute; left: 0; right: 0; display: flex; justify-content: center; }}
    #cta-h {{ font-family: 'Archivo Black'; font-size: 104px; color: #0b0b0b; line-height: 1; }}
    #cta-pill {{ font-weight: 900; font-size: 42px; background: {YEL}; color: #0b0b0b; padding: 18px 40px; border-radius: 999px; border: 4px solid #0b0b0b; }}
    #cta-sub {{ font-weight: 700; font-size: 40px; color: #222; }}
    #cta-save {{ font-weight: 900; font-size: 44px; color: #fff; background: #0b0b0b; padding: 16px 36px; border-radius: 18px; }}
    #cta-save b {{ color: {YEL}; }}
"""
CTA_BODY = """    <div id="cta-h-w" class="cw clip" data-start="0" data-duration="7.5" data-track-index="0" style="top:236px">
      <div id="cta-h" data-var-text="cta-headline">NAK SET NI?</div>
    </div>
    <div id="cta-pill-w" class="cw clip" data-start="0.75" data-duration="6.75" data-track-index="1" style="top:372px">
      <div id="cta-pill" data-var-text="cta-store">Dapatkan di Twinnies Home Music</div>
    </div>
    <div id="cta-sub-w" class="cw clip" data-start="1.4" data-duration="6.1" data-track-index="2" style="top:480px">
      <div id="cta-sub" data-var-text="cta-sub">DM untuk harga &amp; stok terkini</div>
    </div>
    <div id="cta-save-w" class="cw clip" data-start="3.6" data-duration="3.9" data-track-index="3" style="top:550px">
      <div id="cta-save"><b>SAVE</b> video ni untuk rujukan!</div>
    </div>"""
CTA_JS = """    tl.fromTo("#cta-h", { opacity: 0, scale: 1.8 }, { opacity: 1, scale: 1, duration: 0.28, ease: "power4.out" }, 0);
    tl.fromTo("#cta-pill", { opacity: 0, y: 40, scale: 0.85 }, { opacity: 1, y: 0, scale: 1, duration: 0.3, ease: "back.out(2)" }, 0.75);
    tl.to("#cta-pill", { scale: 1.05, duration: 0.6, ease: "sine.inOut", yoyo: true, repeat: 3 }, 1.4);
    tl.fromTo("#cta-sub", { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.3, ease: "power2.out" }, 1.4);
    tl.fromTo("#cta-save", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }, 3.6);
    tl.to(["#cta-h", "#cta-pill", "#cta-sub", "#cta-save"], { opacity: 0, duration: 0.25, ease: "power2.in" }, 7.1);"""

# ---------------------------------------------------------------- root
SCENES = [("hook", 0, 4.5), ("progress", 4.35, 24.0)] + [(p["id"], p["start"], p["dur"]) for p in PRODUCTS] + \
         [("recap", 28.33, 4.92), ("cta", 33.25, 7.85)]

# (id, file, hit_time, peak_in_file, media_start, duration, volume)
SFX = [
    ("s-hook-impact", "impact-bass-1", 0.0, 0.073, 0, 1.4, 0.45),
    ("s-hook-whoosh", "whoosh-cinematic", 1.30, 2.503, 1.9, 1.5, 0.5),
    ("s-p1-whoosh", "whoosh", 4.47, 0.162, 0, 0.57, 0.6),
    ("s-p2-whoosh", "whoosh", 10.36, 0.162, 0, 0.57, 0.6),
    ("s-p3-whoosh", "whoosh-cinematic", 16.03, 2.503, 1.9, 1.3, 0.45),
    ("s-p4-whoosh", "whoosh", 21.12, 0.162, 0, 0.57, 0.6),
    ("s-p5-whoosh", "whoosh", 25.95, 0.162, 0, 0.57, 0.6),
    ("s-recap-whoosh", "whoosh-cinematic", 28.33, 2.503, 1.9, 1.3, 0.45),
    ("s-riser", "riser", 33.25, 3.472, 0, 3.45, 0.3),
    ("s-cta-impact", "impact-bass-2", 33.25, 1.986, 1.8, 1.3, 0.4),
    ("s-cta-sparkle", "sparkle", 33.25 + 1.05, 0.027, 0, 1.6, 0.4),
    ("s-cta-save", "pop", 33.25 + 3.75, 0.12, 0, 0.7, 0.8),
]
# number-badge pops (badge lands ~0.3 s after scene start)
for p in PRODUCTS:
    SFX.append((f"s-{p['id']}-num", "pop", p["start"] + 0.42, 0.12, 0, 0.7, 0.7))
    for i, at in enumerate(p["chip_at"]):
        f, pk, vol = (("click", 0.073, 0.9) if i % 2 == 0 else ("key-press", 0.076, 2.2))
        SFX.append((f"s-{p['id']}-c{i + 1}", f, p["start"] + at + 0.12, pk, 0, 0.4, vol))
for i, at in enumerate(RECAP_TICKS):
    f, pk, vol = (("pop", 0.12, 0.7) if i % 2 == 0 else ("click", 0.073, 0.9))
    SFX.append((f"s-recap-t{i + 1}", f, 28.33 + at + 0.1, pk, 0, 0.5, vol))
SFX.append(("s-recap-tag", "impact-bass-1", 28.33 + 2.95, 0.073, 0, 0.9, 0.3))

FRAME = 1 / 30
MEDIA_LEN = {'impact-bass-1':2.12,'impact-bass-2':2.59,'whoosh':0.57,'whoosh-cinematic':5.54,'pop':0.72,'click':0.37,'key-press':0.43,'riser':10.03,'sparkle':1.80}


def audio_tags():
    out = []
    for n, (eid, f, hit, peak, ms, dur, vol) in enumerate(SFX):
        start = round(hit + FRAME - (peak - ms), 3)
        if start < 0:
            ms += -start
            start = 0
        dur = min(dur, TOTAL - start, MEDIA_LEN[f] - ms)
        ms_attr = f' data-media-start="{ms:.3f}"' if ms else ""
        fade = ' data-fade-out="0.25"' if f in ("riser", "whoosh-cinematic", "impact-bass-2") else ""
        out.append(f'      <audio id="{eid}" class="clip" src="assets/sfx/{f}.mp3" data-start="{start:.3f}" data-duration="{dur:.2f}"'
                   f'{ms_attr} data-volume="{vol}"{fade} data-track-index="{20 + n}"></audio>')
    return "\n".join(out)


# camera moves on the footage: (tween|set, time, props, duration, ease)
CAM = [
    ("set", 0, "scale: 1, rotation: 0, x: 0, y: 0"),
    ("to", 1.3, "scale: 1.04", 3.0, "none"),
    ("set", 4.35, "scale: 1"),
    ("to", 6.4, "scale: 1.16, x: -30", 1.75, "sine.inOut"),
    ("set", 8.17, "scale: 1.12, x: 0"),
    ("to", 8.17, "scale: 1.0", 2.0, "power2.out"),
    ("to", 11.97, "scale: 1.2, y: 40", 2.05, "sine.inOut"),
    ("set", 14.05, "scale: 1.15, y: 0"),
    ("to", 14.05, "scale: 1.0", 1.5, "power2.out"),
    ("set", 18.58, "scale: 1.28"),
    ("to", 18.58, "scale: 1.04", 2.4, "power3.out"),
    ("set", 21.07, "scale: 1"),
    ("to", 23.1, "scale: 1.12", 2.0, "sine.inOut"),
    ("to", 25.1, "scale: 1.18", 0.65, "power1.in"),
    ("set", 25.8, "scale: 1"),
    ("to", 28.33, "scale: 1.1, rotation: -1.5", 4.9, "none"),
    ("set", 33.25, "scale: 1, rotation: 0"),
]
FLASHES = [(1.30, 0.95), (4.47, 0.5), (10.33, 0.5), (16.03, 0.55), (21.1, 0.5), (25.9, 0.45), (28.33, 0.6), (33.25, 0.7)]


def root_html():
    hosts = []
    for n, (cid, st, du) in enumerate(SCENES):
        hosts.append(f'      <div id="{cid}" data-composition-id="{cid}" data-composition-src="compositions/{cid}.html" '
                     f'data-start="{st}" data-duration="{du}" data-track-index="{3 + n}" data-track-kind="graphics" '
                     f'data-width="{W}" data-height="{H}" style="z-index:{10 + n}"></div>')
    cam = []
    for c in CAM:
        if c[0] == "set":
            cam.append(f'      tl.set("#cam", {{ {c[2]} }}, {c[1]});')
        else:
            cam.append(f'      tl.to("#cam", {{ {c[2]}, duration: {c[3]}, ease: "{c[4]}" }}, {c[1]});')
    fl = ['      tl.set("#flash", { opacity: 0 }, 0);']
    for t, a in FLASHES:
        fl.append(f'      tl.set("#flash", {{ opacity: {a} }}, {t});\n      tl.to("#flash", {{ opacity: 0, duration: 0.22, ease: "power2.out" }}, {t});')
    vars_ = [
        {"id": "hook-line-1", "type": "string", "label": "Hook baris 1", "default": "NAK REKOD LAGU"},
        {"id": "hook-line-2", "type": "string", "label": "Hook baris 2", "default": "DARI RUMAH?"},
        {"id": "cta-store", "type": "string", "label": "Nama kedai (CTA)", "default": "Dapatkan di Twinnies Home Music"},
    ]
    return f"""<!doctype html>
<html lang="ms" data-composition-variables='{json.dumps(vars_)}'>
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="assets/vendor/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: {W}px; height: {H}px; overflow: hidden; background: #000; }}
      #root {{ width: 100%; height: 100%; position: relative; overflow: hidden; font-family: Inter, sans-serif; }}
      #cam, #teaser-cam {{ position: absolute; inset: 0; transform-origin: 50% 50%; }}
      #main-video, #teaser {{ position: absolute; left: 0; top: 0; width: {W}px; height: {H}px; object-fit: cover; }}
      #teaser-cam {{ z-index: 2; }}
      #cam {{ z-index: 1; }}
      #flash {{ position: absolute; inset: 0; background: #fff; opacity: 0; z-index: 40; pointer-events: none; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="{W}" data-height="{H}">
      <div id="cam">
        <video id="main-video" class="clip" src="assets/footage.mp4" data-start="0" data-duration="{TOTAL}"
          data-has-audio="true" data-volume="0.9" playsinline data-track-index="0"></video>
      </div>
      <div id="teaser-cam">
        <video id="teaser" class="clip" src="assets/footage.mp4" data-start="0" data-duration="1.3"
          data-media-start="29.4" muted playsinline data-track-index="1"></video>
      </div>
      <div id="flash" class="clip" data-start="0" data-duration="{TOTAL}" data-track-index="2" data-layout-ignore></div>
{chr(10).join(hosts)}
{audio_tags()}
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#teaser-cam", {{ scale: 1.3 }}, {{ scale: 1.05, duration: 1.3, ease: "power2.out" }}, 0);
{chr(10).join(cam)}
{chr(10).join(fl)}
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
"""


os.makedirs(f"{OUT}/compositions", exist_ok=True)
files = {"index.html": root_html(),
         "compositions/hook.html": scene("hook", 4.5, HOOK_CSS, HOOK_BODY, HOOK_JS),
         "compositions/progress.html": progress_scene(),
         "compositions/recap.html": recap_scene(),
         "compositions/cta.html": scene("cta", 7.85, CTA_CSS, CTA_BODY, CTA_JS)}
for p in PRODUCTS:
    files[f"compositions/{p['id']}.html"] = product_scene(p)
for k, v in files.items():
    open(f"{OUT}/{k}", "w").write(v)
print("wrote", len(files), "files;", len(SFX), "sfx")
