import { CALMON_LOCALES } from '../../i18n/calmon-locales.mjs';
import panels from '../calmon-key-panel.json' with { type: 'json' };
import { tourCopy } from './tour-copy.mjs';
const en = {
  label: 'Animated demonstration of Calmon window management',
  start: 'Play demo', pause: 'Pause', play: 'Continue', restart: 'Restart demo',
  ready: 'Watch how Calmon arranges and switches windows.', noScript: 'Enable JavaScript to play the feature demo.',
  modeEnter: 'Double-tap and release ⌘ to enter leader mode', modeActive: 'Leader mode · keep using command keys', modeExited: 'Leader mode exited', nativeShortcut: 'macOS shortcut · no leader mode needed', thenKey: 'then',
  menu: 'Calmon menu', menuTitles: ['File', 'Edit', 'View', 'Window', 'Help'], leader: 'Leader Mode', desktop: 'Desktop', chooseApp: 'Add an App',
  close: 'Close window', minimize: 'Minimize window', full: 'Full Screen',
  appNames: { safari: 'Safari', notes: 'Notes', finder: 'Finder', terminal: 'Terminal', mail: 'Mail', calendar: 'Calendar', music: 'Music' },
};
const zh = {
  label: 'Calmon 窗口管理功能动画演示',
  start: '播放演示', pause: '暂停', play: '继续', restart: '从头重播',
  ready: '观看 Calmon 如何排列与切换窗口。', noScript: '启用 JavaScript，即可播放功能演示。',
  modeEnter: '双击并松开 ⌘，进入前导模式', modeActive: '前导模式已开启 · 可连续操作', modeExited: '已退出前导模式', nativeShortcut: 'macOS 快捷键 · 无需前导模式', thenKey: '再按',
  menu: 'Calmon 菜单', menuTitles: ['文件', '编辑', '显示', '窗口', '帮助'], leader: '前导模式', desktop: '桌面', chooseApp: '添加 App',
  close: '关闭窗口', minimize: '最小化窗口', full: '全屏',
  appNames: { safari: 'Safari', notes: '备忘录', finder: '访达', terminal: '终端', mail: '邮件', calendar: '日历', music: '音乐' },
};
export function desktopCopy(code) {
  const locale = CALMON_LOCALES[code];
  if (!locale.demo) return { ...(code === 'en' ? en : zh), map:locale.keyboardMapLabel, spaceKey:code==='en'?'Space':'空格', tour:tourCopy[code==='en'?'en':'zh-Hans'] };
  const [pause,play,restart,modeEnter,modeActive,nativeShortcut,thenKey,noScript,modeExited] = locale.demo;
  const panel = panels[locale.htmlLang];
  const appNames = Object.fromEntries(['notes','finder','terminal','mail','calendar','music'].map((app,i)=>[app,locale.apps[i]]));
  const windowTitles = Object.fromEntries(['safari-guide','notes-week','notes-ideas','finder-work','terminal-dev','mail-inbox','calendar-plan','music-player'].map((id,i)=>[id,locale.windows[i]]));
  const captionFeatures = [0,0,0,5,-1,0,5,1,0,2,2,4,4,3,5,5,4,5,4,2,1,1,0,0,0];
  return {label:locale.description,start:play,pause,play,restart,ready:locale.description,noScript,modeEnter,modeActive,modeExited,nativeShortcut,thenKey,menu:'Calmon',menuTitles:locale.menus,leader:modeActive,desktop:panel[0].rows[2].title,chooseApp:locale.features[3][0],close:panel[4].rows[1].title,minimize:panel[0].rows[1].title,full:panel[3].rows[1].title,map:locale.keyboardMapLabel,spaceKey:'Space',appNames:{safari:'Safari',...appNames},windowTitles,tour:captionFeatures.map(index=>index<0?locale.shortcutContext:locale.features[index][1])};
}
