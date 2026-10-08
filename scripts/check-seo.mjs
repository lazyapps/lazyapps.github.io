import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { attr, text, readPages, dist, site } from './lib/seo.mjs';

const pages = await readPages();
assert(pages.length > 0, 'No built pages. Run npm run build first.');
const byUrl = new Map(pages.map(page => [page.url, page]));
const knownAliases = new Map([[`${site}/fondfont/`, `${site}/fondfont/en/`]]);
const product = /\/(chmate|fondfont|keyhop|yiyan|world-book|xvdl|shheep)\//;
const localizedProduct = /\/(chmate|fondfont|keyhop|yiyan)\//;
const meta = (page, key) => page.metas.find(node => attr(node, 'name') === key || attr(node, 'property') === key);

for (const page of pages) {
  const check = (condition, message) => assert(condition, `${page.url}: ${message}`);
  check(page.links.filter(node => attr(node, 'rel') === 'canonical').length === 1, 'Expected one canonical');
  check(byUrl.has(page.canonical), `Canonical target is not built: ${page.canonical}`);
  check(page.canonical === (knownAliases.get(page.url) ?? page.url), 'Unexpected canonical alias');
  check(page.language, 'Missing document language');
  const titles = page.nodes.filter(node => node.tagName === 'title');
  check(titles.length === 1 && text(titles[0]).trim(), 'Expected one nonempty title');
  check(page.metas.filter(node => attr(node, 'name') === 'description').length === 1 && attr(meta(page, 'description'), 'content')?.trim(), 'Expected one nonempty description');
  check(page.nodes.filter(node => node.tagName === 'h1').length === 1, 'Expected one H1');
  check(attr(meta(page, 'og:url'), 'content') === page.canonical, 'OG URL differs from canonical');
  check(!/location\.replace\s*\(/.test(page.html), 'Unexpected automatic redirect');

  for (const key of ['og:image', 'twitter:image']) {
    const image = new URL(attr(meta(page, key), 'content'));
    check(image.origin === site && existsSync(join(dist, decodeURIComponent(image.pathname))), `${key} asset missing`);
  }

  const languageLinks = new Map(page.alternates.map(node => [attr(node, 'hreflang'), attr(node, 'href')]));
  check(languageLinks.size === page.alternates.length, 'Repeated hreflang');
  if (localizedProduct.test(page.url)) {
    check(languageLinks.get(page.language) === page.canonical, 'Missing self hreflang');
    check(languageLinks.has('x-default'), 'Missing x-default');
    for (const [language, url] of languageLinks) {
      if (language === 'x-default') continue;
      check(page.nodes.some(node => node.tagName === 'a' && attr(node, 'href') === new URL(url).pathname && attr(node, 'hreflang') === language), `Missing crawlable language link: ${language}`);
    }
  }
  for (const [language, url] of languageLinks) {
    const target = byUrl.get(url);
    check(target && target.canonical === url && !target.noindex, `Hreflang target is not canonical/indexable: ${url}`);
    if (language !== 'x-default') {
      check(target.language.toLowerCase() === language.toLowerCase() || target.language.toLowerCase().startsWith(`${language.toLowerCase()}-`), `Hreflang language mismatch: ${url}`);
    }
    const reciprocal = new Map(target.alternates.map(node => [attr(node, 'hreflang'), attr(node, 'href')]));
    check(reciprocal.size === languageLinks.size && [...languageLinks].every(([key, value]) => reciprocal.get(key) === value), `Nonreciprocal hreflang: ${url}`);
  }

  const jsonLd = page.nodes.filter(node => node.tagName === 'script' && attr(node, 'type') === 'application/ld+json').map(node => JSON.parse(text(node)));
  if (product.test(page.url)) {
    const app = jsonLd.find(data => ['SoftwareApplication', 'WebApplication'].includes(data['@type']));
    check(app?.url === page.canonical && app?.inLanguage === page.language, 'App structured data does not match page');
    check(app.name && app.description && app.operatingSystem, 'Incomplete basic app metadata');
    check(app['@type'] === 'WebApplication' ? app.browserRequirements : app.downloadUrl, 'Missing browser requirements or download URL');
    if (page.url === `${site}/shheep/`) check(app.applicationCategory === 'GameApplication', 'Missing game application category');
    check(!app.aggregateRating && !app.review && !app.offers, 'Unverified ratings/reviews/offers');
  }
  if (page.url === `${site}/`) {
    const graph = jsonLd.flatMap(data => data['@graph'] ?? []);
    check(graph.some(data => data['@type'] === 'WebSite') && graph.some(data => data['@type'] === 'Organization'), 'Missing site identity data');
  }

  for (const anchor of page.nodes.filter(node => node.tagName === 'a' && attr(node, 'href'))) {
    const url = new URL(attr(anchor, 'href'), page.url);
    if (url.origin !== site) continue;
    const path = join(dist, decodeURIComponent(url.pathname));
    check(byUrl.has(`${url.origin}${url.pathname}`) || existsSync(path) || existsSync(join(path, 'index.html')), `Broken internal link: ${url.pathname}`);
  }
}

const sitemap = await readFile(join(dist, 'sitemap.xml'), 'utf8');
assert(sitemap.includes('xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'), 'Missing sitemap namespace');
const urls = [...sitemap.matchAll(/<loc>([^<]+)<\/loc>/g)].map(match => match[1]);
const expected = pages.filter(page => !page.noindex && page.url === page.canonical).map(page => page.url);
assert.equal(new Set(urls).size, urls.length, 'Duplicate sitemap URLs');
assert.deepEqual([...urls].sort(), expected.sort(), 'Sitemap must contain exactly the indexable canonical pages');
const robots = await readFile(join(dist, 'robots.txt'), 'utf8');
assert(robots.includes(`Sitemap: ${site}/sitemap.xml`) && /^Allow: \/$/m.test(robots) && !/^Disallow: \/$/m.test(robots), 'robots.txt must permit crawling and declare sitemap');
console.log(`SEO checks passed: ${pages.length} pages, ${urls.length} canonical sitemap URLs, reciprocal hreflang, language links, social assets, JSON-LD, internal links.`);
