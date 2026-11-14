// Photoreal shipping box (regular slotted carton) rendered with Three.js and
// composited over the shop photo: kraft board, printed front, corrugated cut
// edges, glossy packing tape, flaps on real hinges, soft contact shadow.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const W = 52, H = 46, D = 34, T = 0.55; // cm (outer), wall thickness

function loadImage(src) {
  return new Promise((res, rej) => { const i = new Image(); i.onload = () => res(i); i.onerror = rej; i.src = src; });
}

export async function createBox(canvas, { width = 1080, height = 1920, kraftSrc = "assets/img/kraft.png", insideSrc = "assets/img/inside.png" } = {}) {
  const [kraftImg, insideImg] = await Promise.all([loadImage(kraftSrc), loadImage(insideSrc)]);
  await document.fonts.ready;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 0.95;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.35;

  const cam = new THREE.PerspectiveCamera(58, width / height, 1, 2000);

  // ---------- textures ----------
  const tex = (c, srgb = true) => { const t = new THREE.CanvasTexture(c); if (srgb) t.colorSpace = THREE.SRGBColorSpace; t.anisotropy = 8; return t; };
  function kraftCanvas(wcm, hcm, ppc = 22, ox = 0, oy = 0) {
    const c = document.createElement("canvas"); c.width = Math.round(wcm * ppc); c.height = Math.round(hcm * ppc);
    const g = c.getContext("2d");
    g.drawImage(kraftImg, ox, oy, Math.min(kraftImg.width * 0.7, kraftImg.width - ox), Math.min(kraftImg.height * 0.7, kraftImg.height - oy), 0, 0, c.width, c.height);
    return [c, g, ppc];
  }
  const ink = "rgba(52,32,18,0.86)";
  // front: printed
  const [fc, fg, fp] = kraftCanvas(W, H);
  fg.fillStyle = ink; fg.strokeStyle = ink; fg.textAlign = "center";
  fg.font = `italic 700 ${12.5 * fp}px "EB Garamond", serif`; fg.fillText("Bullet", fc.width / 2, 21 * fp);
  fg.font = `800 ${3.6 * fp}px "JetBrains Mono", monospace`; fg.fillText("A C - 1 5 C", fc.width / 2, 28 * fp);
  fg.font = `500 ${1.7 * fp}px "JetBrains Mono", monospace`; fg.fillText("ACOUSTIC AMPLIFIER  ·  15 WATT", fc.width / 2, 31.6 * fp);
  fg.font = `500 ${1.45 * fp}px "JetBrains Mono", monospace`; fg.fillText("MIC + GUITAR INPUT  ·  CHORUS  ·  BLUETOOTH", fc.width / 2, 34.2 * fp);
  fg.textAlign = "left"; fg.font = `600 ${1.4 * fp}px "JetBrains Mono", monospace`;
  fg.fillText("▲▲  THIS SIDE UP", 2.6 * fp, 4.4 * fp);
  fg.lineWidth = 0.18 * fp; fg.strokeRect(W * fp - 12.5 * fp, 2.9 * fp, 10 * fp, 2.3 * fp);
  fg.textAlign = "center"; fg.fillText("FRAGILE", W * fp - 7.5 * fp, 4.5 * fp);
  fg.textAlign = "left"; fg.fillText("MADE IN PRC   ·   1 PC", 2.6 * fp, (H - 2.6) * fp);
  // umbrella / glass handling icons
  fg.lineWidth = 0.16 * fp;
  fg.beginPath(); fg.arc((W - 10) * fp, (H - 4.2) * fp, 1.3 * fp, Math.PI, 0); fg.stroke();
  fg.beginPath(); fg.moveTo((W - 10) * fp, (H - 4.2) * fp); fg.lineTo((W - 10) * fp, (H - 2.2) * fp); fg.stroke();
  fg.beginPath(); fg.moveTo((W - 6.4) * fp, (H - 5.4) * fp); fg.lineTo((W - 4.4) * fp, (H - 5.4) * fp); fg.lineTo((W - 5.0) * fp, (H - 3.8) * fp); fg.lineTo((W - 5.8) * fp, (H - 3.8) * fp); fg.closePath(); fg.stroke();
  fg.beginPath(); fg.moveTo((W - 5.4) * fp, (H - 3.8) * fp); fg.lineTo((W - 5.4) * fp, (H - 2.3) * fp); fg.stroke();
  const frontTex = tex(fc);
  // side: shipping label with barcode
  const [sc, sg, sp] = kraftCanvas(D, H, 22, 200, 100);
  sg.fillStyle = "#f1eee7"; sg.fillRect(6 * sp, 24 * sp, 16 * sp, 11 * sp);
  sg.fillStyle = "#1b1b1b"; let bx = 7.2 * sp;
  for (let i = 0; i < 60; i++) { const w = (i * 37) % 3 + 1; sg.fillRect(bx, 25.4 * sp, w * 0.09 * sp, 5.2 * sp); bx += (w * 0.09 + 0.12) * sp; }
  sg.font = `600 ${1.05 * sp}px "JetBrains Mono", monospace`; sg.fillText("6 9 2 1 0 0 3 5 7 0 8", 7.4 * sp, 32.4 * sp);
  sg.fillText("AC-15C  BRN", 7.4 * sp, 34 * sp);
  sg.fillStyle = ink; sg.font = `800 ${2.6 * sp}px "JetBrains Mono", monospace`; sg.fillText("AC-15C", 6 * sp, 10 * sp);
  sg.font = `italic 700 ${5 * sp}px "EB Garamond", serif`; sg.fillText("Bullet", 6 * sp, 17.5 * sp);
  const sideTex = tex(sc);
  const [pc] = kraftCanvas(W, D, 22, 300, 400); const plainTex = tex(pc);
  const [pc2] = kraftCanvas(W, D, 22, 120, 700); const plainTex2 = tex(pc2);
  // corrugated cut edge
  const flute = (() => { const c = document.createElement("canvas"); c.width = 256; c.height = 32; const g = c.getContext("2d");
    g.fillStyle = "#b28a5a"; g.fillRect(0, 0, 256, 32); g.fillStyle = "#c9a26f"; g.fillRect(0, 0, 256, 5); g.fillRect(0, 27, 256, 5);
    g.strokeStyle = "#8b6a42"; g.lineWidth = 2; g.beginPath(); for (let x = 0; x <= 256; x += 2) g.lineTo(x, 16 + Math.sin(x / 5) * 9); g.stroke();
    const t = tex(c); t.wrapS = THREE.RepeatWrapping; t.repeat.set(12, 1); return t; })();
  // inside view: dust bag + foam
  const insideTex = tex(insideImg);
  const grain = (() => { const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d"); const id = g.createImageData(256, 256);
    let s = 9; for (let i = 0; i < id.data.length; i += 4) { s = (s * 16807) % 2147483647; const v = 110 + (s % 40); id.data[i] = id.data[i + 1] = id.data[i + 2] = v; id.data[i + 3] = 255; }
    g.putImageData(id, 0, 0); const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(6, 6); return t; })();

  const board = (map) => new THREE.MeshStandardMaterial({ map, roughness: 0.92, bumpMap: grain, bumpScale: 0.25 });
  const edgeMat = new THREE.MeshStandardMaterial({ map: flute, roughness: 1 });
  const innerMat = new THREE.MeshStandardMaterial({ color: 0xc8b08c, roughness: 1, map: plainTex2 });

  // BoxGeometry face order: +x, -x, +y, -y, +z, -z
  const slab = (w, h, d, mats) => { const m = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), mats); m.castShadow = true; m.receiveShadow = true; return m; };

  const box = new THREE.Group(); scene.add(box);
  // walls
  { const m = slab(W, H, T, [edgeMat, edgeMat, edgeMat, edgeMat, board(frontTex), innerMat]); m.position.set(0, H / 2, D / 2 - T / 2); box.add(m); }
  { const m = slab(W, H, T, [edgeMat, edgeMat, edgeMat, edgeMat, innerMat, board(plainTex)]); m.position.set(0, H / 2, -D / 2 + T / 2); box.add(m); }
  { const m = slab(T, H, D - 2 * T, [board(sideTex), innerMat, edgeMat, edgeMat, edgeMat, edgeMat]); m.position.set(W / 2 - T / 2, H / 2, 0); box.add(m); }
  { const m = slab(T, H, D - 2 * T, [innerMat, board(sideTex), edgeMat, edgeMat, edgeMat, edgeMat]); m.position.set(-W / 2 + T / 2, H / 2, 0); box.add(m); }
  // contents seen from above: dust bag over the amp + foam caps
  const contents = new THREE.Mesh(new THREE.PlaneGeometry(W - 2 * T, D - 2 * T), new THREE.MeshPhysicalMaterial({ map: insideTex, roughness: 0.35, clearcoat: 0.8, clearcoatRoughness: 0.3 }));
  contents.rotation.x = -Math.PI / 2; contents.position.y = H - 4.5; contents.receiveShadow = true; box.add(contents);

  // flaps (pivot groups on the hinge lines)
  function flap(w, d, mat, pivot, offset, yLift) {
    const p = new THREE.Group(); p.position.copy(pivot); p.position.y += yLift;
    const m = slab(w, T * 0.9, d, mat); m.position.copy(offset); p.add(m); box.add(p); return p;
  }
  const topMatA = [edgeMat, edgeMat, board(plainTex), innerMat, edgeMat, edgeMat];
  const topMatB = [edgeMat, edgeMat, board(plainTex2), innerMat, edgeMat, edgeMat];
  const minorL = flap(15, D - 2 * T, topMatB, new THREE.Vector3(-W / 2 + T, H, 0), new THREE.Vector3(7.5, 0, 0), T * 0.45);
  const minorR = flap(15, D - 2 * T, topMatB, new THREE.Vector3(W / 2 - T, H, 0), new THREE.Vector3(-7.5, 0, 0), T * 0.45);
  const front = flap(W, D / 2, topMatA, new THREE.Vector3(0, H, D / 2), new THREE.Vector3(0, 0, -D / 4), T * 1.35);
  const back = flap(W, D / 2, topMatB, new THREE.Vector3(0, H, -D / 2), new THREE.Vector3(0, 0, D / 4), T * 1.35);

  // packing tape: halves ride on each major flap, plus the tabs down the sides
  const tapeMat = new THREE.MeshPhysicalMaterial({ color: 0xdcae68, roughness: 0.2, clearcoat: 1, clearcoatRoughness: 0.08, transparent: true, opacity: 0.9, side: THREE.DoubleSide, envMapIntensity: 0.4 });
  const tapeOn = (parent, w, d, pos) => { const m = new THREE.Mesh(new THREE.PlaneGeometry(w, d), tapeMat); m.rotation.x = -Math.PI / 2; m.position.copy(pos); parent.add(m); return m; };
  const tapeF = tapeOn(front, W + 0.2, 3.6, new THREE.Vector3(0, T * 0.5 + 0.02, -D / 2 + 1.8));
  const tapeB = tapeOn(back, W + 0.2, 3.6, new THREE.Vector3(0, T * 0.5 + 0.02, D / 2 - 1.8));
  const sideTape = [];
  for (const sx of [1, -1]) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(7.2, 9), tapeMat);
    m.rotation.y = sx * Math.PI / 2; m.position.set(sx * (W / 2 + 0.03), H - 4.5 + T, 0); box.add(m); sideTape.push(m);
  }
  // knife slit along the seam
  const slit = new THREE.Mesh(new THREE.PlaneGeometry(W, 0.18), new THREE.MeshBasicMaterial({ color: 0x1a0f07 }));
  slit.rotation.x = -Math.PI / 2; slit.position.set(0, H + T * 1.9 + 0.03, 0); box.add(slit);

  // ---------- lights + shadow catcher ----------
  const hemi = new THREE.HemisphereLight(0xfff0dd, 0x5a3a28, 0.9); scene.add(hemi);
  const key = new THREE.DirectionalLight(0xffe6c8, 2.1); key.position.set(-70, 140, 120); key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048); Object.assign(key.shadow.camera, { left: -90, right: 90, top: 90, bottom: -90, near: 10, far: 500 });
  key.shadow.radius = 8; key.shadow.bias = -0.0004; scene.add(key);
  const fill = new THREE.DirectionalLight(0xcfd8ff, 0.45); fill.position.set(90, 60, 40); scene.add(fill);
  const frontLight = new THREE.DirectionalLight(0xffe2c0, 0.55); frontLight.position.set(-10, 20, 160); scene.add(frontLight);
  const floor = new THREE.Mesh(new THREE.PlaneGeometry(600, 600), new THREE.ShadowMaterial({ opacity: 0.5 }));
  floor.rotation.x = -Math.PI / 2; floor.receiveShadow = true; scene.add(floor);
  // ambient-occlusion skirt
  const ao = (() => { const c = document.createElement("canvas"); c.width = c.height = 256; const g = c.getContext("2d");
    const r = g.createRadialGradient(128, 128, 30, 128, 128, 128); r.addColorStop(0, "rgba(0,0,0,0.85)"); r.addColorStop(0.55, "rgba(0,0,0,0.45)"); r.addColorStop(1, "rgba(0,0,0,0)");
    g.fillStyle = r; g.fillRect(0, 0, 256, 256); return new THREE.CanvasTexture(c); })();
  const aoM = new THREE.Mesh(new THREE.PlaneGeometry(W * 1.45, D * 1.7), new THREE.MeshBasicMaterial({ map: ao, transparent: true, depthWrite: false }));
  aoM.rotation.x = -Math.PI / 2; aoM.position.y = 0.05; scene.add(aoM);

  const ease = (x) => (x <= 0 ? 0 : x >= 1 ? 1 : 1 - Math.pow(1 - x, 3));
  const back1 = (x) => { const c1 = 1.4, c3 = c1 + 1; x = Math.min(1, Math.max(0, x)); return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };

  // camera rig, tuned so the box sits where the amp stands in the photo
  const CAM = { pos: new THREE.Vector3(-14, 74, 104), look: new THREE.Vector3(-2, 33.2, 0) };

  function render(t) {
    // knife runs along the seam, tape halves lose their hold
    slit.scale.x = Math.max(0.001, ease((t - 0.45) / 0.4));
    slit.position.x = -W / 2 * (1 - slit.scale.x);
    slit.visible = t > 0.45 && t < 1.2;
    sideTape.forEach((m) => (m.visible = t < 0.95));
    // flaps open on their hinges
    front.rotation.x = THREE.MathUtils.degToRad(215) * back1((t - 1.12) / 0.55);
    back.rotation.x = -THREE.MathUtils.degToRad(200) * back1((t - 1.42) / 0.55);
    minorL.rotation.z = THREE.MathUtils.degToRad(115) * back1((t - 1.7) / 0.45);
    minorR.rotation.z = -THREE.MathUtils.degToRad(115) * back1((t - 1.78) / 0.45);
    // camera: subtle settle, then dive into the box
    const dive = Math.pow(Math.min(1, Math.max(0, (t - 2.5) / 0.7)), 2.2);
    const p = CAM.pos.clone().lerp(new THREE.Vector3(1, 92, 6), dive);
    const settle = 0;
    p.z += settle * 6; p.y += settle * 2;
    const l = CAM.look.clone().lerp(new THREE.Vector3(1, H - 4, -1), dive);
    cam.position.copy(p); cam.lookAt(l);
    renderer.render(scene, cam);
  }
  return { render };
}
