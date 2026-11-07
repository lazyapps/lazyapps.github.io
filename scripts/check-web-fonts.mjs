import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import { resolve, dirname } from 'node:path';
import { attr, readPages, dist, text } from './lib/seo.mjs';

const manifest = JSON.parse(await readFile('scripts/assets/fonts/web-fonts.json', 'utf8'));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const points = range => new Set(range.split(',').flatMap(part => {
  const [start, end = start] = part.trim().slice(2).split('-').map(value => parseInt(value, 16));
  return Array.from({ length: end - start + 1 }, (_, index) => start + index);
}));
const fonts = new Map();
const allowedPreloads = new Set();
for (const [source, checksum] of Object.entries(manifest.sources)) {
  assert.equal(hash(await readFile(source)), checksum, `${source}: rerun the manual font optimizer`);
}
for (const face of manifest.fonts) {
  assert.equal(hash(await readFile(face.source)), face.sourceSHA256, `${face.source}: source font changed`);
  allowedPreloads.add(face.sourceSHA256);
  const union = new Set();
  for (const output of face.outputs) {
    assert.equal(hash(await readFile(output.file)), output.sha256, `${output.file}: generated font changed`);
    const coverage = points(face.retain ? face.effectiveUnicodeRange : output.unicodeRange);
    for (const point of coverage) {
      assert(!union.has(point), `${face.id}: overlapping core/extended coverage`);
      union.add(point);
    }
    fonts.set(resolve(output.file), { face, output, coverage });
    if (output.kind === 'core') allowedPreloads.add(output.sha256);
    if (!face.retain) {
      assert(output.verification.globalHintTablesUnchanged, `${face.id}: hinting must stay intact`);
      assert.deepEqual(output.hintTables, face.original.hintTables);
      assert.deepEqual(output.metrics, face.original.metrics);
      assert.equal(output.verification.outlines, output.characters, 'Every supported glyph must retain its outline and advance');
      assert(output.familyNames.every(name => name.startsWith('Lazyapps')), 'Keep derivative family/PostScript names');
    }
  }
  assert.deepEqual([...union].sort((a, b) => a - b), [...points(face.effectiveUnicodeRange)].sort((a, b) => a - b), `${face.id}: supported characters lost`);
  if (face.merged) {
    assert.equal(hash(await readFile(face.merged.file)), face.merged.sha256);
    assert.equal(face.merged.unicodeRange, face.effectiveUnicodeRange);
    assert.deepEqual(face.merged.hintTables, face.original.hintTables);
    assert.deepEqual(face.merged.metrics, face.original.metrics);
    assert(face.merged.verification.globalHintTablesUnchanged);
    assert.equal(face.merged.verification.outlines, face.merged.characters);
    assert(face.merged.familyNames.every(name => name.startsWith('Lazyapps')));
    fonts.set(resolve(face.merged.file), { face, output: face.merged, coverage: points(face.merged.unicodeRange) });
    allowedPreloads.add(face.merged.sha256);
  }
}
const panel = JSON.parse(await readFile('scripts/assets/calmon/key-panel-text-source.json', 'utf8'));
for (const [file, checksum] of Object.entries({...panel.websiteInputs, ...panel.outputs})) {
  assert.equal(hash(await readFile(file)), checksum, `${file}: rerun prepare-calmon-key-panel.py after changing panel content`);
}
for (const output of panel.fonts) {
  const face = {id: 'calmon-panel', family: 'calmon Panel', style: 'normal', weight: '400', display: 'swap'};
  const coverage = points(output.unicodeRange);
  assert.equal(hash(await readFile(output.file)), output.sha256);
  assert.deepEqual(output.metrics, panel.source.metrics);
  assert.deepEqual(output.hintTables, panel.source.hintTables);
  assert(output.verification.globalHintTablesUnchanged);
  assert.equal(output.verification.outlines, output.characters);
  assert(output.familyNames.every(name => /^(calmon Panel Web|CalmonPanelWeb)/.test(name)));
  fonts.set(resolve(output.file), {face, output, coverage});
  if (output.kind === 'core') allowedPreloads.add(output.sha256);
}

for (const sheet of ['src/assets/s/calmon-panel-fonts.css', 'src/assets/s/site.css', 'src/assets/s/yilo-hand.css', 'src/assets/s/yilo-hand-cjk.css', 'src/assets/s/fondfont-fonts.css', 'src/components/calmon-desktop/desktop.css']) {
  const families = new Map();
  const css = await readFile(sheet, 'utf8');
  for (const match of css.matchAll(/@font-face\s*\{([^}]+)\}/g)) {
    const fields = Object.fromEntries([...match[1].matchAll(/([\w-]+)\s*:\s*([^;{}]+)/g)].map(item => [item[1], item[2].trim()]));
    const url = fields.src.match(/url\(["']?([^"')]+)/)?.[1];
    const entry = fonts.get(resolve(dirname(sheet), url.split('?')[0]));
    if (!entry) continue; // Existing unmodified Calmon Han face.
    assert.equal(fields['font-family'].replaceAll('"', '').replaceAll("'", ''), entry.face.family);
    assert.equal(fields['font-display'], entry.face.display);
    assert.equal(fields['font-style'], entry.face.style);
    assert.equal(fields['font-weight'], entry.face.weight);
    const coverage = points(fields['unicode-range']);
    assert.deepEqual([...coverage], [...entry.coverage], `${sheet}: ranges must match actual effective cmaps`);
    const previous = families.get(entry.face.family) ?? new Set();
    for (const point of coverage) assert(!previous.has(point), `${sheet}: a later face intercepts U+${point.toString(16)}`);
    families.set(entry.face.family, new Set([...previous, ...coverage]));
    assert(url.endsWith('?no-inline'), 'Do not embed font cores into CSS');
  }
}

let checked = 0;
const pages = await readPages();
const siteCore = manifest.fonts.find(face => face.id === 'sofia-latin').sourceSHA256;
for (const page of pages) {
  const preloads = page.nodes.filter(node => node.tagName === 'link' && attr(node, 'rel') === 'preload' && attr(node, 'as') === 'font');
  const hrefs = preloads.map(node => attr(node, 'href'));
  assert.equal(new Set(hrefs).size, hrefs.length, `${page.url}: duplicate font preloads`);
  const hashes = [];
  for (const preload of preloads) {
    const href = attr(preload, 'href');
    assert(href?.startsWith('/_astro/') && !href.startsWith('data:'), 'Font preloads must be external, fingerprinted assets');
    assert.equal(attr(preload, 'crossorigin'), 'anonymous', 'Match font CORS mode to avoid duplicate requests');
    const checksum = hash(await readFile(dist + href.slice(1)));
    assert(allowedPreloads.has(checksum), `${page.url}: do not eagerly preload an extended subset`);
    hashes.push(checksum);
  }
  if (page.nodes.some(node => node.tagName === 'link' && /\/_astro\/site\.[^/]+\.css$/.test(attr(node, 'href') ?? ''))) {
    assert(hashes.includes(siteCore), `${page.url}: shared logo core preload missing`);
    checked++;
  }
  if (/\/yilo\/(?:(?:de|es|fr|pt-br|ru|ar|hi|ko)\/)?$/.test(page.url)) {
    const han = manifest.fonts.find(face => face.id === 'yilo-han');
    const covered = fonts.get(resolve(han.outputs.find(output => output.kind === 'core').file)).coverage;
    const supported = points(han.effectiveUnicodeRange);
    for (const character of text(page.nodes.find(node => node.tagName === 'body'))) {
      const point = character.codePointAt(0);
      assert(!supported.has(point) || covered.has(point), `${page.url}: rerun the optimizer for new common Han text`);
    }
  }
}
assert(checked > 0);
console.log(`Web fonts verified: ${manifest.fonts.length} source faces, exact disjoint ranges, intact glyph metrics/hinting, and external core preloads on ${checked} pages.`);
