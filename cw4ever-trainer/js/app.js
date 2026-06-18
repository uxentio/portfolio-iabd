// app.js — Lógica del entrenador CW: generación de sesiones, práctica de copia y estadísticas

import { CWPlayer } from './audio.js';
import {
  MORSE, KOCH_ORDER, GROUPS, ABBREVIATIONS,
  timing, textToEvents,
} from './morse.js';

const player = new CWPlayer();
const $ = (id) => document.getElementById(id);

// ---------- Estado y ajustes persistentes ----------
const DEFAULTS = {
  charWpm: 20,
  effWpm: 12,
  freq: 600,
  kochLevel: 2,        // nº de caracteres Koch activos (mínimo 2: K, M)
  groupSize: 5,
  groupCount: 5,
  mode: 'koch',        // koch | letras | numeros | mixto | abrev | callsigns
};

let settings = load();
let current = null;     // { text, groups }
let stats = { sessions: 0, chars: 0, hits: 0 };

function load() {
  try {
    return { ...DEFAULTS, ...JSON.parse(localStorage.getItem('cw4ever') || '{}') };
  } catch { return { ...DEFAULTS }; }
}
function save() {
  localStorage.setItem('cw4ever', JSON.stringify(settings));
}

// ---------- Generación de sesiones ----------
function activeChars() {
  switch (settings.mode) {
    case 'koch':    return KOCH_ORDER.slice(0, settings.kochLevel);
    case 'letras':  return GROUPS.letras;
    case 'numeros': return GROUPS.numeros;
    case 'mixto':   return [...GROUPS.letras, ...GROUPS.numeros, ...GROUPS.puntuacion];
    default:        return KOCH_ORDER.slice(0, settings.kochLevel);
  }
}

function randItem(arr) { return arr[Math.floor(Math.random() * arr.length)]; }

function randomCallsign() {
  const prefixes = ['EA', 'EB', 'EC', 'G', 'DL', 'F', 'I', 'W', 'K', 'N', 'VK', 'JA', 'PA', 'OK', 'SP'];
  const digits = '0123456789';
  const letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
  const p = randItem(prefixes);
  const d = randItem(digits.split(''));
  let suffix = '';
  const len = 2 + Math.floor(Math.random() * 2);
  for (let i = 0; i < len; i++) suffix += randItem(letters.split(''));
  return p + d + suffix;
}

function generate() {
  const groups = [];

  if (settings.mode === 'abrev') {
    for (let i = 0; i < settings.groupCount; i++) groups.push(randItem(ABBREVIATIONS));
  } else if (settings.mode === 'callsigns') {
    for (let i = 0; i < settings.groupCount; i++) groups.push(randomCallsign());
  } else {
    const chars = activeChars();
    for (let i = 0; i < settings.groupCount; i++) {
      let g = '';
      for (let j = 0; j < settings.groupSize; j++) g += randItem(chars);
      groups.push(g);
    }
  }

  current = { groups, text: groups.join(' ') };
  return current;
}

// ---------- Reproducción ----------
async function playCurrent() {
  if (!current) generate();
  player.setFrequency(settings.freq);
  const t = timing(settings.charWpm, settings.effWpm);
  const events = textToEvents(current.text, t);

  setPlaying(true);
  $('lamp').classList.remove('off');
  const finished = await player.play(events, {
    onSymbol: () => flashLamp(),
  });
  $('lamp').classList.add('off');
  setPlaying(false);
  return finished;
}

let lampTimer = null;
function flashLamp() {
  const lamp = $('lamp');
  lamp.classList.add('lit');
  clearTimeout(lampTimer);
  lampTimer = setTimeout(() => lamp.classList.remove('lit'), 60);
}

function setPlaying(on) {
  $('btnPlay').disabled = on;
  $('btnStop').disabled = !on;
  $('btnNew').disabled = on;
}

// ---------- Corrección de la copia ----------
function check() {
  if (!current) return;
  const expected = current.text.toUpperCase().replace(/\s+/g, ' ').trim();
  const got = $('answer').value.toUpperCase().replace(/\s+/g, ' ').trim();

  const expGroups = expected.split(' ');
  const gotGroups = got.split(' ');

  let hits = 0, total = 0;
  const html = expGroups.map((eg, i) => {
    const gg = gotGroups[i] || '';
    return eg.split('').map((c, j) => {
      total++;
      const ok = gg[j] === c;
      if (ok) hits++;
      return `<span class="${ok ? 'ok' : 'bad'}">${c}</span>`;
    }).join('');
  }).join(' ');

  const pct = total ? Math.round((hits / total) * 100) : 0;
  $('result').innerHTML =
    `<div class="score">Aciertos: <strong>${hits}/${total}</strong> (${pct}%)</div>` +
    `<div class="diff">${html}</div>` +
    `<div class="hint">Tu copia: <code>${got || '—'}</code></div>`;
  $('result').classList.add('show');

  // Progreso Koch: sube de nivel si la precisión es alta
  if (settings.mode === 'koch' && pct >= 90 && settings.kochLevel < KOCH_ORDER.length) {
    settings.kochLevel++;
    save();
    syncUI();
    $('result').innerHTML +=
      `<div class="levelup">¡Nivel Koch superado! Nuevo carácter: ` +
      `<strong>${KOCH_ORDER[settings.kochLevel - 1]}</strong></div>`;
  }

  // Estadísticas de sesión
  stats.sessions++;
  stats.chars += total;
  stats.hits += hits;
  updateStats();
}

function updateStats() {
  const acc = stats.chars ? Math.round((stats.hits / stats.chars) * 100) : 0;
  $('stats').textContent =
    `Sesiones: ${stats.sessions} · Caracteres: ${stats.chars} · Precisión media: ${acc}%`;
}

function reveal() {
  if (!current) return;
  $('result').innerHTML =
    `<div class="diff">${current.text}</div>` +
    `<div class="hint">Solución (los grupos van separados por espacios).</div>`;
  $('result').classList.add('show');
}

// ---------- Tabla de referencia ----------
function buildChart() {
  const order = [...GROUPS.letras, ...GROUPS.numeros];
  $('chart').innerHTML = order.map((c) =>
    `<div class="cell"><span class="ch">${c}</span><span class="mo">${MORSE[c]}</span></div>`
  ).join('');
}

// ---------- Sincronización UI <-> ajustes ----------
function syncUI() {
  $('charWpm').value = settings.charWpm;
  $('effWpm').value = settings.effWpm;
  $('freq').value = settings.freq;
  $('groupSize').value = settings.groupSize;
  $('groupCount').value = settings.groupCount;
  $('mode').value = settings.mode;

  $('charWpmVal').textContent = settings.charWpm;
  $('effWpmVal').textContent = settings.effWpm;
  $('freqVal').textContent = settings.freq;
  $('groupSizeVal').textContent = settings.groupSize;
  $('groupCountVal').textContent = settings.groupCount;

  const kochActive = settings.mode === 'koch';
  $('kochBox').style.display = kochActive ? '' : 'none';
  const fixedGroups = settings.mode === 'abrev' || settings.mode === 'callsigns';
  $('groupSizeRow').style.display = fixedGroups ? 'none' : '';
  if (kochActive) {
    $('kochInfo').textContent =
      `Nivel ${settings.kochLevel}/${KOCH_ORDER.length} — caracteres: ` +
      KOCH_ORDER.slice(0, settings.kochLevel).join(' ');
  }
}

function bind() {
  const slider = (id, key, fmt = (v) => v) => {
    $(id).addEventListener('input', (e) => {
      settings[key] = Number(e.target.value);
      $(id + 'Val').textContent = fmt(settings[key]);
      save();
      if (key === 'freq') player.setFrequency(settings.freq);
    });
  };
  slider('charWpm', 'charWpm');
  slider('effWpm', 'effWpm');
  slider('freq', 'freq');
  slider('groupSize', 'groupSize');
  slider('groupCount', 'groupCount');

  $('mode').addEventListener('change', (e) => {
    settings.mode = e.target.value;
    save(); syncUI(); generate();
    $('answer').value = ''; $('result').classList.remove('show');
  });

  $('btnPlay').addEventListener('click', playCurrent);
  $('btnReplay').addEventListener('click', playCurrent);
  $('btnStop').addEventListener('click', () => { player.stop(); setPlaying(false); $('lamp').classList.add('off'); });
  $('btnNew').addEventListener('click', () => {
    generate();
    $('answer').value = '';
    $('result').classList.remove('show');
    $('answer').focus();
  });
  $('btnCheck').addEventListener('click', check);
  $('btnReveal').addEventListener('click', reveal);

  $('answer').addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); check(); }
  });

  // Atajos de teclado globales
  document.addEventListener('keydown', (e) => {
    if (document.activeElement === $('answer')) return;
    if (e.key === ' ') { e.preventDefault(); playCurrent(); }
    if (e.key.toLowerCase() === 'n') { generate(); $('answer').value = ''; $('result').classList.remove('show'); }
  });
}

// ---------- Init ----------
function init() {
  syncUI();
  bind();
  buildChart();
  generate();
  updateStats();
  setPlaying(false);
}

document.addEventListener('DOMContentLoaded', init);
