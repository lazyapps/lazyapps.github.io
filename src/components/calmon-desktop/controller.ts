import { Desktop } from './model.mjs';
import { windowContent } from './content.mjs';
import { createDesktopTour, keysForTourStep } from './tour.mjs';

export function initDesktop(root: HTMLElement) {
  const t = JSON.parse(root.dataset.copy!);
  const art = JSON.parse(root.dataset.art!);
  const language = root.dataset.language!;
  const model = new Desktop();
  const screen = root.querySelector<HTMLElement>('.pd-screen')!;
  const visual = root.querySelector<HTMLElement>('.pd-demo-visual')!;
  const windows = root.querySelector<HTMLElement>('.pd-windows')!;
  const tabs = root.querySelector<HTMLElement>('[data-desktop-tabs]')!;
  const caption = root.querySelector<HTMLElement>('[data-desktop-caption]')!;
  const cue = root.querySelector<HTMLElement>('.pd-input-cue')!;
  const reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const nodes = new Map<string, HTMLElement>();
  let windowMotionRevision = 0;
  let leader = false, labels = false;
  let frames = new Map<string, any>();
  let tourPlaying = !reduced.matches, tourStarted = false, tourIndex = -1, tourElapsed = 0;
  let visible = false, animation = 0, lastFrame = 0;
  let tourApplied = false, tourKeys: string[] = [];
  let tourLeaderActivated = false, tourUsesLeader = false, tourEntry = -1;
  let tourRestarting = false, restartRevision = 0;
  const escape = (text: unknown) => String(text).replace(/[&<>"']/g, x => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[x]!));
  const windowTitle = (w: any) => t.windowTitles?.[w.id] ?? w.title[language === 'zh-Hans' ? 0 : 1];
  const title = (id: string) => { const w = model.window(id); return w ? `${t.appNames[w.app]} — ${windowTitle(w)}` : ''; };
  const labelFor = (type: string, id: string) => model.labels().find(x => x.type === type && x.id === id)?.key ?? '';
  const appIcon = (app: string) => `<img src="${art[app]}" alt="" draggable="false">`;
  function renderWindow(id: string, frame: any) {
    const w = model.window(id), stack = model.stack(id);
    let node = nodes.get(id);
    if (!node) {
      node = document.createElement('article'); node.className = 'pd-window'; node.dataset.window = id;
      node.setAttribute('role', 'group'); node.setAttribute('aria-label', title(id));
      node.innerHTML = `<div class="pd-stack-pages"></div><div class="pd-titlebar" data-drag-window="${id}"><div class="pd-traffic">${['close','minimize','full'].map(action => `<button type="button" data-command="${action}" data-target="${id}" aria-label="${escape(action === 'full' ? t.full : t[action])}" title="${escape(action === 'full' ? t.full : t[action])}"></button>`).join('')}</div><span class="pd-titlebar-name">${escape(windowTitle(w))}</span></div><div class="pd-content">${windowContent(w.app, t, art)}</div>`;
      const viewport = document.createElement('div'); viewport.className = 'pd-window-viewport';
      viewport.append(node); windows.append(viewport); nodes.set(id, node);
    }
    const viewport = node.parentElement!;
    viewport.hidden = !frame;
    node.hidden = !frame;
    if (!frame) return;
    const { x, y, w: width, h: height, z } = frame;
    node.style.transform = `translate(${x}px,${y}px)`;
    node.style.width = `${width}px`; node.style.height = `${height}px`; node.style.zIndex = String(z);
    viewport.style.zIndex = String(z);
    // The stationary desktop viewport clips moving windows, including behind pinned columns.
    viewport.style.clipPath = frame.clip
      ? `inset(0 ${Math.max(0, screen.clientWidth - frame.clip.x - frame.clip.w - 2)}px 0 ${Math.max(0, frame.clip.x - 2)}px)`
      : '';
    node.classList.toggle('is-focused', id === model.focused);
    node.classList.toggle('has-stack', stack.members.length > 1);
    node.classList.toggle('is-pinned', !!frame.pinned);
    node.classList.toggle('is-floating', stack.mode === 'float');
    node.classList.toggle('is-full', stack.mode === 'full');
    node.dataset.mode = stack.mode; node.dataset.column = model.column(stack)?.id ?? '';
    const pages = node.querySelector<HTMLElement>('.pd-stack-pages')!;
    pages.innerHTML = stack.members.length > 1 ? stack.members.map((member, i) => `<button type="button" data-command="focus" data-value="${member}" aria-pressed="${member === id}" aria-label="${escape(title(member))}" title="${escape(title(member))}"></button>`).join('') : '';

  }
  function icon(stack: any) {
    return `<button type="button" class="pd-tab" data-command="focus" data-value="${stack.active}" data-stack="${stack.id}" data-minimized="${stack.mode === 'min'}" aria-label="${escape(title(stack.active))}" title="${escape(title(stack.active))}" aria-pressed="${stack.active === model.focused}">${appIcon(stack.app)}<span class="pd-label">${labelFor('window', stack.id)}</span></button>`;
  }
  function renderTabs() {
    const mark = (deck: string) => `<span><span>${deck.toUpperCase()}</span><span>DECK</span></span>`;
    const groupIcons = (number:number) => model.tiled(number).map(column=>{
      const members=column.stacks.map(id=>model.stack(id));
      if(number!==model.current||members.length===1)return members.map(icon).join('');
      return `<span class="pd-cell-tabs" style="--cells:${members.length}">${members.map((stack,i)=>icon(stack).replace('class="pd-tab"',`class="pd-tab pd-cell-tab" style="--cell:${i}"`)).join('')}</span>`;
    }).join('')+model.stacks.filter(s=>s.desktop===number&&s.mode==='min').map(icon).join('');
    const groups=model.desktops.map(number=>`<div class="pd-desktop-group ${number===model.current?'is-current':''}" data-desktop="${number}"><button type="button" class="pd-desktop-number" data-command="desktop" data-value="${number}" aria-label="${t.desktop} ${number}" aria-pressed="${number===model.current}"><span>${number}</span></button>${groupIcons(number)}</div>`).join('');

    const map = '<canvas width="108" height="64"></canvas>';
    const deck = (type: string, items: any[]) => items.length ? `<div class="pd-deck" data-deck="${type}"><button type="button" class="pd-deck-mark" data-menu="${type}" aria-label="${type === 'sky' ? 'Sky Deck' : 'Max Deck'}">${mark(type)}</button>${items.map(icon).join('')}</div>` : '';
    tabs.innerHTML = `<div class="pd-deck" data-deck="pin"><button type="button" class="pd-deck-mark" data-command="chooser" aria-label="Pin Deck" title="${t.chooseApp}">${mark('pin')}</button>${model.pins.map(app => `<button type="button" class="pd-pin-app" data-command="launch" data-value="${app}" data-pin-app="${app}" data-running="${model.runningApps.has(app)}" data-windows="${model.windows.some(w=>w.app===app)}" aria-label="${escape(t.appNames[app])} · Pin Deck" title="${escape(t.appNames[app])} · Pin Deck">${appIcon(app)}<span class="pd-label">${labelFor('app', app)}</span></button>`).join('')}</div>${deck('sky', model.stacks.filter(s => s.mode === 'float'))}${deck('max', model.stacks.filter(s => s.mode === 'full'))}<div class="pd-desktop-groups">${groups}</div><button type="button" class="pd-map" data-command="map" aria-label="${escape(t.map)}" title="${t.leader}">${map || '<span><i></i></span>'}</button>`;
  }
  function adaptTabs() {
    const width = screen.clientWidth, deckCount = model.pins.length + model.stacks.filter(s => s.mode === 'float' || s.mode === 'full').length;
    const deckSections = 1 + Number(model.stacks.some(s => s.mode === 'float')) + Number(model.stacks.some(s => s.mode === 'full'));
    const slots = model.desktops.length + model.columns.filter(c=>c.desktop===model.current).length + model.stacks.filter(s=>s.mode==='min'||s.mode==='tile'&&s.desktop!==model.current).length;
    const currentCount = model.tiled().length;
    const required = (size:number) => {
      const m=art.tabMetrics[String(size)];
      return deckSections*m.markWidth+deckCount*(m.deckItemWidth??m.itemWidth)+currentCount*m.currentSlotWidth+(slots-currentCount)*m.itemWidth+(model.desktops.length-1)*(m.groupGap??24)+(deckSections+1)*20+54;
    };
    let size=width>800?26:24;
    while(size>18&&required(size)>width-24)size-=2;
    const wrap=required(size)>width-24;
    if(wrap)size=24;
    const m=art.tabMetrics[String(size)];
    tabs.dataset.wrap=String(wrap);
    tabs.style.setProperty('--pd-tab-size',`${size}px`);
    tabs.style.setProperty('--pd-deck-size',`${size*.8}px`);
    tabs.style.setProperty('--pd-section-gap','20px');
    for(const [key,value] of Object.entries(m))tabs.style.setProperty(`--native-${key}`,`${value}${key==='lensScale'?'':'px'}`);
    const focused = tabs.querySelector<HTMLElement>('.pd-tab[aria-pressed=true]');
    const group = focused?.closest<HTMLElement>('.pd-desktop-group');
    if (focused && group && group.scrollWidth > group.clientWidth) group.scrollLeft = Math.max(0, focused.offsetLeft - group.clientWidth / 2);
  }
  function renderMap() {
    const canvas = tabs.querySelector<HTMLCanvasElement>('.pd-map canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d')!; ctx.scale(2, 2);
    const width = screen.clientWidth, height = screen.clientHeight - 40 - tabs.offsetHeight - 16;
    const scale = Math.min(22 / height, 40 / width), sw = width * scale, sh = height * scale;
    const box = {x:(54-sw)/2,y:28-sh,w:sw,h:sh};
    if (leader) { ctx.fillStyle='#000';ctx.fillRect(0,1,54,31); }
    ctx.shadowColor='#000c';ctx.shadowOffsetX=.5;ctx.shadowOffsetY=.5;ctx.lineWidth=1;
    const left = new Map<number,number>(), right = new Map<number,number>();
    for (const [id, frame] of frames) {
      if (frame.floating || model.stack(id)?.mode !== 'tile') continue;
      let x=box.x+frame.x*scale,y=box.y+(frame.y-40)*scale,w=Math.max(1,frame.w*scale-1),h=Math.max(1,frame.h*scale-1);
      const outside=x+w<=box.x||x>=box.x+box.w;
      if (x+w<=box.x) {if(!left.has(frame.x))left.set(frame.x,left.size);x=box.x-2-(left.get(frame.x)!%6)*2;w=1;}
      else if(x>=box.x+box.w){if(!right.has(frame.x))right.set(frame.x,right.size);x=box.x+box.w+1+(right.get(frame.x)!%6)*2;w=1;}
      else { const end=Math.min(x+w,box.x+box.w-1);x=Math.max(x,box.x+1);w=Math.max(.5,end-x); }
      ctx.globalAlpha=outside?.4:.85;
      if(id===model.focused&&!outside){ctx.fillStyle=model.accent;ctx.fillRect(x,y,w,h);}else{ctx.strokeStyle='#fff';ctx.strokeRect(x+.5,y+.5,w,h);}
    }
    ctx.globalAlpha=1;ctx.strokeStyle='#fff';ctx.beginPath();ctx.roundRect(box.x-.5,box.y-1,box.w+1,box.h+1,2);ctx.stroke();
    ctx.fillStyle='#fff';ctx.fillRect(26,28,2,1.5);ctx.fillRect(23.5,29.5,7,1);
  }
  function followWindowMotion() {
    const revision = ++windowMotionRevision;
    const animations = [...nodes.values()].flatMap(node => node.getAnimations());
    screen.dataset.moving = String(animations.length > 0);
    if (animations.length) void Promise.allSettled(animations.map(animation => animation.finished)).then(() => {
      if (revision === windowMotionRevision) screen.dataset.moving = 'false';
    });
  }
  function render() {
    root.style.setProperty('--pd-accent', model.accent);
    root.dataset.currentDesktop = String(model.current); root.dataset.focusedWindow = model.focused ?? '';
    root.dataset.tourPlaying = String(tourPlaying); root.dataset.demoStep = String(tourIndex); root.dataset.tourRestarting = String(tourRestarting); root.dataset.tourRevision = String(restartRevision);
    root.dataset.full = String(!!model.fullSpace);
    screen.dataset.leader = String(leader); screen.dataset.labels = String(leader && labels); screen.dataset.full = String(!!model.fullSpace);
    renderTabs(); adaptTabs();
    frames = model.layout(screen.clientWidth, screen.clientHeight, tabs.offsetHeight + 16);
    for (const w of model.windows) renderWindow(w.id, frames.get(w.id));
    for (const [id, node] of nodes) if (!model.window(id)) { node.parentElement!.remove(); nodes.delete(id); }
    root.querySelector<HTMLElement>('[data-menu-app]')!.textContent = t.appNames[model.window()?.app] ?? t.appNames.finder;
    renderMap();
    const mode=cue.querySelector<HTMLElement>('[data-demo-mode]');
    if(mode){
      const state=leader?'active':tourUsesLeader?(tourApplied?'exited':'enter'):'shortcut';
      mode.dataset.state=state;
      mode.textContent=state==='active'?t.modeActive:state==='enter'?t.modeEnter:state==='exited'?t.modeExited:t.nativeShortcut;
    }
    cue.querySelectorAll<HTMLElement>('[data-trigger]').forEach(key=>key.classList.toggle('is-current',leader));
    const playLabel = tourPlaying ? t.pause : tourStarted ? t.play : t.start;
    root.querySelector<HTMLElement>('[data-tour-text]')!.textContent = playLabel;
    root.querySelector<HTMLElement>('[data-tour-glyph]')!.textContent = tourPlaying ? 'Ⅱ' : '▶';
    const toggle = root.querySelector<HTMLButtonElement>('[data-tour="toggle"]')!;
    toggle.setAttribute('aria-label', playLabel); toggle.title = playLabel;
    caption.setAttribute('aria-live', tourPlaying ? 'off' : 'polite');
    followWindowMotion();
  }
  function reset() {
    model.reset(); nodes.forEach(node => node.parentElement!.remove()); nodes.clear(); leader = false; labels = false;
    caption.textContent = t.ready; render();
  }
  let presentationVersion = 0;
  let pendingPresentation: (() => void) | null = null;
  let presentationAnimations: Animation[] = [];
  function finishPresentation() {
    presentationVersion++;
    const pending = pendingPresentation;
    pendingPresentation = null;
    if (pending) {
      root.dataset.resetting = 'true';
      pending();
      void screen.offsetWidth;
      delete root.dataset.resetting;
    }
    presentationAnimations.forEach(animation => animation.cancel());
    presentationAnimations = [];
  }
  async function dissolve(change: () => void) {
    finishPresentation();
    if (reduced.matches) { change(); return; }
    const version = presentationVersion;
    pendingPresentation = change;
    const targets = [screen, caption.parentElement!];
    presentationAnimations = targets.map(target => target.animate([{opacity:1}, {opacity:0}],
      {duration:160, easing:'ease-in-out', fill:'forwards'}));
    try { await Promise.all(presentationAnimations.map(animation => animation.finished)); }
    catch { return; }
    if (version !== presentationVersion) return;
    pendingPresentation = null;
    root.dataset.resetting = 'true';
    change();
    void screen.offsetWidth;
    delete root.dataset.resetting;
    const outgoing = presentationAnimations;
    presentationAnimations = targets.map(target => target.animate([{opacity:0}, {opacity:1}],
      {duration:240, easing:'cubic-bezier(.22,1,.36,1)', fill:'both'}));
    outgoing.forEach(animation => animation.cancel());
    try { await Promise.all(presentationAnimations.map(animation => animation.finished)); }
    catch { return; }
    if (version === presentationVersion) finishPresentation();
  }
  let tour = createDesktopTour(model);
  function prepareTourStep() {
    const step=tour[tourIndex];
    tourApplied=false;tourElapsed=0;tourStarted=true;tourLeaderActivated=false;
    step.prepare?.();
    if(step.leaderBefore!==undefined){leader=step.leaderBefore;labels=leader;}
    if(step.labelJump&&leader&&!labels){leader=false;labels=false;}
    tourKeys=keysForTourStep(step,leader,labels);
    tourEntry=tourKeys.findIndex((key,i)=>key==='⌘'&&tourKeys[i+1]==='⌘');
    tourUsesLeader=tourEntry>=0||leader;
    caption.textContent=t.tour[step.caption];
    cue.hidden=false;
    const triggerOffset=tourUsesLeader&&tourEntry<0?2:0;
    const displayKeys=triggerOffset?['⌘','⌘',...tourKeys]:tourKeys;
    cue.innerHTML=`<span class="pd-mode-status" data-demo-mode></span><span class="pd-cue-keys" aria-hidden="true">`+displayKeys.map((key,i)=>{
      const trigger=tourUsesLeader&&i<2;
      const separator=tourUsesLeader&&i===2?`<span class="pd-cue-next">${t.thenKey}</span>`:'';
      return `${separator}<kbd data-key-index="${i-triggerOffset}" ${trigger?'data-trigger':''}>${escape(key==='SPACE'?t.spaceKey:key)}</kbd>`;
    }).join('')+'</span>';
    render();
  }
  function tourTick(now: number) {
    animation=0;
    if(lastFrame)tourElapsed+=Math.min(now-lastFrame,100);lastFrame=now;
    if(tourIndex<0){tourIndex=0;prepareTourStep();}
    const step=tour[tourIndex],cause=Math.max(1800,tourKeys.length*450);
    const doubleCommand=tourEntry>=0;
    if(doubleCommand&&!tourLeaderActivated&&tourElapsed>=320){tourLeaderActivated=true;leader=true;labels=true;render();}
    const keyStarts=tourKeys.map((_,i)=>{
      if(doubleCommand&&i<2)return i*180;
      return i===tourKeys.length-1?cause-100:doubleCommand?650+(i-2)*350:i*350;
    });
    const currentKey=Math.max(0,keyStarts.findLastIndex(start=>tourElapsed>=start));
    cue.querySelectorAll<HTMLElement>('kbd').forEach(key=>{
      const i=Number(key.dataset.keyIndex);
      if(key.hasAttribute('data-trigger')){
        key.classList.toggle('is-current',leader||!tourLeaderActivated&&i===currentKey);
        key.classList.toggle('is-pressed',!tourLeaderActivated&&i>=0&&tourElapsed>=keyStarts[i]&&tourElapsed<keyStarts[i]+120);
        return;
      }
      const held=(tourKeys[i]==='⇧'||!doubleCommand&&['⌘','⌃','⌥'].includes(tourKeys[i]))&&tourElapsed>=keyStarts[i];
      key.classList.toggle('is-current',i===currentKey||held);
      key.classList.toggle('is-pressed',!tourApplied&&tourElapsed>=keyStarts[i]&&(tourElapsed<keyStarts[i]+120||held));
    });
    if(!tourApplied&&tourElapsed>=cause){
      tourApplied=true;
      const apply = () => {
        step.run();model.clean();
        if(step.leaderAfter!==undefined){leader=step.leaderAfter;labels=leader&&step.revealLabels===true;}
        else if(tourKeys.length&&leader)labels=false;
        render();
      };
      if(step.dissolve)void dissolve(apply);else apply();
    }
    if(tourElapsed>=cause+2600){
      tourIndex++;
      if(tourIndex>=tour.length){restartTour();return;}
      prepareTourStep();
    }
    animation=requestAnimationFrame(tourTick);
  }
  function syncTour() {
    cancelAnimationFrame(animation);animation=0;lastFrame=0;
    if(tourPlaying&&!tourRestarting&&visible&&!document.hidden)animation=requestAnimationFrame(tourTick);
    render();
  }
  function restartTour() {
    const revision=++restartRevision;
    tourRestarting=true;
    cancelAnimationFrame(animation);animation=0;lastFrame=0;render();
    void dissolve(()=>{
      reset();tour=createDesktopTour(model);tourIndex=0;prepareTourStep();
    }).then(()=>{
      if(revision!==restartRevision)return;
      tourRestarting=false;syncTour();
    });
  }
  root.querySelectorAll<HTMLButtonElement>('[data-tour]').forEach(button => {
    button.addEventListener('click', () => {
      finishPresentation();
      if (button.dataset.tour === 'replay') {
        tourStarted = true; tourPlaying = true; restartTour();
      } else {
        tourPlaying = !tourPlaying; tourStarted = true; syncTour();
      }
    });
  });
  const fitDesktop = () => {
    screen.style.setProperty('--pd-scale', String(visual.clientWidth / screen.clientWidth));
  };
  fitDesktop();
  new ResizeObserver(fitDesktop).observe(visual);
  new IntersectionObserver(entries => {
    visible = entries[0].isIntersecting && entries[0].intersectionRatio >= .35;
    syncTour();
  }, { threshold: [0, .35] }).observe(visual);
  document.addEventListener('visibilitychange', syncTour);
  reduced.addEventListener('change', () => { if (reduced.matches) { finishPresentation(); tourPlaying = false; syncTour(); } });
  render();
}
