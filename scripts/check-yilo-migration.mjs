import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { runInNewContext } from 'node:vm';
import { createHash } from 'node:crypto';
import config from '../astro.config.mjs';
import { yiloLegacyRoutes } from '../src/content/yilo-routes.mjs';
import { YILO_LOCALES } from '../src/i18n/yilo-locales.mjs';
import copy from '../src/i18n/yilo-short-copy.json' with { type: 'json' };
import { attr, readPages, site, dist, text } from './lib/seo.mjs';

const pages = await readPages();
const byUrl = new Map(pages.map(page => [page.url, page]));
const sitemap = await readFile(`${dist}sitemap.xml`, 'utf8');
const screenshotReview = JSON.parse(await readFile('scripts/assets/presskit/screenshot-sources.json', 'utf8')).yilo;
const screenshotFiles = ['learning-record.png', 'learning-settings.png', 'language-selection.png'];
const hash = bytes => createHash('sha256').update(bytes).digest('hex');
const opengraph = JSON.parse(await readFile('scripts/assets/yilo/opengraph-source.json', 'utf8'));
const icon = JSON.parse(await readFile('scripts/assets/yilo/AppIcon.icon/icon.json', 'utf8'));
assert.deepEqual(opengraph.background, icon['fill-specializations'].find(item => !item.appearance).value, 'Yilo OG must reuse the native app background');
assert.deepEqual(opengraph.size, [1200, 630]);
assert.deepEqual(opengraph.safeRect, [285, 0, 630, 630]);
for (const [source, sha256] of Object.entries(opengraph.sources)) assert.equal(hash(await readFile(source)), sha256, `Yilo OG source changed: ${source}`);
for (const card of opengraph.cards) {
  const image = await readFile(card.output);
  assert.equal(hash(image), card.sha256, 'Yilo OG must match its source receipt');
  assert.deepEqual([image.readUInt32BE(16), image.readUInt32BE(20)], opengraph.size);
  const [x, y, width, height] = card.contentBounds;
  assert(x >= 285 && y >= 0 && x + width <= 915 && y + height <= 630, 'Yilo OG brand content must fit the central square');
}
const presskit = JSON.parse(await readFile('public/presskit/yilo/manifest.json', 'utf8'));
assert(!presskit.files.some(file => file.path === 'desktop-wallpaper.png'), 'Do not distribute the retired Yilo wallpaper');
assert(!byUrl.get(`${site}/yilo/presskit/`).html.includes('desktop-wallpaper.png'), 'Do not show the retired wallpaper in the Press Kit');
const fixtureHash = hash(await readFile('scripts/assets/yilo/capture/YiloWebsiteCapture.swift'));
assert.equal(screenshotReview.captures.length, 48, 'Yilo needs three product captures and one hero capture for each of its 12 languages');
assert(!sitemap.includes('/yiyan/'), 'Legacy product URLs must leave the sitemap');
for (const [from, to] of Object.entries(yiloLegacyRoutes)) {
  assert.deepEqual(config.redirects[from], { destination: to, status: 301 });
  const page = byUrl.get(`${site}${from}/`);
  assert(page?.noindex && page.canonical === `${site}${to}`, `${from}: legacy fallback must canonicalize to Yilo`);
  assert.equal(page.redirectTo, to, `${from}: no-JavaScript fallback target`);
  assert.equal(attr(page.metas.find(meta => attr(meta, 'http-equiv') === 'refresh'), 'content'), `0;url=${to}`, `${from}: redirect must be immediate`);
  const script = text(page.nodes.find(node => attr(node, 'data-yilo-redirect') !== undefined));
  for (const [search, hash] of [['', ''], ['?utm_source=old&name=%E4%BA%A6%E8%A8%80', '#brew'], ['?next=https://example.com', '#zh-Hant']]) {
    let result;
    runInNewContext(script, { location: { search, hash, replace: destination => { result = destination; } } });
    assert.equal(result, to + search + hash, `${from}: preserve search/hash and fixed destination`);
  }
}
for (const [code, locale] of Object.entries(YILO_LOCALES)) {
  const page = byUrl.get(`${site}${locale.selectedUrl}`);
  const c = copy[code || 'zh-hans'];
  assert(page && page.canonical === locale.canonical, `${code}: missing new canonical page`);
  assert.equal(text(page.nodes.find(node => node.tagName === 'h1')), c.headline);
  const visible = text(page.nodes.find(node => node.tagName === 'body'));
  assert(visible.includes(c.formerName) && visible.includes(c.screenshotNote), `${code}: former name and record context must be explicit`);
  for (const [index, filename] of screenshotFiles.entries()) {
    const source = `scripts/assets/presskit/yilo/${page.language}/${filename}`;
    const capture = screenshotReview.captures.find(capture => capture.source === source);
    assert(capture && capture.contentLanguage === page.language && capture.nativeLocale === page.language, `${code}: screenshot must use the actual matching native UI language`);
    assert.equal(capture.captureFixtureSha256, fixtureHash, 'Capture fixture changed; recapture the native screenshots');
    const samplePath = `scripts/assets/yilo/capture/records/${page.language}.json`;
    const sample = JSON.parse(await readFile(samplePath, 'utf8'));
    assert.equal(sample.configuration.sourceLanguage, page.language, 'Sample source must match the page language');
    assert.equal(sample.configuration.learningNotesLanguage, page.language, 'Learning explanations must match the page language');
    assert.equal(capture.sourceLanguage, page.language, 'Native source setting must match the page language');
    assert.deepEqual(capture.targetLanguages, sample.translations.map(translation => translation.language), 'Settings and record targets must agree');
    assert(!capture.targetLanguages.includes(page.language), 'Learning targets must differ from the source language');
    if (index === 0) {
      assert.equal(capture.recordSource, samplePath);
      assert.equal(capture.recordSha256, hash(await readFile(samplePath)), 'Recapture localized sample content');
    }
    const image = page.nodes.find(node => node.tagName === 'img' && attr(node, 'alt') === c.screenshots[index]);
    assert(image, `${code}: missing localized screenshot ${filename}`);
    const native = await readFile(source);
    assert.equal(hash(await readFile(`${dist}${attr(image, 'src').replace(/^\//, '')}`)), hash(native), `${code}: product image must preserve the localized native export`);
    assert.deepEqual([Number(attr(image, 'width')), Number(attr(image, 'height'))], [native.readUInt32BE(16), native.readUInt32BE(20)], `${code}: image dimensions must match the native capture`);
  }
  assert(!page.html.includes('/v/yiyan/'), 'Retired branded film must not be advertised');
  assert(page.html.includes('brew tap cxa/yilo https://github.com/cxa/yilo') && page.html.includes('brew install --cask cxa/yilo/yiyan'), 'Keep real Homebrew identifiers');
  assert(page.nodes.some(node => node.tagName === 'a' && attr(node, 'href') === 'https://github.com/cxa/yilo/releases'), 'Keep real release URL');
}
for (const filename of screenshotFiles) {
  const captures = screenshotReview.captures.filter(capture => capture.source.endsWith(`/${filename}`));
  assert.equal(new Set(captures.map(capture => capture.sha256)).size, 12, `${filename}: do not reuse one English screenshot across locales`);
}
for (const page of pages.filter(page => !page.redirectTo)) {
  for (const node of page.nodes.filter(node => node.tagName === 'a')) {
    const href = attr(node, 'href') ?? '';
    assert(!/^(?:https:\/\/lazyapps\.com)?\/(?:yiyan(?:\/|$)|presskit\/yiyan\/)/.test(href), `${page.url}: active legacy link ${href}`);
  }
}
for (const [oldName, newName] of [
  ['yiyan-presskit.zip', 'yilo-presskit.zip'], ['icon.png', 'icon.png'],
  ['learning-notes-en.png', 'learning-record-preview-en.png'], ['follow-up-en.png', 'learning-record-preview-en.png'],
  ['zh-Hans/social-card.png', 'social-card-zh.png'], ['zh-Hant/social-card.png', 'social-card-zh.png'],
]) assert((await readFile(`${dist}presskit/yiyan/${oldName}`)).equals(await readFile(`${dist}presskit/yilo/${newName}`)), `Legacy download must contain current bytes: ${oldName}`);
console.log('Yilo migration verified: 12 locales, 13 legacy fallbacks, query/fragment preservation, current download aliases and no active old-brand links. HTTP 301 still requires a supporting host; GitHub Pages serves HTML fallbacks.');
