export function mountSafariEdges() {
  const root = document.documentElement;
  const body = document.body;
  const properties = ['--edge-top-background', '--edge-bottom-background'];
  const previousStyles = properties.map(name => ({
    name,
    value: root.style.getPropertyValue(name),
    priority: root.style.getPropertyPriority(name),
  }));
  const edges = ['top', 'bottom'].map(edge => {
    const element = body.querySelector<HTMLDivElement>(`:scope > .edge-${edge}`)
      ?? document.createElement('div');
    element.className = `edge-${edge}`;
    element.setAttribute('aria-hidden', 'true');
    if (!element.isConnected) body.prepend(element);
    return element;
  });
  const metas = Array.from(document.querySelectorAll<HTMLMetaElement>('meta[name="theme-color"]'));
  const previousMeta = metas.map(element => ({ element, content: element.getAttribute('content') }));
  let createdMeta: HTMLMetaElement | undefined;
  if (!metas.length) {
    createdMeta = document.createElement('meta');
    createdMeta.name = 'theme-color';
    document.head.append(createdMeta);
    metas.push(createdMeta);
  }

  const motion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const viewport = window.visualViewport;
  let frame = 0;

  function update() {
    frame = 0;
    // The canvas is solid; cards and edge-faded artwork sit above it.
    const color = getComputedStyle(root).getPropertyValue('--page-background').trim();
    for (const name of properties) {
      if (root.style.getPropertyValue(name) !== color) root.style.setProperty(name, color);
    }
    for (const meta of metas) {
      if (meta.content !== color) meta.content = color;
    }
  }

  function schedule() {
    if (!frame) frame = requestAnimationFrame(update);
  }

  const observer = new MutationObserver(schedule);
  observer.observe(root, { attributes: true, attributeFilter: ['class', 'style'] });
  observer.observe(body, { attributes: true, attributeFilter: ['class', 'style'], childList: true });
  const layout = new ResizeObserver(schedule);
  layout.observe(body);
  window.addEventListener('scroll', schedule, { passive: true });
  window.addEventListener('resize', schedule);
  window.addEventListener('orientationchange', schedule);
  viewport?.addEventListener('resize', schedule);
  viewport?.addEventListener('scroll', schedule, { passive: true });
  motion.addEventListener('change', schedule);
  update();
  schedule();

  return () => {
    cancelAnimationFrame(frame);
    observer.disconnect();
    layout.disconnect();
    window.removeEventListener('scroll', schedule);
    window.removeEventListener('resize', schedule);
    window.removeEventListener('orientationchange', schedule);
    viewport?.removeEventListener('resize', schedule);
    viewport?.removeEventListener('scroll', schedule);
    motion.removeEventListener('change', schedule);
    for (const { name, value, priority } of previousStyles) {
      if (value) root.style.setProperty(name, value, priority);
      else root.style.removeProperty(name);
    }
    for (const { element, content } of previousMeta) {
      if (content === null) element.removeAttribute('content');
      else element.content = content;
    }
    createdMeta?.remove();
    for (const edge of edges) edge.remove();
  };
}
