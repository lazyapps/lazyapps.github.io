import assert from 'node:assert/strict';
import { languageHash, languageFromHash, matchLanguage, resolvePressLanguage, materialLanguage } from '../src/i18n/presskit-language.mjs';
import { presentationLanguages as supported, pressPresentations } from '../src/content/presskit-presentation.mjs';
import { supported as appLanguages } from '../src/content/presskit-catalog.mjs';

const resolve = options => resolvePressLanguage({ supported, ...options });
assert.equal(resolve({ hash: '#fr', saved: 'de', preferred: ['ja'] }), 'fr', 'Explicit entry language must override saved/browser preferences');
assert.equal(resolve({ hash: '#en', saved: 'ar', preferred: ['ar'] }), 'en', 'English product/home entries must override a saved Arabic preference');
assert.equal(resolve({ saved: 'pt-br', preferred: ['fr'] }), 'pt-BR');
assert.equal(resolve({ preferred: ['xx', 'zh-TW', 'fr'] }), 'zh-Hant');
assert.equal(resolve({ preferred: ['xx', 'de-AT'] }), 'de');
assert.equal(resolve({ hash: '#unknown', saved: 'ko' }), 'ko');
assert.equal(resolve({ hash: '#%E0%A4%A', preferred: ['ja'] }), 'ja', 'Malformed fragments must not throw');
assert.equal(resolve({ hash: '#main', saved: 'fr' }), 'fr');
assert.equal(resolve({}), 'en');
assert.equal(languageFromHash('#LANGUAGE-ZH_hant', supported), 'zh-Hant');
assert.equal(languageFromHash('#language-fr', supported), 'fr', 'Previously shared links remain readable');
assert.equal(languageFromHash('#zh-Hans', supported), 'zh-Hans');
assert.equal(languageFromHash('#main', supported), undefined, 'Ordinary accessibility anchors are not language changes');
assert.equal(matchLanguage('zh-HK', supported), 'zh-Hant');
assert.equal(matchLanguage('zh-CN', supported), 'zh-Hans');
assert.equal(matchLanguage('pt-PT', supported), 'pt');
assert.equal(languageHash('pt-BR'), '#pt-BR');

for (const product of pressPresentations) {
  assert.deepEqual(Object.keys(product.locales), supported, 'Every Press Kit must accept the same presentation language');
  for (const [tag, copy] of Object.entries(product.locales)) {
    assert(copy.name && copy.summary && copy.website && copy.availability && copy.links.length);
    assert.equal(copy.materialTag, materialLanguage(tag, appLanguages[product.slug].tags));
    assert(appLanguages[product.slug].tags.includes(copy.materialTag), 'Presentation must not invent downloadable languages');
  }
}
for (const slug of ['fondfont', 'yiyan']) {
  const product = pressPresentations.find(item => item.slug === slug);
  for (const tag of ['zh-Hans', 'zh-Hant']) {
    assert(product.locales[tag].name.includes(' · '), 'Bilingual names must share the middle-dot separator');
    assert(!/[（）()]/.test(product.locales[tag].name), 'Bilingual names must not use parentheses');
  }
}
assert(!pressPresentations.some(product => product.slug === 'keyhop'), 'Retired KeyHop must not appear in Press Kits');
for (const slug of ['world-book', 'xvdl']) {
  const copy = pressPresentations.find(product => product.slug === slug).locales.ar;
  assert.equal(copy.summaryLang, 'en');
  assert.equal(copy.materialTag, 'en');
}
console.log('Press Kit language rules passed: hash precedence, regional matching, malformed/ordinary anchors, 17 presentation languages and unchanged App download coverage.');
