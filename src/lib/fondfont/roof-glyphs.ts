import * as THREE from 'three';
import manifest from './roof-fonts.json' with { type: 'json' };

type Locale = keyof typeof manifest;
const entry = (locale: string) => manifest[(locale in manifest ? locale : 'en') as Locale];

/** Classic specimen glyphs per locale; their fonts are subset by prepare-fondfont-roof-fonts.py. */
export const ROOF_GLYPHS: Record<string, string[]> = Object.fromEntries(Object.entries(manifest).map(([k, v]) => [k, v.glyphs]));

const COLS = 6, ROWS = 2, CELL = 160;
/** Half-extent of a glyph's ink relative to its box (every glyph's ink is normalised to 80% of the cell). */
export const INK_HALF = .45;
/** Each glyph changes typeface every PERIOD_MIN..PERIOD_MIN+PERIOD_SPREAD seconds, cross-fading over FADE seconds. */
export const PERIOD_MIN = 6, PERIOD_SPREAD = 5, FADE = 1.2;
const INK = '#352a3e', ACCENT = '#d0142c';
const random = (seed: number) => { const x = Math.sin(seed * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };
const smooth = (t: number) => { const p = Math.min(1, Math.max(0, t)); return p * p * (3 - 2 * p); };
const gcd = (a: number, b: number): number => b ? gcd(b, a % b) : a;

export type RoofBounds = { halfWidth: number; halfDepth: number; left: number };
export type GlyphPose = { x: number; z: number; rotation: number; scale: number };

/**
 * Brownian-like drift, as a pure function of time: a sum of sinusoids whose amplitude
 * falls as 1/frequency (the Brownian spectrum), normalised to [-1, 1]. Seeking to any
 * time — posters, reduced motion, resumed playback — gives the same pose.
 */
function drift(seed: number, seconds: number) {
  let value = 0, total = 0;
  for (let k = 0; k < 6; k++) {
    const frequency = .07 * Math.pow(1.85, k) * (.8 + .4 * random(seed + k * 7.3));
    const amplitude = 1 / frequency;
    value += amplitude * Math.sin(frequency * seconds + random(seed + k * 3.1) * Math.PI * 2);
    total += amplitude;
  }
  return value / total;
}

/** Cell layout: six columns by two rows right of the camera island, centres jittered per load. */
export function roofGlyphLayout(count: number, bounds: RoofBounds, seed = 0) {
  const x0 = bounds.left, x1 = bounds.halfWidth, z0 = -bounds.halfDepth, z1 = bounds.halfDepth;
  const cellW = (x1 - x0) / COLS, cellD = (z1 - z0) / ROWS;
  return Array.from({ length: count }, (_, i) => {
    const col = i % COLS, row = Math.floor(i / COLS) % ROWS, r = (k: number) => random(seed * 13 + i * 7 + k);
    // Neighbours can never touch: ink diameter + jitter + both glyphs' drift stay within one cell pitch.
    const size = Math.min(cellW, cellD) * (.66 + r(13) * .1);
    const rangeX = cellW * .13, rangeZ = cellD * .1;
    // Keep the ink (about 45% of the glyph box from its centre, at the largest drift scale) on the screen.
    const ink = size * INK_HALF * 1.05;
    const clamp = (v: number, lo: number, hi: number) => lo > hi ? (lo + hi) / 2 : Math.min(hi, Math.max(lo, v));
    return {
      x: clamp(x0 + cellW * (col + .5) + (r(41) - .5) * cellW * .06, x0 + ink + rangeX, x1 - ink - rangeX),
      z: clamp(z0 + cellD * (row + .5) + (r(59) - .5) * cellD * .06, z0 + ink + rangeZ, z1 - ink - rangeZ),
      size, rangeX, rangeZ,
    };
  });
}

export function sampleRoofGlyph(index: number, seconds: number, cell: ReturnType<typeof roofGlyphLayout>[number], seed = 0): GlyphPose {
  const s = index * 97 + 5 + seed * 1009;
  return {
    x: cell.x + cell.rangeX * drift(s, seconds),
    z: cell.z + cell.rangeZ * drift(s + 1000, seconds),
    rotation: .16 * drift(s + 2000, seconds),
    scale: 1 + .05 * drift(s + 3000, seconds),
  };
}

/**
 * Typeface schedule for one glyph slot: every period the glyph moves to another font of the
 * pool (never the same twice in a row, visiting the whole pool), cross-fading from the last one.
 */
export function sampleRoofFont(slot: number, seconds: number, fontCount: number, seed = 0) {
  const r = (k: number) => random(seed * 31 + slot * 17 + k);
  const period = PERIOD_MIN + PERIOD_SPREAD * r(1), offset = period * r(2);
  const steps = Array.from({ length: fontCount - 1 }, (_, i) => i + 1).filter(b => gcd(b, fontCount) === 1);
  const step = steps[Math.floor(r(3) * steps.length)] ?? 1, start = Math.floor(r(4) * fontCount);
  const epoch = Math.floor((seconds + offset) / period), into = seconds + offset - epoch * period;
  const font = (e: number) => ((start + e * step) % fontCount + fontCount) % fontCount;
  return { current: font(epoch), previous: font(epoch - 1), mix: smooth(into / FADE) };
}

/** The locale's roof typefaces (file names relative to the public roof font folder). */
export function roofFontFiles(locale: string) {
  return entry(locale).fonts.map(font => font.file);
}

/** Drifting specimen glyphs laid flat on the phone-roof screen, each cycling through typefaces. */
export function createRoofGlyphs(anchor: THREE.Object3D, locale: string, families: string[], seed: number) {
  const glyphs = entry(locale).glyphs, fonts = families.length;
  const bounds: RoofBounds = {
    halfWidth: Number(anchor.userData.screen_half_width) - .12,
    halfDepth: Number(anchor.userData.screen_half_depth) - .1,
    left: Number(anchor.userData.camera_island_right) + .16,
  };
  // Atlas: one column per glyph, one row per typeface; each glyph is centred on its ink box.
  // Glyphs are white so the material colour tints them (ink or accent red).
  const canvas = document.createElement('canvas');
  canvas.width = CELL * glyphs.length; canvas.height = CELL * fonts;
  const ctx = canvas.getContext('2d')!;
  ctx.textAlign = 'center'; ctx.textBaseline = 'alphabetic'; ctx.fillStyle = '#ffffff';
  families.forEach((family, f) => glyphs.forEach((glyph, g) => {
    let size = CELL * .74;
    ctx.font = `400 ${size}px "${family}"`;
    let m = ctx.measureText(glyph);
    const extent = Math.max(m.actualBoundingBoxLeft + m.actualBoundingBoxRight, m.actualBoundingBoxAscent + m.actualBoundingBoxDescent);
    // Normalise every typeface to the same ink extent so small-on-body fonts (e.g. Dongle) read equally.
    size *= CELL * .8 / Math.max(extent, 1); ctx.font = `400 ${size}px "${family}"`; m = ctx.measureText(glyph);
    ctx.fillText(glyph, (g + .5) * CELL + (m.actualBoundingBoxLeft - m.actualBoundingBoxRight) / 2, (f + .5) * CELL + (m.actualBoundingBoxAscent - m.actualBoundingBoxDescent) / 2);
  }));
  const texture = new THREE.CanvasTexture(canvas);
  texture.colorSpace = THREE.SRGBColorSpace; texture.anisotropy = 8;
  const layout = roofGlyphLayout(glyphs.length, bounds, seed);
  const order = glyphs.map((_, i) => i).sort((a, b) => random(seed * 5 + a * 3) - random(seed * 5 + b * 3));
  const accents = new Set([Math.floor(random(seed + .5) * glyphs.length), Math.floor(random(seed + 1.5) * glyphs.length)]);
  const group = new THREE.Group(); group.name = 'RoofGlyphs';
  const geometries: THREE.BufferGeometry[] = [], materials: THREE.MeshStandardMaterial[] = [];
  // Two layers per slot: the outgoing and the incoming typeface.
  const slots = layout.map((cell, slot) => {
    const layers = [0, 1].map(() => {
      const geometry = new THREE.PlaneGeometry(cell.size, cell.size);
      const material = new THREE.MeshStandardMaterial({ map: texture, color: accents.has(slot) ? ACCENT : INK, transparent: true, depthWrite: false, roughness: .55, polygonOffset: true, polygonOffsetFactor: -2 });
      const mesh = new THREE.Mesh(geometry, material);
      mesh.rotation.x = -Math.PI / 2; mesh.castShadow = false; mesh.receiveShadow = true;
      geometries.push(geometry); materials.push(material); group.add(mesh);
      return { mesh, material, font: -1 };
    });
    return { cell, glyph: order[slot], layers };
  });
  const showFont = (layer: (typeof slots)[number]['layers'][number], glyph: number, font: number) => {
    if (layer.font === font) return;
    layer.font = font;
    const uv = layer.mesh.geometry.getAttribute('uv') as THREE.BufferAttribute;
    const u0 = glyph / glyphs.length, du = 1 / glyphs.length, v1 = 1 - font / fonts, dv = 1 / fonts;
    // PlaneGeometry vertex order: top-left, top-right, bottom-left, bottom-right.
    for (let k = 0; k < 4; k++) uv.setXY(k, u0 + (k % 2) * du, k < 2 ? v1 : v1 - dv);
    uv.needsUpdate = true;
  };
  anchor.add(group);
  return {
    group, texture, materials, geometries,
    update(seconds: number) {
      slots.forEach(({ cell, glyph, layers }, slot) => {
        const pose = sampleRoofGlyph(slot, seconds, cell, seed), type = sampleRoofFont(slot, seconds, fonts, seed);
        showFont(layers[0], glyph, type.previous); showFont(layers[1], glyph, type.current);
        layers[0].material.opacity = 1 - type.mix; layers[0].mesh.visible = type.mix < 1;
        layers[1].material.opacity = type.mix;
        for (const { mesh } of layers) { mesh.position.set(pose.x, 0, pose.z); mesh.rotation.z = pose.rotation; mesh.scale.setScalar(pose.scale); }
      });
    },
  };
}
