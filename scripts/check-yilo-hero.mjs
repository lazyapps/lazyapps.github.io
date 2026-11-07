import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { readFile } from 'node:fs/promises';
import hero from '../src/i18n/yilo-hero-copy.json' with { type: 'json' };
import copy from '../src/i18n/yilo-short-copy.json' with { type: 'json' };
import examples from '../src/i18n/yilo-examples.json' with { type: 'json' };
import source from './assets/yilo/hero-video-source.json' with { type: 'json' };
import webMusic from './assets/yilo/web-music-source.json' with { type: 'json' };
import demoCopy from '../src/i18n/yilo-demo-copy.json' with { type: 'json' };
import artCopy from '../src/i18n/yilo-art-copy.json' with { type: 'json' };
import { YILO_LOCALES } from '../src/i18n/yilo-locales.mjs';
import { attr, readPages, site, dist, text } from './lib/seo.mjs';

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
if (source.descriptiveTextRevision) {
  const fields = ['brand', 'input', 'feedback', 'lesson', 'closing', 'fiction', 'punch', 'formerName'];
  assert.deepEqual(Object.fromEntries(Object.entries(hero).map(([tag, value]) => [tag, Object.fromEntries(fields.map(key => [key, value[key]]))])), source.descriptiveTextRevision.renderedCopy, 'Rendered film copy changed; recompose the video and poster');
}
if (source.renderedCopy) {
  for (const [tag, fields] of Object.entries(source.renderedCopy)) {
    for (const [key, value] of Object.entries(fields)) assert.equal(hero[tag][key], value, `${tag}/${key}: movie copy changed; update the film and poster`);
  }
}
const locales = Object.keys(YILO_LOCALES).map(code => code || 'zh-hans').sort();
assert.deepEqual(source.outputs.map(item => item.locale).sort(), locales);
assert.deepEqual(Object.keys(hero).sort(), locales);
assert.deepEqual(Object.keys(demoCopy).sort(), locales);
assert.deepEqual(Object.keys(artCopy).sort(), locales);
assert.equal(hash(await readFile(webMusic.source)), webMusic.sourceSHA256);
assert.equal(hash(await readFile(webMusic.output)), webMusic.sha256);
assert.equal(hash(await readFile(dist + webMusic.output.replace(/^public\//, ''))), webMusic.sha256);
assert.equal(copy['zh-hans'].headline, '边蹬边学');
assert.equal(copy['zh-hant'].headline, '邊蹬邊學');
for (const [path, sha256] of Object.entries(source.sources)) assert.equal(hash(await readFile(path)), sha256, `Yilo film source changed: ${path}; recompose and review`);
assert.equal(source.style, 'original-straight-hatched-line-illustration-local-h3');
assert.equal(source.generation.model, 'MiniMax-H3');
const generation = JSON.parse(await readFile(source.generation.receipt, 'utf8'));
assert.equal(generation.model, 'MiniMax-H3');
assert.equal(generation.outputSHA256, hash(await readFile(source.generation.receipt.replace('.generation.json', '.mp4'))));
assert.equal(generation.anchorSHA256, hash(await readFile(generation.anchor)));
assert.equal(hash(await readFile('video/yilo-hero/public/pedaling-h3.mp4')), generation.outputSHA256);
assert.equal(source.reference, 'https://x.com/pmamtraveller/status/2118294851431092442');
const nativeSource = JSON.parse(await readFile(source.nativeRecordSource, 'utf8'));
assert.equal(nativeSource.captures.length, 12, 'Every movie locale needs a native record capture');
assert.equal(new Set(nativeSource.captures.map(item => item.nativeLocale)).size, 12);
for (const capture of nativeSource.captures) {
  const image = await readFile(capture.source);
  assert.equal(hash(image), capture.sha256, 'Native hero record changed');
  assert.equal(capture.pixelWidth, image.readUInt32BE(16));
  assert.equal(capture.pixelHeight, image.readUInt32BE(20));
  assert(capture.pixelWidth >= 800, 'Do not enlarge a low-resolution native capture in the movie');
  assert.equal(hash(await readFile(`video/yilo-hero/public/records/${capture.contentLanguage.toLowerCase()}.png`)), capture.sha256, 'Movie must use the exact native export');
  assert.equal(hash(await readFile(capture.originalSource)), capture.captureFixtureSha256, 'Native capture fixture changed');
  assert.equal(hash(await readFile(capture.recordSource)), capture.recordSha256, 'Short native record changed');
  assert.equal(capture.nativeLocale, capture.contentLanguage);
  assert.equal(capture.nativeTextSize, 'extraLarge');
  const record = JSON.parse(await readFile(capture.recordSource, 'utf8'));
  assert.equal(record.originalText, examples.source[capture.contentLanguage.toLowerCase()]);
  assert.equal(record.configuration.sourceLanguage, capture.contentLanguage);
  assert.equal(record.configuration.learningNotesLanguage, capture.contentLanguage);
  assert.equal(capture.recordSource, `scripts/assets/yilo/capture/hero-records/${capture.contentLanguage}.json`);
  assert.equal(capture.sourceLanguage, capture.contentLanguage);
  assert.equal(record.translations[0].text, examples.agent[capture.contentLanguage === 'en' ? 'zh-hans' : 'en']);
  assert.equal(record.translations[1].text, examples.agent[capture.contentLanguage === 'ja' ? 'zh-hans' : 'ja']);
  assert.deepEqual(record.translations.map(item => item.language), capture.contentLanguage === 'en' ? ['zh-Hans', 'ja'] : capture.contentLanguage === 'ja' ? ['en', 'zh-Hans'] : ['en', 'ja']);
  assert.deepEqual(capture.targetLanguages, record.translations.map(item => item.language));
}
const music = JSON.parse(await readFile(source.musicSource, 'utf8'));
assert.equal(music.outputSHA256, hash(await readFile(music.output)));
assert.equal(music.sourceSHA256, hash(await readFile(music.source)));
assert.equal(music.title, 'Fluffing a Duck');
assert.equal(music.license, 'CC BY 4.0');
const pages = await readPages();
for (const [code, locale] of Object.entries(YILO_LOCALES)) {
  const tag = code || 'zh-hans';
  assert.equal(hero[tag].lineTitle, copy[tag].headline, `${tag}: preserve the playful page title`);
  const page = pages.find(page => page.url === site + locale.selectedUrl);
  const demo = page.nodes.find(node => attr(node, 'data-yilo-demo') !== undefined);
  assert(demo, `${tag}: missing native web animation`);
  assert.equal(attr(demo, 'data-locale'), tag);
  assert.equal(attr(demo, 'aria-label'), hero[tag].alt);
  assert.equal(JSON.parse(attr(demo, 'data-input')).join(' '), examples.source[tag]);
  assert.equal(text(page.nodes.find(node => attr(node, 'data-source-word') !== undefined)), artCopy[tag].word, `${tag}: pelican must think in its own language`);
  const illustrations = page.nodes.filter(node => attr(node, 'data-yilo-art') !== undefined);
  assert.equal(illustrations.length, 10);
  for (const illustration of illustrations) {
    assert.equal(attr(illustration, 'data-source-locale'), tag, `${tag}: illustration locale mismatch`);
    assert([artCopy[tag].word, artCopy[tag].glyph, artCopy[tag].refine].some(value => text(illustration).includes(value)), `${tag}: show this language as the illustration source`);
  }
  assert(!page.nodes.some(node => node.tagName === 'video'), `${tag}: web hero must not embed a movie`);
  const capture = nativeSource.captures.find(item => item.contentLanguage.toLowerCase() === tag);
  const record = page.nodes.find(node => node.tagName === 'image' && attr(node, 'data-layer') === 'learn');
  assert(record, `${tag}: native demo needs its real localized record`);
  assert.equal(hash(await readFile(dist + attr(record, 'href').replace(/^\//, ''))), capture.sha256);
  assert(Math.abs(Number(attr(record,'width'))/Number(attr(record,'height'))-capture.pixelWidth/capture.pixelHeight)<.001, 'Native record must retain its complete aspect ratio');
  const audio = page.nodes.find(node => attr(node, 'data-demo-audio') !== undefined);
  assert.equal(attr(audio,'src'), webMusic.output.replace(/^public/, ''));
  assert.equal(attr(audio,'preload'), 'none');
  assert.equal(attr(audio,'autoplay'), undefined, 'Music must require an explicit user action');
  assert(!page.nodes.some(node => ['toggle','replay'].includes(attr(node,'data-action'))), 'Do not add pause or replay controls');
  assert(text(page.nodes.find(node => node.tagName === 'body')).includes(copy[tag].formerName), `${tag}: show former name`);
  assert(page.nodes.some(node => node.tagName === 'a' && attr(node, 'href') === 'https://incompetech.com/music/royalty-free/index.html?isrc=USUAN1100768'), 'Music attribution missing');
}
for (const item of source.outputs) {
  assert.deepEqual([item.width, item.height, item.fps, item.frames, item.seconds], [1280, 608, 24, 336, 14]);
  assert.equal(item.codec, 'h264');
  assert.equal(item.pixelFormat, 'yuv420p');
  assert.deepEqual(item.audio, { codec: 'aac', sampleRate: '48000', channels: 2 });
  for (const media of [item.video, item.poster]) {
    const bytes = await readFile(media.path);
    assert.equal(hash(bytes), media.sha256, `${media.path}: unreviewed media change`);
    assert.equal(hash(await readFile(dist + media.path.replace(/^public\//, ''))), media.sha256, 'Built animation differs from the reviewed export');
  }
  const bytes = await readFile(item.video.path);
  assert(bytes.indexOf(Buffer.from('moov')) < bytes.indexOf(Buffer.from('mdat')), 'MP4 needs fast-start metadata');
  assert(bytes.includes(Buffer.from(source.metadata.title)), 'Current Yilo title missing in movie metadata');
  assert(!bytes.includes(Buffer.from('Upcoming learning feature preview')), 'Stale upcoming-feature metadata');
  const tag = item.locale === 'zh-hans' ? 'zh-Hans' : item.locale === 'zh-hant' ? 'zh-Hant' : item.locale === 'pt-br' ? 'pt-BR' : item.locale;
  const kit = pages.find(page => page.url === `${site}/yilo/presskit/`);
  assert(kit.nodes.some(node => node.tagName === 'a' && attr(node, 'href') === `/v/yilo/hero-${item.locale}-${source.version}.mp4`), 'Press Kit must offer each localized MP4');
  const readme = await readFile(`public/presskit/yilo/${tag}/README.md`, 'utf8');
  assert(readme.includes(hero[item.locale].posterNote) && readme.includes(`https://lazyapps.com/v/yilo/hero-${item.locale}-${source.version}.mp4`), 'Media package needs localized movie context and movie link');
}
const home = pages.find(page => page.url === site + '/');
assert(home.nodes.some(node => attr(node,'data-yilo-demo') !== undefined && attr(node,'data-locale') === 'en'), 'Homepage must use the native English animation');
assert(!home.nodes.some(node => node.tagName === 'video'), 'Homepage must not embed the old movie');
console.log('Yilo verified: 13 native web animations, 12 matching native record captures, localized opt-in audio, no Pause/Replay buttons, and 12 credited downloadable films with exact source/output hashes and current Press Kit links.');
