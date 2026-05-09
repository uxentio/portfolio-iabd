/**
 * Apps Script de la hoja "Estación IoT".
 *
 * Expone dos endpoints HTTP cuando se despliega como web app:
 *   - POST  → n8n llama cuando llega una lectura y añade una fila.
 *   - GET   → n8n llama desde el chatbot para leer el histórico.
 *
 * Autor: autor
 */

// =============================================================
// ESCRITURA - n8n añade una fila por cada lectura del ESP32
// =============================================================
function doPost(e) {
  try {
    // Nota sobre el hack del '=':
    // En algunas versiones de n8n las expresiones que empiezan por '='
    // (p.ej. ={{ JSON.stringify(...) }} ) dejan ese carácter al principio
    // del body o de los valores. Si lo escribiésemos tal cual, Google
    // Sheets interpretaría el '=' como fórmula y saldrían #NAME? y #ERROR!.
    // Por eso lo quitamos tanto del JSON completo como de cada campo.
    var raw = e.postData.contents;
    if (raw.charAt(0) === '=') raw = raw.substring(1);
    var datos = JSON.parse(raw);

    var c = function(v) {
      if (v === null || v === undefined || v === 'null') return 'N/A';
      var s = String(v);
      while (s.charAt(0) === '=') s = s.substring(1);
      return s;
    };

    var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    hoja.appendRow([
      c(datos.timestamp),
      c(datos.temp_interior),
      c(datos.humedad_interior),
      c(datos.luz),
      c(datos.presencia),
      c(datos.temp_exterior),
      c(datos.hum_exterior),
      c(datos.viento),
      c(datos.uv),
      c(datos.ciudad),
      c(datos.nivel_alerta)
    ]);

    return ContentService
      .createTextOutput(JSON.stringify({"ok": true}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (error) {
    return ContentService
      .createTextOutput(JSON.stringify({"ok": false, "error": error.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}

// =============================================================
// LECTURA - n8n consulta el historico
// =============================================================
// Uso:
//   ?action=last&n=20    → ultimas N filas
//   ?action=all           → todas las filas
//   ?action=stats         → estadisticas resumen
//   (sin accion)          → ultimas 20 por defecto
// =============================================================
function doGet(e) {
  try {
    var params = e.parameter || {};
    var action = params.action || 'last';
    var n = parseInt(params.n, 10) || 20;

    var hoja = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
    var datos = hoja.getDataRange().getValues();
    if (datos.length <= 1) {
      return respond({"ok": true, "rows": [], "count": 0});
    }

    var cabeceras = datos[0];
    var filas = datos.slice(1);

    // Convertir filas en objetos
    var rows = filas.map(function(fila) {
      var obj = {};
      cabeceras.forEach(function(cab, i) { obj[cab] = fila[i]; });
      return obj;
    });

    if (action === 'all') {
      return respond({"ok": true, "count": rows.length, "rows": rows});
    }

    if (action === 'stats') {
      var tempInt = rows.map(function(r) { return parseFloat(r['Temp_Interior']); }).filter(function(v) { return !isNaN(v); });
      var humInt  = rows.map(function(r) { return parseFloat(r['Humedad']); }).filter(function(v) { return !isNaN(v); });
      var tempExt = rows.map(function(r) { return parseFloat(r['Temp_Exterior']); }).filter(function(v) { return !isNaN(v); });
      return respond({
        "ok": true,
        "count": rows.length,
        "stats": {
          "temp_interior": stats(tempInt),
          "humedad_interior": stats(humInt),
          "temp_exterior": stats(tempExt),
          "primera": rows[0]['Timestamp'],
          "ultima":  rows[rows.length - 1]['Timestamp']
        }
      });
    }

    // Default: ultimas N filas
    var ultimas = rows.slice(-n);
    return respond({"ok": true, "count": ultimas.length, "rows": ultimas});

  } catch (error) {
    return respond({"ok": false, "error": error.toString()});
  }
}

// =============================================================
// HELPERS
// =============================================================
function respond(obj) {
  return ContentService
    .createTextOutput(JSON.stringify(obj))
    .setMimeType(ContentService.MimeType.JSON);
}

function stats(arr) {
  if (arr.length === 0) return null;
  var min = Math.min.apply(null, arr);
  var max = Math.max.apply(null, arr);
  var avg = arr.reduce(function(a, b) { return a + b; }, 0) / arr.length;
  return { min: round(min), max: round(max), avg: round(avg), count: arr.length };
}

function round(v) { return Math.round(v * 100) / 100; }
