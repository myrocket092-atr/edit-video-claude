// Macro shot of an acoustic guitar: spruce top, soundhole + rosette, rosewood
// fretboard, bridge, six strings. Strings visibly vibrate (long-exposure blur
// envelope) on every strum hit, synced to the generated guitar audio.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { BokehPass } from "three/addons/postprocessing/BokehPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

// strum hits, mirroring tools/make_music.py strum_pattern()
const CHORD_STRINGS = { G: [0, 1, 2, 3, 4, 5], D: [2, 3, 4, 5], Em: [0, 1, 2, 3, 4, 5], C: [1, 2, 3, 4, 5] };
export function strumHits(chords, bpm, total, start = 0) {
  const beat = 60 / bpm;
  const pat = [[0, true, 1.0], [1, true, 0.8], [1.5, false, 0.6], [2.5, false, 0.6], [3, true, 0.85], [3.5, false, 0.6]];
  const hits = [];
  let t = start;
  for (const c of chords) {
    for (const [b, down, v] of pat) {
      const at = t + b * beat;
      if (at >= total) continue;
      const strs = CHORD_STRINGS[c];
      const order = down ? strs : [...strs].reverse();
      order.forEach((s, k) => hits.push({ t: at + k * (down ? 0.012 : 0.009), s, v }));
    }
    t += 4 * beat;
  }
  return hits;
}

function canvasTex(w, h, draw, srgb = true) {
  const c = document.createElement("canvas"); c.width = w; c.height = h;
  draw(c.getContext("2d"), w, h);
  const t = new THREE.CanvasTexture(c);
  if (srgb) t.colorSpace = THREE.SRGBColorSpace;
  t.anisotropy = 8;
  return t;
}
function rand(seed) { let x = seed; return () => ((x = (x * 16807) % 2147483647) / 2147483647); }

export function createGuitar(canvas, { width = 1080, height = 1920 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0b0705);
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.22;

  const cam = new THREE.PerspectiveCamera(30, width / height, 0.5, 400);

  // ---------- textures ----------
  const R = rand(7);
  const spruce = canvasTex(1024, 2048, (g, w, h) => {
    const grd = g.createLinearGradient(0, 0, w, 0);
    grd.addColorStop(0, "#d8b07a"); grd.addColorStop(0.5, "#e2bd88"); grd.addColorStop(1, "#d3a872");
    g.fillStyle = grd; g.fillRect(0, 0, w, h);
    let x = 0;
    while (x < w) {
      const gap = 6 + R() * 10;
      g.strokeStyle = `rgba(${120 + R() * 30},${70 + R() * 20},${30},${0.25 + R() * 0.35})`;
      g.lineWidth = 1 + R() * 2.2;
      g.beginPath();
      for (let y = 0; y <= h; y += 64) g.lineTo(x + Math.sin(y * 0.002 + x) * 2.5, y);
      g.stroke();
      x += gap;
    }
    for (let i = 0; i < 160; i++) { // medullary rays (silk)
      g.fillStyle = `rgba(255,240,210,${0.04 + R() * 0.05})`;
      g.fillRect(R() * w, R() * h, 40 + R() * 120, 2 + R() * 3);
    }
  });
  spruce.wrapS = spruce.wrapT = THREE.RepeatWrapping;
  const rosewood = canvasTex(512, 2048, (g, w, h) => {
    g.fillStyle = "#3a2116"; g.fillRect(0, 0, w, h);
    for (let i = 0; i < 260; i++) {
      g.strokeStyle = `rgba(${20 + R() * 40},${10 + R() * 15},${5},${0.3 + R() * 0.4})`;
      g.lineWidth = 1 + R() * 3; const x = R() * w;
      g.beginPath(); g.moveTo(x, 0); g.bezierCurveTo(x + 10, h * 0.3, x - 10, h * 0.6, x + 4, h); g.stroke();
    }
  });
  const rosette = canvasTex(1024, 1024, (g, w, h) => {
    const c = w / 2; g.clearRect(0, 0, w, h);
    const ring = (r1, r2, col) => { g.beginPath(); g.arc(c, c, r2, 0, Math.PI * 2); g.arc(c, c, r1, 0, Math.PI * 2, true); g.fillStyle = col; g.fill(); };
    // radii as fraction of outer (6.2 cm); hole edge at 4.3 cm
    const s = c / 6.2;
    ring(4.55 * s, 4.75 * s, "#151010"); ring(4.75 * s, 4.82 * s, "#efe6d6");
    ring(4.82 * s, 5.4 * s, "#2a1a12");
    for (let a = 0; a < 360; a += 3) { // herringbone-ish band
      g.save(); g.translate(c, c); g.rotate((a * Math.PI) / 180);
      g.fillStyle = a % 6 ? "#d9c7a4" : "#4a2c1c"; g.fillRect(4.9 * s, -3, 0.42 * s, 6); g.restore();
    }
    ring(5.4 * s, 5.47 * s, "#efe6d6"); ring(5.47 * s, 5.62 * s, "#151010"); ring(5.62 * s, 5.68 * s, "#efe6d6");
  });
  const wound = canvasTex(8, 64, (g) => { g.fillStyle = "#777"; g.fillRect(0, 0, 8, 64); for (let y = 0; y < 64; y += 4) { g.fillStyle = "#fff"; g.fillRect(0, y, 8, 2); } }, false);
  wound.wrapS = wound.wrapT = THREE.RepeatWrapping; wound.repeat.set(1, 900);

  // ---------- body: guitar outline extruded down (sides), spruce top with the soundhole ----------
  const HOLE = 4.3;
  // half-width (cm) along z (neck joint at z=-10, tail at z=+40)
  const prof = [[-10, 0], [-9.6, 7], [-8.5, 11], [-6, 13.6], [-2, 14.6], [3, 13.6], [8, 11.8], [11, 11.6], [15, 13.5], [21, 18], [27, 19.6], [33, 18], [37.5, 12], [40, 4], [40.3, 0]];
  const outline = new THREE.Shape();
  prof.forEach(([z, w], i) => (i ? outline.lineTo(w, -z) : outline.moveTo(w, -z)));
  [...prof].reverse().forEach(([z, w]) => outline.lineTo(-w, -z));
  const hole = new THREE.Path(); hole.absarc(0, 0, HOLE, 0, Math.PI * 2, true); outline.holes.push(hole);
  spruce.repeat.set(1 / 18, 1 / 36);
  const topMat = new THREE.MeshPhysicalMaterial({ map: spruce, roughness: 0.32, clearcoat: 1, clearcoatRoughness: 0.08 });
  const sideMat = new THREE.MeshPhysicalMaterial({ color: 0x3b2114, roughness: 0.4, clearcoat: 1, clearcoatRoughness: 0.1 });
  const bodyGeo = new THREE.ExtrudeGeometry(outline, { depth: 10, bevelEnabled: true, bevelThickness: 0.25, bevelSize: 0.25, bevelSegments: 3, curveSegments: 64 });
  const body = new THREE.Mesh(bodyGeo, [topMat, sideMat]);
  body.rotation.x = -Math.PI / 2; body.position.y = -10.25; // extrude goes +z(shape) -> world +y; top cap at y = 0
  body.receiveShadow = true; scene.add(body);
  const cavity = new THREE.Mesh(new THREE.CircleGeometry(16, 64), new THREE.MeshStandardMaterial({ color: 0x2c1c10, roughness: 0.95 }));
  cavity.rotation.x = -Math.PI / 2; cavity.position.y = -9.5; scene.add(cavity);
  // neck under the fretboard beyond the body
  const neck = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.6, 62, 48), new THREE.MeshPhysicalMaterial({ color: 0x5a3018, roughness: 0.45, clearcoat: 0.6 }));
  neck.rotation.x = Math.PI / 2; neck.scale.set(1.05, 1, 0.8); neck.position.set(0, -2.2, -41); scene.add(neck);
  const glow = new THREE.PointLight(0xffb070, 12, 30, 2); glow.position.set(0, -5, 2); scene.add(glow);
  const ros = new THREE.Mesh(new THREE.RingGeometry(HOLE, 6.2, 128), new THREE.MeshPhysicalMaterial({ map: rosette, transparent: true, roughness: 0.3, clearcoat: 1, clearcoatRoughness: 0.08 }));
  ros.rotation.x = -Math.PI / 2; ros.position.y = 0.01; ros.receiveShadow = true;
  { const g = ros.geometry, p = g.attributes.position, u = g.attributes.uv; for (let i = 0; i < p.count; i++) u.setXY(i, 0.5 + p.getX(i) / 12.4, 0.5 + p.getY(i) / 12.4); }
  scene.add(ros);

  // ---------- fretboard + frets (neck runs toward -z) ----------
  const fbMat = new THREE.MeshStandardMaterial({ map: rosewood, roughness: 0.55 });
  const fb = new THREE.Mesh(new THREE.BoxGeometry(5.6, 0.6, 68), fbMat);
  fb.position.set(0, 0.3, -(HOLE + 0.6) - 34); fb.castShadow = fb.receiveShadow = true; scene.add(fb);
  const fretMat = new THREE.MeshPhysicalMaterial({ color: 0xd8d2c4, metalness: 1, roughness: 0.22 });
  const SCALE = 64.5;
  for (let n = 5; n <= 20; n++) {
    const fromNut = SCALE - SCALE / Math.pow(2, n / 12); // distance from nut
    const z = -(HOLE + 0.6) - ((SCALE - SCALE / Math.pow(2, 20 / 12)) - fromNut) - 0.4;
    const f = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 5.5, 16), fretMat);
    f.rotation.z = Math.PI / 2; f.position.set(0, 0.6, z); f.castShadow = true; scene.add(f);
  }
  // fret markers
  for (const [n, xs] of [[5, [0]], [7, [0]], [9, [0]], [12, [-1.2, 1.2]], [15, [0]], [17, [0]]]) {
    const fromNut = SCALE - SCALE / Math.pow(2, (n - 0.5) / 12);
    const z = -(HOLE + 0.6) - ((SCALE - SCALE / Math.pow(2, 20 / 12)) - fromNut) - 0.4;
    for (const x of xs) { const d = new THREE.Mesh(new THREE.CircleGeometry(0.3, 32), new THREE.MeshPhysicalMaterial({ color: 0xf2efe8, roughness: 0.2, iridescence: 0.6 })); d.rotation.x = -Math.PI / 2; d.position.set(x, 0.605, z); scene.add(d); }
  }

  // ---------- bridge ----------
  const BZ = 16.5;
  const bridge = new THREE.Mesh(new THREE.BoxGeometry(15, 0.9, 3.0), new THREE.MeshStandardMaterial({ map: rosewood, roughness: 0.5 }));
  bridge.position.set(0, 0.45, BZ + 0.9); bridge.castShadow = bridge.receiveShadow = true; scene.add(bridge);
  const saddle = new THREE.Mesh(new THREE.BoxGeometry(7.4, 0.42, 0.28), new THREE.MeshStandardMaterial({ color: 0xece4d0, roughness: 0.4 }));
  saddle.position.set(0, 1.08, BZ); saddle.castShadow = true; scene.add(saddle);
  const pinMat = new THREE.MeshPhysicalMaterial({ color: 0xf3efe6, roughness: 0.25, clearcoat: 1 });
  const dotMat = new THREE.MeshStandardMaterial({ color: 0x111111, roughness: 0.4 });
  for (let i = 0; i < 6; i++) {
    const x = (i - 2.5) * 1.15;
    const pin = new THREE.Mesh(new THREE.SphereGeometry(0.32, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), pinMat);
    pin.position.set(x, 0.9, BZ + 1.4); pin.scale.y = 0.6; pin.castShadow = true; scene.add(pin);
    const dot = new THREE.Mesh(new THREE.CircleGeometry(0.1, 16), dotMat); dot.rotation.x = -Math.PI / 2; dot.position.set(x, 1.1, BZ + 1.4); scene.add(dot);
  }

  // ---------- strings ----------
  const NUT_Z = -(HOLE + 0.6) - 68, NUT_Y = 1.05, SAD_Y = 1.3;
  const spanSad = 1.06, spanNut = 0.75;
  const radii = [0.066, 0.056, 0.046, 0.036, 0.022, 0.018];
  const isWound = [true, true, true, true, false, false];
  const bronze = new THREE.MeshPhysicalMaterial({ color: 0xc9a46b, metalness: 1, roughness: 0.3, bumpMap: wound, bumpScale: 0.4 });
  const steel = new THREE.MeshPhysicalMaterial({ color: 0xe8eaee, metalness: 1, roughness: 0.18 });
  const ghostMat = (w) => new THREE.MeshBasicMaterial({ color: w ? 0xd8b37a : 0xf0f2f6, transparent: true, opacity: 0.0, side: THREE.DoubleSide, depthWrite: false });
  const strings = [];
  const SEG = 80;
  for (let i = 0; i < 6; i++) {
    const xS = (i - 2.5) * spanSad, xN = (i - 2.5) * spanNut;
    const a = new THREE.Vector3(xS, SAD_Y, BZ), b = new THREE.Vector3(xN, NUT_Y, NUT_Z);
    const len = a.distanceTo(b);
    const geo = new THREE.CylinderGeometry(radii[i], radii[i], len, 12, SEG, true);
    const m = new THREE.Mesh(geo, isWound[i] ? bronze : steel);
    m.position.copy(a).add(b).multiplyScalar(0.5);
    m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), b.clone().sub(a).normalize());
    m.castShadow = true; scene.add(m);
    // vibration ghost: a ribbon spanning the string's swing
    const rg = new THREE.PlaneGeometry(1, len, 1, SEG);
    const ghost = new THREE.Mesh(rg, ghostMat(isWound[i]));
    ghost.position.copy(m.position); ghost.quaternion.copy(m.quaternion);
    scene.add(ghost);
    strings.push({ mesh: m, ghost, base: geo.attributes.position.array.slice(), len, rg });
  }

  // ---------- light ----------
  const key = new THREE.SpotLight(0xffd29a, 2600, 0, 0.42, 0.7, 2);
  key.position.set(-26, 42, 10); key.target.position.set(0, 0, -2);
  key.castShadow = true; key.shadow.mapSize.set(2048, 2048); key.shadow.bias = -0.0002; key.shadow.radius = 3;
  scene.add(key, key.target);
  const fill = new THREE.DirectionalLight(0x9fb4ff, 0.25); fill.position.set(30, 20, 30); scene.add(fill);
  const back = new THREE.SpotLight(0xffb070, 1400, 0, 0.6, 0.9, 2); back.position.set(10, 25, -70); back.target.position.set(0, 0, 0); scene.add(back, back.target);

  // far bokeh lights (shop lamps), defocused by the bokeh pass
  const bokehMat = (c) => new THREE.MeshBasicMaterial({ color: c, toneMapped: false });
  const R2 = rand(21);
  for (let i = 0; i < 26; i++) {
    const s = new THREE.Mesh(new THREE.SphereGeometry(0.6 + R2() * 0.9, 16, 12), bokehMat(new THREE.Color().setHSL(0.07 + R2() * 0.05, 0.8, 0.45 + R2() * 0.3)));
    s.position.set(-40 + R2() * 80, 6 + R2() * 40, -90 - R2() * 60); scene.add(s);
  }

  // ---------- post: depth of field ----------
  const composer = new EffectComposer(renderer);
  composer.setPixelRatio(1); composer.setSize(width, height);
  composer.addPass(new RenderPass(scene, cam));
  const bokeh = new BokehPass(scene, cam, { focus: 20, aperture: 0.004, maxblur: 0.016 });
  composer.addPass(bokeh);
  composer.addPass(new OutputPass());

  // ---------- per-frame ----------
  function amplitudes(hits, t) {
    const amp = [0, 0, 0, 0, 0, 0];
    for (const h of hits) {
      const dt = t - h.t;
      if (dt < 0 || dt > 3) continue;
      const attack = Math.min(1, dt / 0.012);
      amp[h.s] += h.v * attack * Math.exp(-dt * (h.s < 3 ? 2.4 : 3.2));
    }
    return amp.map((a) => Math.min(1.4, a));
  }

  const shots = {
    // close, soundhole + fretboard end, strings crossing frame
    try: (k) => ({ pos: [6.5 - 1.8 * k, 7.5 - 0.6 * k, 10.5 - 2 * k], look: [0.0, 0.6, -2.0], focus: -1 }),
    // low from the bridge, strings receding toward the soundhole
    jam: (k) => ({ pos: [-6.5 + 3 * k, 6.0, 33 - 3 * k], look: [0.5, 0.4, 1], focus: 4 }),
  };

  // t: time since shot start; k: 0..1 shot progress; hits in shot-local time
  function render(shot, t, k, hits) {
    const sh = shots[shot](k);
    cam.position.set(...sh.pos); cam.lookAt(...sh.look); cam.updateMatrixWorld();
    const amp = amplitudes(hits, t);
    strings.forEach((S, i) => {
      const A = amp[i] * (0.26 - i * 0.028);       // cm of swing at mid-string
      const g = S.mesh.geometry.attributes.position;
      const ph = Math.sin(t * 2 * Math.PI * (7 + i * 1.3));  // visible slow component (alias-free)
      for (let j = 0; j < g.count; j++) {
        const y = S.base[j * 3 + 1];
        const u = y / S.len + 0.5;                 // 0..1 along string
        g.setX(j, S.base[j * 3] + A * 0.35 * ph * Math.sin(Math.PI * u));
      }
      g.needsUpdate = true;
      const rp = S.rg.attributes.position;
      for (let j = 0; j < rp.count; j++) {
        const y = rp.getY(j); const u = y / S.len + 0.5;
        const side = j % 2 === 0 ? -1 : 1;
        rp.setX(j, side * A * Math.sin(Math.PI * u));
      }
      rp.needsUpdate = true;
      S.ghost.material.opacity = Math.min(0.55, amp[i] * 0.5);
    });
    // focus on the strings at the soundhole
    const target = new THREE.Vector3(0, 1.1, sh.focus);
    bokeh.uniforms.focus.value = cam.position.distanceTo(target);
    composer.render();
  }
  return { render };
}
