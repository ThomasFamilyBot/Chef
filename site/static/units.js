// Unit math shared by the shopping list. House units: g, tsp, TBLS, cup, oz (weight), fl oz, lb.
(function (global) {
  const VOL = { tsp: 1, TBLS: 3, 'fl oz': 6, cup: 48, pint: 96, quart: 192, gallon: 768 };
  const WT = { g: 1, oz: 28.3495, lb: 453.592 };
  const EPS = 0.02;

  function family(unit) {
    if (unit in VOL) return 'volume';
    if (unit in WT) return 'weight';
    return 'count:' + unit;
  }

  // nice fraction for a number, to eighths/thirds
  function frac(x) {
    const whole = Math.floor(x + 1e-9);
    let rem = x - whole;
    const cands = [[0, ''], [1 / 8, '1/8'], [1 / 4, '1/4'], [1 / 3, '1/3'], [3 / 8, '3/8'], [1 / 2, '1/2'], [5 / 8, '5/8'], [2 / 3, '2/3'], [3 / 4, '3/4'], [7 / 8, '7/8'], [1, '']];
    let best = cands[0];
    for (const c of cands) if (Math.abs(c[0] - rem) < Math.abs(best[0] - rem)) best = c;
    let w = whole, f = best[1];
    if (best[0] === 1) { w += 1; f = ''; }
    if (Math.abs(best[0] - rem) > 0.06 && rem > 0) return (Math.round(x * 100) / 100).toString();
    if (w && f) return `${w} ${f}`;
    if (f) return f;
    return `${w}`;
  }

  function fmtVolume(tsp, allFlOz) {
    if (allFlOz) {
      const fl = tsp / 6;
      if (fl >= 8 - EPS) {
        const cups = fl / 8;
        const r = frac(cups);
        if (!r.includes('.')) return r + (cups > 1 + EPS ? ' cups' : ' cup');
      }
      return frac(fl) + ' fl oz';
    }
    const parts = [];
    let rem = tsp;
    if (rem >= 12 - EPS) {
      const whole = Math.floor(rem / 48 + EPS);
      rem -= whole * 48;
      const fr = [[36, '3/4'], [32, '2/3'], [24, '1/2'], [16, '1/3'], [12, '1/4']];
      let fs = '';
      for (const [t, s] of fr) if (rem >= t - EPS) { fs = s; rem -= t; break; }
      if (whole || fs) parts.push(`${whole ? whole : ''}${whole && fs ? ' ' : ''}${fs} ${(whole + (fs ? 0.5 : 0)) > 1 ? 'cups' : 'cup'}`.trim());
    }
    if (rem > EPS) {
      const tb = Math.floor(rem / 3 + EPS);
      rem -= tb * 3;
      if (tb) parts.push(`${tb} TBLS`);
      if (rem > EPS) parts.push(`${frac(rem)} tsp`);
    }
    return parts.join(' + ') || '0';
  }

  function fmtWeight(g, allGrams) {
    if (allGrams) return `${Math.round(g)} g`;
    const oz = g / WT.oz;
    if (oz >= 16 - EPS) {
      const lb = oz / 16;
      const q = Math.round(lb * 4) / 4;
      if (Math.abs(q - lb) < 0.03) return `${frac(q)} lb`;
      const w = Math.floor(lb);
      return `${w} lb ${frac(oz - w * 16)} oz`;
    }
    return `${frac(oz)} oz`;
  }

  const PLURAL = { bunch: 'bunches', head: 'heads', clove: 'cloves', sprig: 'sprigs', stalk: 'stalks', can: 'cans', jar: 'jars', bottle: 'bottles', container: 'containers', package: 'packages', box: 'boxes', bag: 'bags', loaf: 'loaves', stick: 'sticks', slice: 'slices', ear: 'ears', fillet: 'fillets', piece: 'pieces', sheet: 'sheets', leaf: 'leaves', rack: 'racks', pinch: 'pinches', dash: 'dashes', dozen: 'dozen' };

  function fmtCount(n, unit) {
    if (unit === 'each' || unit === 'whole') return frac(n);
    if (unit === 'to taste') return 'to taste';
    if (unit === 'large' || unit === 'medium' || unit === 'small') return `${frac(n)} ${unit}`;
    const u = n > 1 + EPS ? (PLURAL[unit] || unit) : unit;
    return `${frac(n)} ${u}`;
  }

  // entries: [{item, qty, unit, section, from}] -> merged rows
  function merge(entries) {
    const rows = new Map();
    for (const e of entries) {
      if (e.shop === false) continue;
      const fam = family(e.unit);
      const key = e.item.trim().toLowerCase() + '|' + fam;
      let r = rows.get(key);
      if (!r) { r = { item: e.item.trim(), fam, unit: e.unit, section: e.section, total: 0, units: new Set(), from: [] }; rows.set(key, r); }
      const q = Number(e.qty) || 0;
      if (fam === 'volume') r.total += q * VOL[e.unit];
      else if (fam === 'weight') r.total += q * WT[e.unit];
      else r.total += q;
      r.units.add(e.unit);
      if (e.from && !r.from.includes(e.from)) r.from.push(e.from);
      if (!r.section || r.section === 'Other') r.section = e.section;
    }
    const out = [];
    for (const r of rows.values()) {
      let text;
      const us = [...r.units];
      if (r.fam === 'volume' && us.length === 1 && (us[0] === 'gallon' || us[0] === 'quart' || us[0] === 'pint')) text = `${frac(r.total / VOL[us[0]])} ${us[0]}${r.total / VOL[us[0]] > 1 + EPS ? 's' : ''}`;
      else if (r.fam === 'volume') text = fmtVolume(r.total, us.every(u => u === 'fl oz'));
      else if (r.fam === 'weight') text = fmtWeight(r.total, [...r.units].every(u => u === 'g'));
      else text = fmtCount(r.total, r.unit);
      out.push({ item: r.item, section: r.section || 'Other', amount: text, from: r.from, key: r.item.toLowerCase() + '|' + r.fam });
    }
    return out;
  }

  global.Units = { merge, fmtVolume, fmtWeight, fmtCount, frac, family };
})(window);
