// Website presentation languages are independent of the App's download folders.
import { pressKits, glossary } from './presskit-catalog.mjs';
import ui from './presskit-ui.json' with { type: 'json' };
import calmonUI from '../i18n/calmon-media-ui.json' with { type: 'json' };
import { materialLanguage, languageHash } from '../i18n/presskit-language.mjs';
import { CHMATE_LOCALES } from '../i18n/chmate-locales.mjs';
import { FONDFONT_LOCALES } from '../i18n/fondfont-locales.mjs';
import { YILO_LOCALES } from '../i18n/yilo-locales.mjs';
import { DOZE_LOCALES, DOZE_RELEASE } from '../i18n/doze-locales.mjs';
import { SHHEEP_LOCALES } from '../i18n/shheep-locales.mjs';
import { CALMON_LOCALES, CALMON_RELEASE } from '../i18n/calmon-locales.mjs';

const translations = { calmon: CALMON_LOCALES, doze: DOZE_LOCALES, chmate: CHMATE_LOCALES, fondfont: FONDFONT_LOCALES, yilo: YILO_LOCALES, shheep: SHHEEP_LOCALES };
const traditionalSummaries = {
  'world-book': 'iPhone 與 iPad 離線世界地圖集，可查國家資料、瀏覽 3D 地球和比較排名。',
  xvdl: 'Mac Safari 的影片下載擴充功能，可從支援的網頁下載影片。',
  calmon: 'Calmon 將 Mac 視窗排成可捲動的欄，支援 App 堆疊、固定欄、視窗標籤、Pin Deck 常用 App 與 Sky Deck 浮動視窗。',
};
const plain = value => value.replace(/<[^>]*>/g, '').replaceAll('&amp;', '&').replaceAll('&nbsp;', ' ').trim();
export const calmonPressLanguages = Object.values(CALMON_LOCALES).map(t=>t.htmlLang);
const regionalUI = {'es-419':'es','fr-CA':'fr','pt-PT':'pt','zh-HK':'zh-Hant'};
export const calmonPressUI = Object.fromEntries(Object.values(CALMON_LOCALES).map(t=>{
  const inherited = ui[t.htmlLang] ?? ui[regionalUI[t.htmlLang]];
  if (inherited) return [t.htmlLang,inherited];
  const [allKits,downloadZip,copyImages,support,privacy,materialLanguage] = calmonUI[t.htmlLang];
  return [t.htmlLang,{allKits,downloadZip,copyImages,support,privacy,materialLanguage,language:t.select,skip:t.skip,home:t.home,hubTitle:[glossary[t.htmlLang].headings[0],''],hubIntro:t.description,products:glossary[t.htmlLang].headings[0]}];
}));
export const calmonPressOptions = Object.values(CALMON_LOCALES).map(t=>({language:t.htmlLang,label:t.languageName,url:languageHash(t.htmlLang)}));
export const presentationLanguages = Object.keys(ui);
export const languageOptions = presentationLanguages.map(tag => ({ language: tag, label: glossary[tag].name, url: languageHash(tag) }));
export const pressPresentations = pressKits.map(kit => ({
  slug: kit.slug,
  locales: Object.fromEntries((kit.slug === 'calmon' ? [...new Set([...calmonPressLanguages, ...presentationLanguages])] : presentationLanguages).map(tag => {
    const productTag = kit.slug === 'calmon' && tag === 'pt' ? 'pt-PT' : tag;
    const copy = kit.locales.find(locale => locale.tag === productTag);
    const marketing = Object.values(translations[kit.slug] ?? {}).find(locale => locale.htmlLang === productTag);
    const chinese = tag === 'zh-Hans' ? kit.summary.zh : tag === 'zh-Hant' ? traditionalSummaries[kit.slug] : undefined;
    const category = ['chmate', 'fondfont', 'world-book', 'shheep'].includes(kit.slug) ? 'store' : kit.slug === 'yilo' ? 'beta' : 'mac';
    const g = glossary[tag];
    const release = kit.slug === 'calmon' ? CALMON_RELEASE : kit.slug === 'doze' ? DOZE_RELEASE : undefined;
    return [tag, {
      name: copy?.name ?? kit.names.en,
      summary: copy?.summary ?? (marketing ? plain(marketing.sub ?? marketing.description) : chinese ?? kit.summary.en),
      summaryLang: copy || marketing || chinese ? tag : 'en',
      website: copy?.website ?? marketing?.selectedUrl ?? (kit.slug === 'calmon' ? CALMON_LOCALES.en.selectedUrl : kit.slug === 'doze' ? DOZE_LOCALES.en.selectedUrl : `/${kit.slug}/`),
      platform: copy?.platform ?? kit.platform.en,
      availability: kit.slug === 'yilo' ? (copy?.availability ?? kit.availability.en) : kit.slug === 'calmon' ? marketing.availability : release ? (release.status === 'published' ? g.availability.mac : g.availability.upcomingMac) : g.availability[category],
      materialTag: materialLanguage(productTag, kit.locales.map(locale => locale.tag)),
      links: kit.links.map(link => ({ url: link.url, label: release ? (release.status === 'published' ? g.links.download : g.links.releases) : link.url.includes('apps.apple.com') ? 'App Store' : link.url.includes('testflight.') ? g.links.beta : link.url.endsWith('/releases') ? g.links.download : link.url.includes('github.com') ? g.links.source : kit.slug === 'shheep' ? g.links.demo : g.links.play })),
    }];
  })),
}));
