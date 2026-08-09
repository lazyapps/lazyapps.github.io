const HAS_GSAP = typeof gsap !== 'undefined'
  && typeof window.ScrollTrigger !== 'undefined'
  && typeof window.CustomEase !== 'undefined';

if (HAS_GSAP) {
  gsap.registerPlugin(CustomEase);
  CustomEase.create("pop", "0.17, 0.67, 0.3, 1.33");

  gsap.registerPlugin(ScrollTrigger);
}

function initContentRevealScroll(){
  const prefersReduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  const ctx = gsap.context(() => {

    document.querySelectorAll('[data-reveal-group]').forEach(groupEl => {
      const groupStaggerSec = (parseFloat(groupEl.getAttribute('data-stagger')) || 100) / 1000;
      const groupDistance = groupEl.getAttribute('data-distance') || '2em';
      const triggerStart = groupEl.getAttribute('data-start') || 'top 80%';

      const animDuration = 0.8;
      const animEase = "pop";

      if (prefersReduced) {
        gsap.set(groupEl, { clearProps: 'all', y: 0, autoAlpha: 1 });
        return;
      }

      const directChildren = Array.from(groupEl.children).filter(el => el.nodeType === 1);
      if (!directChildren.length) {
        gsap.set(groupEl, { y: groupDistance, autoAlpha: 0 });
        ScrollTrigger.create({
          trigger: groupEl,
          start: triggerStart,
          once: true,
          onEnter: () => gsap.to(groupEl, {
            y: 0,
            autoAlpha: 1,
            duration: animDuration,
            ease: animEase,
            onComplete: () => gsap.set(groupEl, { clearProps: 'all' })
          })
        });
        return;
      }

      const slots = [];
      directChildren.forEach(child => {
        const nestedGroup = child.matches('[data-reveal-group-nested]')
          ? child
          : child.querySelector(':scope [data-reveal-group-nested]');

        if (nestedGroup) {
          const includeParent =
            child.getAttribute('data-ignore') !== 'true' &&
            (
              child.getAttribute('data-ignore') === 'false' ||
              nestedGroup.getAttribute('data-ignore') === 'false'
            );

          const nestedChildren = Array.from(nestedGroup.children).filter(
            el => el.nodeType === 1 && el.getAttribute('data-ignore') !== 'true'
          );

          slots.push({
            type: 'nested',
            parentEl: child,
            nestedEl: nestedGroup,
            includeParent,
            nestedChildren
          });
        } else {
          if (child.getAttribute('data-ignore') === 'true') return;
          slots.push({ type: 'item', el: child });
        }
      });

      slots.forEach(slot => {
        if (slot.type === 'item') {
          const isNestedSelf = slot.el.matches('[data-reveal-group-nested]');
          const d = isNestedSelf ? groupDistance : (slot.el.getAttribute('data-distance') || groupDistance);
          gsap.set(slot.el, { y: d, autoAlpha: 0 });
        } else {
          if (slot.includeParent) gsap.set(slot.parentEl, { y: groupDistance, autoAlpha: 0 });
          const nestedD = slot.nestedEl.getAttribute('data-distance') || groupDistance;
          slot.nestedChildren.forEach(target => gsap.set(target, { y: nestedD, autoAlpha: 0 }));
        }
      });

      slots.forEach(slot => {
        if (slot.type === 'nested' && slot.includeParent) {
          gsap.set(slot.parentEl, { y: groupDistance });
        }
      });

      ScrollTrigger.create({
        trigger: groupEl,
        start: triggerStart,
        once: true,
        onEnter: () => {
          const tl = gsap.timeline();

          slots.forEach((slot, slotIndex) => {
            const slotTime = slotIndex * groupStaggerSec;

            if (slot.type === 'item') {
              tl.to(slot.el, {
                y: 0,
                autoAlpha: 1,
                duration: animDuration,
                ease: animEase,
                onComplete: () => gsap.set(slot.el, { clearProps: 'all' })
              }, slotTime);
            } else {
              if (slot.includeParent) {
                tl.to(slot.parentEl, {
                  y: 0,
                  autoAlpha: 1,
                  duration: animDuration,
                  ease: animEase,
                  onComplete: () => gsap.set(slot.parentEl, { clearProps: 'all' })
                }, slotTime);
              }
              const nestedMs = parseFloat(slot.nestedEl.getAttribute('data-stagger'));
              const nestedStaggerSec = isNaN(nestedMs) ? groupStaggerSec : nestedMs / 1000;
              slot.nestedChildren.forEach((nestedChild, nestedIndex) => {
                tl.to(nestedChild, {
                  y: 0,
                  autoAlpha: 1,
                  duration: animDuration,
                  ease: animEase,
                  onComplete: () => gsap.set(nestedChild, { clearProps: 'all' })
                }, slotTime + nestedIndex * nestedStaggerSec);
              });
            }
          });
        }
      });
    });

  });

  return () => ctx.revert();
}



function warmUpRevealMachinery(){
  const warm = document.createElement('div');
  warm.style.cssText = 'position:fixed;top:-9999px;left:-9999px;width:1px;height:1px;pointer-events:none';
  document.body.appendChild(warm);
  const ctx = gsap.context(() => {
    gsap.set(warm, { y: '2em', autoAlpha: 0 });
    ScrollTrigger.create({ trigger: warm, start: 'top 80%', once: true, onEnter: () => {} });
    gsap.to(warm, { y: 0, autoAlpha: 1, duration: 0.01, ease: 'pop' });
  });
  ScrollTrigger.refresh();
  ctx.revert();
  warm.remove();
}

function beginPageTheme(){
  document.documentElement.classList.add('is-page-theme');
  restorePageThemeColor();
}

function restorePageThemeColor(){
  document.querySelectorAll('meta[name="theme-color"][data-page-color]').forEach((meta) => {
    meta.setAttribute('content', meta.dataset.pageColor);
  });
}

function handoffToContent(){
  beginPageTheme();
  initContentRevealScroll();
  document.documentElement.classList.add('is-loaded');
}

document.addEventListener("DOMContentLoaded", () => {
  const loader = document.getElementById('loader');

  if (!HAS_GSAP || typeof window.SplitText === 'undefined') {
    beginPageTheme();
    document.documentElement.classList.add('is-loaded');
    if (loader) loader.remove();
    return;
  }

  warmUpRevealMachinery();

  if (!loader) { handoffToContent(); return; }

  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    loader.remove();
    handoffToContent();
    return;
  }

  gsap.delayedCall(2.3, beginPageTheme);
  gsap.delayedCall(2.85, handoffToContent);
  gsap.delayedCall(3.6, () => loader.remove());
});
