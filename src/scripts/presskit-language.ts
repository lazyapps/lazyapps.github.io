import ui from '../content/presskit-ui.json';
import glossary from '../content/presskit-glossary.json';
import { languageHash, languageFromHash, resolvePressLanguage } from '../i18n/presskit-language.mjs';

type ProductCopy = {
  name: string; summary: string; summaryLang: string; website: string;
  platform: string; availability: string; materialTag: string;
  links: { url: string; label: string }[];
};
type Presentation = { slug: string; locales: Record<string, ProductCopy> };
type Language = keyof typeof ui;
const data = JSON.parse(document.querySelector('#press-page-data')!.textContent!) as { product?: string; products: Presentation[] };
const languages = Object.keys(ui);
const picker = document.querySelector<HTMLSelectElement>('[data-locale-mode="hash"]')!;
const product = data.products.find(item => item.slug === data.product);
let saved: string | null = null;
try { saved = localStorage.getItem('presskit.locale'); } catch {}
let current = resolvePressLanguage({ hash: location.hash, saved, preferred: navigator.languages, supported: languages }) as Language;

function applyLanguage(tag: Language) {
  current = tag;
  const g = glossary[tag];
  const labels: Record<string, string> = {
    ...ui[tag], hubTitle: ui[tag].hubTitle.join(' '), hubTitleFirst: ui[tag].hubTitle[0], hubTitleSecond: ui[tag].hubTitle[1],
    kit: g.headings[0], website: g.headings[1], platformLabel: g.headings[3], availabilityLabel: g.headings[4],
    mediaContact: g.headings[5], officialLinks: g.headings[7], usageLabel: g.headings[9], usage: g.usage,
  };
  document.documentElement.lang = tag;
  document.documentElement.dir = tag === 'ar' ? 'rtl' : 'ltr';
  document.querySelectorAll<HTMLElement>('[data-press-text]').forEach(element => {
    element.textContent = labels[element.dataset.pressText!];
  });
  picker.value = languageHash(tag);
  picker.setAttribute('aria-label', ui[tag].language);
  const pickerWrapper = picker.closest<HTMLElement>('.locale')!;
  pickerWrapper.hidden = false;
  pickerWrapper.querySelector('.locale__now')!.textContent = g.name;
  pickerWrapper.querySelector('.locale__short')!.textContent = tag === 'zh-Hans' ? '简' : tag === 'zh-Hant' ? '繁' : tag.split('-')[0].toUpperCase();
  document.querySelectorAll<HTMLElement>('[data-press-home],.site-header__home').forEach(element => element.setAttribute('aria-label', ui[tag].home));
  const footer = document.querySelector<HTMLElement>('#site-footer')!;
  footer.lang = tag;
  footer.dir = tag === 'ar' ? 'rtl' : 'ltr';
  footer.querySelector('[data-press-footer-nav]')!.setAttribute('aria-label', [ui[tag].contact, g.headings[0], ui[tag].privacy].join(', '));
  document.querySelectorAll<HTMLAnchorElement>('[data-press-route]').forEach(link => {
    link.href = link.dataset.pressRoute + languageHash(tag);
  });
  document.querySelector<HTMLAnchorElement>('[data-press-privacy]')!.href = tag.startsWith('zh') ? '/privacy.zh.html' : '/privacy.en.html';

  if (product) {
    const copy = product.locales[tag];
    document.querySelectorAll<HTMLElement>('[data-press-product]').forEach(element => {
      const key = element.dataset.pressProduct as 'name' | 'summary' | 'platform' | 'availability';
      element.textContent = copy[key];
      if (key === 'summary' || key === 'name') {
        element.lang = key === 'summary' ? copy.summaryLang : /^[A-Za-z0-9 .&-]+$/.test(copy.name) ? 'en' : tag;
        element.dir = element.lang === 'ar' ? 'rtl' : 'ltr';
        if (key === 'name') element.toggleAttribute('data-bilingual', copy.name.includes(' · '));
      }
    });
    document.querySelector<HTMLAnchorElement>('[data-press-website]')!.href = copy.website;
    document.querySelectorAll<HTMLAnchorElement>('[data-press-official]').forEach(link => {
      const official = copy.links[Number(link.dataset.pressOfficial)];
      link.href = official.url;
      link.querySelector('span')!.textContent = official.label;
    });
    document.querySelector<HTMLElement>('[data-kit-materials]')!.dataset.enhanced = '';
    document.querySelectorAll<HTMLDetailsElement>('[data-kit-panel]').forEach(panel => {
      const active = panel.dataset.kitPanel === copy.materialTag;
      panel.hidden = !active;
      panel.open = active;
    });
    document.querySelector<HTMLElement>('[data-press-material-language]')!.hidden = copy.materialTag === tag;
    const materialName = document.querySelector<HTMLElement>('[data-press-material-name]')!;
    materialName.textContent = glossary[copy.materialTag as Language].name;
    materialName.lang = copy.materialTag;
    materialName.dir = copy.materialTag === 'ar' ? 'rtl' : 'ltr';
    document.title = `${copy.name} — ${g.headings[0]} | lazyapps`;
  } else {
    data.products.forEach(item => {
      const card = document.querySelector<HTMLElement>(`[data-product="${item.slug}"]`)!;
      const copy = item.locales[tag];
      const name = card.querySelector<HTMLElement>('[data-press-card-name]')!;
      name.textContent = copy.name;
      name.lang = /^[A-Za-z0-9 .&-]+$/.test(copy.name) ? 'en' : tag;
      name.toggleAttribute('data-bilingual', copy.name.includes(' · '));
      const summary = card.querySelector<HTMLElement>('[data-press-card-summary]')!;
      summary.textContent = copy.summary;
      summary.lang = copy.summaryLang;
      summary.dir = copy.summaryLang === 'ar' ? 'rtl' : 'ltr';
    });
    document.title = `lazyapps — ${ui[tag].hubTitle.join(' ')}`;
  }
  try { localStorage.setItem('presskit.locale', tag); } catch {}
}

applyLanguage(current);
// Language fragments represent UI state, not element IDs or scroll targets.
if (!location.hash || languageFromHash(location.hash, languages) || /^#language-/i.test(location.hash)) history.replaceState(null, '', location.pathname + location.search + languageHash(current));
picker.addEventListener('change', () => {
  const tag = languageFromHash(picker.value, languages) as Language;
  if (tag === current) return;
  history.pushState(null, '', location.pathname + location.search + languageHash(tag));
  applyLanguage(tag);
});
const fromHash = () => {
  const tag = languageFromHash(location.hash, languages) as Language | undefined;
  if (tag) {
    applyLanguage(tag);
    if (location.hash !== languageHash(tag)) history.replaceState(null, '', location.pathname + location.search + languageHash(tag));
  }
};
window.addEventListener('hashchange', fromHash);
window.addEventListener('popstate', fromHash);
