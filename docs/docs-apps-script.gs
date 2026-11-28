/**
 * ChefBot Docs: lets scripts/push_docs.py rewrite a recipe's Google Doc in place (same Doc, same link).
 * Setup: docs/DOCS_API.md. Needs the advanced service "Drive API" (v3) switched on under Services.
 *
 * Every request is a POST with JSON: {secret, action, ...}. The secret is set once by the first
 * "claim" request (push_docs.py --setup) and is never in the repo. Only Google Docs that sit in one of
 * the claimed folders can be touched.
 */
var DOC_MIME = 'application/vnd.google-apps.document';

function doPost(e) {
  try {
    return out(handle(JSON.parse(e.postData.contents)));
  } catch (err) {
    return out({ok: false, error: 'exception', detail: String(err)});
  }
}

function doGet() {
  return out({ok: true, service: 'chefbot-docs'});
}

function out(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

function handle(req) {
  var props = PropertiesService.getScriptProperties();
  var secret = props.getProperty('SECRET');
  if (req.action === 'claim') {
    if (secret) return {ok: false, error: 'already claimed'};
    if (!req.secret || req.secret.length < 32 || !req.folders || !req.folders.length) return {ok: false, error: 'bad claim'};
    props.setProperty('SECRET', req.secret);
    props.setProperty('FOLDERS', req.folders.join(','));
    return {ok: true, claimed: true};
  }
  if (!secret || req.secret !== secret) return {ok: false, error: 'forbidden'};
  var folders = (props.getProperty('FOLDERS') || '').split(',');

  if (req.action === 'create') {
    if (folders.indexOf(req.folder) < 0) return {ok: false, error: 'folder not allowed'};
    var made = Drive.Files.create({name: req.title, mimeType: DOC_MIME, parents: [req.folder]},
        Utilities.newBlob(req.html, 'text/html', 'recipe.html'), {fields: 'id,modifiedTime'});
    return {ok: true, id: made.id, modifiedTime: made.modifiedTime, method: 'create'};
  }

  var f = Drive.Files.get(req.id, {fields: 'id,name,mimeType,parents,trashed,createdTime,modifiedTime'});
  if (f.trashed) return {ok: false, error: 'trashed'};
  if (f.mimeType !== DOC_MIME) return {ok: false, error: 'not a Google Doc'};
  if (!(f.parents || []).some(function (p) { return folders.indexOf(p) >= 0; })) return {ok: false, error: 'folder not allowed'};

  if (req.action === 'status') return {ok: true, id: f.id, name: f.name, createdTime: f.createdTime, modifiedTime: f.modifiedTime};

  if (req.action === 'replace') {
    // Don't overwrite a Doc a person has edited since we last wrote it.
    if (!req.force) {
      var modified = new Date(f.modifiedTime).getTime();
      var base = req.lastPushed ? new Date(req.lastPushed).getTime() : new Date(f.createdTime).getTime();
      if (modified - base > 120000) return {ok: false, error: 'edited', modifiedTime: f.modifiedTime};
    }
    var method = 'update';
    try {
      Drive.Files.update({name: req.title || f.name}, req.id, Utilities.newBlob(req.html, 'text/html', 'recipe.html'));
      if (Drive.Files.get(req.id, {fields: 'mimeType'}).mimeType !== DOC_MIME) throw new Error('lost Doc type');
    } catch (err) {
      method = 'copy';
      replaceByCopy(req.id, req.html, req.title || f.name, f.parents[0]);
    }
    var after = Drive.Files.get(req.id, {fields: 'id,modifiedTime'});
    return {ok: true, id: after.id, modifiedTime: after.modifiedTime, method: method,
            text: DocumentApp.openById(req.id).getBody().getText()};
  }
  return {ok: false, error: 'unknown action'};
}

/** Fallback: convert the HTML into a scratch Doc, copy its body over the real Doc, trash the scratch Doc. */
function replaceByCopy(id, html, title, folder) {
  var tmp = Drive.Files.create({name: 'scratch: ' + title, mimeType: DOC_MIME, parents: [folder]},
      Utilities.newBlob(html, 'text/html', 'recipe.html'), {fields: 'id'});
  try {
    var src = DocumentApp.openById(tmp.id).getBody();
    var doc = DocumentApp.openById(id);
    var dst = doc.getBody();
    dst.clear();
    for (var i = 0; i < src.getNumChildren(); i++) {
      var el = src.getChild(i).copy();
      var type = el.getType();
      if (type === DocumentApp.ElementType.PARAGRAPH) dst.appendParagraph(el);
      else if (type === DocumentApp.ElementType.TABLE) dst.appendTable(el);
      else if (type === DocumentApp.ElementType.LIST_ITEM) dst.appendListItem(el);
    }
    if (dst.getNumChildren() > 1) dst.removeChild(dst.getChild(0));
    doc.setName(title);
    doc.saveAndClose();
  } finally {
    Drive.Files.update({trashed: true}, tmp.id);
  }
}
