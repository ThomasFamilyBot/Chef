// Chef site behaviour: selection stored per-phone in localStorage; shareable via URL hash.
(function (global) {
  const KEY = 'chef.selection.v1';
  const CHECK = 'chef.checked.v1';
  const CUSTOM = 'chef.custom.v1';
  let DATA = null;

  function base() { return document.querySelector('nav .brand').getAttribute('href').replace('index.html', ''); }
  async function data() {
    if (DATA) return DATA;
    const res = await fetch(base() + 'recipes.json', { cache: 'no-cache' });
    DATA = await res.json();
    return DATA;
  }
  function getSel() { try { const s = JSON.parse(localStorage.getItem(KEY)) || {}; return { r: s.r || {}, t: s.t || [], m: s.m || [] }; } catch { return { r: {}, t: [], m: [] }; } }
  function setSel(s) { try { localStorage.setItem(KEY, JSON.stringify(s)); } catch {} updateNav(); }
  function getCustom() { try { return JSON.parse(localStorage.getItem(CUSTOM)) || []; } catch { return []; } }
  function setCustom(list) { try { localStorage.setItem(CUSTOM, JSON.stringify(list)); } catch {} }
  function addCustom(section, amount, item) { const l = getCustom(); l.push({ id: 'c' + Date.now() + Math.random().toString(36).slice(2, 6), section, amount: amount || '', item: item || '' }); setCustom(l); }

  function updateNav() {
    const s = getSel();
    const n = Object.keys(s.r).length + s.t.length;
    const el = document.getElementById('nav-count');
    if (el) el.textContent = n ? n : '';
    document.querySelectorAll('button.add[data-slug]').forEach(b => {
      const on = !!s.r[b.dataset.slug];
      b.textContent = on ? '✓ On shopping list' : '+ Shopping list';
      b.classList.toggle('on', on);
    });
  }
  function toggleRecipe(slug) {
    const s = getSel();
    if (s.r[slug]) delete s.r[slug]; else s.r[slug] = 1;
    setSel(s);
  }
  document.addEventListener('click', e => {
    const b = e.target.closest('button.add[data-slug]');
    if (b) { toggleRecipe(b.dataset.slug); }
  });

  (function () {
    const b = document.getElementById('theme-toggle'); if (!b) return;
    const apply = () => { const dark = document.documentElement.getAttribute('data-theme') === 'dark'; b.textContent = dark ? '☀' : '☾'; };
    b.addEventListener('click', () => { const dark = document.documentElement.getAttribute('data-theme') === 'dark'; if (dark) document.documentElement.removeAttribute('data-theme'); else document.documentElement.setAttribute('data-theme', 'dark'); try { localStorage.setItem('chef.theme', dark ? 'light' : 'dark'); } catch {} apply(); });
    apply();
  })();
  function setNavHeight() { const n = document.querySelector('nav.nav'); if (n) document.documentElement.style.setProperty('--nav-h', n.offsetHeight + 'px'); }
  window.addEventListener('load', setNavHeight); window.addEventListener('resize', setNavHeight); setNavHeight();

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
        if (ok && r && have.length) {
          const items = r.ingredients.map(i => i.item.toLowerCase());
          hits = have.filter(h => items.some(it => it.includes(h))).length;
          ok = hits > 0;
        }
        c.hidden = !ok; if (ok) n++;
        const badge = c.querySelector('.match');
        if (badge) badge.remove();
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

  function parseHash() {
    const h = location.hash.replace(/^#/, '');
    if (!h) return null;
    const p = new URLSearchParams(h);
    const sel = { r: {}, t: [], m: [] };
    (p.get('r') || '').split(',').filter(Boolean).forEach(x => { const [slug, m] = x.split(':'); sel.r[slug] = Math.max(1, Number(m) || 1); });
    sel.t = (p.get('t') || '').split(',').filter(Boolean);
    sel.m = (p.get('m') || '').split(',').filter(Boolean);
    sel.c = (p.get('c') || '').split(';').filter(Boolean).map((s, i) => { const [section, amount, item] = s.split('~').map(x => decodeURIComponent(x)); return { id: 'h' + i + '_' + Date.now(), section, amount, item }; });
    return sel;
  }
  function toHash(sel) {
    const r = Object.entries(sel.r).map(([s, m]) => m > 1 ? `${s}:${m}` : s).join(',');
    const t = sel.t.join(',');
    const m = (sel.m || []).join(',');
    const c = (getCustom()).map(x => [x.section, x.amount || '', x.item || ''].map(encodeURIComponent).join('~')).join(';');
    return [r ? `r=${r}` : '', t ? `t=${t}` : '', m ? `m=${m}` : '', c ? `c=${c}` : ''].filter(Boolean).join('&');
  }

  function shopPage() {
    const fromHash = parseHash();
    if (fromHash) { setSel({ r: fromHash.r, t: fromHash.t, m: fromHash.m }); if (fromHash.c && fromHash.c.length) setCustom(fromHash.c); }
    const groups = document.getElementById('groups');
    const picks = document.querySelectorAll('input[data-recipe]'), tpicks = document.querySelectorAll('input[data-template]');
    const mults = document.querySelectorAll('input[data-mult]');
    function checked() { try { return JSON.parse(localStorage.getItem(CHECK)) || {}; } catch { return {}; } }
    function setChecked(c) { try { localStorage.setItem(CHECK, JSON.stringify(c)); } catch {} }

    function syncPicker() {
      const s = getSel();
      picks.forEach(i => i.checked = !!s.r[i.dataset.recipe]);
      // selected recipes float to the top of the picker so they are easy to find and uncheck
      const ul = document.getElementById('pick-recipes');
      if (ul) {
        const items = [...ul.querySelectorAll('li')];
        items.sort((a, b) => {
          const sa = !!s.r[a.querySelector('input[data-recipe]').dataset.recipe], sb = !!s.r[b.querySelector('input[data-recipe]').dataset.recipe];
          if (sa !== sb) return sa ? -1 : 1;
          return a.dataset.title.localeCompare(b.dataset.title);
        });
        items.forEach(li => { li.classList.toggle('selected', !!s.r[li.querySelector('input[data-recipe]').dataset.recipe]); ul.appendChild(li); });
      }
      mults.forEach(i => i.value = s.r[i.dataset.mult] || 1);
      tpicks.forEach(i => i.checked = s.t.includes(i.dataset.template));
      document.querySelectorAll('input[data-menu]').forEach(i => { i.checked = s.m.includes(i.dataset.menu); });
    }
    picks.forEach(i => i.addEventListener('change', () => { const s = getSel(); if (i.checked) s.r[i.dataset.recipe] = Number(document.querySelector(`input[data-mult="${i.dataset.recipe}"]`).value) || 1; else { delete s.r[i.dataset.recipe]; if (DATA) s.m = s.m.filter(id => { const m = DATA.menus.find(x => x.id === id); return !(m && m.slugs.includes(i.dataset.recipe)); }); } setSel(s); syncPicker(); render(); }));
    mults.forEach(i => i.addEventListener('change', () => { const s = getSel(); if (s.r[i.dataset.mult]) { s.r[i.dataset.mult] = Math.max(1, Number(i.value) || 1); setSel(s); render(); } }));
    tpicks.forEach(i => i.addEventListener('change', () => { const s = getSel(); s.t = s.t.filter(t => t !== i.dataset.template); if (i.checked) s.t.push(i.dataset.template); setSel(s); render(); }));
    document.querySelectorAll('input[data-menu]').forEach(i => i.addEventListener('change', () => addMenu(i.dataset.menu, i.checked).then(() => { syncPicker(); render(); })));
    document.getElementById('clear-sel').onclick = () => { setSel({ r: {}, t: [], m: [] }); syncPicker(); render(); };
    document.getElementById('uncheck').onclick = () => { setChecked({}); render(); };
    document.getElementById('blank-all').onclick = () => { data().then(d => { d.sections.forEach(sec => addCustom(sec, '', '')); render(); }); };
    document.getElementById('blank-one').onclick = () => { addCustom('Other', '', ''); render(); };
    document.getElementById('clear-custom').onclick = () => { setCustom([]); render(); };
    document.getElementById('hide-checked').onchange = render;
    document.getElementById('pick-q').addEventListener('input', e => {
      const t = e.target.value.toLowerCase();
      document.querySelectorAll('#pick-recipes li').forEach(li => li.hidden = t && !li.dataset.title.includes(t));
    });
    document.getElementById('share').onclick = async () => {
      const url = location.origin + location.pathname + '#' + toHash(getSel());
      try { await navigator.clipboard.writeText(url); document.getElementById('share').textContent = 'Link copied!'; }
      catch { prompt('Copy this link:', url); }
      setTimeout(() => document.getElementById('share').textContent = 'Copy share link', 2000);
    };

    async function render() {
      const d = await data();
      const s = getSel();
      history.replaceState(null, '', location.pathname + (Object.keys(s.r).length || s.t.length || s.m.length || getCustom().length ? '#' + toHash(s) : ''));
      const entries = [], names = [];
      const byslug = Object.fromEntries(d.recipes.map(r => [r.slug, r]));
      for (const t of d.templates) if (s.t.includes(t.slug)) { names.push(t.name); t.items.forEach(i => entries.push({ ...i, section: i.section_resolved || i.section, from: t.name })); }
      for (const [slug, m] of Object.entries(s.r)) {
        const r = byslug[slug]; if (!r) continue;
        names.push(m > 1 ? `${r.title} ×${m}` : r.title);
        r.ingredients.forEach(i => entries.push({ ...i, qty: (Number(i.qty) || 0) * m, from: r.title }));
      }
      const rows = Units.merge(entries);
      const order = d.sections;
      rows.sort((a, b) => (order.indexOf(a.section) - order.indexOf(b.section)) || a.item.localeCompare(b.item));
      const ck = checked(), hide = document.getElementById('hide-checked').checked;
      const custom = getCustom();
      const sections = [...new Set([...rows.map(r => r.section), ...custom.map(c => c.section)])];
      sections.sort((a, b) => order.indexOf(a) - order.indexOf(b));
      groups.innerHTML = '';
      const esc = s => String(s).replace(/[&<>"]/g, ch => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]));
      for (const sec of sections) {
        const secRows = rows.filter(r => r.section === sec && !(hide && ck[r.key]));
        const secCustom = custom.filter(c => c.section === sec && !(hide && ck['custom:' + c.id]));
        if (!secRows.length && !secCustom.length) continue;
        const h = document.createElement('h3'); h.innerHTML = `${esc(sec)} <button class="btn small plus no-print" title="Add your own item to ${esc(sec)}">+</button>`;
        h.querySelector('button').addEventListener('click', () => { addCustom(sec, '', ''); render(); setTimeout(() => { const last = groups.querySelector(`li.custom[data-sec="${CSS.escape(sec)}"]:last-of-type input.item`); if (last) last.focus(); }, 0); });
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
          const save = () => { const l = getCustom(); const row = l.find(x => x.id === c.id); if (row) { row.amount = li.querySelector('input.amt').value; row.item = li.querySelector('input.item').value; setCustom(l); } history.replaceState(null, '', location.pathname + '#' + toHash(getSel())); };
          li.querySelector('input.amt').addEventListener('change', save); li.querySelector('input.item').addEventListener('change', save);
          li.querySelector('button.x').addEventListener('click', () => { setCustom(getCustom().filter(x => x.id !== c.id)); render(); });
          ul.appendChild(li);
        }
      }
      document.getElementById('list-empty').hidden = rows.length > 0 || custom.length > 0;
      document.getElementById('for').textContent = names.length ? 'For: ' + names.join(' · ') : '';
      const nCustom = getCustom().length;
      document.getElementById('list-title').textContent = (names.length || nCustom) ? `Shopping list (${rows.length + nCustom} items)` : 'Your list';
    }
    data().then(() => { syncPicker(); render(); updateNav(); });
  }

  function addMenu(id, on) {
    return data().then(d => {
      const m = d.menus.find(x => x.id === id); if (!m) return;
      const s = getSel();
      s.m = s.m.filter(x => x !== id);
      if (on) { s.m.push(id); m.slugs.forEach(slug => { if (!s.r[slug]) s.r[slug] = 1; }); }
      else {
        // drop this menu's recipes unless another selected menu still needs them
        const keep = new Set(d.menus.filter(x => s.m.includes(x.id)).flatMap(x => x.slugs));
        m.slugs.forEach(slug => { if (!keep.has(slug)) delete s.r[slug]; });
      }
      setSel(s);
    });
  }
  function menusPage() {
    updateNav();
    document.querySelectorAll('button.add-menu').forEach(b => b.addEventListener('click', () => addMenu(b.dataset.menu, true).then(() => { b.textContent = '✓ Added — open Shopping List'; b.classList.add('on'); })));
  }

  global.Chef = { indexPage, recipePage, shopPage, menusPage, addMenu, getSel, setSel, data };
})(window);
