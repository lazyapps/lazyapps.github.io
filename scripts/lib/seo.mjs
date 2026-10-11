import { readdir, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, relative } from 'node:path';
import { fileURLToPath } from 'node:url';
import { parse } from 'parse5';
import config from '../../astro.config.mjs';

export const site = new URL(config.site).origin;
export const dist = fileURLToPath(new URL('../../dist/', import.meta.url));
const publicDir = fileURLToPath(new URL('../../public/', import.meta.url));

export const attr = (node, name) => node?.attrs?.find(attribute => attribute.name === name)?.value;
export const text = node => node.nodeName === '#text' ? node.value : (node.childNodes ?? []).map(text).join('');

function elements(node) {
  return [node, ...(node.childNodes ?? []).flatMap(elements)];
}

export async function readPages() {
  const pages = [];
  async function visit(directory) {
    for (const entry of await readdir(directory, { withFileTypes: true })) {
      const path = join(directory, entry.name);
      if (entry.isDirectory()) {
        await visit(path);
      } else if (entry.name.endsWith('.html') && !existsSync(join(publicDir, relative(dist, path)))) {
        const html = await readFile(path, 'utf8');
        const nodes = elements(parse(html));
        const links = nodes.filter(node => node.tagName === 'link');
        const metas = nodes.filter(node => node.tagName === 'meta');
        const refresh = metas.find(node => attr(node, 'http-equiv')?.toLowerCase() === 'refresh');
        pages.push({
          path,
          html,
          nodes,
          links,
          metas,
          url: new URL(relative(dist, path).replace(/index\.html$/, ''), `${site}/`).href,
          canonical: attr(links.find(node => attr(node, 'rel') === 'canonical') ?? {}, 'href'),
          alternates: links.filter(node => attr(node, 'rel') === 'alternate' && attr(node, 'hreflang')),
          language: attr(nodes.find(node => node.tagName === 'html'), 'lang'),
          redirectTo: attr(refresh, 'content')?.match(/url=(.+)$/i)?.[1],
          noindex: !!refresh || metas.some(node => /^(robots|googlebot)$/i.test(attr(node, 'name') ?? '') && /\bnoindex\b/i.test(attr(node, 'content') ?? '')),
        });
      }
    }
  }
  await visit(dist);
  return pages.sort((a, b) => a.url.localeCompare(b.url));
}

export const escapeXml = value => value.replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&apos;');
