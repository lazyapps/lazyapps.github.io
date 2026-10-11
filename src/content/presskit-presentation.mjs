// Website presentation languages are independent of the App's download folders.
import { pressKits, glossary } from './presskit-catalog.mjs';
import ui from './presskit-ui.json' with { type: 'json' };
import { materialLanguage, languageHash } from '../i18n/presskit-language.mjs';
import { CHMATE_LOCALES } from '../i18n/chmate-locales.mjs';
import { FONDFONT_LOCALES } from '../i18n/fondfont-locales.mjs';
import { YIYAN_LOCALES } from '../i18n/yiyan-locales.mjs';
import { SHHEEP_LOCALES } from '../i18n/shheep-locales.mjs';

const translations = { chmate: CHMATE_LOCALES, fondfont: FONDFONT_LOCALES, yiyan: YIYAN_LOCALES, shheep: SHHEEP_LOCALES };
const traditionalSummaries = {
  'world-book': 'iPhone 與 iPad 離線世界地圖集，可查國家資料、瀏覽 3D 地球和比較排名。',
  xvdl: 'Mac Safari 的影片下載擴充功能，可從支援的網頁下載影片。',
};
const plain = value => value.replace(/<[^>]*>/g, '').replaceAll('&amp;', '&').replaceAll('&nbsp;', ' ').trim();
export const presentationLanguages = Object.keys(ui);
export const languageOptions = presentationLanguages.map(tag => ({ language: tag, label: glossary[tag].name, url: languageHash(tag) }));
export const pressPresentations = pressKits.map(kit => ({
  slug: kit.slug,
  locales: Object.fromEntries(presentationLanguages.map(tag => {
    const copy = kit.locales.find(locale => locale.tag === tag);
    const marketing = Object.values(translations[kit.slug] ?? {}).find(locale => locale.htmlLang === tag);
    const chinese = tag === 'zh-Hans' ? kit.summary.zh : tag === 'zh-Hant' ? traditionalSummaries[kit.slug] : undefined;
    const category = ['chmate', 'fondfont', 'world-book'].includes(kit.slug) ? 'store' : kit.slug === 'yiyan' ? 'beta' : kit.slug === 'shheep' ? 'upcoming' : 'mac';
    const g = glossary[tag];
    return [tag, {
      name: copy?.name ?? kit.names.en,
      summary: copy?.summary ?? (marketing ? plain(marketing.sub ?? marketing.description) : chinese ?? kit.summary.en),
      summaryLang: copy || marketing || chinese ? tag : 'en',
      website: copy?.website ?? marketing?.selectedUrl ?? `/${kit.slug}/`,
      platform: copy?.platform ?? kit.platform.en,
      availability: g.availability[category],
      materialTag: materialLanguage(tag, kit.locales.map(locale => locale.tag)),
      links: kit.links.map(link => ({ url: link.url, label: link.url.includes('apps.apple.com') ? 'App Store' : link.url.includes('testflight.') ? g.links.beta : link.url.endsWith('/releases') ? g.links.download : link.url.includes('github.com') ? g.links.source : kit.slug === 'shheep' ? g.links.demo : g.links.play })),
    }];
  })),
}));
