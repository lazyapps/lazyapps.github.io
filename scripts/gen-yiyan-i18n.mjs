#!/usr/bin/env node
// Extracts every translated slot from the existing yi pages and emits an i18n module.
import { readFileSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = join(import.meta.dirname, '..');
const PAGES = process.env.YIYAN_PAGES ?? '/tmp/opencode/baseline/yiyan';
const PAGE_EXT = '.html';

function grab(html, re) {
  const m = html.match(re);
  if (!m) throw new Error('no match: ' + re);
  return m[1];
}

function grabAll(html, re) {
  return [...html.matchAll(re)].map((m) => m[1]);
}

const SLOTS = {
  htmlLang: (h) => grab(h, /<html lang="([^"]+)"/),
  htmlDir: (h) => (/<html lang="[^"]+" dir="([^"]+)"/.exec(h) || [])[1] || undefined,
  title: (h) => grab(h, /<title>([^<]*)<\/title>/),
  description: (h) => grab(h, /<meta name="description" content="([^"]+)">/),
  canonical: (h) => grab(h, /<link rel="canonical" href="([^"]+)">/),
  ogTitle: (h) => grab(h, /<meta property="og:title" content="([^"]+)">/),
  ogDesc: (h) => grab(h, /<meta property="og:description" content="([^"]+)">/),
  ogUrl: (h) => grab(h, /<meta property="og:url" content="([^"]+)">/),
  navAria: (h) => grab(h, /<nav class="mono topbar__nav" aria-label="([^"]+)">/),
  homeAria: (h) => grab(h, /class="topbar__home" aria-label="([^"]+)">/),
  appTitle: (h) => grab(h, /<h2 class="dsp"[^>]*>([\s\S]*?)<\/h2>/),
  appTitleAttrs: (h) => grab(h, /<h2 class="dsp"([^>]*)>/),
  loaderLogo: (h) => grab(h, /<span class="loader__logo-img"[^>]*>([^<]*)<\/span>/),
  localeNow: (h) => grab(h, /<span class="locale__now"[^>]*>([^<]*)<\/span>/),
  selectAria: (h) => grab(h, /<select data-locale-select aria-label="([^"]+)">/),
  selectedUrl: (h) => grab(h, /<option value="([^"]+)"[^>]*selected>/),
  h1: (h) => grab(h, /<h1 class="phero__h1 dsp">(.*?)<\/h1>/s),
  sub: (h) => grab(h, /<p class="phero__sub">(.*?)<\/p>/s),
};

function extractPair(sec) {
  const cells = [...sec.matchAll(/<div class="pair__cell[^"]*">([\s\S]*?)<\/div>/g)].map((m) => m[1]);
  const why = sec.match(/<div class="pair__why">([\s\S]*?)<\/div>/);
  const whyLabels = why ? grabAll(why[1], /<p class="mono">(.*?)<\/p>/g) : [];
  const whyLines = why ? grabAll(why[1], /<p class="line"[^>]*>([\s\S]*?)<\/p>/gs) : [];
  const cta = grabAll(cells[0], /<a data-hover href="([^"]+)">([\s\S]*?)<\/a>/g);
  const srcMono = cells[0].match(/<p class="mono">([\s\S]*?)<\/p>/);
  return {
    headA: grab(sec, /<h2 class="mono">(.*?)<\/h2>/),
    headB: grab(sec, /<p class="mono">(.*?)<\/p>/s),
    h2: grab(sec, /<h2 class="pair__h2 dsp">(.*?)<\/h2>/),
    cellSrc: cells[0],
    cellOut: cells[1],
    whyHtml: why ? why[1] : '',
    srcLabel: srcMono ? srcMono[1] : '',
    srcLine: grab(cells[0], /<p class="line"[^>]*>([\s\S]*?)<\/p>/s),
    outLabel: cells[1].match(/<p class="mono">([\s\S]*?)<\/p>/) ? grab(cells[1], /<p class="mono">([\s\S]*?)<\/p>/) : '',
    outLine: grab(cells[1], /<p class="line"[^>]*>([\s\S]*?)<\/p>/s),
    ctaUrl: cta[0] ? cta[0] : '',
    ctaHtml: cta[0] ? cta[1] : '',
    whyLabel: whyLabels[0] || '',
    why: whyLines[0] || '',
    reuseLabel: whyLabels[1] || '',
    reuse: why ? grabAll(why[1], /<code>(.*?)<\/code>/g) : [],
  };
}

function extract(html) {
  const out = {};
  for (const [k, fn] of Object.entries(SLOTS)) out[k] = fn(html);

  const firsts = grabAll(html, /<span class="button-023__text is--first">(.*?)<\/span>/g);
  out.cta = [firsts[0], firsts[1], firsts[2]];

  out.trust = grabAll(html, /<svg[^>]*>[\s\S]*?<\/svg>\s*([^<]+)<\/li>/g).map((t) => t.trim());
  out.cssTrust = /\.phero__trust li\{[^}]*text-transform:uppercase/.test(grab(html, /<style(?:\s[^>]*)?>([\s\S]*?)<\/style>/s))
    ? 'latin'
    : 'cjk';
  out.shotAltMain = grab(html, /<img src="\/i\/yiyan-showcase\.png" alt="([^"]+)">/);
  out.shotAltDetail = grab(html, /<img src="\/i\/yiyan-showcase-detail\.png" alt="([^"]+)">/);

  out.cards = [1, 2, 3, 4].map((n) => {
    const block = grab(html, new RegExp(`(<article class="card card--c${n}">[\\s\\S]*?<\\/article>)`));
    return {
      tag: grab(block, /<p class="card__tag"[^>]*>(.*?)<\/p>/),
      tagLang: /<p class="card__tag" lang="en">/.test(block),
      title: grab(block, /<h3 class="card__title dsp">(.*?)<\/h3>/),
      p: grab(block, /<p class="card__p">(.*?)<\/p>/),
    };
  });

  const pairs = [...html.matchAll(/<section class="pair wrap"[^>]*>([\s\S]*?)<\/section>/g)].map((m) => m[1]);
  out.pair = extractPair(pairs[0]);
  out.iphone = extractPair(pairs[1]);

  const bounds = grab(html, /<section class="bounds wrap"[^>]*>([\s\S]*?)<\/section>/);
  out.bounds = {
    headA: grab(bounds, /<h2 class="mono">(.*?)<\/h2>/),
    headB: grab(bounds, /<p class="mono">(.*?)<\/p>/s),
    h2: grab(bounds, /<h2 class="bounds__h2 dsp">(.*?)<\/h2>/),
    note: grab(bounds, /<p class="phero__sub bounds__note">(.*?)<\/p>/s),
    items: [...bounds.matchAll(/<p class="bounds__q">(.*?)<\/p>\s*<p class="bounds__a">([\s\S]*?)<\/p>/sg)]
      .map((m) => ({ q: m[1], a: m[2].replace(/\s+/g, ' ').trim() })),
  };

  out.next = {
    imgAlt: grab(html, /<img class="next__plate next__plate--icon" src="[^"]*" alt="([^"]*)">/),
    q: grab(html, /<h2 class="next__q dsp">(.*?)<\/h2>/),
  };

  const brew = grab(html, /<div class="brew"[^>]*>([\s\S]*?)<div class="base">/);
  out.brew = {
    h3: grab(brew, /<h3 class="dsp">(.*?)<\/h3>/s),
    label: grab(brew, /<div class="brew__head">[\s\S]*?<span>(.*?)<\/span>/),
    install: grab(brew, /<pre dir="ltr">([\s\S]*?)<\/pre>/s),
    p: grab(brew, /<p class="bounds__a">([\s\S]*?)<\/p>/s),
  };

  const foot = grab(html, /<div class="base">([\s\S]*?)<\/div>/);
  out.footer = [...foot.matchAll(/<a [^>]*>[\s\S]*?<\/a>/g)]
    .map((m) => m[0])
    .filter((link) => !link.includes('href="/privacy.zh.html"'));

  return out;
}

const DATA = {};
DATA[''] = extract(readFileSync(join(PAGES, `index${PAGE_EXT}`), 'utf8'));
for (const code of ['ar', 'de', 'en', 'es', 'fr', 'hi', 'ja', 'ko', 'pt-br', 'ru', 'zh-hant']) {
  DATA[code] = extract(readFileSync(join(PAGES, code, `index${PAGE_EXT}`), 'utf8'));
}

const bad = [];
for (const [code, d] of Object.entries(DATA)) {
  const c = [d.trust.length, d.cards.length, d.pair.reuse.length, d.bounds.items.length, d.footer.length].join(',');
  if (c !== '3,4,3,6,3') bad.push(`${code}: counts ${c}`);
}
if (bad.length) {
  console.error('STRUCTURE MISMATCH:', bad.join('\n'));
  process.exit(1);
}

const OPEN_CODE_REPLACEMENTS = [
  ['Pi、Claude Code 或 Codex', 'Pi、Claude Code、Codex 或 OpenCode'],
  ['Pi أو Claude Code أو Codex', 'Pi أو Claude Code أو Codex أو OpenCode'],
  ['Pi, Claude Code oder Codex', 'Pi, Claude Code, Codex oder OpenCode'],
  ['Pi, Claude Code or Codex', 'Pi, Claude Code, Codex or OpenCode'],
  ['Pi, Claude Code o Codex', 'Pi, Claude Code, Codex u OpenCode'],
  ['Pi, Claude Code ni Codex', 'Pi, Claude Code, Codex ni OpenCode'],
  ['Pi, Claude Code ou Codex', 'Pi, Claude Code, Codex ou OpenCode'],
  ['Pi, Claude Code या Codex', 'Pi, Claude Code, Codex या OpenCode'],
  ['Pi、Claude Code、Codex', 'Pi、Claude Code、Codex、OpenCode'],
  ['Pi, Claude Code, Codex', 'Pi, Claude Code, Codex, OpenCode'],
  ['no Pi, no Claude Code ou no Codex', 'no Pi, no Claude Code, no Codex ou no OpenCode'],
  ['do Pi, do Claude Code ou do Codex', 'do Pi, do Claude Code, do Codex ou do OpenCode'],
  ['Pi, Claude Code или Codex', 'Pi, Claude Code, Codex или OpenCode'],
  ['Pi · Claude Code · Codex', 'Pi · Claude Code · Codex · OpenCode'],
];

function addOpenCode(value) {
  if (value.includes('OpenCode')) return value;

  for (const [before, after] of OPEN_CODE_REPLACEMENTS) {
    if (value.includes(before)) return value.replaceAll(before, after);
  }

  return value;
}

const src = `// Generated by scripts/gen-yiyan-i18n.mjs — do not edit by hand.
export const YIYAN_LOCALES = ${JSON.stringify(stripBookMarks(DATA), null, 2)};
`;

function stripBookMarks(value) {
  if (typeof value === 'string') return addOpenCode(value.replace(/[《》]/g, ''));
  if (Array.isArray(value)) return value.map(stripBookMarks);
  if (value && typeof value === 'object') {
    return Object.fromEntries(Object.entries(value).map(([k, v]) => [k, stripBookMarks(v)]));
  }
  return value;
}
writeFileSync(join(ROOT, 'src/i18n/yiyan-locales.mjs'), src);
console.log('wrote src/i18n/yiyan-locales.mjs with', Object.keys(DATA).length, 'locales');
for (const [code, d] of Object.entries(DATA)) console.log(code || '(root)', '|', d.title.slice(0, 52));
