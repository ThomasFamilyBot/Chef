// Chef site behaviour.
// Shopping lists: one named list per person. State lives on the phone (localStorage) and, when
// CHEF_CFG.api is set, is mirrored to the family Google Sheet through the Apps Script web app so every
// phone sees the same list. Last write wins per list; other phones re-pull every 15 s while open.
(function (global) {
  const CFG = global.CHEF_CFG || { api: '', lists: ['Household'] };
  const LIST_KEY = 'chef.list';
  let DATA = null;
  let rerender = null;           // set by shopPage; called after a remote update
  let pushTimer = null, pulling = false;

  function base() { return document.querySelector('nav .brand').getAttribute('href').replace('index.html', ''); }
  async function data() {
    if (DATA) return DATA;
    const res = await fetch(base() + 'recipes.json', { cache: 'no-cache' });
    DATA = await res.json();
    return DATA;
  }

  /* ---------- per-list state ---------- */
  function listName() { try { const n = localStorage.getItem(LIST_KEY); if (n && CFG.lists.includes(n)) return n; } catch {} return CFG.lists[0]; }
  function setListName(n) { try { localStorage.setItem(LIST_KEY, n); } catch {} }
  function emptyState() { return { sel: { r: {}, t: [], m: [] }, custom: [], checked: {}, updated: 0 }; }
  function stateKey(n) { return 'chef.list.' + n; }
  function getState(n) {
    n = n || listName();
    try {
      const raw = localStorage.getItem(stateKey(n));
      if (raw) { const s = JSON.parse(raw); return { sel: { r: s.sel?.r || {}, t: s.sel?.t || [], m: s.sel?.m || [] }, custom: s.custom || [], checked: s.checked || {}, updated: s.updated || 0 }; }
      // one-time migration from the pre-list storage
      if (n === CFG.lists[0]) {
        const old = JSON.parse(localStorage.getItem('chef.selection.v1') || 'null');
        if (old) {
          const s = { sel: { r: old.r || {}, t: old.t || [], m: old.m || [] }, custom: JSON.parse(localStorage.getItem('chef.custom.v1') || '[]'), checked: JSON.parse(localStorage.getItem('chef.checked.v1') || '{}'), updated: Date.now() };
          localStorage.setItem(stateKey(n), JSON.stringify(s)); ['chef.selection.v1', 'chef.custom.v1', 'chef.checked.v1'].forEach(k => localStorage.removeItem(k));
          return s;
        }
      }
    } catch {}
    return emptyState();
  }
  function saveState(s, { remote = true } = {}) {
    s.updated = Date.now();
    try { localStorage.setItem(stateKey(listName()), JSON.stringify(s)); } catch {}
    updateNav();
    if (remote) pushSoon();
  }
  const getSel = () => getState().sel;
  function setSel(sel) { const s = getState(); s.sel = sel; saveState(s); }
  const getCustom = () => getState().custom;
  function setCustom(list) { const s = getState(); s.custom = list; saveState(s); }
  function addCustom(section, amount, item) { const l = getCustom(); l.push({ id: 'c' + Date.now() + Math.random().toString(36).slice(2, 6), section, amount: amount || '', item: item || '' }); setCustom(l); }
  const checked = () => getState().checked;
  function setChecked(c) { const s = getState(); s.checked = c; saveState(s); }

  /* ---------- sync with the shared sheet ---------- */
  function status(msg, cls) { const el = document.getElementById('sync-status'); if (el) { el.textContent = msg; el.className = 'muted small sync ' + (cls || ''); } }
  function pushSoon() { if (!CFG.api) return; clearTimeout(pushTimer); status('Saving…', 'busy'); pushTimer = setTimeout(push, 800); }
  async function push() {
    if (!CFG.api) return;
    const name = listName(), s = getState(name);
    try {
      const res = await fetch(CFG.api, { method: 'POST', body: JSON.stringify({ list: name, updated: s.updated, state: { sel: s.sel, custom: s.custom, checked: s.checked } }), headers: { 'Content-Type': 'text/plain;charset=utf-8' }, redirect: 'follow' });
      const txt = await res.text();
      let j; try { j = JSON.parse(txt); } catch (e) { throw new Error(res.status === 403 || /You need access|Sign in/i.test(txt) ? 'access' : 'badjson'); }
      if (j.stale && j.state) { adopt(name, j); status('Updated from another phone', 'ok'); }
      else status('Saved to the shared list', 'ok');
    } catch (e) {
      if (e && e.message === 'access') status('Not saved to the shared sheet: its web app is not set to "Anyone" (fix in Apps Script → Manage deployments). Saved on this phone.', 'warn');
      else status('Offline. Saved on this phone; will sync when back online.', 'warn');
    }
  }
  function adopt(name, j) {
    const s = { sel: { r: j.state.sel?.r || {}, t: j.state.sel?.t || [], m: j.state.sel?.m || [] }, custom: j.state.custom || [], checked: j.state.checked || {}, updated: j.updated || Date.now() };
    try { localStorage.setItem(stateKey(name), JSON.stringify(s)); } catch {}
    updateNav(); if (rerender) rerender();
  }
  async function pull({ quiet = false } = {}) {
    if (!CFG.api || pulling) return;
    pulling = true;
    const name = listName();
    try {
      const res = await fetch(CFG.api + (CFG.api.includes('?') ? '&' : '?') + 'list=' + encodeURIComponent(name) + '&_=' + Date.now(), { redirect: 'follow' });
      const txt = await res.text();
      let j; try { j = JSON.parse(txt); } catch (e) { throw new Error(res.status === 403 || /You need access|Sign in/i.test(txt) ? 'access' : 'badjson'); }
      const local = getState(name);
      if (j.state && (j.updated || 0) > (local.updated || 0)) { adopt(name, j); if (!quiet) status('Updated from the shared list', 'ok'); }
      else if (!j.state && local.updated) { pushSoon(); }     // the sheet has nothing yet; seed it from this phone
      else if (!quiet) status('Shared list · in sync', 'ok');
    } catch (e) {
      if (e && e.message === 'access') status('The shared sheet\'s web app is not set to "Anyone". In Apps Script (as ahinthomas@gmail.com): Deploy → Manage deployments → edit → Who has access: Anyone → New version. Showing this phone\'s copy meanwhile.', 'warn');
      else if (e && e.message === 'badjson') status('The shared sheet replied with something other than list data; check the Apps Script code. Showing this phone\'s copy.', 'warn');
      else if (!quiet) status('Offline. Showing this phone\'s copy.', 'warn');
    }
    finally { pulling = false; }
  }
  function startPolling() {
    if (!CFG.api) { status('Local only. Set up the shared sheet (docs/SHARED_LISTS.md) so every phone sees the same lists.', 'warn'); return; }
    pull();
    setInterval(() => { if (document.visibilityState === 'visible') pull({ quiet: true }); }, 15000);
    document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') pull({ quiet: true }); });
  }

  /* ---------- nav ---------- */
  function updateNav() {
    const s = getState();
    const n = Object.keys(s.sel.r).length + s.sel.t.length;
    const el = document.getElementById('nav-count');
    if (el) el.textContent = n ? n : '';
    document.querySelectorAll('button.add[data-slug]').forEach(b => {
      const on = !!s.sel.r[b.dataset.slug];
      b.textContent = on ? `✓ On ${listName()}'s list` : `+ ${listName()}'s list`;
      b.classList.toggle('on', on);
    });
  }
  function toggleRecipe(slug) { const sel = getSel(); if (sel.r[slug]) delete sel.r[slug]; else sel.r[slug] = 1; setSel(sel); }
  document.addEventListener('click', e => { const b = e.target.closest('button.add[data-slug]'); if (b) toggleRecipe(b.dataset.slug); });

  (function () {
    const b = document.getElementById('theme-toggle'); if (!b) return;
    const apply = () => { const dark = document.documentElement.getAttribute('data-theme') === 'dark'; b.textContent = dark ? '☀' : '☾'; };
    b.addEventListener('click', () => { const dark = document.documentElement.getAttribute('data-theme') === 'dark'; if (dark) document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', 'dark'); try { localStorage.setItem('chef.theme', dark ? 'light' : 'dark'); } catch {} apply(); });
    apply();
  })();
  function setNavHeight() { const n = document.querySelector('nav.nav'); if (n) document.documentElement.style.setProperty('--nav-h', n.offsetHeight + 'px'); }
  window.addEventListener('load', setNavHeight); window.addEventListener('resize', setNavHeight); setNavHeight();

  /* ---------- recipes index ---------- */
  function indexPage() {
    const q = document.getElementById('q'), list = document.getElementById('list');
    const cards = [...list.querySelectorAll('.card')];
    let active = null;
    data().then(d => {
      const tags = new Map();
      d.recipes.forEach(r => (r.tags || []).forEach(t => tags.set(t, (tags.get(t) || 0) + 1)));
      const box = document.getElementById('tags');
      [...tags.entries()].sort((a, b) => b[1] - a[1]).slice(0, 24).forEach(([t, n]) => {
        const s = document.createElement('button'); s.className = 'tag btn'; s.textContent = `${t} (${n})`;
        s.onclick = () => { active = active === t ? null : t; box.querySelectorAll('.tag').forEach(x => x.classList.toggle('on', x.textContent.startsWith(active + ' ('))); apply(); };
        box.appendChild(s);
      });
      apply();
    });
    const fTime = document.getElementById('f-time'), fCourse = document.getElementById('f-course'), fProt = document.getElementById('f-protein'), fHave = document.getElementById('f-have');
    function apply() {
      const text = (q.value || '').toLowerCase().trim();
      const maxT = Number(fTime.value) || 0, course = fCourse.value, prot = fProt.value;
      const have = (fHave.value || '').toLowerCase().split(',').map(s => s.trim()).filter(Boolean);
      let n = 0;
      const byslug = Object.fromEntries((DATA ? DATA.recipes : []).map(r => [r.slug, r]));
      const scored = [];
      cards.forEach(c => {
        const r = byslug[c.dataset.slug];
        const hay = r ? (r.title + ' ' + r.tags.join(' ') + ' ' + r.text).toLowerCase() : c.textContent.toLowerCase();
        let ok = (!text || text.split(/\s+/).every(w => hay.includes(w))) && (!active || (r && r.tags.includes(active)));
        if (ok && r && maxT) { const tt = r.times && (r.times.total || r.times.cook); ok = !!tt && tt <= maxT; }
        if (ok && r && course) ok = r.tags.includes(course);
        if (ok && r && prot) ok = r.tags.includes(prot);
        let hits = 0;
        if (ok && r && have.length) { const items = r.ingredients.map(i => i.item.toLowerCase()); hits = have.filter(h => items.some(it => it.includes(h))).length; ok = hits > 0; }
        c.hidden = !ok; if (ok) n++;
        const badge = c.querySelector('.match'); if (badge) badge.remove();
        if (ok && have.length) { const b = document.createElement('span'); b.className = 'tag match'; b.textContent = have.length > 1 ? `${hits}/${have.length} ingredients` : 'ingredient match'; c.querySelector('.card-title').after(b); }
        scored.push([c, ok ? hits : -1]);
      });
      if (have.length) { scored.sort((a, b) => b[1] - a[1]).forEach(([c]) => list.appendChild(c)); }
      document.getElementById('empty').hidden = n > 0;
      const cnt = document.getElementById('count'); if (cnt) cnt.textContent = (text || maxT || course || prot || have.length || active) ? `${n} of ${cards.length} recipes` : '';
    }
    q.addEventListener('input', apply);
    [fTime, fCourse, fProt].forEach(el => el.addEventListener('change', apply));
    fHave.addEventListener('input', apply);
    updateNav();
  }

  function recipePage() { updateNav(); }

  /* ---------- share links ---------- */
  function parseHash() {
    const h = location.hash.replace(/^#/, '');
    if (!h) return null;
    const p = new URLSearchParams(h);
    const sel = { r: {}, t: [], m: [] };
    (p.get('r') || '').split(',').filter(Boolean).forEach(x => { const [slug, m] = x.split(':'); sel.r[slug] = Math.max(1, Number(m) || 1); });
    sel.t = (p.get('t') || '').split(',').filter(Boolean);
    sel.m = (p.get('m') || '').split(',').filter(Boolean);
    const custom = (p.get('c') || '').split(';').filter(Boolean).map((s, i) => { const [section, amount, item] = s.split('~').map(x => decodeURIComponent(x)); return { id: 'h' + i + '_' + Date.now(), section, amount, item }; });
    return { sel, custom };
  }
  function toHash(s) {
    const r = Object.entries(s.sel.r).map(([k, m]) => m > 1 ? `${k}:${m}` : k).join(',');
    const t = s.sel.t.join(','), m = (s.sel.m || []).join(',');
    const c = s.custom.map(x => [x.section, x.amount || '', x.item || ''].map(encodeURIComponent).join('~')).join(';');
    return [r ? `r=${r}` : '', t ? `t=${t}` : '', m ? `m=${m}` : '', c ? `c=${c}` : ''].filter(Boolean).join('&');
  }

  /* ---------- menus ---------- */
  function addMenu(id, on) {
    return data().then(d => {
      const m = d.menus.find(x => x.id === id); if (!m) return;
      const s = getState();
      s.sel.m = s.sel.m.filter(x => x !== id);
      if (on) { s.sel.m.push(id); m.slugs.forEach(slug => { if (!s.sel.r[slug]) s.sel.r[slug] = 1; }); }
      else { const keep = new Set(d.menus.filter(x => s.sel.m.includes(x.id)).flatMap(x => x.slugs)); m.slugs.forEach(slug => { if (!keep.has(slug)) delete s.sel.r[slug]; }); }
      saveState(s);
    });
  }
  function menusPage() {
    updateNav();
    document.querySelectorAll('button.add-menu').forEach(b => b.addEventListener('click', () => addMenu(b.dataset.menu, true).then(() => { b.textContent = `✓ Added to ${listName()}'s list`; b.classList.add('on'); })));
  }

  /* ---------- shopping list page ---------- */
  function shopPage() {
    const fromHash = parseHash();
    if (fromHash) { const s = getState(); s.sel = fromHash.sel; if (fromHash.custom.length) s.custom = fromHash.custom; saveState(s); }
    const groups = document.getElementById('groups');
    const picks = document.querySelectorAll('input[data-recipe]'), tpicks = document.querySelectorAll('input[data-template]');
    const mults = document.querySelectorAll('input[data-mult]');

    // list switch
    const sw = document.getElementById('list-switch');
    if (sw) {
      CFG.lists.forEach(n => { const b = document.createElement('button'); b.className = 'btn small'; b.textContent = n; b.dataset.list = n; b.addEventListener('click', () => { setListName(n); syncSwitch(); syncPicker(); render(); updateNav(); pull(); }); sw.appendChild(b); });
    }
    function syncSwitch() { if (sw) sw.querySelectorAll('button').forEach(b => b.classList.toggle('on', b.dataset.list === listName())); }

    function syncPicker() {
      const s = getState();
      picks.forEach(i => i.checked = !!s.sel.r[i.dataset.recipe]);
      const ul = document.getElementById('pick-recipes');
      if (ul) {
        const items = [...ul.querySelectorAll('li')];
        items.sort((a, b) => { const sa = !!s.sel.r[a.querySelector('input[data-recipe]').dataset.recipe], sb = !!s.sel.r[b.querySelector('input[data-recipe]').dataset.recipe]; if (sa !== sb) return sa ? -1 : 1; return a.dataset.title.localeCompare(b.dataset.title); });
        items.forEach(li => { li.classList.toggle('selected', !!s.sel.r[li.querySelector('input[data-recipe]').dataset.recipe]); ul.appendChild(li); });
      }
      mults.forEach(i => i.value = s.sel.r[i.dataset.mult] || 1);
      tpicks.forEach(i => i.checked = s.sel.t.includes(i.dataset.template));
      document.querySelectorAll('input[data-menu]').forEach(i => { i.checked = s.sel.m.includes(i.dataset.menu); });
    }
    picks.forEach(i => i.addEventListener('change', () => { const s = getState(); if (i.checked) s.sel.r[i.dataset.recipe] = Number(document.querySelector(`input[data-mult="${i.dataset.recipe}"]`).value) || 1; else { delete s.sel.r[i.dataset.recipe]; if (DATA) s.sel.m = s.sel.m.filter(id => { const m = DATA.menus.find(x => x.id === id); return !(m && m.slugs.includes(i.dataset.recipe)); }); } saveState(s); syncPicker(); render(); }));
    mults.forEach(i => i.addEventListener('change', () => { const s = getState(); if (s.sel.r[i.dataset.mult]) { s.sel.r[i.dataset.mult] = Math.max(1, Number(i.value) || 1); saveState(s); render(); } }));
    tpicks.forEach(i => i.addEventListener('change', () => { const s = getState(); s.sel.t = s.sel.t.filter(t => t !== i.dataset.template); if (i.checked) s.sel.t.push(i.dataset.template); saveState(s); render(); }));
    document.querySelectorAll('input[data-menu]').forEach(i => i.addEventListener('change', () => addMenu(i.dataset.menu, i.checked).then(() => { syncPicker(); render(); })));
    document.getElementById('clear-sel').onclick = () => { const s = getState(); s.sel = { r: {}, t: [], m: [] }; s.custom = []; s.checked = {}; saveState(s); syncPicker(); render(); };
    document.getElementById('uncheck').onclick = () => { setChecked({}); render(); };
    document.getElementById('blank-all').onclick = () => { data().then(d => { const l = getCustom(); d.sections.forEach(sec => l.push({ id: 'c' + Date.now() + Math.random().toString(36).slice(2, 6), section: sec, amount: '', item: '' })); setCustom(l); render(); }); };
    document.getElementById('blank-one').onclick = () => { addCustom('Other', '', ''); render(); };
    document.getElementById('clear-custom').onclick = () => { setCustom([]); render(); };
    document.getElementById('hide-checked').onchange = render;
    document.getElementById('pick-q').addEventListener('input', e => { const t = e.target.value.toLowerCase(); document.querySelectorAll('#pick-recipes li').forEach(li => li.hidden = t && !li.dataset.title.includes(t)); });
    document.getElementById('share').onclick = async () => {
      const url = location.origin + location.pathname + '#' + toHash(getState());
      try { await navigator.clipboard.writeText(url); document.getElementById('share').textContent = 'Link copied!'; } catch { prompt('Copy this link:', url); }
      setTimeout(() => document.getElementById('share').textContent = 'Copy share link', 2000);
    };

    const esc = s => String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
    async function render() {
      const d = await data();
      const st = getState(), s = st.sel;
      history.replaceState(null, '', location.pathname + (Object.keys(s.r).length || s.t.length || s.m.length || st.custom.length ? '#' + toHash(st) : ''));
      const entries = [], names = [];
      const byslug = Object.fromEntries(d.recipes.map(r => [r.slug, r]));
      for (const t of d.templates) if (s.t.includes(t.slug)) { names.push(t.name); t.items.forEach(i => entries.push({ ...i, section: i.section_resolved || i.section, from: t.name })); }
      for (const [slug, m] of Object.entries(s.r)) { const r = byslug[slug]; if (!r) continue; names.push(m > 1 ? `${r.title} ×${m}` : r.title); r.ingredients.forEach(i => entries.push({ ...i, qty: (Number(i.qty) || 0) * m, from: r.title })); }
      const rows = Units.merge(entries);
      const order = d.sections;
      rows.sort((a, b) => (order.indexOf(a.section) - order.indexOf(b.section)) || a.item.localeCompare(b.item));
      const ck = st.checked, hide = document.getElementById('hide-checked').checked;
      const custom = st.custom;
      const sections = [...new Set([...rows.map(r => r.section), ...custom.map(c => c.section)])];
      sections.sort((a, b) => order.indexOf(a) - order.indexOf(b));
      groups.innerHTML = '';
      for (const sec of sections) {
        const secRows = rows.filter(r => r.section === sec && !(hide && ck[r.key]));
        const secCustom = custom.filter(c => c.section === sec && !(hide && ck['custom:' + c.id]));
        if (!secRows.length && !secCustom.length) continue;
        const h = document.createElement('h3'); h.innerHTML = `${esc(sec)} <button class="btn small plus no-print" title="Add your own item to ${esc(sec)}">+</button>`;
        h.querySelector('button').addEventListener('click', () => { addCustom(sec, '', ''); render().then(() => { const last = groups.querySelector(`li.custom[data-sec="${CSS.escape(sec)}"]:last-of-type input.item`); if (last) last.focus(); }); });
        groups.appendChild(h);
        const ul = document.createElement('ul'); ul.className = 'checklist'; groups.appendChild(ul);
        for (const r of secRows) {
          const li = document.createElement('li');
          li.className = ck[r.key] ? 'done' : '';
          li.innerHTML = `<label><input type="checkbox" ${ck[r.key] ? 'checked' : ''}> <span class="amt">${esc(r.amount)}</span> <span class="item">${esc(r.item)}</span> <span class="from muted small">${esc(r.from.join(', '))}</span></label>`;
          li.querySelector('input').addEventListener('change', e => { const c = checked(); if (e.target.checked) c[r.key] = 1; else delete c[r.key]; setChecked(c); li.classList.toggle('done', e.target.checked); if (hide) render(); });
          ul.appendChild(li);
        }
        for (const c of secCustom) {
          const key = 'custom:' + c.id;
          const li = document.createElement('li');
          li.className = 'custom' + (ck[key] ? ' done' : ''); li.dataset.sec = sec;
          li.innerHTML = `<input type="checkbox" ${ck[key] ? 'checked' : ''}> <input class="amt" placeholder="qty" value="${esc(c.amount)}"> <input class="item" placeholder="your item" value="${esc(c.item)}"> <button class="btn small x no-print" title="Remove">×</button>`;
          li.querySelector('input[type=checkbox]').addEventListener('change', e => { const k = checked(); if (e.target.checked) k[key] = 1; else delete k[key]; setChecked(k); li.classList.toggle('done', e.target.checked); if (hide) render(); });
          const save = () => { const l = getCustom(); const row = l.find(x => x.id === c.id); if (row) { row.amount = li.querySelector('input.amt').value; row.item = li.querySelector('input.item').value; setCustom(l); } };
          li.querySelector('input.amt').addEventListener('change', save); li.querySelector('input.item').addEventListener('change', save);
          li.querySelector('button.x').addEventListener('click', () => { setCustom(getCustom().filter(x => x.id !== c.id)); render(); });
          ul.appendChild(li);
        }
      }
      document.getElementById('list-empty').hidden = rows.length > 0 || custom.length > 0;
      document.getElementById('for').textContent = names.length ? 'For: ' + names.join(' · ') : '';
      const nCustom = custom.length;
      document.getElementById('list-title').textContent = `${listName()}'s list` + ((names.length || nCustom) ? ` (${rows.length + nCustom} items)` : '');
    }
    rerender = () => { syncPicker(); render(); };
    data().then(() => { syncSwitch(); syncPicker(); render(); updateNav(); startPolling(); });
  }

  global.Chef = { indexPage, recipePage, shopPage, menusPage, addMenu, getSel, setSel, data, listName, pull };
})(window);
