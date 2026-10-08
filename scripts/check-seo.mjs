import assert from 'node:assert/strict';
import { existsSync } from 'node:fs';
import { readFile } from 'node:fs/promises';
import { join } from 'node:path';
import { attr, text, readPages, dist, site } from './lib/seo.mjs';
import { SHHEEP_LOCALES } from '../src/i18n/shheep-locales.mjs';

const pages = await readPages();
assert(pages.length > 0, 'No built pages. Run npm run build first.');
const byUrl = new Map(pages.map(page => [page.url, page]));
const knownAliases = new Map([[`${site}/fondfont/`, `${site}/fondfont/en/`]]);
const product = /\/(chmate|fondfont|keyhop|yiyan|world-book|xvdl|shheep)\//;
const localizedProduct = /\/(chmate|fondfont|keyhop|yiyan|shheep)\//;
const meta = (page, key) => page.metas.find(node => attr(node, 'name') === key || attr(node, 'property') === key);
const shheepLocales = Object.values(SHHEEP_LOCALES);
assert.deepEqual(shheepLocales.map(locale => locale.htmlLang).sort(), ['en', 'zh-Hans', 'zh-Hant', 'ja', 'ko', 'es', 'pt-BR', 'de', 'fr', 'it', 'ru'].sort(), 'Shheep must cover all 11 app languages');
assert.equal(new Set(shheepLocales.map(locale => locale.title)).size, 11, 'Shheep titles must be translated');
assert.equal(new Set(shheepLocales.map(locale => locale.description)).size, 11, 'Shheep descriptions must be translated');
for (const locale of shheepLocales) assert(byUrl.has(`${site}${locale.selectedUrl}`), `Missing Shheep locale page: ${locale.htmlLang}`);

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
  if (page.url.startsWith(`${site}/shheep/`)) {
    const locale = shheepLocales.find(locale => `${site}${locale.selectedUrl}` === page.url);
    check(locale, 'Unexpected Shheep locale URL');
    check(page.language === locale.htmlLang, 'Incorrect Shheep page language');
    check(text(titles[0]).trim() === locale.title, 'Incorrect localized title');
    check(attr(meta(page, 'description'), 'content') === locale.description, 'Incorrect localized description');
    check(attr(meta(page, 'og:locale'), 'content') === locale.ogLocale, 'Incorrect OG locale');
    check(attr(meta(page, 'og:image:alt'), 'content') === locale.imageAlt, 'Incorrect localized social image description');
    check(languageLinks.size === 12 && languageLinks.get('x-default') === `${site}/shheep/`, 'Expected all 11 languages and English fallback');
    for (const other of shheepLocales) check(languageLinks.get(other.htmlLang) === `${site}${other.selectedUrl}`, `Missing Shheep alternate: ${other.htmlLang}`);
    const game = page.nodes.find(node => attr(node, 'class')?.split(' ').includes('shheep-game'));
    check(attr(game, 'data-language') === locale.htmlLang, 'Game default language must match the page');
    const h1 = page.nodes.find(node => node.tagName === 'h1');
    check(locale.headline.every(line => text(h1).includes(line)), 'Headline is not localized');
    for (const [, body] of [...locale.cards, ...locale.details]) check(page.html.includes(body.replaceAll('&', '&amp;')), 'Missing translated page content');
  }
  if (localizedProduct.test(page.url)) {
    check(languageLinks.get(page.language) === page.canonical, 'Missing self hreflang');
    check(languageLinks.has('x-default'), 'Missing x-default');
    const pickers = page.nodes.filter(node => node.tagName === 'select' && attr(node, 'data-locale-picker') !== undefined);
    check(pickers.length === 1, 'Expected one shared language picker');
    const options = pickers[0].childNodes.filter(node => node.tagName === 'option');
    check(options.length === languageLinks.size - 1, 'Language picker must cover every alternate');
    check(options.filter(node => attr(node, 'selected') !== undefined).length === 1, 'Expected one selected language');
    for (const option of options) {
      check(languageLinks.get(attr(option, 'lang')) === `${site}${attr(option, 'value')}`, 'Language picker option differs from hreflang');
      if (attr(option, 'selected') !== undefined) check(`${site}${attr(option, 'value')}` === page.canonical, 'Selected language differs from canonical');
    }
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
    if (page.url.startsWith(`${site}/shheep/`)) check(app.applicationCategory === 'GameApplication', 'Missing game application category');
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
