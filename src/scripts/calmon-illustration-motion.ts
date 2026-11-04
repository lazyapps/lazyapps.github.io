export function observeIllustrationMotion(selector: string) {
  const arts = [...document.querySelectorAll(selector)];
  const visible = new Set<Element>();
  const loader = document.getElementById('loader');
  let ready = !loader;
  const syncMotion = () => {
    for (const art of arts) {
      art.classList.toggle('is-active', ready && !document.hidden && visible.has(art));
    }
  };
  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting && entry.intersectionRatio >= .75) visible.add(entry.target);
      else visible.delete(entry.target);
    }
    syncMotion();
  }, { threshold: .75 });
  arts.forEach(art => observer.observe(art));
  document.addEventListener('visibilitychange', syncMotion);
  if (loader) {
    const waitForLoader = new MutationObserver(() => {
      if (loader.isConnected && getComputedStyle(loader).display !== 'none') return;
      ready = true;
      waitForLoader.disconnect();
      syncMotion();
    });
    waitForLoader.observe(loader, { attributes: true, attributeFilter: ['style'] });
    waitForLoader.observe(document.body, { childList: true });
    if (getComputedStyle(loader).display === 'none') {
      ready = true;
      waitForLoader.disconnect();
    }
  }
}
