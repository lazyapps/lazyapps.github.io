import { createMarkdownProcessor, rehypeHeadingIds } from '@astrojs/markdown-remark';
import { computerUseParts } from './computer-use.mjs';

function remarkComputerUse() {
  return (tree, file) => {
    const { locale } = file.data.astro.frontmatter;
    function walk(node) {
      if (!node.children || node.type === 'link' || node.type === 'linkReference') return;
      node.children = node.children.flatMap(child => {
        if (child.type !== 'text') {
          walk(child);
          return child;
        }
        return computerUseParts(child.value, locale).map(part => part.href
          ? { type: 'link', url: part.href, data: { hProperties: { className: 'term-link', lang: 'en', dir: 'ltr' } }, children: [{ type: 'text', value: part.text }] }
          : { type: 'text', value: part.text });
      });
    }
    walk(tree);
  };
}

function rehypePressDocument() {
  return (tree, file) => {
    const { base, prefix } = file.data.astro.frontmatter;
    rehypeHeadingIds()(tree, file);
    function walk(node) {
      if (node.type === 'element') {
        if (/^h[1-6]$/.test(node.tagName)) {
          node.tagName = `h${Math.min(6, Number(node.tagName[1]) + 2)}`;
          node.properties.id = `${prefix}-${node.properties.id}`;
        }
        for (const property of ['href', 'src']) {
          const value = node.properties[property];
          if (typeof value !== 'string') continue;
          if (value.startsWith('#')) node.properties[property] = `#${prefix}-${value.slice(1)}`;
          else if (!/^(?:[a-z][a-z\d+.-]*:|\/)/i.test(value)) {
            const url = new URL(value, `https://lazyapps.com${base}`);
            node.properties[property] = url.pathname + url.search + url.hash;
          }
        }
        if (node.tagName === 'a') node.properties.dir ??= 'auto';
        if (node.tagName === 'table') {
          node.children.forEach(walk);
          const table = { ...node };
          node.tagName = 'div';
          node.properties = { className: 'press-markdown__table', tabIndex: 0, role: 'region', ariaLabel: file.data.astro.frontmatter.tableLabel };
          node.children = [table];
          return;
        }
      }
      node.children?.forEach(walk);
    }
    walk(tree);
  };
}

const processor = createMarkdownProcessor({
  syntaxHighlight: false,
  smartypants: false,
  remarkRehype: { allowDangerousHtml: false },
  remarkPlugins: [remarkComputerUse],
  rehypePlugins: [rehypePressDocument],
});

export async function renderPressMarkdown(source, { base, prefix, locale, tableLabel }) {
  const { code } = await (await processor).render(source, { frontmatter: { base, prefix, locale, tableLabel } });
  return code;
}
