import test from 'node:test';
import assert from 'node:assert/strict';
import { Desktop, WIDTHS } from '../src/components/calmon-desktop/model.mjs';
const valid = d => {
  const members = d.stacks.flatMap(s => s.members);
  assert.equal(new Set(members).size, members.length, 'No window may belong to two stacks');
  assert.deepEqual(members.slice().sort(), d.windows.map(w => w.id).sort(), 'No windows lost');
  for (const s of d.stacks) { assert(s.members.includes(s.active)); assert(d.desktops.includes(s.desktop)); }
  for (const c of d.columns) { assert(c.stacks.length > 0 && c.stacks.length <= 3); for (const id of c.stacks) { const s = d.stack(id); assert.equal(s.mode, 'tile'); assert.equal(s.desktop, c.desktop); } }
  for (const s of d.stacks.filter(s => s.mode === 'tile')) assert.equal(d.columns.filter(c => c.stacks.includes(s.id)).length, 1);
};
test('separating and regrouping preserves identities and the selected page', () => {
  const d = new Desktop(); d.execute('leave-stack'); valid(d); assert.equal(d.stack().members.length, 1); assert(d.available('join-stack'));
  d.execute('join-stack'); valid(d); assert.equal(d.stack().members.length, 2); assert.equal(d.focused, 'notes-week');
  d.execute('cycle-stack'); assert.equal(d.focused, 'notes-ideas');
});
test('columns hold up to three stacks, and moving out preserves other cells', () => {
  const d = new Desktop(); d.place('finder-work', 'notes-week', 'below'); d.place('terminal-dev', 'notes-week', 'above'); valid(d);
  assert.equal(d.column(d.stack('notes-week')).stacks.length, 3);
  assert.equal(d.place('mail-inbox', 'notes-week', 'below'), false);
  d.focus('finder-work'); d.consume(1); valid(d); assert.equal(d.column().stacks.length, 1);
});
test('resize pair reaches the right edge with exactly one gap', () => {
  const d = new Desktop(); d.focus('mail-inbox'); d.column().width = 3; d.execute('shrink'); valid(d);
  const frames = d.layout(1000, 600), focus = frames.get('mail-inbox');
  assert.equal(Math.round(focus.x + focus.w), 988);
  const neighbor = frames.get('terminal-dev'); assert.equal(Math.round(focus.x - neighbor.x - neighbor.w), d.gap);
  assert.equal(WIDTHS[d.column().width], .5);
});
test('pin stays at the edge when focus and viewport move', () => {
  const d = new Desktop(); d.focus('safari-home'); d.execute('pin');
  const before = d.layout(1000, 600).get('safari-home'); d.focus('mail-inbox');
  const after = d.layout(1000, 600).get('safari-home');
  assert.deepEqual([after.x, after.y, after.w, after.h], [before.x, before.y, before.w, before.h]);
  d.focus('notes-week'); d.execute('pin'); assert.equal(d.column().pin, 'right'); valid(d);
});
test('end columns beside a pinned reference retain only the desktop margin', () => {
  for (const width of [390, 1280]) for (const side of ['left', 'right']) for (const single of [false, true]) {
    const d = new Desktop(); d.execute('pin'); d.column().pin = side;
    const working = d.tiled().filter(c => !c.pin);
    const end = side === 'left' ? working.at(-1) : working[0];
    if (single) for (const c of working.filter(c => c !== end)) d.stack(c.stacks[0]).mode = 'float';
    const id = d.stack(end.stacks[0]).active;
    d.clean(); d.focus(id);
    const frames = d.layout(width, 600), focused = frames.get(d.focused), pin = frames.get('notes-week');
    if (side === 'left') {
      assert(Math.abs(focused.x + focused.w - (width - 12)) < .001, `${width}px: excess right padding`);
      assert(Math.abs(focused.x - pin.x - pin.w - d.gap) < .001);
    } else {
      assert(Math.abs(focused.x - 12) < .001, `${width}px: excess left padding`);
      assert(Math.abs(pin.x - focused.x - focused.w - d.gap) < .001);
    }
    d.focus('notes-week');
    assert.equal(d.layout(width, 600).get(id).w, focused.w);
  }
});
test('floating one member leaves the app stack and tiles back without duplication', () => {
  const d = new Desktop(); d.execute('float'); valid(d); assert.equal(d.stack().mode, 'float'); assert.equal(d.stack('notes-ideas').mode, 'tile');
  d.execute('float'); valid(d); assert.equal(d.stack().mode, 'tile');
});
test('full screen is preserved in Max Deck while returning to desktop', () => {
  const d = new Desktop(); d.execute('full'); valid(d); const full = d.stack().id;
  d.execute('leave-full'); assert.equal(d.fullSpace, null); assert.equal(d.stack(full).mode, 'full');
  d.focus(d.stack(full).active); assert.equal(d.fullSpace, full); d.execute('full'); valid(d); assert.equal(d.fullSpace, null);
});
test('Pin Deck is global, uses independent add/remove states, and opens existing windows in place', () => {
  const d = new Desktop(); assert(!d.available('add-pin')); assert(d.available('remove-pin'));
  d.focus('finder-work'); d.execute('add-pin'); assert(!d.available('add-pin')); assert(d.available('remove-pin'));
  d.execute('desktop', 2); assert(d.pins.includes('finder')); d.launch('finder'); assert.equal(d.current, 1);
  d.execute('remove-pin'); assert(d.windows.some(w => w.id === 'finder-work')); valid(d);
});
test('desktop transfer follows focus; deleting an occupied desktop keeps every window', () => {
  const d = new Desktop(); d.execute('new-desktop'); const third = d.current;
  d.focus('notes-week'); d.execute('send-desktop', third); valid(d); assert.equal(d.current, third); assert.equal(d.focused, 'notes-week');
  d.execute('delete-desktop'); valid(d); assert.equal(d.desktops.length, 2); assert.equal(d.windows.length, 9);
});
test('move all keeps full-screen windows out of the batch', () => {
  const d = new Desktop(); d.execute('full'); const full = d.stack().id; d.execute('leave-full'); d.execute('send-all', 2); valid(d);
  assert.equal(d.stack(full).desktop, 1); assert(d.stacks.filter(s => s.mode !== 'full').every(s => s.desktop === 2));
});
test('labels keep pinned app keys stable and match their ordinary tabs', () => {
  const d = new Desktop(); const first = d.labels().filter(x => x.type === 'app');
  d.focus('mail-inbox'); d.execute('leave-stack'); d.execute('desktop', 2);
  assert.deepEqual(d.labels().filter(x => x.type === 'app').map(x => x.key), first.map(x => x.key));
  for (const app of first) { const ordinary = d.labels().find(x => x.type === 'window' && x.window === app.window); assert.equal(ordinary.key, app.key); }
});
test('close, minimize and relaunch leave a valid usable desktop', () => {
  const d = new Desktop(); d.execute('minimize'); valid(d); d.focus('notes-week'); assert.equal(d.stack().mode, 'tile');
  d.execute('close'); valid(d); d.focus('music-player'); d.execute('close'); d.launch('music'); valid(d);
});

test('homepage tour preserves stacked windows through splits, scrolling, and pinning', async () => {
  const { createDesktopTour } = await import('../src/components/calmon-desktop/tour.mjs');
  for (const [width, height] of [[320, 260], [480, 360]]) {
    const d = new Desktop(), stops = createDesktopTour(d, true);
    const notes = d.stack('notes-week'), members = notes.members.slice();
    assert.equal(d.column(notes).stacks.length, 2, 'The opening already shows a vertical split');
    assert(!d.stacks.some(stack => stack.mode === 'float'));
    const opening = JSON.stringify(d);
    for (const [index, step] of stops.entries()) {
      step.run(); d.clean(); valid(d);
      assert.deepEqual(d.stack('notes-week').members, members, 'The whole app stack moves together');
      if (index === 0) assert.equal(d.column(notes).stacks.length, 1);
      if (index === 3) assert.equal(d.focused, 'notes-ideas', 'Cycling shows the other Notes window');
      if (index === 4) {
        const frames = d.layout(width, height);
        const upper = frames.get('safari-home'), lower = frames.get('notes-ideas');
        assert.equal(upper.x, lower.x);
        assert(Math.abs(lower.y - upper.y - upper.h - d.gap) < .001);
      }
      if (index === 6) assert(d.column(notes).pin);
      assert([...d.layout(width, height).values()].some(frame => frame.x < width && frame.x + frame.w > 0 && frame.w > 0 && frame.h > 0), 'Every step keeps windows visible');
    }
    d.reset(); createDesktopTour(d, true);
    assert.equal(JSON.stringify(d), opening, 'A repeat restores the opening split');
  }
});
test('entire tour stays valid and demonstrates scrolling with keyboard cues', async () => {
  const { createDesktopTour, keysForTourStep } = await import('../src/components/calmon-desktop/tour.mjs');
  const { tourCopy } = await import('../src/components/calmon-desktop/tour-copy.mjs');
  const d = new Desktop(), stops = createDesktopTour(d);
  assert(stops.every(step => step.keys && !step.cue && !step.context && !step.target), 'The entire tour uses keyboard cues, without swipe, click, menu, or drag demonstrations');
  assert.deepEqual(stops[0].keys, ['⌘','⌘','→']);
  assert.deepEqual(stops[1].keys, ['→']);
  assert.deepEqual(stops[2].keys, ['→']);
  assert.deepEqual(stops.slice(0, 6).map(step => step.keys.at(-1)), ['→', '→', '→', '←', '←', '←']);
  const openingFocus = ['finder-work', 'terminal-dev', 'mail-inbox', 'terminal-dev', 'finder-work', 'notes-week'];
  const focused = new Set();
  let leader = false, labels = false, columnSteps = 0;
  for (let i = 0; i < stops.length; i++) {
    for (const copy of Object.values(tourCopy)) assert(copy[stops[i].caption], `Step ${i} must have a caption in every language`);
    const step = stops[i];
    if (step.leaderBefore !== undefined) { leader = step.leaderBefore; labels = leader; }
    if (step.labelJump && leader && !labels) leader = false;
    const keys = keysForTourStep(step, leader, labels);
    assert(!keys.includes('Esc'), 'The demo never shows an Esc key');
    const entry = keys.findIndex((key, index) => key === '⌘' && keys[index + 1] === '⌘');
    if (entry >= 0) {
      assert(!leader, `Step ${i} cannot double-tap an already active mode`);
      leader = true; labels = true;
    }
    const native = keys[0] === '⌘' && keys[1] === '`';
    assert(leader || native, `Step ${i} cannot run a leader key outside leader mode`);
    if (step.labelJump) assert(labels, `Step ${i} needs visible labels before jumping`);
    assert(keys.length && keys.every(key => typeof key === 'string' && key.length), `Step ${i} must show valid keys before acting`);
    const columnOrder = d.tiled().map(column => column.stacks.slice());
    const focusedBefore = d.focused;
    const openingWidths = i < 6 ? [390, 1280].map(width => d.layout(width, 600)) : [];
    stops[i].run(); d.clean(); valid(d);
    if (i < 6) {
      assert.equal(d.focused, openingFocus[i], 'The opening navigates right, then retraces the same columns to the left');
      [390, 1280].forEach((width, index) => {
        for (const [id, frame] of d.layout(width, 600)) assert.equal(frame.w, openingWidths[index].get(id).w, `${id} keeps its width in either direction`);
      });
    }
    if (keys.includes(',')) {
      columnSteps++;
      assert.equal(d.tiled().length, columnOrder.length - 1, 'Comma joins the stack into its left neighbor');
      assert.deepEqual(d.column().stacks, [d.stack('safari-home').id, d.stack('notes-week').id]);
      assert.equal(d.focused, focusedBefore, 'Joining preserves focus');
      for (const width of [390, 1280]) {
        const frames = d.layout(width, 600);
        const upper = frames.get('safari-home'), lower = frames.get(d.focused);
        assert.equal(upper.x, lower.x);
        assert.equal(upper.w, lower.w);
        assert(Math.abs(lower.y - upper.y - upper.h - d.gap) < .001, 'The result is two vertically arranged cells');
      }
    }
    if (keys.includes('.')) {
      columnSteps++;
      assert.equal(d.tiled().length, columnOrder.length + 1, 'Period splits the stack into a column on the right');
      assert.equal(d.column().stacks.length, 1);
      assert.equal(d.focused, focusedBefore, 'Splitting preserves focus');
      assert.deepEqual(d.tiled().slice(0, 2).map(column => column.stacks), [[d.stack('safari-home').id], [d.stack('notes-week').id]]);
    }
    if (step.leaderAfter !== undefined) leader = step.leaderAfter;
    labels = leader && step.revealLabels === true;
    if (i < 7) { assert(d.columns.every(c => c.stacks.length === 1 && !c.pin)); focused.add(d.focused); }
    const frames = d.layout(390, 510);
    const floating = d.stacks.filter(stack => stack.mode === 'float');
    assert.deepEqual(floating.map(stack => stack.active), step.caption === 11 ? ['mail-inbox'] : [], 'Floating windows appear only in the Sky Deck demonstration');
    for (const frame of frames.values()) { assert(frame.w > 0 && frame.h > 0); assert(Number.isFinite(frame.x)); }
  }
  assert(focused.size >= 5, 'The opening must scroll through five apps');
  assert.equal(leader, true, 'The final result keeps its leader-mode context');
  assert.equal(columnSteps, 2, 'The tour demonstrates both comma and period');
});
test('tour repeats from the same clean desktop after changing columns, pins, desktops, and full screen', async () => {
  const { createDesktopTour } = await import('../src/components/calmon-desktop/tour.mjs');
  const d = new Desktop();
  let initial;
  for (let iteration = 0; iteration < 3; iteration++) {
    const stops = createDesktopTour(d);
    if (iteration === 0) initial = JSON.stringify(d);
    else assert.equal(JSON.stringify(d), initial, 'Each iteration restores the same opening scene');
    for (const step of stops) { step.run(); d.clean(); valid(d); }
    assert.equal(d.stack('mail-inbox').desktop, 2, 'The tour moves a window to the second desktop before restarting');
    assert(d.stacks.some(stack => stack.mode === 'full'), 'The tour leaves a native full-screen window before restarting');
    d.reset();
  }
});
test('new desktops insert after the current one; deletion keeps consecutive numbers', () => {
  const d = new Desktop(); d.execute('new-desktop'); valid(d);
  assert.equal(d.current,2); assert.equal(d.stack('calendar-plan').desktop,3);
  d.execute('delete-desktop'); valid(d); assert.deepEqual(d.desktops,[1,2]);
});
test('focusing a floating or pinned window does not move the scrolling strip', () => {
  const d = new Desktop(); d.focus('mail-inbox'); const before=d.layout(1000,600).get('mail-inbox');
  d.focus('music-player'); const after=d.layout(1000,600).get('mail-inbox');
  assert.equal(before.x,after.x);
});

test('default scroll frames show 90% columns, with exact 12pt edges at both ends', () => {
  for (const width of [320,390,768,1280]) {
    const d = new Desktop(); d.focus('safari-home');
    const first = d.layout(width,600).get('safari-home'); assert.equal(first.x,12);
    d.focus('mail-inbox'); const last=d.layout(width,600).get('mail-inbox'); assert(Math.abs(width-last.x-last.w-12)<.001);
    d.gap=24; const changed=d.layout(width,600).get('mail-inbox'); assert(Math.abs(width-changed.x-changed.w-12)<.001);
  }
});
test('swipes resist at the end while keyboard navigation wraps', () => {
  const d=new Desktop();d.focus('mail-inbox');assert.equal(d.swipe(1),false);assert.equal(d.focused,'mail-inbox');
  d.navigate(1);assert.equal(d.focused,'safari-home');
});

test('offscreen neighbors clip at the physical screen edge, not the desktop margin', () => {
  const d=new Desktop();d.focus('notes-week');const frame=d.layout(1000,600).get('safari-home');assert(frame.x<0);assert.equal(frame.clip.x,0);assert.equal(frame.clip.w,1000);
});
test('floating rules separate native app stack members and remain reversible', () => {
  const d=new Desktop();d.execute('always-float');valid(d);assert(d.stacks.filter(s=>s.app==='notes').every(s=>s.mode==='float'&&s.members.length===1));d.execute('always-float');valid(d);
});

test('moving one app-stack member to another desktop leaves its sibling in place', () => {
  const d=new Desktop();d.sendDesktop(2);valid(d);assert.equal(d.stack('notes-week').desktop,2);assert.equal(d.stack('notes-ideas').desktop,1);
});
test('retiled windows retain their column width and floating windows can be pinned', () => {
  const d=new Desktop();d.column().width=4;d.execute('float');d.execute('float');assert.equal(d.column().width,4);
  d.execute('float');assert(d.available('pin'));d.execute('pin');valid(d);assert.equal(d.stack().mode,'tile');assert.equal(d.column().pin,'left');
});

test('Pin Deck remembers the last focused member even after separation', () => {
  const d=new Desktop();d.focus('safari-guide');d.execute('leave-stack');d.focus('notes-week');d.launch('safari');assert.equal(d.focused,'safari-guide');valid(d);
});

test('resizing a middle column fits its neighbor inside both viewport edges', () => {
  for(const width of [390,1000]){const d=new Desktop();d.execute('shrink');const frames=d.layout(width,600),a=frames.get('notes-week'),b=frames.get('finder-work');assert.equal(a.x,12);assert(Math.abs(b.x+b.w-(width-12))<.001);assert.equal(b.x-a.x-a.w,12);}
});

test('pinned boundaries never expose a sliced neighboring window', () => {
  for (const width of [390, 1280]) for (const side of ['left', 'right']) {
    const d = new Desktop(); d.execute('pin'); d.column().pin = side;
    for (const id of ['finder-work', 'terminal-dev', 'mail-inbox', 'safari-home']) {
      d.focus(id);
      const frames = d.layout(width, 600), pin = frames.get('notes-week');
      const edge = side === 'left' ? pin.x + pin.w + d.gap : pin.x - d.gap;
      for (const [window, frame] of frames) {
        if (frame.pinned || frame.floating) continue;
        assert(!(frame.x < edge - .001 && frame.x + frame.w > edge + .001),
          `${width}px ${side} pin: ${window} straddles the pinned boundary and leaves a vertical fragment`);
      }
    }
  }
});

test('two pinned edges keep each working column whole inside the remaining space', () => {
  for (const width of [390, 1280]) {
    const d = new Desktop(); d.execute('pin'); d.focus('safari-home'); d.execute('pin');
    for (const id of ['finder-work', 'terminal-dev', 'mail-inbox']) {
      d.focus(id);
      const frames = d.layout(width, 600), left = frames.get('notes-week'), right = frames.get('safari-home');
      const start = left.x + left.w + d.gap, end = right.x - d.gap;
      for (const frame of frames.values()) {
        if (frame.pinned || frame.floating) continue;
        assert(Math.abs(frame.x - start) < .001);
        assert(Math.abs(frame.x + frame.w - end) < .001);
      }
    }
  }
});

test('wrapping focus at either end moves windows without resizing them', () => {
  for (const width of [390, 1280]) {
    const d = new Desktop(); d.focus('mail-inbox');
    const before = d.layout(width, 600);
    d.navigate(1);
    const after = d.layout(width, 600);
    for (const [id, frame] of before) assert.equal(after.get(id).w, frame.w, `${id} changes width when focus wraps`);
    d.navigate(-1);
    for (const [id, frame] of before) assert.equal(d.layout(width, 600).get(id).w, frame.w);
    assert.equal(d.swipe(1), false);
    assert.deepEqual(d.layout(width, 600), before, 'An outward swipe keeps both dimensions and focus');
  }
});


test('every tour step keeps a window on screen instead of showing an empty desktop', async () => {
  const { createDesktopTour } = await import('../src/components/calmon-desktop/tour.mjs');
  const d = new Desktop();
  for (const step of createDesktopTour(d)) {
    step.prepare?.(); step.run(); d.clean();
    assert([...d.layout(1280, 800, 64).values()].some(frame => frame.x < 1280 && frame.x + frame.w > 0),
      `Caption ${step.caption} leaves the viewer on an empty desktop`);
  }
});
