export const WIDTHS = [1, .9, .75, 2 / 3, .5, 1 / 3, .25];
export const HOME_KEYS = ['A', 'S', 'D', 'F', 'J', 'K', 'L', ';'];
const member = (id, app, content, title) => ({ id, app, content, title });

export const WINDOWS = [
  member('safari-home', 'safari', 'web', ['lazyapps', 'lazyapps']),
  member('safari-guide', 'safari', 'guide', ['calmon 使用说明', 'calmon guide']),
  member('notes-week', 'notes', 'note', ['本周', 'This week']),
  member('notes-ideas', 'notes', 'ideas', ['灵感', 'Ideas']),
  member('finder-work', 'finder', 'files', ['项目', 'Projects']),
  member('terminal-dev', 'terminal', 'terminal', ['网站开发', 'Website']),
  member('mail-inbox', 'mail', 'mail', ['收件箱', 'Inbox']),
  member('calendar-plan', 'calendar', 'calendar', ['日程', 'Schedule']),
  member('music-player', 'music', 'music', ['正在播放', 'Now playing']),
];

export class Desktop {
  constructor() { this.reset(); }
  reset() {
    this.serial = 20;
    this.desktops = [1, 2];
    this.current = 1;
    this.focused = 'notes-week';
    this.fullSpace = null;
    this.pins = ['safari', 'notes'];
    this.gap = 12;
    this.accent = '#00ff00';
    this.remembered = {};
    this.rememberedApps = {};
    this.runningApps = new Set(['safari','notes','finder','terminal','mail','calendar','music']);
    this.tiledFocus = { 1: 'notes-week', 2: 'calendar-plan' };
    this.windows = structuredClone(WINDOWS);
    this.stacks = [
      ['safari', 1, ['safari-home', 'safari-guide'], 'tile'],
      ['notes', 1, ['notes-week', 'notes-ideas'], 'tile'],
      ['finder', 1, ['finder-work'], 'tile'],
      ['terminal', 1, ['terminal-dev'], 'tile'],
      ['mail', 1, ['mail-inbox'], 'tile'],
      ['calendar', 2, ['calendar-plan'], 'tile'],
      ['music', 1, ['music-player'], 'float'],
    ].map(([app, desktop, members, mode], i) => ({ id: `s${i}`, app, desktop, members, active: members[0], mode,
      rect: { x: .62, y: .19, w: .3, h: .55 }, previousMode: 'tile' }));
    this.columns = this.stacks.filter(s => s.mode === 'tile').map(s => ({ id: `c${s.id}`, desktop: s.desktop, stacks: [s.id], width: 1, pin: null, split: .5 }));
    this.floatRules = [];
  }
  stack(id = this.focused) { return this.stacks.find(s => s.id === id || s.members.includes(id)); }
  column(stack = this.stack()) { return this.columns.find(c => c.stacks.includes(stack?.id)); }
  window(id = this.focused) { return this.windows.find(w => w.id === id); }
  active(stack) { return this.window(stack.active); }
  tiled(desktop = this.current) { return this.columns.filter(c => c.desktop === desktop); }
  clean() {
    this.stacks = this.stacks.filter(s => s.members.length);
    for (const s of this.stacks) if (!s.members.includes(s.active)) s.active = s.members[0];
    const ids = new Set(this.stacks.filter(s => s.mode === 'tile').map(s => s.id));
    for (const c of this.columns) c.stacks = c.stacks.filter(id => ids.has(id));
    this.columns = this.columns.filter(c => c.stacks.length);
    if (this.fullSpace && !this.stack(this.fullSpace)) this.fullSpace = null;
    if (!this.window()) this.focused = this.stacks.find(s => s.desktop === this.current && s.mode !== 'min')?.active ?? null;
  }
  focus(id) {
    const stack = this.stack(id);
    if (!stack) return false;
    if (stack.mode === 'min') this.tile(stack);
    this.current = stack.desktop;
    stack.active = stack.members.includes(id) ? id : stack.active;
    this.focused = stack.active;
    this.fullSpace = stack.mode === 'full' ? stack.id : null;
    this.remembered[stack.desktop] = this.focused;
    this.rememberedApps[`${stack.desktop}:${stack.app}`] = this.focused;
    if (stack.mode === 'tile' && !this.column(stack)?.pin) this.tiledFocus[stack.desktop] = this.focused;
    return true;
  }
  newColumn(stack, index = this.columns.length) {
    const c = { id: `c${++this.serial}`, desktop: stack.desktop, stacks: [stack.id], width: 1, pin: null, split: .5 };
    this.columns.splice(index, 0, c);
    return c;
  }
  detach(id = this.focused) {
    const stack = this.stack(id);
    if (!stack || stack.members.length === 1) return stack;
    stack.members = stack.members.filter(item => item !== id);
    const separate = { ...structuredClone(stack), id: `s${++this.serial}`, members: [id], active: id };
    this.stacks.push(separate);
    this.clean();
    return separate;
  }
  tile(stack = this.stack()) {
    if (!stack) return false;
    if (stack.mode === 'tile' && this.column(stack)) return true;
    stack.mode = 'tile'; this.fullSpace = null;
    const column = this.newColumn(stack);
    if (stack.savedWidth !== undefined) column.width = stack.savedWidth;
    return true;
  }
  available(action) {
    const s = this.stack(), c = this.column(s);
    if (['new-desktop', 'reset', 'tile-all', 'leave-full'].includes(action)) return action !== 'leave-full' || !!this.fullSpace;
    if (action === 'delete-desktop') return this.desktops.length > 1;
    if (!s) return false;
    if (action === 'join-stack') return this.stacks.some(other => other.id !== s.id && other.app === s.app && other.desktop === s.desktop && other.mode === 'tile') && s.mode === 'tile';
    if (action === 'leave-stack') return s.members.length > 1 && s.mode === 'tile';
    if (action === 'add-pin') return !this.pins.includes(s.app) && this.pins.length < 10;
    if (action === 'remove-pin') return this.pins.includes(s.app);
    if (action === 'float') return s.mode !== 'full';
    if (action === 'pin') return !!c?.pin || (s.mode === 'float' || !!c) && this.tiled().filter(col=>col.pin).length < 2;
    if (['grow', 'shrink'].includes(action)) return s.mode === 'float' || !!c && (action === 'grow' ? c.width > (c.pin ? 2 : 0) : c.width < WIDTHS.length - 1);
    return true;
  }
  navigate(direction) {
    const stack = this.stack(), column = this.column(stack);
    const columns = this.tiled().filter(c => !c.pin);
    if (!columns.length) return false;
    const index = Math.max(0, columns.indexOf(column));
    const target = columns[(index + direction + columns.length) % columns.length];
    const next = this.stacks.find(s => s.id === target.stacks[0]);
    return this.focus(next.active);
  }
  swipe(direction) {
    const columns = this.tiled().filter(c => !c.pin);
    const index = columns.indexOf(this.column() ?? this.column(this.stack(this.tiledFocus[this.current])));
    const next = index + direction;
    if ((next < 0 || next >= columns.length) && !this.tiled().some(c => c.pin)) return false;
    if (!columns.length) return false;
    return this.focus(this.stack(columns[(next + columns.length) % columns.length].stacks[0]).active);
  }
  vertical(direction) {
    const s = this.stack(), c = this.column(s);
    if (!c) return false;
    const index = c.stacks.indexOf(s.id), next = c.stacks[index + direction];
    return next ? this.focus(this.stack(next).active) : false;
  }
  moveColumn(direction) {
    const c = this.column();
    if (!c) return false;
    if (c.pin) {
      const edge = direction < 0 ? 'left' : 'right';
      const occupied = this.tiled().find(other => other !== c && other.pin === edge);
      if (occupied || c.pin === edge) return false;
      c.pin = edge; return true;
    }
    const columns = this.tiled().filter(c => !c.pin), next = columns[columns.indexOf(c) + direction];
    if (!next) return false;
    const a = this.columns.indexOf(c), b = this.columns.indexOf(next);
    [this.columns[a], this.columns[b]] = [this.columns[b], this.columns[a]];
    return true;
  }
  moveCell(direction) {
    const s = this.stack(), c = this.column();
    if (!c) return false;
    const index = c.stacks.indexOf(s.id), next = index + direction;
    if (next < 0 || next >= c.stacks.length) return false;
    [c.stacks[index], c.stacks[next]] = [c.stacks[next], c.stacks[index]];
    return true;
  }
  place(sourceId, targetId, placement = 'below') {
    const source = this.stack(sourceId), target = this.stack(targetId), from = this.column(source), to = this.column(target);
    if (!source || !target || source.id === target.id || source.desktop !== target.desktop || !to || source.mode !== 'tile') return false;
    const vertical = placement === 'above' || placement === 'below';
    if (vertical && from !== to && to.stacks.length >= 3) return false;
    if (from) from.stacks = from.stacks.filter(id => id !== source.id);
    if (vertical) to.stacks.splice(to.stacks.indexOf(target.id) + (placement === 'below' ? 1 : 0), 0, source.id);
    else this.newColumn(source, this.columns.indexOf(to) + (placement === 'right' ? 1 : 0));
    this.clean(); this.focus(source.active);
    return true;
  }
  consume(direction) {
    const source = this.stack(), c = this.column(source), columns = this.tiled().filter(c => !c.pin);
    if (!source || !c || c.pin) return false;
    if (c.stacks.length > 1) {
      c.stacks = c.stacks.filter(id => id !== source.id);
      this.newColumn(source, this.columns.indexOf(c) + (direction > 0 ? 1 : 0)); this.clean(); return true;
    }
    const neighbor = columns[columns.indexOf(c) + direction];
    if (!neighbor || neighbor.stacks.length >= 3) return false;
    return this.place(source.active, this.stack(neighbor.stacks[direction < 0 ? neighbor.stacks.length - 1 : 0]).active, direction < 0 ? 'below' : 'above');
  }
  resize(direction) {
    const s = this.stack(), c = this.column(s);
    if (!this.available(direction > 0 ? 'grow' : 'shrink')) return false;
    if (s.mode === 'float') {
      s.rect.w = Math.min(.9, Math.max(.2, s.rect.w + direction * .1));
      s.rect.h = Math.min(.85, Math.max(.25, s.rect.h + direction * .1));
    } else c.width = Math.min(6, Math.max(c.pin ? 2 : 0, c.width - direction));
    return true;
  }
  resizeTo(fraction) {
    const c = this.column();
    if (!c) return false;
    c.width = WIDTHS.reduce((best, width, i) => Math.abs(width - fraction) < Math.abs(WIDTHS[best] - fraction) ? i : best, c.width);
    if (c.pin) c.width = Math.max(2, c.width);
    return true;
  }
  changeDesktop(number) {
    if (!this.desktops.includes(number)) return false;
    this.remembered[this.current] = this.focused;
    this.current = number; this.fullSpace = null;
    this.focused = this.remembered[number] && this.stack(this.remembered[number])?.desktop === number ? this.remembered[number]
      : this.stacks.find(s => s.desktop === number && s.mode === 'tile')?.active ?? this.stacks.find(s => s.desktop === number)?.active ?? null;
    return true;
  }
  renumber() {
    const mapping = new Map(this.desktops.map((id, index) => [id, index + 1]));
    this.desktops = this.desktops.map(id => mapping.get(id));
    for (const stack of this.stacks) stack.desktop = mapping.get(stack.desktop);
    for (const column of this.columns) column.desktop = mapping.get(column.desktop);
    this.current = mapping.get(this.current);
    this.remembered = Object.fromEntries(Object.entries(this.remembered).filter(([id]) => mapping.has(Number(id))).map(([id, value]) => [mapping.get(Number(id)), value]));
    this.tiledFocus = Object.fromEntries(Object.entries(this.tiledFocus).filter(([id]) => mapping.has(Number(id))).map(([id, value]) => [mapping.get(Number(id)), value]));
  }
  sendDesktop(number, all = false) {
    if (!this.desktops.includes(number) || number === this.current) return false;
    const focus = this.focused;
    const selected = !all && this.stack() ? this.detach(this.focused) : null;
    const sources = all ? this.stacks.filter(s => s.desktop === this.current && s.mode !== 'full') : [selected].filter(Boolean);
    for (const s of sources) {
      const c = this.column(s);
      if (c) c.stacks = c.stacks.filter(id => id !== s.id);
      s.desktop = number;
      if (s.mode === 'tile') this.newColumn(s);
    }
    this.clean(); this.changeDesktop(number); if (focus) this.focus(focus);
    return true;
  }
  launch(app) {
    const matching = this.stacks.filter(s => s.app === app);
    const remembered = this.rememberedApps[`${this.current}:${app}`];
    const stack = matching.find(s=>s.members.includes(remembered)) ?? matching.find(s => s.desktop === this.current) ?? matching[0];
    this.runningApps.add(app);
    if (stack) return this.focus(stack.active);
    const template = WINDOWS.find(w => w.app === app);
    if (!template) return false;
    const window = { ...structuredClone(template), id: `w${++this.serial}` };
    this.windows.push(window);
    const newStack = { id: `s${++this.serial}`, app, desktop: this.current, members: [window.id], active: window.id,
      mode: this.floatRules.includes(app) ? 'float' : 'tile', rect: { x: .22, y: .15, w: .5, h: .55 }, previousMode: 'tile' };
    this.stacks.push(newStack);
    if (newStack.mode === 'tile') this.newColumn(newStack);
    return this.focus(window.id);
  }
  execute(action, value) {
    const s = this.stack(), c = this.column(s);
    let result = true;
    switch (action) {
      case 'focus': return this.focus(value);
      case 'next': return this.navigate(1);
      case 'previous': return this.navigate(-1);
      case 'up': return this.vertical(-1);
      case 'down': return this.vertical(1);
      case 'move-left': return this.moveColumn(-1);
      case 'move-right': return this.moveColumn(1);
      case 'move-up': return this.moveCell(-1);
      case 'move-down': return this.moveCell(1);
      case 'consume-left': return this.consume(-1);
      case 'consume-right': return this.consume(1);
      case 'grow': return this.resize(1);
      case 'shrink': return this.resize(-1);
      case 'height-grow': case 'height-shrink':
        if (!c || c.stacks.length !== 2) return false;
        c.split = Math.max(1 / 3, Math.min(2 / 3, c.split + (action === 'height-grow' ? 1 : -1) * (c.stacks[0] === s.id ? 1 : -1) / 6)); break;
      case 'pin':
        if (!this.available('pin')) return false;
        if (s.mode === 'float') this.tile(s);
        { const column = this.column(s);
          if (column.pin) column.pin = null;
          else { const used = this.tiled().filter(other => other.pin).map(other => other.pin);
            column.pin = used.includes('left') ? 'right' : 'left'; column.width = 5; }
        } break;
      case 'focus-pin': {
        const pin = this.tiled().find(col => col.pin === (value ?? 'left'));
        if (!pin) return false;
        if (c === pin) { const other = this.tiled().find(col => !col.pin); if (other) this.focus(this.stack(other.stacks[0]).active); }
        else this.focus(this.stack(pin.stacks[0]).active); break;
      }
      case 'float': {
        if (!s || s.mode === 'full') return false;
        if (s.mode === 'float') this.tile(s);
        else { const separate = this.detach(); separate.savedWidth = c?.width; separate.previousMode = 'tile'; separate.mode = 'float'; separate.rect = { x: .25, y: .18, w: .5, h: .5 }; }
        break;
      }
      case 'full': {
        if (!s) return false;
        if (s.mode === 'full') { s.mode = s.previousMode; this.fullSpace = null; if (s.mode === 'tile') this.newColumn(s).width = s.savedWidth ?? 1; }
        else { const separate = this.detach(); separate.savedWidth = c?.width; separate.previousMode = separate.mode; separate.mode = 'full'; this.fullSpace = separate.id; }
        break;
      }
      case 'leave-full': this.fullSpace = null; this.focused = this.stacks.find(item => item.desktop === this.current && item.mode === 'tile')?.active ?? null; break;
      case 'minimize': if (!s) return false; this.detach().mode = 'min'; this.focused = this.stacks.find(item => item.desktop === this.current && item.mode === 'tile' && item.id !== s.id)?.active ?? null; break;
      case 'join-stack': {
        if (!this.available(action)) return false;
        const target = this.stacks.find(other => other.id !== s.id && other.app === s.app && other.desktop === s.desktop && other.mode === 'tile');
        s.members = s.members.filter(id => id !== this.focused); target.members.push(this.focused); target.active = this.focused; break;
      }
      case 'leave-stack': {
        if (!this.available(action)) return false;
        const position = this.columns.indexOf(c); const separate = this.detach(); this.newColumn(separate, position + 1); break;
      }
      case 'add-pin': if (!this.available(action)) return false; this.pins.push(s.app); break;
      case 'remove-pin': if (!this.available(action)) return false; this.pins = this.pins.filter(app => app !== s.app); break;
      case 'tile-all': for (const stack of this.stacks.filter(item => item.desktop === this.current && item.mode === 'float')) this.tile(stack); break;
      case 'new-desktop': {
        if (this.desktops.length >= 9) return false;
        const number = Math.max(...this.desktops) + 1;
        this.desktops.splice(this.desktops.indexOf(this.current) + 1, 0, number);
        this.changeDesktop(number); this.renumber(); break;
      }
      case 'delete-desktop': {
        if (!this.available(action)) return false;
        const number = this.current, target = this.desktops.find(d => d !== number);
        this.sendDesktop(target, true); for (const stack of this.stacks.filter(item => item.desktop === number)) stack.desktop = target;
        this.desktops = this.desktops.filter(d => d !== number); this.current = target; this.renumber(); break;
      }
      case 'desktop': return this.changeDesktop(value);
      case 'send-desktop': return this.sendDesktop(value);
      case 'send-all': return this.sendDesktop(value, true);
      case 'launch': return this.launch(value);
      case 'cycle-stack': if (!s) return false; this.focus(s.members[(s.members.indexOf(s.active) + 1) % s.members.length]); break;
      case 'close': if (!s) return false; s.members = s.members.filter(id => id !== this.focused); this.windows = this.windows.filter(w => w.id !== this.focused); this.focused = null; break;
      case 'always-float':
        if (!s) return false;
        this.floatRules = this.floatRules.includes(s.app) ? this.floatRules.filter(app => app !== s.app) : [...this.floatRules, s.app];
        for (const stack of this.stacks.filter(item => item.app === s.app && item.mode !== 'full')) {
          if (this.floatRules.includes(s.app)) {
            for (const id of stack.members.slice()) this.detach(id).mode = 'float';
          } else this.tile(stack);
        } break;
      default: result = false;
    }
    this.clean();
    return result;
  }
  labels() {
    const result = [], assigned = new Map();
    let next = 0;
    const key = () => { const n = next++; return n < 8 ? HOME_KEYS[n] : HOME_KEYS[Math.floor(n / 8) - 1] + HOME_KEYS[n % 8]; };
    for (const app of this.pins) {
      const stack = this.stacks.find(s => s.app === app && s.desktop === this.current) ?? this.stacks.find(s => s.app === app);
      const label = key(); result.push({ type: 'app', id: app, key: label, window: stack?.active });
      if (stack) assigned.set(stack.id, label);
    }
    for (const stack of this.stacks) result.push({ type: 'window', id: stack.id, window: stack.active, key: assigned.get(stack.id) ?? key() });
    return result;
  }
  layout(width, height, bottomInset) {
    const gap = this.gap, margin = 12, top = 40, bottom = bottomInset ?? (width < 600 ? 114 : 84);
    const area = { x: margin, y: top, w: Math.max(1, width - margin * 2), h: height - top - bottom };
    const result = new Map();
    const full = this.stack(this.fullSpace);
    if (full) { result.set(full.active, { x: 0, y: 0, w: width, h: height, z: 70 }); return result; }
    const columns = this.tiled(), left = columns.find(c => c.pin === 'left'), right = columns.find(c => c.pin === 'right');
    const pinnedWidth = c => c ? Math.min(area.w * WIDTHS[c.width], Math.max(70, area.w - 150)) : 0;
    const lw = pinnedWidth(left), rw = pinnedWidth(right);
    const viewport = { x: area.x + (left ? lw + gap : 0), w: Math.max(80, area.w - (left ? lw + gap : 0) - (right ? rw + gap : 0)) };
    const normal = columns.filter(c => !c.pin);
    const widths = normal.map((c, i) => {
      const edge = (left && !right && i === normal.length - 1) || (right && !left && i === 0);
      const fraction = c.width === 1 && edge ? 1 :
        c.width === 1 && normal.length > 1 && (i === 0 || i === normal.length - 1) ? .95 : WIDTHS[c.width];
      return Math.max(60, viewport.w * fraction);
    });
    const selectedColumn = this.column();
    const focusColumn = selectedColumn && !selectedColumn.pin ? selectedColumn : this.column(this.stack(this.tiledFocus[this.current]));
    const index = Math.max(0, normal.indexOf(focusColumn));
    if (widths[index] < viewport.w * .9 && widths.length > 1) {
      const adjacent = index === widths.length - 1 ? index - 1 : index + 1;
      widths[adjacent] = Math.max(60, viewport.w - widths[index] - gap);
    }
    const total = widths.reduce((sum, w) => sum + w, 0) + gap * Math.max(0, widths.length - 1);
    const targetX = widths.slice(0, index).reduce((sum, w) => sum + w + gap, 0);
    const paired = normal[index]?.width >= 2 && normal.length > 1;
    const pairStart = index === normal.length - 1 ? index - 1 : index;
    const pairedX = widths.slice(0, pairStart).reduce((sum,w)=>sum+w+gap,0);
    let scroll = Math.min(Math.max(0, paired ? pairedX : targetX - Math.max(0, (viewport.w - widths[index]) / 2)), Math.max(0, total - viewport.w));
    // A pinned side is a hard edge: keep whole columns beside it instead of a centered neighbor sliver.
    if (left && !right) scroll = paired ? pairedX : targetX;
    else if (right && !left) scroll = paired ? pairedX : targetX - (viewport.w - widths[index]);
    const addColumn = (column, x, w, pinned = false) => {
      if (!column) return;
      const count = column.stacks.length;
      let y = top;
      column.stacks.forEach((id, i) => {
        const stack = this.stack(id);
        const h = count === 2 ? (area.h - gap) * (i === 0 ? column.split : 1 - column.split) : (area.h - gap * (count - 1)) / count;
        const clipLeft = left ? viewport.x : 0;
        const clipRight = right ? viewport.x + viewport.w : width;
        result.set(stack.active, { x, y, w, h, z: stack.active === this.focused ? 8 : column === focusColumn ? 6 : 4, pinned,
          clip: pinned ? null : { x: clipLeft, w: clipRight - clipLeft } }); y += h + gap;
      });
    };
    let x = viewport.x - scroll;
    normal.forEach((c, i) => {
      if (left && right) addColumn(c, viewport.x, viewport.w);
      else { addColumn(c, x, widths[i]); x += widths[i] + gap; }
    });
    addColumn(left, area.x, lw, true); addColumn(right, width - margin - rw, rw, true);
    for (const stack of this.stacks.filter(s => s.desktop === this.current && s.mode === 'float')) {
      const r = stack.rect, w = Math.min(area.w, Math.max(160, r.w * width)), h = Math.max(130, r.h * area.h);
      result.set(stack.active, { x: Math.max(margin, Math.min(width - margin - w, r.x * width)), y: Math.max(top, Math.min(height - bottom - h, top + r.y * area.h)), w, h, z: stack.active === this.focused ? 20 : 2, floating: true });
    }
    return result;
  }
}
