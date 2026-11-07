export function initYiloDemo(root: HTMLElement) {
  const motion = matchMedia('(prefers-reduced-motion: reduce)');
  const portrait = matchMedia('(max-aspect-ratio: 3/4)');
  const lines: string[] = JSON.parse(root.dataset.input!);
  const get = <T extends SVGElement>(selector: string) => root.querySelector<T>(selector)!;
  const all = <T extends SVGElement>(selector: string) => [...root.querySelectorAll<T>(selector)];
  const svg = get<SVGSVGElement>('.yilo-demo__scene');
  const audio = root.querySelector<HTMLAudioElement>('[data-demo-audio]')!;
  const soundToggle = root.querySelector<HTMLButtonElement>('[data-action="sound"]')!;
  const input = get<SVGGElement>('[data-layer="input"]');
  const record = get<SVGImageElement>('[data-layer="learn"]');
  const conversation = get<SVGGElement>('[data-layer="conversation"]');
  const pelican = get<SVGGElement>('[data-pelican-layout]');
  const bubble = get<SVGGElement>('[data-conversation-bubble]');
  const people = all<SVGGElement>('[data-person-reveal]');
  const heads = all<SVGGElement>('[data-person-head]');
  const hands = all<SVGPathElement>('[data-person-hand]');
  const phrase = root.querySelector<HTMLElement>('[data-ending-phrase]')!;
  const outcome = root.querySelector<HTMLElement>('[data-ending-outcome]')!;
  const wheels = all<SVGGElement>('[data-wheel]');
  const thoughts = all<SVGCircleElement>('[data-thought]');
  const laptopLines = all<SVGPathElement>('[data-laptop-line]');
  const inputLines = [...root.querySelectorAll<HTMLElement>('[data-input-line]')];
  const carets = [...root.querySelectorAll<HTMLElement>('[data-typing-caret]')];
  const frontLeg = get<SVGPathElement>('[data-leg="front"]');
  const backLeg = get<SVGPathElement>('[data-leg="back"]');
  const frontFoot = get<SVGPathElement>('[data-foot="front"]');
  const backFoot = get<SVGPathElement>('[data-foot="back"]');
  const crank = get<SVGPathElement>('[data-crank]');
  const eye = get<SVGGElement>('[data-eye]');
  const compact = root.classList.contains('yilo-demo--compact');
  const heading = root.closest('.phero')?.querySelector('h1');
  const ratio = Number(root.dataset.recordRatio);
  let elapsed = 3200, visualTime = 3200, last = 0, animation = 0;
  let playing = !motion.matches, visible = false, sound = false, looped = false, stacked = false;
  let ready = !document.getElementById('loader');
  let renderedTime = -1, renderedVisual = -1;

  const smooth = (time: number, from: number, to: number) => {
    const x = Math.max(0, Math.min(1, (time-from)/(to-from)));
    return x*x*(3-2*x);
  };
  const attr = (element: Element, name: string, value: string | number) => {
    const next = String(value);
    if (element.getAttribute(name)!==next) element.setAttribute(name,next);
  };
  const opacity = (element: SVGElement, value: number) => attr(element,'opacity',value.toFixed(3));
  const leg = (pedal: number[]) => {
    const dx = pedal[0]-288, dy = pedal[1]-386, distance = Math.hypot(dx,dy);
    const along = (60*60-62*62+distance*distance)/(2*distance);
    const bend = Math.sqrt(60*60-along*along);
    return `M288 386L${288+along*dx/distance+bend*dy/distance} ${386+along*dy/distance-bend*dx/distance}L${pedal[0]} ${pedal[1]}`;
  };
  function render(force=false) {
    const time = Math.min(elapsed,12500);
    if (!force && time===renderedTime && visualTime===renderedVisual) return;
    renderedTime=time; renderedVisual=visualTime;
    const angle = visualTime/1400*Math.PI*2;
    const front = [335+27*Math.cos(angle),458+27*Math.sin(angle)];
    const back = [335-27*Math.cos(angle),458-27*Math.sin(angle)];
    attr(frontLeg,'d',leg(front)); attr(backLeg,'d',leg(back));
    attr(frontFoot,'transform',`translate(${front.join(' ')})`);
    attr(backFoot,'transform',`translate(${back.join(' ')})`);
    attr(crank,'d',`M${back.join(' ')}L${front.join(' ')}`);
    wheels.forEach(wheel => attr(wheel,'transform',`rotate(${visualTime/1400*540})`));
    const blink = Math.max(0,1-Math.abs((visualTime%5400)-2700)/100);
    attr(eye,'transform',`translate(320 250) scale(1 ${1-.9*blink})`);
    thoughts.forEach((dot,i) => opacity(dot,.35+.65*(.5+.5*Math.sin(visualTime/300-i*1.1))));
    laptopLines.forEach((line,i)=>opacity(line,.55+.45*(.5+.5*Math.sin(visualTime/400-i))));

    const ghost = looped && time<180 ? 1-smooth(time,0,180) : 0;
    const entering = looped ? smooth(time,170,360) : 1;
    const leaving = smooth(time,9250,9520);
    opacity(input,stacked ? entering*(1-leaving) : entering*(1-smooth(time,1900,2120)));
    attr(input,'transform',`translate(0 ${stacked?0:-8*smooth(time,1900,2120)})`);
    const readIn = smooth(time,2140,2580);
    const preview = stacked ? .65*(looped?smooth(time,180,440):1) : 0;
    opacity(record,Math.max(readIn,preview)*(1-leaving));
    attr(record,'transform',`translate(0 ${16*(1-readIn)-8*leaving})`);
    opacity(conversation,Math.max(ghost,smooth(time,9650,9750)));
    const endingTime = ghost>0?12500:time;
    people.forEach((person,i)=>{
      const progress=smooth(endingTime,9650+i*100,10050+i*100);
      opacity(person,progress);attr(person,'transform',`translate(0 ${12*(1-progress)})`);
    });
    opacity(bubble,smooth(endingTime,10060,10360));
    phrase.style.opacity=String(smooth(endingTime,10160,10460));
    outcome.style.opacity=String(smooth(endingTime,10260,10620));
    const nod = Math.sin(Math.PI*smooth(endingTime,10500,11700));
    attr(heads[0],'transform',`rotate(${3*nod} 63 174)`);
    attr(hands[1],'transform',`rotate(${-3*nod} 12 194)`);
    const recenter = ghost>0 ? 1 : looped&&time<600 ? 1-smooth(time,180,600) : smooth(time,9250,9800);
    attr(pelican,'transform',stacked?`translate(${100+130*recenter} -97.6) scale(.6)`:'translate(0 0)');

    let characters=Math.floor(Math.min(1,time/1600)*lines.join('').length);
    inputLines.forEach((line,i)=>{
      const next=lines[i].slice(0,Math.max(0,characters));
      if(line.textContent!==next)line.textContent=next;
      const active=characters>=0&&characters<lines[i].length;
      carets[i].style.opacity=String(active&&time%600<340?1:0);
      characters-=lines[i].length;
    });
    attr(root,'data-scene',time<2300?'input':time<9650?'learn':'conversation');
  }
  function fit() {
    stacked=!compact&&root.clientWidth<=680&&portrait.matches;
    root.dataset.layout=stacked?'stacked':'wide';
    attr(svg,'viewBox',stacked?'-48 -48 856 948':'-48 112 1376 704');
    root.style.setProperty('--demo-aspect',stacked?'856 / 948':'1376 / 704');
    attr(get('[data-road]'),'d',stacked?'M-2000 710H3000V900H-2000Z':'M-2000 621H3000V816H-2000Z');
    opacity(get('[data-small-road]'),stacked?.65:0);
    attr(record,'x',stacked?20:480);attr(record,'y',stacked?300:214);
    attr(record,'width',stacked?720:780);attr(record,'height',(stacked?720:780)*ratio);
    attr(get('[data-input-bubble]'),'d',stacked?'M410 58H740V225H704L687 245L683 225H410Z':'M480 254H1230V426H1169L1148 452L1142 426H480Z');
    const rtl=root.dir==='rtl';
    const label=get<SVGTextElement>('[data-input-label]');
    attr(label,'x',stacked?(rtl?718:432):(rtl?1202:508));attr(label,'y',stacked?99:292);
    label.style.fontSize=stacked?'24px':'28px';
    const inputText=get<SVGForeignObjectElement>('[data-input-text]');
    attr(inputText,'x',stacked?432:508);attr(inputText,'y',stacked?119:314);
    attr(inputText,'width',stacked?286:694);attr(inputText,'height',stacked?105:106);
    const inputCopy=root.querySelector<HTMLElement>('.input')!;
    inputCopy.style.fontSize=stacked?'28px':'38px';
    inputCopy.style.lineHeight=stacked?'1.2':'1.25';
    attr(get('[data-people-layout]'),'transform',stacked?'translate(-710 -41) scale(1.18)':'translate(0 0)');
    attr(get('[data-ending-bubble]'),'d',stacked?'M30 300H730V458H627L608 478L600 458H30Z':'M533 240H1189V403H1128L1107 433L1101 403H533Z');
    const text=get<SVGForeignObjectElement>('[data-ending-text]');
    attr(text,'x',stacked?54:555);attr(text,'y',stacked?316:263);
    attr(text,'width',stacked?652:612);attr(text,'height',stacked?145:140);
    if(heading){
      const section=root.closest('.phero')!;
      const styles=getComputedStyle(section);
      const available=innerHeight-heading.getBoundingClientRect().bottom-scrollY-parseFloat(styles.rowGap||'0')-parseFloat(styles.paddingBottom||'0');
      root.style.setProperty('--demo-max-height',`${Math.max(120,available)}px`);
    }
    const view=svg.viewBox.baseVal;
    const scale=Math.min(svg.clientWidth/view.width,svg.clientHeight/view.height);
    const inset=(svg.clientWidth-view.width*scale)/2+(view.x+view.width-(stacked?740:1260))*scale;
    root.style.setProperty('--demo-control-inset',`${Math.max(8,inset)}px`);
    render(true);
  }
  function tick(now: number) {
    if(last){
      const delta=Math.min(now-last,80), next=(elapsed+delta)%14000;
      visualTime+=Math.max(0,Math.min(delta,12500-elapsed));
      if(next<elapsed){visualTime+=next;looped=true;if(sound)audio.currentTime=0;}
      elapsed=next;
    }
    last=now;render();animation=requestAnimationFrame(tick);
  }
  function sync() {
    cancelAnimationFrame(animation);animation=0;last=0;
    const present=visible&&ready&&!document.hidden;
    if(playing&&present)animation=requestAnimationFrame(tick);
    if(present&&sound){if(playing)audio.currentTime=elapsed/1000;audio.play().catch(()=>{});}else audio.pause();
    root.dataset.playing=String(playing);
    render();
  }
  soundToggle.addEventListener('click',()=>{sound=!sound;root.dataset.sound=String(sound);soundToggle.setAttribute('aria-pressed',String(sound));sync();});
  root.querySelector<HTMLElement>('[data-controls]')!.hidden=false;
  new IntersectionObserver(([entry])=>{visible=entry.isIntersecting&&entry.intersectionRatio>=.2;sync();},{threshold:[0,.2]}).observe(root);
  new ResizeObserver(fit).observe(root);
  if(heading)new ResizeObserver(fit).observe(heading);
  window.addEventListener('resize',fit);
  portrait.addEventListener('change',fit);
  document.fonts.ready.then(fit);
  document.addEventListener('visibilitychange',sync);
  motion.addEventListener('change',()=>{playing=!motion.matches;if(motion.matches){elapsed=3200;looped=false;}sync();});
  if(!ready){
    const loader=new MutationObserver(()=>{if(!document.getElementById('loader')){ready=true;loader.disconnect();sync();}});
    loader.observe(document.body,{childList:true});
  }
  fit();sync();
}
