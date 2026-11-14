// Photoreal-ish XLR + 1/4" jack plugs rendered with Three.js and composited onto the
// top-panel photo. Orthographic camera tilted to the panel's angle in the photo,
// so a plug standing on the panel plane lines up with the real sockets.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const PX_PER_CM = 36; // image px per cm at the sockets (XLR flange ~2.6 cm ≈ 93 px)

export function createPlugs(canvas, opt) {
  const { width, height, pixelRatio, xlr, jack, tiltDeg, rollDeg } = opt;
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width * pixelRatio, height * pixelRatio, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.05;
  renderer.localClippingEnabled = true;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFShadowMap;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.03).texture;
  scene.environmentIntensity = 0.85;

  // --- camera: ortho, origin = XLR socket centre on the panel plane (y = 0)
  const s = 1 / PX_PER_CM;
  const cam = new THREE.OrthographicCamera(-xlr[0] * s, (width - xlr[0]) * s, xlr[1] * s, -(height - xlr[1]) * s, 0.1, 200);
  const tilt = THREE.MathUtils.degToRad(tiltDeg);
  cam.position.set(0, Math.cos(tilt) * 60, Math.sin(tilt) * 60);
  cam.up.set(0, 0, -1);
  cam.lookAt(0, 0, 0);
  cam.rotateZ(THREE.MathUtils.degToRad(rollDeg));
  cam.updateMatrixWorld();

  // screen (image px inside the canvas) -> point on the panel plane
  const ray = new THREE.Raycaster();
  const plane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
  function onPanel(px, py) {
    const ndc = new THREE.Vector2((px / width) * 2 - 1, -(py / height) * 2 + 1);
    ray.setFromCamera(ndc, cam);
    const p = new THREE.Vector3();
    ray.ray.intersectPlane(plane, p);
    return p;
  }

  // --- lights: soft key from the upper-left of the photo, cool fill
  const key = new THREE.DirectionalLight(0xfff2e0, 2.4);
  key.position.set(-14, 26, -10);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  key.shadow.camera.left = -20; key.shadow.camera.right = 20; key.shadow.camera.top = 20; key.shadow.camera.bottom = -20;
  key.shadow.radius = 6;
  key.shadow.bias = -0.0005;
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xd8e4ff, 0.6);
  fill.position.set(12, 10, 14);
  scene.add(fill);

  // shadow catcher on the panel
  const catcher = new THREE.Mesh(new THREE.PlaneGeometry(80, 80), new THREE.ShadowMaterial({ opacity: 0.38 }));
  catcher.rotation.x = -Math.PI / 2;
  catcher.position.y = 0.002;
  catcher.receiveShadow = true;
  scene.add(catcher);

  const clip = [new THREE.Plane(new THREE.Vector3(0, 1, 0), 0)]; // hide what is inside the socket

  // --- materials
  const nickel = new THREE.MeshPhysicalMaterial({ color: 0xc9ccd1, metalness: 1, roughness: 0.28, clearcoat: 0.3, clippingPlanes: clip });
  const knurlTex = (() => {
    const c = document.createElement("canvas"); c.width = 8; c.height = 256;
    const g = c.getContext("2d"); g.fillStyle = "#888"; g.fillRect(0, 0, 8, 256);
    for (let y = 0; y < 256; y += 8) { g.fillStyle = "#fff"; g.fillRect(0, y, 8, 3); }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(1, 6); return t;
  })();
  const nickelKnurl = new THREE.MeshPhysicalMaterial({ color: 0xbfc3c8, metalness: 1, roughness: 0.38, bumpMap: knurlTex, bumpScale: 0.6, clippingPlanes: clip });
  const rubber = new THREE.MeshPhysicalMaterial({ color: 0x141416, metalness: 0, roughness: 0.62, clearcoat: 0.15, clearcoatRoughness: 0.6, clippingPlanes: clip });
  const cableMat = new THREE.MeshPhysicalMaterial({ color: 0x0d0d0e, metalness: 0, roughness: 0.45, clearcoat: 0.35, clearcoatRoughness: 0.4 });
  const chrome = new THREE.MeshPhysicalMaterial({ color: 0xe6e8eb, metalness: 1, roughness: 0.12, clippingPlanes: clip });

  const lathe = (pts, mat, seg = 64) => {
    const m = new THREE.Mesh(new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y)), seg), mat);
    m.castShadow = true; return m;
  };

  // XLR male: nickel barrel (Ø ~1.9 cm) with a latch slot, black boot, cable
  function buildXlr() {
    const g = new THREE.Group();
    g.add(lathe([[0, -1.6], [0.92, -1.6], [0.95, -1.5], [0.95, 1.2], [0.97, 1.25], [0.97, 1.7], [0.9, 1.75], [0, 1.75]], nickel));
    const grip = lathe([[0.985, 0.35], [0.985, 1.15]], nickelKnurl, 96); g.add(grip);
    const slot = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.7, 0.2), new THREE.MeshStandardMaterial({ color: 0x1a1a1a, roughness: 0.8, clippingPlanes: clip }));
    slot.position.set(0, 0.0, 0.9); g.add(slot);
    g.add(lathe([[0.86, 1.72], [0.86, 2.1], [0.8, 2.25], [0.78, 2.6], [0.72, 2.75], [0.70, 3.1], [0.6, 3.35], [0.52, 3.9], [0.42, 4.4], [0.36, 4.7], [0, 4.7]], rubber));
    for (let i = 0; i < 4; i++) { const r = new THREE.Mesh(new THREE.TorusGeometry(0.76 - i * 0.06, 0.035, 8, 48), rubber); r.rotation.x = Math.PI / 2; r.position.y = 2.35 + i * 0.32; g.add(r); }
    return g;
  }
  // 1/4" TS plug: chrome barrel with knurl, black boot
  function buildJack() {
    const g = new THREE.Group();
    g.add(lathe([[0, -3.0], [0.31, -3.0], [0.31, 0], [0.62, 0], [0.66, 0.05], [0.66, 2.6], [0.6, 2.7], [0, 2.7]], chrome));
    g.add(lathe([[0.675, 0.6], [0.675, 1.9]], nickelKnurl, 96));
    g.add(lathe([[0.56, 2.65], [0.56, 3.0], [0.5, 3.3], [0.42, 3.9], [0.34, 4.5], [0.3, 4.8], [0, 4.8]], rubber));
    return g;
  }

  function cableFrom(top, anchor, bend) {
    const p0 = top.clone();
    const p1 = top.clone().add(new THREE.Vector3(0, 2.2, 0));
    const p2 = top.clone().add(bend);
    const curve = new THREE.CatmullRomCurve3([p0, p1, p2, anchor], false, "centripetal");
    return curve;
  }

  const X = buildXlr(); scene.add(X);
  const J = buildJack(); scene.add(J);
  const xlrBase = onPanel(xlr[0], xlr[1]);
  const jackBase = onPanel(jack[0], jack[1]);
  const xlrAnchor = onPanel(-200, -150).add(new THREE.Vector3(0, 14, 0));
  const jackAnchor = onPanel(160, -250).add(new THREE.Vector3(0, 12, 0));
  let xlrCable = null, jackCable = null;
  function setCable(old, curve, r) {
    if (old) { scene.remove(old); old.geometry.dispose(); }
    const m = new THREE.Mesh(new THREE.TubeGeometry(curve, 120, r, 16, false), cableMat);
    m.castShadow = true; scene.add(m); return m;
  }

  // state: { xlr: 0..1 inserted, jack: 0..1, xlrOn, jackOn }
  function render(st) {
    X.visible = st.xlrOn; J.visible = st.jackOn;
    const lift = (k, far) => (1 - k) * far;
    X.position.copy(xlrBase).add(new THREE.Vector3(0, lift(st.xlr, 6), 0));
    X.rotation.z = (1 - st.xlr) * 0.08;
    J.position.copy(jackBase).add(new THREE.Vector3(0, lift(st.jack, 6), 0));
    J.rotation.x = (1 - st.jack) * -0.06;
    X.updateMatrixWorld(); J.updateMatrixWorld();
    if (st.xlrOn) xlrCable = setCable(xlrCable, cableFrom(X.localToWorld(new THREE.Vector3(0, 4.6, 0)), xlrAnchor, new THREE.Vector3(-2.5, 6, -3)), 0.33);
    else if (xlrCable) xlrCable.visible = false;
    if (st.jackOn) jackCable = setCable(jackCable, cableFrom(J.localToWorld(new THREE.Vector3(0, 4.7, 0)), jackAnchor, new THREE.Vector3(1.5, 5, -3)), 0.29);
    else if (jackCable) jackCable.visible = false;
    renderer.render(scene, cam);
  }
  return { render };
}
