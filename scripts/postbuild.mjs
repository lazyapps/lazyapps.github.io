import { rename, rm, writeFile, cp, copyFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { yiloRedirects } from '../src/content/yilo-routes.mjs';
import { readPages, escapeXml } from './lib/seo.mjs';

const dist = fileURLToPath(new URL('../dist/', import.meta.url));

for (const name of ['privacy.en', 'privacy.zh']) {
  const dir = dist + name;
  const index = dir + '/index.html';
  if (!existsSync(index)) continue;
  await rename(index, dist + name + '.html');
  await rm(dir, { recursive: true, force: true });
}

console.log('postbuild: flattened /privacy.*.html');

// GitHub Pages serves static HTML. A 301 requires a supporting host/CDN;
// preserve search and fragment in the browser fallback without a history entry.
for (const [from, destination] of Object.entries(yiloRedirects)) {
  const path = `${dist}${from.slice(1)}/index.html`;
  const html = `<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<title>Yilo — moved permanently</title>
<link rel="canonical" href="https://lazyapps.com${destination}">
<meta name="robots" content="noindex">
<script data-yilo-redirect>location.replace(${JSON.stringify(destination)} + location.search + location.hash)</script>
<meta http-equiv="refresh" content="0;url=${destination}">
</head><body><a href="${destination}">Continue to Yilo</a></body></html>`;
  await writeFile(path, html);
}
// Existing direct media links receive current bytes, including the old ZIP URL.
await copyFile(`${dist}presskit/yilo/en/learning-record.png`, `${dist}presskit/yilo/learning-record-preview-en.png`);
await copyFile(`${dist}presskit/yilo/en/learning-settings.png`, `${dist}presskit/yilo/learning-languages-en.png`);
await copyFile(`${dist}presskit/yilo/en/language-selection.png`, `${dist}presskit/yilo/language-selection-en.png`);
await cp(`${dist}presskit/yilo`, `${dist}presskit/yiyan`, { recursive: true });
for (const [oldName, currentName] of [
  ['yiyan-presskit.zip', 'yilo-presskit.zip'],
  ['learning-notes-en.png', 'learning-record-preview-en.png'],
  ['follow-up-en.png', 'learning-record-preview-en.png'],
]) await copyFile(`${dist}presskit/yilo/${currentName}`, `${dist}presskit/yiyan/${oldName}`);
for (const tag of ['zh-Hans', 'zh-Hant']) await copyFile(`${dist}presskit/yilo/social-card-zh.png`, `${dist}presskit/yiyan/${tag}/social-card.png`);
console.log('postbuild: Yilo legacy page fallbacks and current media aliases');

const pages = await readPages();
const urls = pages.filter(page => page.canonical === page.url && !page.noindex).map(page => page.url);
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(url => `  <url><loc>${escapeXml(url)}</loc></url>`).join('\n')}
</urlset>
`;
await writeFile(dist + 'sitemap.xml', sitemap);
console.log(`postbuild: sitemap.xml with ${urls.length} canonical URLs`);
