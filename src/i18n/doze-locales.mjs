import copy from './doze-copy.json' with { type: 'json' };
import release from './doze-release.json' with { type: 'json' };
export { release as DOZE_RELEASE };
const identities = [
  ['', 'zh-Hans', '眯会儿', '简体中文', 'zh_CN'],
  ['en', 'en', 'Doze', 'English', 'en_US'],
  ['zh-hant', 'zh-Hant', '瞇會兒', '繁體中文', 'zh_TW'],
  ['es', 'es', 'Siestita', 'Español', 'es_ES'],
  ['pt-br', 'pt-BR', 'Cochilo', 'Português', 'pt_BR'],
  ['fr', 'fr', 'Petit Repos', 'Français', 'fr_FR'],
  ['de', 'de', 'Schlummer', 'Deutsch', 'de_DE'],
  ['ja', 'ja', 'ひとやすみ', '日本語', 'ja_JP'],
  ['ko', 'ko', '잠깐 쉼', '한국어', 'ko_KR'],
  ['ru', 'ru', 'Дрёма', 'Русский', 'ru_RU'],
  ['ar', 'ar', 'غفوة', 'العربية', 'ar_AR'],
  ['hi', 'hi', 'झपकी', 'हिन्दी', 'hi_IN'],
];
export const DOZE_LOCALES = Object.fromEntries(identities.map(([code, htmlLang, name, languageName, ogLocale]) => {
  const t = copy[htmlLang];
  const selectedUrl = `/doze/${code ? `${code}/` : ''}`;
  return [code, { ...t, code, htmlLang, htmlDir: htmlLang === 'ar' ? 'rtl' : 'ltr', name, languageName, ogLocale,
    brand: name === 'Doze' ? name : `${name} · Doze`,
    title: `${name} — ${t.positioning}`, selectedUrl, canonical: `https://lazyapps.com${selectedUrl}`,
    availability: release.status === 'published' ? t.available : t.upcoming,
    cta: release.status === 'published' ? t.download : t.releases,
    ctaUrl: release.releasesUrl,
    ogAsset: `doze-opengraph-${code || 'zh-hans'}.png`,
  }];
}));
export const DOZE_LANGUAGE_OPTIONS = Object.values(DOZE_LOCALES).map(t => ({ language: t.htmlLang, label: t.languageName, url: t.selectedUrl }));
