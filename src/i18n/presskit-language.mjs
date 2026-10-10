export const languageHash = tag => `#${tag}`;

export function matchLanguage(value, supported) {
  if (typeof value !== 'string') return undefined;
  const tag = value.trim().replaceAll('_', '-').toLowerCase();
  const exact = supported.find(item => item.toLowerCase() === tag);
  if (exact) return exact;
  if (/^zh(?:-|$)/.test(tag)) {
    return supported.find(item => item === (/^zh-(?:hant|tw|hk|mo)(?:-|$)/.test(tag) ? 'zh-Hant' : 'zh-Hans'));
  }
  const base = tag.split('-')[0];
  return supported.find(item => item.toLowerCase() === base)
    ?? supported.find(item => item.toLowerCase().startsWith(`${base}-`));
}

export function languageFromHash(hash, supported) {
  if (!hash.startsWith('#')) return undefined;
  try {
    // Older shared links still resolve, then normalize to the language code alone.
    const tag = decodeURIComponent(hash.slice(1)).replace(/^language-/i, '');
    if (!/^[a-z]{2,3}(?:[-_][a-z0-9]{2,8})*$/i.test(tag)) return undefined;
    return matchLanguage(tag, supported);
  } catch { return undefined; }
}

export function resolvePressLanguage({ hash = '', saved, preferred = [], supported }) {
  return languageFromHash(hash, supported)
    ?? matchLanguage(saved, supported)
    ?? preferred.map(value => matchLanguage(value, supported)).find(Boolean)
    ?? 'en';
}

export const materialLanguage = (tag, supported) => supported.includes(tag) ? tag : 'en';
