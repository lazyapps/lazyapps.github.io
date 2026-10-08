// Capture the FondFont scene canvas with headless Chrome (works while no browser window is visible).
// node scripts/capture-fondfont-scene.mjs <outdir> <width> <height> <name=url>...
// macOS only: drives /Applications/Google Chrome.app over the DevTools protocol on port 9333.
// A job URL of "same" re-captures the current page three seconds later (live motion).
// Use ?scenePoster for the preserved-buffer canvas read; names starting with "ss-" take a page screenshot.
import {spawn} from 'node:child_process';
import {writeFileSync,mkdtempSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
const [out,width,height,...jobs]=process.argv.slice(2);
import {existsSync} from 'node:fs';
const CHROME='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
if(!existsSync(CHROME)){console.error(`Google Chrome not found at ${CHROME}`);process.exit(1);}
const profile=mkdtempSync(join(tmpdir(),'fondfont-chrome-'));
const chrome=spawn(CHROME,['--headless=new','--remote-debugging-port=9333',`--user-data-dir=${profile}`,'--force-device-scale-factor=2',`--window-size=${width},${height}`,'--hide-scrollbars','about:blank'],{stdio:'ignore'});
const sleep=ms=>new Promise(r=>setTimeout(r,ms));
let tabs;for(let i=0;i<50;i++){try{tabs=await (await fetch('http://127.0.0.1:9333/json')).json();if(tabs.length)break;}catch{}await sleep(200);}
if(!tabs?.length){console.error('Chrome DevTools endpoint did not start');chrome.kill();process.exit(1);}
const page=tabs.find(t=>t.type==='page');const ws=new WebSocket(page.webSocketDebuggerUrl);await new Promise(r=>ws.onopen=r);
let id=0;const pending=new Map();ws.onmessage=e=>{const m=JSON.parse(e.data);if(m.id&&pending.has(m.id)){pending.get(m.id)(m);pending.delete(m.id);}};
const send=(method,params={})=>new Promise(r=>{const i=++id;pending.set(i,r);ws.send(JSON.stringify({id:i,method,params}));});
await send('Emulation.setDeviceMetricsOverride',{width:+width,height:+height,deviceScaleFactor:2,mobile:+width<600});
for(const job of jobs){
  const [name,url]=job.split('=',2).length===2?[job.slice(0,job.indexOf('=')),job.slice(job.indexOf('=')+1)]:[job,job];
  if(url==='same')await sleep(3000);else{await send('Page.navigate',{url});await sleep(9000);}
  if(name.startsWith('ss-')){const shot=await send('Page.captureScreenshot',{format:'png'});writeFileSync(`${out}/${name}.png`,Buffer.from(shot.result.data,'base64'));console.log(name,'screenshot');continue;}
  const r=await send('Runtime.evaluate',{expression:`(()=>{const h=document.querySelector('[data-fondfont-scene]');const c=h.querySelector('canvas');return JSON.stringify({d:c.toDataURL('image/png'),w:c.width,h:c.height,frame:h.dataset.sceneFrame,ready:h.className})})()`,returnByValue:true});
  const v=JSON.parse(r.result.result.value);writeFileSync(`${out}/${name}.png`,Buffer.from(v.d.split(',')[1],'base64'));
  console.log(name,v.w,v.h,v.ready,v.frame);
}
ws.close();chrome.kill();
