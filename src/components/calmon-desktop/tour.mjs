// The keys appear before their action; every action continues the same desktop.
export function createDesktopTour(model, compact = false) {
  const destinationDesktop = 2;
  model.focus('music-player');
  model.execute('close');
  model.focus('notes-week');
  if (compact) {
    model.execute('consume-left');
    return [
      { caption:21,keys:['⌘','⌘','.'],leaderAfter:true,run:()=>model.execute('consume-right') },
      { caption:5,keys:['→'],leaderAfter:true,run:()=>model.navigate(1) },
      { caption:22,keys:['←'],leaderAfter:true,run:()=>model.navigate(-1) },
      { caption:7,keys:['⌘','`'],leaderBefore:false,leaderAfter:false,run:()=>model.execute('cycle-stack') },
      { caption:20,keys:['⌘','⌘',','],leaderAfter:true,run:()=>model.execute('consume-left') },
      { caption:21,keys:['.'],leaderAfter:true,run:()=>model.execute('consume-right') },
      { caption:9,keys:['SPACE','P'],leaderAfter:true,run:()=>model.execute('pin') },
      { caption:10,keys:['→'],leaderAfter:true,run:()=>model.navigate(1) },
    ];
  }
  const jump = (id, caption = 6, dissolve = false) => ({
    caption, dissolve, labelJump: true,
    keys: () => ['⌘', '⌘', ...model.labels().find(x => x.type === 'window' && x.id === model.stack(id)?.id).key],
    leaderAfter: false, run: () => model.focus(id),
  });
  return [
    { caption:0, keys:['⌘','⌘','→'],leaderAfter:true,run:()=>model.navigate(1) },
    { caption:1, keys:['→'],leaderAfter:true,run:()=>model.navigate(1) },
    { caption:2, keys:['→'],leaderAfter:true,run:()=>model.navigate(1) },
    { caption:22,keys:['←'],leaderAfter:true,run:()=>model.navigate(-1) },
    { caption:23,keys:['←'],leaderAfter:true,run:()=>model.navigate(-1) },
    { caption:24,keys:['←'],leaderAfter:true,run:()=>model.navigate(-1) },
    jump('safari-home',3),
    { caption:4, keys:['⌘','⌘'],revealLabels:true,leaderAfter:true,run:()=>{} },
    { caption:5, keys:['→'],run:()=>model.navigate(1) },
    jump('finder-work'),
    jump('notes-week'),
    { caption:7, keys:['⌘','`'],leaderBefore:false,leaderAfter:false,run:()=>model.execute('cycle-stack') },
    { caption:20,keys:['⌘','⌘',','],leaderAfter:true,run:()=>model.execute('consume-left') },
    { caption:21,keys:['.'],leaderAfter:true,run:()=>model.execute('consume-right') },
    { caption:8, keys:['⌘','⌘','−'],leaderAfter:true,run:()=>model.execute('shrink') },
    { caption:9, keys:['⌘','⌘','SPACE','P'],leaderAfter:true,run:()=>model.execute('pin') },
    { caption:10,keys:['⌘','⌘','→'],leaderAfter:true,run:()=>model.navigate(1) },
    jump('mail-inbox'),
    { caption:11,keys:['⌘','⌘','SPACE','F'],leaderAfter:true,run:()=>model.execute('float') },
    { caption:12,keys:['⌘','⌘','SPACE','F'],leaderAfter:true,run:()=>model.execute('float') },
    jump('finder-work'),
    { caption:13,keys:['⌘','⌘','SPACE','A'],leaderAfter:true,run:()=>model.execute('add-pin') },
    jump('mail-inbox'),
    { caption:15,keys:()=>['⌘','⌘','⇧',String(destinationDesktop)],leaderAfter:true,run:()=>model.execute('send-desktop',destinationDesktop) },
    jump('terminal-dev'),
    { caption:16,dissolve:true,keys:['⌘','⌘','SPACE','S'],leaderAfter:true,run:()=>model.execute('full') },
    { caption:17,dissolve:true,keys:['⌘','⌘','1'],leaderAfter:true,run:()=>model.execute('leave-full') },
    jump('terminal-dev',18,true),
    { caption:19,dissolve:true,keys:['⌘','⌘','1'],leaderAfter:true,run:()=>model.execute('leave-full') },
  ];
}

// Commands continue in leader mode; label jumps after a command start a fresh demonstration.
export function keysForTourStep(step, leader, labels) {
  const keys = typeof step.keys === 'function' ? step.keys() : step.keys;
  if (leader && keys[0] === '⌘' && keys[1] === '⌘') {
    if (step.labelJump && !labels) return keys;
    if (keys.length > 2) return keys.slice(2);
  }
  return keys;
}
