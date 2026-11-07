// Each locale keeps the same small set of content groups; arrays follow the page order.
import locale0 from './calmon/ar.json' with { type: 'json' };
import locale1 from './calmon/ca.json' with { type: 'json' };
import locale2 from './calmon/cs.json' with { type: 'json' };
import locale3 from './calmon/da.json' with { type: 'json' };
import locale4 from './calmon/de.json' with { type: 'json' };
import locale5 from './calmon/el.json' with { type: 'json' };
import locale6 from './calmon/es-419.json' with { type: 'json' };
import locale7 from './calmon/es.json' with { type: 'json' };
import locale8 from './calmon/fi.json' with { type: 'json' };
import locale9 from './calmon/fr-CA.json' with { type: 'json' };
import locale10 from './calmon/fr.json' with { type: 'json' };
import locale11 from './calmon/he.json' with { type: 'json' };
import locale12 from './calmon/hi.json' with { type: 'json' };
import locale13 from './calmon/hr.json' with { type: 'json' };
import locale14 from './calmon/hu.json' with { type: 'json' };
import locale15 from './calmon/id.json' with { type: 'json' };
import locale16 from './calmon/it.json' with { type: 'json' };
import locale17 from './calmon/ja.json' with { type: 'json' };
import locale18 from './calmon/ko.json' with { type: 'json' };
import locale19 from './calmon/ms.json' with { type: 'json' };
import locale20 from './calmon/nb.json' with { type: 'json' };
import locale21 from './calmon/nl.json' with { type: 'json' };
import locale22 from './calmon/pl.json' with { type: 'json' };
import locale23 from './calmon/pt-BR.json' with { type: 'json' };
import locale24 from './calmon/pt-PT.json' with { type: 'json' };
import locale25 from './calmon/ro.json' with { type: 'json' };
import locale26 from './calmon/ru.json' with { type: 'json' };
import locale27 from './calmon/sk.json' with { type: 'json' };
import locale28 from './calmon/sl.json' with { type: 'json' };
import locale29 from './calmon/sv.json' with { type: 'json' };
import locale30 from './calmon/th.json' with { type: 'json' };
import locale31 from './calmon/tr.json' with { type: 'json' };
import locale32 from './calmon/uk.json' with { type: 'json' };
import locale33 from './calmon/vi.json' with { type: 'json' };
import locale34 from './calmon/zh-HK.json' with { type: 'json' };
import locale35 from './calmon/zh-Hant.json' with { type: 'json' };
const files = {
  './calmon/ar.json': locale0,
  './calmon/ca.json': locale1,
  './calmon/cs.json': locale2,
  './calmon/da.json': locale3,
  './calmon/de.json': locale4,
  './calmon/el.json': locale5,
  './calmon/es-419.json': locale6,
  './calmon/es.json': locale7,
  './calmon/fi.json': locale8,
  './calmon/fr-CA.json': locale9,
  './calmon/fr.json': locale10,
  './calmon/he.json': locale11,
  './calmon/hi.json': locale12,
  './calmon/hr.json': locale13,
  './calmon/hu.json': locale14,
  './calmon/id.json': locale15,
  './calmon/it.json': locale16,
  './calmon/ja.json': locale17,
  './calmon/ko.json': locale18,
  './calmon/ms.json': locale19,
  './calmon/nb.json': locale20,
  './calmon/nl.json': locale21,
  './calmon/pl.json': locale22,
  './calmon/pt-BR.json': locale23,
  './calmon/pt-PT.json': locale24,
  './calmon/ro.json': locale25,
  './calmon/ru.json': locale26,
  './calmon/sk.json': locale27,
  './calmon/sl.json': locale28,
  './calmon/sv.json': locale29,
  './calmon/th.json': locale30,
  './calmon/tr.json': locale31,
  './calmon/uk.json': locale32,
  './calmon/vi.json': locale33,
  './calmon/zh-HK.json': locale34,
  './calmon/zh-Hant.json': locale35
};
const names = { ar:'العربية', ca:'Català', cs:'Čeština', da:'Dansk', de:'Deutsch', el:'Ελληνικά', es:'Español', 'es-419':'Español (Latinoamérica)', fi:'Suomi', fr:'Français', 'fr-CA':'Français (Canada)', he:'עברית', hi:'हिन्दी', hr:'Hrvatski', hu:'Magyar', id:'Bahasa Indonesia', it:'Italiano', ja:'日本語', ko:'한국어', ms:'Bahasa Melayu', nb:'Norsk bokmål', nl:'Nederlands', pl:'Polski', 'pt-BR':'Português (Brasil)', 'pt-PT':'Português (Portugal)', ro:'Română', ru:'Русский', sk:'Slovenčina', sl:'Slovenščina', sv:'Svenska', th:'ไทย', tr:'Türkçe', uk:'Українська', vi:'Tiếng Việt', 'zh-Hant':'繁體中文', 'zh-HK':'繁體中文（香港）' };
const regions = { ar:'SA',ca:'ES',cs:'CZ',da:'DK',de:'DE',el:'GR',es:'ES',fi:'FI',fr:'FR',he:'IL',hi:'IN',hr:'HR',hu:'HU',id:'ID',it:'IT',ja:'JP',ko:'KR',ms:'MY',nb:'NO',nl:'NL',pl:'PL',ro:'RO',ru:'RU',sk:'SK',sl:'SI',sv:'SE',th:'TH',tr:'TR',uk:'UA',vi:'VN' };
const keys = ['← → / ↑ ↓','⇧ + ← → ↑ ↓',', / .','Space → J / X','Space → A / R','1–9 / ⇧1–9','Esc'];
export const calmonTranslations = Object.fromEntries(Object.entries(files).map(([path, t]) => {
  const code = path.split('/').at(-1).replace('.json','');
  const [headline,positioning,description] = t.hero;
  const [home,select,skip] = t.nav;
  const [download,available,releaseNote,compatibility] = t.release;
  const [keyboardTitle,keyboardMapLabel,keyboardHelp,shortcutContext,panelCaption,shortcutsTitle] = t.keyboard;
  const [setupTitle,applications,accessibility,install,setupDownload,installTail,allow,allowText,open,openText,menuBarNote] = t.setup;
  return [code,{htmlLang:code,languageName:names[code],ogLocale:code.startsWith('zh')?'zh_'+(code==='zh-HK'?'HK':'TW'):code.replace('-','_')+(regions[code]?'_'+regions[code]:''),headline:headline.split('\n'),positioning,description,home,select,skip,download,available,upcoming:available,releaseTitle:available,releaseNote,compatibility,displayQuestion:t.display[0],displayNote:t.display.slice(1).join("\n\n"),features:t.features,keyboardTitle,keyboardMapLabel,keyboardHelp,shortcutContext,panelCaption,shortcutsTitle,keyboardSteps:t.mouse,shortcuts:t.actions.map((action,i)=>[keys[i],action]),setupTitle,setupArt:{applications,accessibility},setupDownload,menuBarNote,steps:[[install,setupDownload+installTail],[allow,allowText],[open,openText]],details:t.faq[0],faqs:t.faq.slice(1),heroSubtitle:t.subtitle,demo:t.demo,menus:t.menus,apps:t.apps,windows:t.windows}];
}));
