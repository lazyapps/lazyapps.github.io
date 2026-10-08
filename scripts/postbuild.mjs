import { rename, rm, writeFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
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

const pages = await readPages();
const urls = pages.filter(page => page.canonical === page.url && !page.noindex).map(page => page.url);
const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${urls.map(url => `  <url><loc>${escapeXml(url)}</loc></url>`).join('\n')}
</urlset>
`;
await writeFile(dist + 'sitemap.xml', sitemap);
console.log(`postbuild: sitemap.xml with ${urls.length} canonical URLs`);
