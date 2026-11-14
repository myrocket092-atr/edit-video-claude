// Generic handheld dynamic vocal mic (no brand), studio-lit, transparent background.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

export function createMic(canvas, { width = 1080, height = 1920 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(width, height, false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.setClearColor(0x000000, 0);

  const scene = new THREE.Scene();
  const pmrem = new THREE.PMREMGenerator(renderer);
  scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;

  const cam = new THREE.PerspectiveCamera(26, width / height, 1, 400);

  // lights: warm key from the left, hard cool rim from behind right, soft top
  const key = new THREE.SpotLight(0xffd7a8, 900, 0, 0.5, 0.8, 2); key.position.set(-30, 30, 30); scene.add(key);
  const rim = new THREE.SpotLight(0xdfe8ff, 1600, 0, 0.45, 0.6, 2); rim.position.set(28, 22, -30); scene.add(rim);
  const top = new THREE.DirectionalLight(0xffffff, 0.35); top.position.set(0, 40, 10); scene.add(top);
  key.target.position.set(0, 12, 0); rim.target.position.set(0, 14, 0); scene.add(key.target, rim.target);

  const body = new THREE.MeshPhysicalMaterial({ color: 0x2b2c30, metalness: 0.75, roughness: 0.42, clearcoat: 0.25, clearcoatRoughness: 0.5 });
  const satin = new THREE.MeshPhysicalMaterial({ color: 0xc5c8cc, metalness: 1, roughness: 0.25 });
  const rubber = new THREE.MeshPhysicalMaterial({ color: 0x111113, roughness: 0.55, clearcoat: 0.3, clearcoatRoughness: 0.4 });

  // woven wire mesh: diamond grid alpha map
  const meshTex = (() => {
    const c = document.createElement("canvas"); c.width = c.height = 512;
    const g = c.getContext("2d"); g.fillStyle = "#000"; g.fillRect(0, 0, 512, 512);
    g.strokeStyle = "#fff"; g.lineWidth = 3.2;
    for (let i = -512; i <= 1024; i += 16) {
      g.beginPath(); g.moveTo(i, 0); g.lineTo(i + 512, 512); g.stroke();
      g.beginPath(); g.moveTo(i, 512); g.lineTo(i + 512, 0); g.stroke();
    }
    const t = new THREE.CanvasTexture(c); t.wrapS = t.wrapT = THREE.RepeatWrapping; t.repeat.set(7, 4); t.anisotropy = 8; return t;
  })();
  const grilleMat = new THREE.MeshPhysicalMaterial({ color: 0xd9dbde, metalness: 1, roughness: 0.3, alphaMap: meshTex, transparent: false, alphaTest: 0.45, side: THREE.DoubleSide });
  const foam = new THREE.MeshStandardMaterial({ color: 0x1a1a1c, roughness: 1 });

  const mic = new THREE.Group();
  const L = (pts, m, seg = 96) => new THREE.Mesh(new THREE.LatheGeometry(pts.map(([r, y]) => new THREE.Vector2(r, y)), seg), m);
  // handle, tapered
  mic.add(L([[0, 0], [1.05, 0], [1.1, 0.2], [1.12, 2], [1.3, 6], [1.48, 10], [1.62, 12.3], [1.66, 12.6], [0, 12.6]], body));
  // XLR end ring
  mic.add(L([[1.0, -0.4], [1.08, -0.35], [1.1, 0.2], [0.98, 0.25]], satin));
  // chrome collar + grille base
  mic.add(L([[1.62, 12.55], [1.8, 12.7], [1.92, 13.0], [1.95, 13.6], [1.9, 13.75], [0, 13.75]], satin));
  // ball grille + inner foam
  const sph = new THREE.SphereGeometry(2.55, 96, 64, 0, Math.PI * 2, 0, Math.PI * 0.78);
  const grille = new THREE.Mesh(sph, grilleMat); grille.position.y = 15.4; mic.add(grille);
  const foamM = new THREE.Mesh(new THREE.SphereGeometry(2.35, 64, 48), foam); foamM.position.y = 15.3; mic.add(foamM);
  const band = new THREE.Mesh(new THREE.TorusGeometry(2.56, 0.07, 12, 128), satin); band.rotation.x = Math.PI / 2; band.position.y = 15.4; mic.add(band);
  const base = new THREE.Mesh(new THREE.CylinderGeometry(2.03, 1.93, 0.9, 96, 1, true), grilleMat); base.position.y = 14.1; mic.add(base);
  // female XLR + cable out of the bottom
  mic.add(L([[0, -0.4], [0.95, -0.4], [0.95, -2.6], [0.85, -2.8], [0, -2.8]], satin));
  mic.add(L([[0.85, -2.7], [0.78, -3.4], [0.6, -4.6], [0.45, -5.6], [0, -5.6]], rubber));
  const curve = new THREE.CatmullRomCurve3([new THREE.Vector3(0, -5.4, 0), new THREE.Vector3(0, -9, 0.3), new THREE.Vector3(1.5, -16, 2), new THREE.Vector3(6, -26, 1), new THREE.Vector3(14, -40, -4)]);
  mic.add(new THREE.Mesh(new THREE.TubeGeometry(curve, 160, 0.34, 16, false), rubber));
  scene.add(mic);

  // t: seconds into the shot (0..dur); level: 0..1 voice envelope
  function render(t, level = 0) {
    const k = t / 3.0;
    mic.rotation.set(0.12, -0.6 + k * 0.4, -0.3 + k * 0.04);
    mic.position.set(0.5, -5 + level * 0.03, 0);
    cam.position.set(-1.5 + k * 1.2, 9 + k * 0.5, 54 - k * 6);
    cam.lookAt(4.0, 7.6 + k * 0.6, 0);
    renderer.render(scene, cam);
  }
  return { render };
}
