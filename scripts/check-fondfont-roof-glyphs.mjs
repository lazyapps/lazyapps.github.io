import assert from 'node:assert/strict';
import { readFileSync, existsSync } from 'node:fs';
import { ROOF_GLYPHS, INK_HALF, FADE, roofGlyphLayout, sampleRoofGlyph, sampleRoofFont, roofFontFiles } from '../src/lib/fondfont/roof-glyphs.ts';

const manifest = JSON.parse(readFileSync(new URL('../src/lib/fondfont/roof-fonts.json', import.meta.url)));
const bytes = readFileSync(new URL('../public/v/fondfont/blender-v3/campus-v3.glb', import.meta.url));
const gltf = JSON.parse(bytes.subarray(20, 20 + bytes.readUInt32LE(12)));
const anchor = gltf.nodes.find(n => n.name === 'PhoneScreenGlyph').extras;
const bounds = { halfWidth: anchor.screen_half_width - .12, halfDepth: anchor.screen_half_depth - .1, left: anchor.camera_island_right + .16 };

// Each locale: twelve glyphs, a varied pool of subset typefaces, files and licences published.
for (const [locale, entry] of Object.entries(manifest)) {
  assert.equal(ROOF_GLYPHS[locale].length, 12, `${locale} has twelve specimen glyphs`);
  assert.ok(entry.fonts.length >= 5, `${locale} rotates through at least five typefaces`);
  assert.equal(new Set(entry.fonts.map(f => f.name)).size, entry.fonts.length, `${locale} typefaces are distinct`);
  for (const file of roofFontFiles(locale)) assert.ok(existsSync(new URL(`../public/v/fondfont/blender-v3/roof/${file}`, import.meta.url)), `${file} published`);
  for (const font of entry.fonts) assert.ok(existsSync(new URL(`../public${font.license}`, import.meta.url)), `${font.name} licence published`);
}

let maxStep = 0, travel = 0, changes = 0, minGap = Infinity;
for (const seed of [47, 1234]) {
  const layout = roofGlyphLayout(12, bounds, seed);
  for (const fonts of [5, 6, 7]) for (let slot = 0; slot < 12; slot++) {
    const seen = new Set();
    let last = -1;
    for (let t = 0; t < 240; t += .25) {
      const f = sampleRoofFont(slot, t, fonts, seed);
      assert.notEqual(f.current, f.previous, 'a glyph never switches to the same typeface');
      assert.ok(f.mix >= 0 && f.mix <= 1);
      if (f.current !== last) { changes++; last = f.current; }
      seen.add(f.current);
    }
    assert.equal(seen.size, fonts, 'each glyph visits the whole typeface pool');
  }
  for (let t = 0; t < 600; t += .1) layout.forEach((cell, i) => {
    const p = sampleRoofGlyph(i, t, cell, seed), q = sampleRoofGlyph(i, t + .1, cell, seed);
    const half = cell.size * p.scale * INK_HALF;
    assert.ok(p.x - half > bounds.left && p.x + half < bounds.halfWidth, `glyph ink stays right of the camera island and inside the screen (${i} at ${t.toFixed(1)}s)`);
    assert.ok(Math.abs(p.z) + half < bounds.halfDepth, 'glyph ink stays inside the screen depth');
    assert.deepEqual(sampleRoofGlyph(i, t, cell, seed), p, 'pose is a pure function of time');
    const step = Math.hypot(q.x - p.x, q.z - p.z); maxStep = Math.max(maxStep, step); travel += step;
  });
  // No two glyphs' ink ever touch (axis-aligned ink boxes, enlarged for the small rotation).
  for (let t = 0; t < 600; t += .5) {
    const poses = layout.map((cell, i) => ({ ...sampleRoofGlyph(i, t, cell, seed), half: cell.size * INK_HALF * 1.08 }));
    for (let a = 0; a < poses.length; a++) for (let b = a + 1; b < poses.length; b++) {
      const A = poses[a], B = poses[b];
      const gap = Math.max(Math.abs(A.x - B.x) - A.half * A.scale - B.half * B.scale, Math.abs(A.z - B.z) - A.half * A.scale - B.half * B.scale);
      minGap = Math.min(minGap, gap);
      assert.ok(gap > 0, `glyphs ${a} and ${b} never overlap (seed ${seed}, ${t}s)`);
    }
  }
}
assert.notDeepEqual(roofGlyphLayout(12, bounds, 47), roofGlyphLayout(12, bounds, 1234), 'each visit gets a fresh arrangement');
assert.ok(maxStep < .05, `drift is calm (max ${maxStep.toFixed(4)} m per 0.1 s)`);
assert.ok(travel / 24 > 4, 'every glyph keeps wandering over ten minutes');
const pools = Object.entries(manifest).map(([l, e]) => `${l} ${e.fonts.length}`).join(', ');
console.log(`Roof glyphs: twelve glyphs per locale, typeface pools (${pools}); ${changes} typeface changes with ${FADE}s cross-fades, never repeating; deterministic Brownian drift within the screen (max ${maxStep.toFixed(4)} m/0.1 s); neighbours never overlap (min gap ${minGap.toFixed(3)} m).`);
