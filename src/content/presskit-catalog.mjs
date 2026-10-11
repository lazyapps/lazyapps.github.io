import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { resolve } from 'node:path';
import originals from './presskits.json' with { type: 'json' };
import supportedLanguages from './presskit-supported-languages.json' with { type: 'json' };
import pressGlossary from './presskit-glossary.json' with { type: 'json' };
import yiyanCopy from '../i18n/yiyan-short-copy.json' with { type: 'json' };
import { CHMATE_LOCALES } from '../i18n/chmate-locales.mjs';
import { FONDFONT_LOCALES } from '../i18n/fondfont-locales.mjs';
import { YIYAN_LOCALES } from '../i18n/yiyan-locales.mjs';
import { SHHEEP_LOCALES } from '../i18n/shheep-locales.mjs';
export const supported = supportedLanguages;
export const glossary = pressGlossary;
const translations = { chmate: CHMATE_LOCALES, fondfont: FONDFONT_LOCALES, yiyan: YIYAN_LOCALES, shheep: SHHEEP_LOCALES };
const plain = value => value.replace(/<[^>]*>/g, '').replaceAll('&amp;', '&').replaceAll('&nbsp;', ' ').trim();
function asset(kit, tag, source, filename, kind, note, shared = false) {
  const g = glossary[tag];
  const original = kit.assets.find(item => item.source === source);
  const lang = tag === 'en' ? 'en' : tag === 'zh-Hans' ? 'zh' : null;
  return { source, filename, kind, label: g.labels[kind], note: lang && original ? original.note[lang] : g.notes[note], shared, contentLanguage: ['icon', 'logo'].includes(kind) || (kind === 'artwork' && shared) ? 'und' : ['world-book', 'xvdl', 'shheep', 'yiyan'].includes(kit.slug) && kind === 'screenshot' ? 'en' : tag };
}
function localeAssets(kit, tag, t) {
  const assets = [asset(kit, tag, kit.assets[0].source, kit.assets[0].filename, kit.assets[0].kind, kit.assets[0].kind, true)];
  if (kit.slug === 'shheep') { const logo = kit.assets.find(item => item.kind === 'logo'); assets.push(asset(kit, tag, logo.source, logo.filename, 'logo', 'logo', true)); }
  if (kit.slug === 'chmate') assets.push(asset(kit, tag, `scripts/assets/presskit/chmate-reading-${tag.toLowerCase()}.png`, 'reading-ipad.png', 'screenshot', 'native'));
  if (kit.slug === 'fondfont') assets.push(asset(kit, tag, `scripts/assets/presskit/fondfont-select-${tag.toLowerCase()}.png`, 'font-selection.png', 'screenshot', 'native'));
  if (kit.slug === 'yiyan') {
    assets.push(asset(kit, tag, 'src/assets/img/yiyan-showcase.png', 'learning-notes-en.png', 'screenshot', 'sharedEnglishCapture', true));
    assets.push(asset(kit, tag, 'src/assets/img/yiyan-showcase-detail.png', 'follow-up-en.png', 'screenshot', 'sharedEnglishCapture', true));
  }
  if (kit.slug === 'shheep') assets.push(asset(kit, tag, 'public/shheep/preview.png', 'bedroom-preview.png', 'screenshot', 'title', true));
  if (kit.slug === 'world-book') assets.push(asset(kit, tag, 'scripts/assets/presskit/world-book-globe.png', 'globe-ipad.png', 'screenshot', 'globe'));
  if (kit.slug === 'xvdl') {
    for (const item of kit.assets.filter(item => item.kind === 'screenshot')) {
      assets.push({ ...asset(kit, tag, item.source, item.filename, item.kind, 'native', true), label: item.label.en });
    }
  }
  let card = kit.assets.find(item => item.kind === 'artwork').source;
  let shared = true;
  if (kit.slug === 'yiyan' && tag.startsWith('zh-')) { card = `src/assets/img/${kit.slug}-opengraph${tag === 'zh-Hant' ? '-zh-hant' : ''}.png`; shared = false; }
  if (kit.slug === 'fondfont' && t.ogAsset !== 'shared') { card = `src/assets/img/fondfont-opengraph-${t.ogAsset}.png`; shared = false; }
  assets.push(asset(kit, tag, card, 'social-card.png', 'artwork', 'artwork', shared));
  return assets;
}
export const pressKits = originals.map(kit => {
  const locales = supported[kit.slug].tags.map(tag => {
    const t = Object.values(translations[kit.slug] ?? {}).find(item => item.htmlLang === tag);
    if (!t && translations[kit.slug]) throw Error(`Missing press copy: ${kit.slug}/${tag}`);
    const lang = tag === 'zh-Hans' ? 'zh' : 'en';
    const g = glossary[tag];
    const name = tag === 'zh-Hans' ? kit.names.zh : tag === 'zh-Hant' ? kit.names.zh.replaceAll('飞键','飛鍵').replaceAll('绎言','繹言').replaceAll('爱装字体','愛裝字體') : kit.names.en;
    let summary = t ? plain(t.sub ?? t.description) : kit.summary.en;
    let description = t ? plain(t.description) : kit.description.en;
    if (kit.slug === 'chmate') description = [t.description, ...t.cards.map(card => card[1]), t.promiseCopy].map(plain).join('\n\n');
    if (kit.slug === 'fondfont') description = [t.description, ...t.features.map(feature => feature[1]), ...t.steps.map(step => step[1]), t.privacyCopy, t.faqs[1][1]].map(plain).join('\n\n');
    if (kit.slug === 'yiyan') { const copy = yiyanCopy[tag.toLowerCase()]; summary = copy.sub; description = [copy.sub, ...copy.cards.map(card => card[1]), ...copy.details.map(detail => detail[1].join(' '))].join('\n\n'); }
    if (kit.slug === 'shheep') {
      summary = plain(t.title.split(' — ')[1]);
      description = [t.description, ...t.cards.map(card => card[1]), t.gameCenterCopy, t.demoNote].join('\n\n');
    }
    const category = ['chmate','fondfont','world-book'].includes(kit.slug) ? 'store' : kit.slug === 'yiyan' ? 'beta' : kit.slug === 'shheep' ? 'upcoming' : 'mac';
    const links = kit.links.map(link => ({url:link.url, label:link.url.includes('apps.apple.com') ? 'App Store' : link.url.includes('testflight.') ? g.links.beta : link.url.endsWith('/releases') ? g.links.download : link.url.includes('github.com') ? g.links.source : kit.slug === 'shheep' ? g.links.demo : g.links.play}));
    return { tag, displayName: g.name, name, summary, description, website: t?.selectedUrl ?? `/${kit.slug}/`, platform: kit.platform[lang], availability: g.availability[category], links, assets: localeAssets(kit, tag, t), headings: g.headings, usage: g.usage };
  });
  // Identity is source bytes, so repeated artwork is stored once even for a subset of languages.
  const identities = new Map();
  for (const locale of locales) for (const a of locale.assets) {
    const bytes = readFileSync(resolve(a.source));
    a.sha256 = createHash('sha256').update(bytes).digest('hex');
    const identity = identities.get(a.sha256) ?? { count: 0, shared: false, asset: a };
    identity.count++; identity.shared ||= a.shared; identities.set(a.sha256, identity);
  }
  const used = new Map();
  for (const locale of locales) for (const a of locale.assets) {
    const identity = identities.get(a.sha256);
    a.shared = identity.shared || identity.count > 1;
    a.path = a.shared ? identity.asset.filename : `${locale.tag}/${a.filename}`;
    // Distinct shared assets need distinct stable names.
    const previous = used.get(a.path);
    if (previous && previous !== a.sha256) throw Error(`Press asset path collision: ${kit.slug}/${a.path}`);
    used.set(a.path, a.sha256);
  }
  const files = [...new Map(locales.flatMap(locale => locale.assets).map(a => [a.path, a])).values()];
  return { ...kit, locales, files };
});
