// Chef shared shopping lists — Google Apps Script web app.
// Stores one row per list name in the bound Google Sheet (columns: name, updated, state).
// Deploy: Extensions → Apps Script → paste this → Deploy → New deployment → type "Web app",
// Execute as: Me, Who has access: Anyone → Deploy → copy the Web app URL into data/site.yaml (lists_api).

function sheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName('lists') || ss.insertSheet('lists');
  if (sh.getLastRow() === 0) sh.appendRow(['name', 'updated', 'state']);
  return sh;
}
function find_(sh, name) {
  var rows = sh.getDataRange().getValues();
  for (var i = 1; i < rows.length; i++) if (String(rows[i][0]) === name) return i + 1;
  return 0;
}
function out_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
function doGet(e) {
  var name = (e && e.parameter && e.parameter.list) || '';
  if (!name) return out_({ ok: false, error: 'list required' });
  var sh = sheet_(), r = find_(sh, name);
  if (!r) return out_({ ok: true, name: name, updated: 0, state: null });
  var row = sh.getRange(r, 1, 1, 3).getValues()[0];
  var state = null; try { state = JSON.parse(row[2]); } catch (err) {}
  return out_({ ok: true, name: name, updated: Number(row[1]) || 0, state: state });
}
function doPost(e) {
  var body = {}; try { body = JSON.parse(e.postData.contents); } catch (err) { return out_({ ok: false, error: 'bad json' }); }
  var name = body.list, updated = Number(body.updated) || Date.now(), state = body.state;
  if (!name) return out_({ ok: false, error: 'list required' });
  var lock = LockService.getScriptLock(); lock.waitLock(5000);
  try {
    var sh = sheet_(), r = find_(sh, name);
    if (r) {
      var current = Number(sh.getRange(r, 2).getValue()) || 0;
      if (current > updated) {            // someone else saved something newer; hand it back instead
        var st = null; try { st = JSON.parse(sh.getRange(r, 3).getValue()); } catch (err) {}
        return out_({ ok: true, name: name, updated: current, state: st, stale: true });
      }
      sh.getRange(r, 2, 1, 2).setValues([[updated, JSON.stringify(state)]]);
    } else {
      sh.appendRow([name, updated, JSON.stringify(state)]);
    }
    return out_({ ok: true, name: name, updated: updated });
  } finally { lock.releaseLock(); }
}
