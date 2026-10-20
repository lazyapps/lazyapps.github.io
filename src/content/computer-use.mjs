export const COMPUTER_USE_REFERENCE = 'https://developers.openai.com/api/docs/guides/tools-computer-use';

export function computerUseParts(text, locale = 'en') {
  const href = locale.startsWith('zh')
    ? 'https://openai.com/zh-Hans-CN/index/codex-for-almost-everything/'
    : COMPUTER_USE_REFERENCE;
  return text.split(/(computer use)/gi).map(text => ({
    text,
    href: /^computer use$/i.test(text) ? href : undefined,
  }));
}
