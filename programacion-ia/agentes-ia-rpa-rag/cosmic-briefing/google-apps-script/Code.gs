/**
 * Apps Script de la hoja "Cosmic Briefing".
 *
 * Expone los endpoints que el workflow de n8n consume:
 *   - POST                       -> el workflow guarda una fila por cada briefing del dia.
 *   - GET ?action=last&n=N       -> tool 'ultimos_briefings' del AI Agent del chatbot.
 *   - GET ?action=search&q=...   -> tool 'buscar_briefing' del AI Agent del chatbot.
 *   - GET ?action=dashboard      -> panel HTML enlazado en cada mensaje de Telegram del briefing diario.
 *
 * Comentarios tecnicos en ASCII a proposito (regla del proyecto).
 *
 * Autor: autor
 */

// =============================================================
// ESCRITURA - n8n guarda un briefing al dia (rama A del workflow)
// =============================================================
function doPost(e) {
  try {
    var raw = e.postData.contents;
    if (raw.charAt(0) === '=') raw = raw.substring(1);
    var datos = JSON.parse(raw);

    // Strippea '=' al principio de cada valor para que Sheets no lo interprete como formula
    var c = function(v) {
      if (v === null || v === undefined || v === 'null') return 'N/A';
      var s = String(v);
      while (s.charAt(0) === '=') s = s.substring(1);
      return s;
    };

    var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    hoja.appendRow([
      c(datos.timestamp),
      c(datos.fecha),
      c(datos.ciudad),
      c(datos.apod_titulo),
      c(datos.apod_url),
      c(datos.papers),
      c(datos.noticias),
      c(datos.iss_visible),
      c(datos.briefing_llm),
      c(datos.tokens)
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({ ok: true }))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({ ok: false, error: error.toString() }))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// =============================================================
// LECTURA - consumida por las tools del chatbot y por el panel publico
// =============================================================
//   ?action=last&n=N       -> tool 'ultimos_briefings' (chatbot)
//   ?action=search&q=...   -> tool 'buscar_briefing' (chatbot)
//   ?action=dashboard      -> panel HTML enlazado desde Telegram en cada briefing
// =============================================================
function doGet(e) {
  try {
    var params = e.parameter || {};
    var action = params.action || 'last';
    var n = parseInt(params.n, 10) || 10;

    var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var datos = hoja.getDataRange().getValues();

    if (action === 'dashboard') {
      return renderDashboard(datos);
    }

    if (datos.length <= 1) {
      return respond({ ok: true, rows: [], count: 0 });
    }

    var cab = datos[0];
    var filas = datos.slice(1);
    var rows = filas.map(function(fila) {
      var obj = {};
      cab.forEach(function(col, i) { obj[col] = fila[i]; });
      return obj;
    });

    if (action === 'search') {
      var q = (params.q || '').toLowerCase();
      if (!q) return respond({ ok: false, error: 'Falta el parámetro q' });
      var filtradas = rows.filter(function(r) {
        return (r.Briefing_LLM || '').toLowerCase().indexOf(q) >= 0 ||
               (r.Noticias || '').toLowerCase().indexOf(q) >= 0 ||
               (r.Papers || '').toLowerCase().indexOf(q) >= 0 ||
               (r.APOD_Titulo || '').toLowerCase().indexOf(q) >= 0;
      });
      return respond({ ok: true, count: filtradas.length, rows: filtradas });
    }

    // Por defecto: action=last
    var ultimas = rows.slice(-n);
    return respond({ ok: true, count: ultimas.length, rows: ultimas });

  } catch (error) {
    return respond({ ok: false, error: error.toString() });
  }
}

function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

// =============================================================
// DASHBOARD HTML - panel con los ultimos briefings.
// La URL se inserta en cada mensaje de Telegram del briefing
// diario, asi el usuario puede abrir el historico desde el chat.
// =============================================================
function renderDashboard(datos) {
  var rows = datos.slice(1).reverse().slice(0, 14);
  var totalBriefings = datos.length - 1;

  var cards = '';
  rows.forEach(function(r) {
    var fecha = r[1] || '';
    var ciudad = r[2] || '';
    var apodT = r[3] || '';
    var apodU = r[4] || '';
    var briefing = (r[8] || '').toString();
    var iss = r[7] || 'NO';
    var tokens = r[9] || 0;

    cards += '<article class="card">' +
      '<header><h3>' + escapeHtml(apodT) + '</h3>' +
      '<small>' + escapeHtml(fecha) + ' &middot; ' + escapeHtml(ciudad) +
      (iss === 'SI' ? ' &middot; <span class="iss">ISS sobre tu zona</span>' : '') +
      ' &middot; ' + tokens + ' tokens</small></header>' +
      (apodU ? '<a href="' + apodU + '" target="_blank"><img src="' + apodU + '" alt="Imagen astronómica del día" loading="lazy"/></a>' : '') +
      '<p>' + escapeHtml(briefing).replace(/\n/g, '<br>') + '</p>' +
      '</article>';
  });

  var html =
'<!doctype html><html lang="es"><head><meta charset="utf-8">' +
'<meta name="viewport" content="width=device-width,initial-scale=1">' +
'<title>Cosmic Briefing — Panel</title>' +
'<style>' +
'*{box-sizing:border-box;margin:0;padding:0}' +
'body{font-family:-apple-system,BlinkMacSystemFont,system-ui,sans-serif;background:#0a0e27;color:#e0e6f0;line-height:1.5;padding:24px}' +
'header.top{text-align:center;margin-bottom:32px;padding:32px 16px;background:linear-gradient(135deg,#1a1f4a,#0a0e27);border-radius:12px}' +
'h1{font-size:2.4rem;font-weight:700;margin-bottom:8px;background:linear-gradient(90deg,#7dd3fc,#a78bfa);-webkit-background-clip:text;-webkit-text-fill-color:transparent}' +
'header.top p{opacity:.7;font-size:.95rem}' +
'.stats{display:flex;justify-content:center;gap:24px;margin-top:16px;flex-wrap:wrap}' +
'.stat{background:rgba(255,255,255,.05);padding:8px 16px;border-radius:8px}' +
'.stat strong{color:#7dd3fc;display:block;font-size:1.4rem}' +
'.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:20px}' +
'.card{background:#141a3d;border:1px solid #2a3266;border-radius:10px;overflow:hidden;transition:transform .2s,border-color .2s}' +
'.card:hover{transform:translateY(-2px);border-color:#7dd3fc}' +
'.card header{padding:14px 16px;background:rgba(0,0,0,.2)}' +
'.card h3{font-size:1.05rem;margin-bottom:4px;color:#fff}' +
'.card small{color:#8896b8;font-size:.78rem}' +
'.iss{color:#fbbf24;font-weight:600}' +
'.card img{width:100%;height:200px;object-fit:cover;display:block}' +
'.card p{padding:14px 16px;font-size:.9rem;color:#c0c8e0}' +
'footer{text-align:center;margin-top:40px;padding:16px;opacity:.5;font-size:.8rem}' +
'</style></head><body>' +
'<header class="top">' +
'<h1>Cosmic Briefing</h1>' +
'<p>Briefing diario de astronomía, ISS, asteroides, lanzamientos, papers y noticias espaciales.</p>' +
'<div class="stats">' +
'<div class="stat"><strong>' + totalBriefings + '</strong>briefings totales</div>' +
'<div class="stat"><strong>' + rows.length + '</strong>recientes</div>' +
'<div class="stat"><strong>Ollama</strong>LLM local</div>' +
'</div>' +
'</header>' +
'<div class="grid">' + cards + '</div>' +
'<footer>Generado por n8n + Ollama (qwen2.5 + nomic-embed-text). autor.</footer>' +
'</body></html>';

  return HtmlService.createHtmlOutput(html)
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
}

function escapeHtml(s) {
  if (s === null || s === undefined) return '';
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
