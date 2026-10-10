import assert from 'node:assert/strict';
import { readFile, access } from 'node:fs/promises';
import { createHash } from 'node:crypto';
import { inflateRawSync } from 'node:zlib';
import { join, posix } from 'node:path';
import { pressKits as kits, supported } from '../src/content/presskit-catalog.mjs';
import { presentationLanguages, pressPresentations } from '../src/content/presskit-presentation.mjs';
import './check-presskit-language.mjs';
import { attr, text, readPages, dist, site } from './lib/seo.mjs';

const pages = await readPages();
const byPath = new Map(pages.map(page => [new URL(page.url).pathname, page]));
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const slugs = new Set(kits.map(kit => kit.slug));
const nativeIcons = JSON.parse(await readFile(new URL('./assets/native-icons/sources.json', import.meta.url), 'utf8'));
const screenshotSources = JSON.parse(await readFile(new URL('./assets/presskit/screenshot-sources.json', import.meta.url), 'utf8'));
assert.equal(slugs.size, kits.length, 'Duplicate presskit product');
assert.deepEqual(Object.keys(screenshotSources).sort(), [...slugs].sort(), 'Screenshot provenance must cover every app');
const anchors = page => page.nodes.filter(node => node.tagName === 'a');
const linksTo = (page, path) => anchors(page).some(node => attr(node, 'href')?.split('#')[0] === path);

// Discover apps from actual built metadata, independent of the presskit registry.
const products = new Map();
for (const page of pages) {
  const data = page.nodes.filter(node => node.tagName === 'script' && attr(node, 'type') === 'application/ld+json').flatMap(node => {
    const value = JSON.parse(text(node));
    return value['@graph'] ?? [value];
  });
  if (!data.some(app => ['SoftwareApplication', 'WebApplication'].includes(app['@type']))) continue;
  const slug = new URL(page.url).pathname.split('/')[1];
  assert(slugs.has(slug), `Product ${slug} is missing a presskit registry entry`);
  assert(linksTo(page, `/${slug}/presskit/`), `${page.url}: missing product presskit link`);
  assert(anchors(page).some(node => attr(node, 'href') === `/${slug}/presskit/#${page.language}`), `${page.url}: presskit entry must preserve the landing page language`);
  products.set(slug, (products.get(slug) ?? 0) + 1);
}
assert(byPath.has('/presskit/'), 'Missing presskit index');
assert(linksTo(byPath.get('/'), '/presskit/'), 'Home footer must link to presskit index');
assert(anchors(byPath.get('/')).some(node => attr(node, 'href') === '/presskit/#en'), 'Main home must pass its English language explicitly');

for (const path of ['/presskit/', ...kits.map(kit => `/${kit.slug}/presskit/`)]) {
  const page = byPath.get(path);
  const pickers = page.nodes.filter(node => node.tagName === 'select' && attr(node, 'data-locale-mode') === 'hash');
  assert.equal(pickers.length, 1, `${path}: expected one shared language picker`);
  const options = pickers[0].childNodes.filter(node => node.tagName === 'option');
  assert.deepEqual(options.map(option => attr(option, 'value')), presentationLanguages.map(tag => `#${tag}`));
  assert(!page.nodes.some(node => attr(node, 'id')?.startsWith('language-') || presentationLanguages.includes(attr(node, 'id'))), `${path}: language state must not cause native fragment scrolling`);
  const data = JSON.parse(text(page.nodes.find(node => attr(node, 'id') === 'press-page-data')));
  assert.deepEqual(data.products, path === '/presskit/' ? pressPresentations : pressPresentations.filter(item => path === `/${item.slug}/presskit/`));
  for (const product of data.products) for (const copy of Object.values(product.locales)) {
    assert(byPath.has(copy.website), `${path}: localized product destination must exist: ${copy.website}`);
  }
}

function imageSize(bytes) {
  if (bytes.subarray(0, 8).equals(Buffer.from('89504e470d0a1a0a', 'hex'))) return [bytes.readUInt32BE(16), bytes.readUInt32BE(20)];
  assert.equal(bytes.readUInt16BE(0), 0xffd8, 'Unsupported press image format');
  let offset = 2;
  while (offset < bytes.length) {
    assert.equal(bytes[offset++], 255, 'Invalid JPEG marker');
    while (bytes[offset] === 255) offset++;
    const marker = bytes[offset++];
    if ([0xc0, 0xc1, 0xc2].includes(marker)) return [bytes.readUInt16BE(offset + 5), bytes.readUInt16BE(offset + 3)];
    offset += bytes.readUInt16BE(offset);
  }
  throw Error('JPEG dimensions missing');
}

function zipContents(bytes) {
  const files = new Map();
  let offset = 0;
  while (bytes.readUInt32LE(offset) === 0x04034b50) {
    assert(!(bytes.readUInt16LE(offset + 6) & 8), 'Unexpected ZIP data descriptor');
    const method = bytes.readUInt16LE(offset + 8);
    const size = bytes.readUInt32LE(offset + 18);
    const nameSize = bytes.readUInt16LE(offset + 26);
    const extraSize = bytes.readUInt16LE(offset + 28);
    const name = bytes.subarray(offset + 30, offset + 30 + nameSize).toString();
    assert(!files.has(name), `Duplicate ZIP member: ${name}`);
    const start = offset + 30 + nameSize + extraSize;
    const compressed = bytes.subarray(start, start + size);
    assert([0, 8].includes(method), 'Unsupported ZIP compression');
    files.set(name, method === 8 ? inflateRawSync(compressed) : compressed);
    offset = start + size;
  }
  assert.equal(bytes.readUInt32LE(offset), 0x02014b50, 'ZIP central directory missing');
  return files;
}

for (const kit of kits) {
  const check = (condition, message) => assert(condition, `${kit.slug}: ${message}`);
  const review = screenshotSources[kit.slug];
  check(/^\d{4}-\d{2}-\d{2}$/.test(review.checkedOn) && /^[a-f0-9]{40}$/.test(review.appSourceCommit), 'Screenshot review needs a date and app source revision');
  const screenshots = kit.files.filter(asset => asset.kind === 'screenshot');
  assert.deepEqual(review.captures.map(capture => capture.source).sort(), screenshots.map(asset => asset.source).sort(), `${kit.slug}: screenshot sources changed; review the current app and update provenance`);
  for (const capture of review.captures) {
    check(hash(await readFile(capture.source)) === capture.sha256, `Screenshot changed without a source review: ${capture.source}`);
    check(capture.originalSource && capture.operation && ['native', 'title-screen', 'edited'].includes(capture.type), 'Screenshot capture context missing');
    const asset = screenshots.find(asset => asset.source === capture.source);
    check(asset.contentLanguage === capture.contentLanguage, 'Screenshot language differs from reviewed source');
    if (capture.type === 'edited') check(review.captures.some(original => original.source === capture.derivedFrom && original.type === 'native'), 'Edited screenshot must include the original native capture');
  }
  check(products.has(kit.slug), 'Registry entry has no product landing page');
  const path = `/${kit.slug}/presskit/`;
  const page = byPath.get(path);
  check(page && page.canonical === site + path, 'Missing canonical presskit page');
  check(page.alternates.length === 0, 'Presskit must not enter product hreflang groups');
  check(linksTo(byPath.get('/presskit/'), path), 'Missing index entry');
  check(linksTo(page, kit.locales.find(locale => locale.tag === 'en').website), 'Missing return link to product');
  const base = `/presskit/${kit.slug}/`;
  const directory = join(dist, base);
  const manifestBytes = await readFile(join(directory, 'manifest.json'));
  const manifest = JSON.parse(manifestBytes);
  assert.deepEqual(manifest.languages, supported[kit.slug].tags, `${kit.slug}: missing app languages`);
  assert.deepEqual(kit.locales.map(locale => locale.tag), supported[kit.slug].tags, `${kit.slug}: catalog language drift`);
  check(manifest.files.length === kit.files.length, 'Manifest length differs from catalog');
  for (const obsolete of ['README.en.md', 'README.zh-Hans.md', 'README.txt']) await assert.rejects(access(join(directory, obsolete)), `${kit.slug}: obsolete README`);
  const archived = zipContents(await readFile(join(directory, `${kit.slug}-presskit.zip`)));
  const expected = ['manifest.json', ...kit.locales.map(locale => `${locale.tag}/README.md`), ...kit.files.map(asset => asset.path)];
  assert.deepEqual([...archived.keys()].sort(), expected.sort(), `${kit.slug}: ZIP must have shared files and language folders directly at root`);
  check(archived.get('manifest.json').equals(manifestBytes), 'Archived manifest differs');
  check(linksTo(page, `${base}${kit.slug}-presskit.zip`), 'Missing package download');
  const languages = new Set(manifest.languages);
  for (const name of archived.keys()) check(!name.includes('/') || languages.has(name.split('/')[0]), 'Unexpected top-level archive folder');
  const identityPaths = new Map();
  const originalIcon = nativeIcons[kit.slug];
  check(originalIcon, 'Missing native App icon provenance');
  for (const [name, checksum] of Object.entries(originalIcon.sourceHashes)) {
    const sourcePath = originalIcon.source.endsWith('.png') ? originalIcon.source : posix.join(originalIcon.source, name);
    check(hash(await readFile(sourcePath)) === checksum, `Native icon source changed: ${name}; export and update provenance`);
  }
  const iconAssets = kit.files.filter(asset => asset.kind === 'icon');
  check(iconAssets.length === 1, 'Expected one original App icon');
  check(iconAssets[0].source === originalIcon.output && iconAssets[0].path === 'icon.png', 'Icon must use the recorded native PNG at archive root');
  check(hash(await readFile(originalIcon.output)) === originalIcon.outputSha256, 'Native icon export changed without provenance update');
  assert.deepEqual(imageSize(await readFile(originalIcon.output)), [1024, 1024], `${kit.slug}: native icon must be 1024 × 1024`);
  for (const asset of kit.files) {
    const bytes = await readFile(join(directory, asset.path));
    const source = await readFile(new URL('../' + asset.source, import.meta.url));
    const metadata = manifest.files.find(item => item.path === asset.path);
    check(bytes.equals(source), `Stale asset ${asset.path}; run python3 scripts/prepare-presskits.py`);
    check(metadata.sha256 === hash(bytes) && metadata.bytes === bytes.length, 'Incorrect asset checksum/size');
    assert.deepEqual([metadata.width, metadata.height], imageSize(bytes), `${kit.slug}: incorrect dimensions`);
    check(archived.get(asset.path).equals(bytes), 'Archived image differs');
    check(linksTo(page, base + asset.path), 'Missing individual image link');
    check(asset.shared === !asset.path.includes('/'), 'Shared asset must be at archive root');
    check(!identityPaths.has(metadata.sha256), 'Identical asset duplicated instead of shared');
    identityPaths.set(metadata.sha256, asset.path);
    if (asset.kind === 'artwork') assert.deepEqual(imageSize(bytes), [1200, 630], 'Social card size differs');
  }
  for (const locale of kit.locales) {
    const readmePath = `${locale.tag}/README.md`;
    const bytes = await readFile(join(directory, readmePath));
    const contents = bytes.toString();
    const panel = page.nodes.find(node => attr(node, 'data-kit-panel') === locale.tag);
    check(panel && text(panel).includes(locale.summary) && text(panel).replace(/\s/g, '').includes(locale.description.replace(/\s/g, '')), `Missing localized material copy: ${locale.tag}`);
    check(contents.includes(`https://lazyapps.com/${kit.slug}/presskit/#${locale.tag}`), 'README Press Kit link must preserve its own language');
    check(archived.get(readmePath).equals(bytes), 'Archived README differs');
    check(linksTo(page, base + readmePath), 'Missing language-specific README download');
    check(contents.startsWith('# ') && contents.includes('\n## ') && contents.includes('](mailto:lazyapps.feedback@gmail.com)'), 'README must use Markdown headings and links');
    for (const value of [locale.name, locale.platform, locale.summary, locale.description, locale.availability, locale.usage]) check(contents.includes(value), `README lacks ${locale.tag} product content`);
    check(locale.assets.some(asset => ['icon', 'logo'].includes(asset.kind)), 'Language kit missing icon/wordmark');
    check(locale.assets.some(asset => asset.kind === 'screenshot'), 'Language kit missing screenshot');
    for (const link of locale.links) check(linksTo(page, link.url) && contents.includes(`[${link.label}](`) && contents.includes(link.url), 'Official link missing');
    for (const asset of locale.assets) {
      check(contents.includes(asset.note) && contents.includes(asset.label), 'Missing localized asset context');
      check(asset.shared || asset.path.startsWith(locale.tag + '/'), 'Language-specific file is in another language folder');
      check(asset.shared || asset.contentLanguage === locale.tag, 'Localized asset content language differs');
      const relative = posix.relative(locale.tag, asset.path);
      check(contents.includes(`](${relative})`), 'README must link to each asset with its correct relative path');
    }
    for (const match of contents.matchAll(/\[[^\]]*\]\(([^)]+)\)/g)) {
      const target = match[1];
      if (/^[a-z]+:/i.test(target)) continue;
      const resolved = posix.normalize(posix.join(locale.tag, target));
      check(!resolved.startsWith('../') && archived.has(resolved), `Broken README asset reference: ${target}`);
    }
  }
}
console.log(`Presskits verified: ${kits.length} products, ${[...products.values()].reduce((a, b) => a + b, 0)} landing pages, ${kits.reduce((sum, kit) => sum + kit.locales.length, 0)} app-language folders, shared files, relative links and ZIPs.`);
