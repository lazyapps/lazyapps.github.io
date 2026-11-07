const observer = new IntersectionObserver(entries => {
  for (const entry of entries) if (entry.isIntersecting) {
    entry.target.classList.add('is-seen');
    observer.unobserve(entry.target);
  }
}, { threshold: .45 });
const observeArt = () => document.querySelectorAll('[data-yilo-art]').forEach(art => observer.observe(art));
if (document.documentElement.classList.contains('is-loaded')) observeArt();
else {
  const loader = new MutationObserver(() => {
    if (!document.documentElement.classList.contains('is-loaded')) return;
    loader.disconnect();
    observeArt();
  });
  loader.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
}
