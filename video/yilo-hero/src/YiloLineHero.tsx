import React from 'react';
import {AbsoluteFill, Easing, Freeze, Img, interpolate, Loop, OffthreadVideo, staticFile, useCurrentFrame} from 'remotion';
import copy from '../../../src/i18n/yilo-hero-copy.json';
import examples from '../../../src/i18n/yilo-examples.json';
import plate from '../public/pedaling-plate.json';
import nativeRecords from '../../../scripts/assets/yilo/hero-native-source.json';
import timing from './timing.json';
import artCopy from '../../../src/i18n/yilo-art-copy.json';

const C={paper:'#f6f2e7',ink:'#333d51',teal:'#70a59e',blue:'#5c6995',green:'#84995c',coral:'#b76450',muted:'#70766b'};
const ease=Easing.bezier(.22,1,.36,1);
const font='"PingFang SC", "Hiragino Sans", "Noto Sans", Arial, sans-serif';
const smooth=(f:number,a:number,b:number)=>interpolate(f,[a,b],[0,1],{extrapolateLeft:'clamp',extrapolateRight:'clamp',easing:ease});

function Definitions(){return <defs>
 {Object.entries({teal:C.teal,blue:C.blue,green:C.green,coral:C.coral}).map(([name,color])=><pattern key={name} id={name} width="8" height="8" patternUnits="userSpaceOnUse" patternTransform={`rotate(${name==='green'?0:name==='coral'?35:-42})`}><path d="M0 2H8" stroke={color} strokeWidth="1.5" fill="none"/></pattern>)}
 <pattern id="cross" width="13" height="13" patternUnits="userSpaceOnUse"><path d="M-3 13L13-3M0 16L16 0M-3 0L13 16M0-3L16 13" stroke={C.teal} strokeWidth="1" fill="none" opacity=".65"/></pattern>
 </defs>}

function Wheel({x,y,angle}:{x:number;y:number;angle:number}){return <g transform={`translate(${x} ${y})`}>
 <circle r="66" fill={C.paper} stroke={C.blue} strokeWidth="2.4"/>
 <circle r="59" fill="url(#blue)" opacity=".2"/>
 <g transform={`rotate(${angle})`}>{Array.from({length:12},(_,i)=><path key={i} d={`M0 0L${63*Math.cos(i*Math.PI/6)} ${63*Math.sin(i*Math.PI/6)}`} stroke={C.blue} strokeWidth="1.05"/>)}</g><circle r="5" fill={C.coral}/>
 </g>}

function PedalHelper({frame}:{frame:number}){
 const a=frame/32*Math.PI*2;
 const hip=[288,386];
 const knee=(pedal:number[])=>{
  const dx=pedal[0]-hip[0],dy=pedal[1]-hip[1],d=Math.hypot(dx,dy);
  const upper=60,lower=62,along=(upper*upper-lower*lower+d*d)/(2*d);
  const bend=Math.sqrt(upper*upper-along*along);
  return [hip[0]+along*dx/d+bend*dy/d,hip[1]+along*dy/d-bend*dx/d];
 };
 const foot=[335+27*Math.cos(a),458+27*Math.sin(a)];
 const back=[335-27*Math.cos(a),458-27*Math.sin(a)];
 const frontKnee=knee(foot),backKnee=knee(back);
 return <g transform="translate(-70 75)">
  <path d="M148 556H480L455 536H170Z" fill="url(#green)"/>
  <Wheel x={220} y={480} angle={frame*7.5}/><Wheel x={418} y={480} angle={frame*7.5}/>
  <path d="M220 480L288 389L335 458L220 480M288 389L385 377L335 458M385 377L418 480M379 359L401 352M269 384H305" stroke={C.blue} strokeWidth="3" fill="none" strokeLinejoin="round"/>
  <path d={`M${hip[0]} ${hip[1]}L${backKnee[0]} ${backKnee[1]}L${back[0]} ${back[1]}`} stroke={C.teal} strokeWidth="6" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
  <path d="M250 367L221 349L238 383L265 392Z" fill="url(#blue)" stroke={C.blue} strokeWidth="1.8"/>
  <path d="M270 310C245 315 239 344 252 370C261 390 291 401 314 389C334 379 337 351 324 328C315 314 296 307 270 310Z" fill={C.paper} stroke={C.blue} strokeWidth="2.2"/>
  <path d="M256 335C264 350 281 371 310 378L316 368C296 360 282 342 276 324Z" fill="url(#teal)"/>
  <path d="M306 337Q326 361 347 369L387 359L388 365L347 378Q319 370 298 349" fill="url(#teal)" stroke={C.blue} strokeWidth="2" strokeLinejoin="round"/>
  <path d="M307 330C310 310 292 293 290 272C287 249 302 232 320 237C338 242 337 262 326 273C314 286 333 301 332 324" fill={C.paper} stroke={C.blue} strokeWidth="2.2"/>
  <path d="M303 257L337 257L408 271L335 279L304 267Z" fill="url(#coral)" stroke={C.coral} strokeWidth="2" strokeLinejoin="round"/>
  <path d="M308 267Q329 307 367 281L408 271L335 278Z" fill="url(#coral)" stroke={C.coral} strokeWidth="1.8"/>
  <circle cx="320" cy="250" r="3.3" fill={C.ink}/>
  <path d="M299 243L292 237M302 239L300 230" stroke={C.blue} strokeWidth="1.5"/>
  <path d={`M${hip[0]} ${hip[1]}L${frontKnee[0]} ${frontKnee[1]}L${foot[0]} ${foot[1]}`} stroke={C.coral} strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
  <path d={`M${foot[0]} ${foot[1]-5}l17 9l-8 2l-4-3l-6 3l-8-3Z M${back[0]} ${back[1]-5}l17 9l-8 2l-4-3l-6 3l-8-3Z`} fill="url(#coral)" stroke={C.coral} strokeWidth="1.8"/>
  <circle cx="335" cy="458" r="14" fill={C.paper} stroke={C.coral} strokeWidth="2"/>
  <path d={`M${back[0]} ${back[1]}L${foot[0]} ${foot[1]}`} stroke={C.coral} strokeWidth="2"/>
  <path d="M409 356L448 356L470 309L411 309Z" fill={C.paper} stroke={C.blue} strokeWidth="1.6"/>
  <path d="M416 316H459M415 322H455M414 328H450" stroke={C.teal} strokeWidth="1.1"/>
 </g>
}

function Learner({opacity,listener=false}:{opacity:number;listener?:boolean}){return <g opacity={opacity} transform={listener?"translate(760 350)":"translate(1150 350) scale(-1 1)"}>
 <path d="M20 174L92 162L128 210L161 302L-30 302L-5 224Z" fill={listener?"url(#teal)":"url(#coral)"}/>
 <ellipse cx="63" cy="124" rx="42" ry="49" fill={C.paper} stroke={C.coral} strokeWidth="1.8"/>
 <path d="M23 126L17 88L40 66L80 71L107 91L105 128L93 99L60 94L39 113Z" fill="url(#blue)"/>
 {!listener&&<path d="M21 128L11 110L6 148L25 155" fill="url(#blue)"/>}
 <path d="M77 127L88 127M70 152L83 154L89 150" stroke={C.blue} strokeWidth="2" fill="none"/>
 <path d="M87 188L132 224L184 206M12 194L-5 237L66 251" stroke={C.coral} strokeWidth="3" fill="none"/>
 {!listener&&<><path d="M130 205L178 186L211 219L163 237Z" fill={C.paper} stroke={C.blue} strokeWidth="1.7"/>
 <path d="M141 206L181 215M146 211L174 220" stroke={C.teal} strokeWidth="1.3"/></>}
 </g>}

const TextBlock=({children,style}:{children:React.ReactNode;style?:React.CSSProperties})=><div style={{fontFamily:font,color:C.ink,lineHeight:1.4,...style}}>{children}</div>;

type HeroProps={locale:string;artOnly?:boolean;useH3?:boolean};

const YiloLineScene:React.FC<HeroProps>=({locale,artOnly=false,useH3=true})=>{
 const frame=useCurrentFrame();
 const c=copy[locale as keyof typeof copy];
 const art=artCopy[locale as keyof typeof artCopy];
 const model=useH3&&!artOnly;
 const en=locale==='en';const rtl=locale==='ar';
 const world=artOnly?1:smooth(frame,8,62);
 const reuse=smooth(frame,236,265);
 const first=examples.reusePhrase[en?'zh-hans':'en'];
 const record=nativeRecords.captures.find(item=>item.contentLanguage.toLowerCase()===locale)!;
 const recordWidth=Math.min(800,540*record.pixelWidth/record.pixelHeight);
 return <AbsoluteFill style={{backgroundColor:C.paper,overflow:'hidden',height:artOnly?720:768,translate:artOnly?'0 0':'0 -160px'}}>
  {model&&<AbsoluteFill style={{opacity:world}}>
   <Loop durationInFrames={plate.frames}>
    <OffthreadVideo muted src={staticFile('pedaling-h3.mp4')} style={{position:'absolute',inset:0,width:1280,height:720,objectFit:'cover'}}/>
   </Loop>
  </AbsoluteFill>}
  <svg width="1280" height={artOnly?720:768} viewBox={`0 0 1280 ${artOnly?720:768}`} style={{position:'absolute',inset:0}}>
   <Definitions/>
   <defs><clipPath id="draw"><rect x="40" y="170" width={1180*(artOnly?1:smooth(frame,8,65))} height="470"/></clipPath></defs>
   <g opacity={model?0:world} clipPath="url(#draw)">
    <path d="M61 625L205 588L321 610L463 569L612 619L850 592L1204 620V642H61Z" fill="url(#green)" opacity=".85"/>
    <path d="M80 635H1200" stroke={C.green} strokeWidth="1.5"/>
    <PedalHelper frame={frame}/>
   </g>
   {!artOnly&&<path d="M0 634Q320 638 640 634T1280 634V768H0Z" fill="url(#green)" opacity={world*.8}/>}
   {!artOnly&&<g opacity={world}>
    <path d="M207 211Q188 211 188 232V251Q188 270 208 270H307Q326 270 326 250V232Q326 211 307 211Z" fill={C.paper} stroke={C.blue} strokeWidth="1.7"/>
    <text x="257" y="245" textAnchor="middle" fill={C.ink} fontFamily={font} fontSize="24" direction={rtl?'rtl':'ltr'}>{art.word}</text>
    {[245,257,269].map((x,i)=><circle key={x} cx={x} cy="259" r="1.7" fill={C.coral} opacity={.35+.65*(.5+.5*Math.sin(frame/7-i*1.1))}/>)}
    <circle cx="242" cy="282" r="4" fill={C.paper} stroke={C.blue} strokeWidth="1.3"/>
    <circle cx="247" cy="294" r="2.3" fill={C.blue}/>
   </g>}
   <Learner opacity={artOnly?0:reuse}/><Learner opacity={artOnly?0:reuse} listener/>
   {!artOnly&&<>
   <g opacity={reuse}>
    <path d="M533 240H1189V403H1128L1107 433L1101 403H533Z" fill={C.paper} stroke={C.blue} strokeWidth="1.7"/>
   </g>
   </>}
  </svg>
  {!artOnly&&<>
  <div style={{position:'absolute',left:555,top:263,width:612,opacity:reuse,direction:rtl?'rtl':'ltr'}}>
   <TextBlock style={{fontSize:40,fontWeight:500,lineHeight:1.25,direction:'ltr',textAlign:rtl?'right':'left',unicodeBidi:'isolate'}}>{first}</TextBlock>
   <TextBlock style={{fontSize:24,color:C.coral,marginTop:12}}>{c.reuse}</TextBlock>
  </div>

  </>}
  <AbsoluteFill style={{opacity:.045,mixBlendMode:'multiply',pointerEvents:'none',display:'grid',gridTemplateColumns:'repeat(8,160px)',gridAutoRows:'160px'}}>
   {Array.from({length:40},(_,i)=><Img key={i} src={staticFile('paper-grain.png')} style={{width:160,height:160}}/>)}
  </AbsoluteFill>
  {!artOnly&&<Img src={staticFile(`records/${locale}.png`)} style={{position:'absolute',left:460+(800-recordWidth)/2,top:196,width:recordWidth,height:'auto',opacity:smooth(frame,12,30)*(1-smooth(frame,238,260))}}/>}
 </AbsoluteFill>
}

export const YiloLineHero:React.FC<HeroProps>=(props)=><Freeze frame={timing.endHoldStartFrame} active={frame=>!props.artOnly&&frame>=timing.endHoldStartFrame}>
 <YiloLineScene {...props}/>
</Freeze>;
