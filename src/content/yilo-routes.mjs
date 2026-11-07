// Explicit inventory of published product URLs, including localized pages.
export const yiloLegacyRoutes = Object.fromEntries([
  '', 'en', 'zh-hant', 'es', 'pt-br', 'fr', 'de', 'ja', 'ko', 'ru', 'ar', 'hi', 'presskit',
].map(path => [path ? `/yiyan/${path}` : '/yiyan', path === 'en' ? '/yilo/' : `/yilo/${path || 'zh-hans'}/`]));

export const yiloRedirects = { ...yiloLegacyRoutes, '/yilo/en': '/yilo/' };
