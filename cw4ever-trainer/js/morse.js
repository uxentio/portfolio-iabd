// morse.js — Tabla de código Morse, orden Koch y cálculo de temporización (Farnsworth)

// Mapa carácter -> patrón Morse (. = dit, - = dah)
export const MORSE = {
  A: '.-',    B: '-...',  C: '-.-.',  D: '-..',   E: '.',     F: '..-.',
  G: '--.',   H: '....',  I: '..',    J: '.---',  K: '-.-',   L: '.-..',
  M: '--',    N: '-.',    O: '---',   P: '.--.',  Q: '--.-',  R: '.-.',
  S: '...',   T: '-',     U: '..-',   V: '...-',  W: '.--',   X: '-..-',
  Y: '-.--',  Z: '--..',
  0: '-----', 1: '.----', 2: '..---', 3: '...--', 4: '....-',
  5: '.....', 6: '-....', 7: '--...', 8: '---..', 9: '----.',
  '.': '.-.-.-', ',': '--..--', '?': '..--..', "'": '.----.',
  '!': '-.-.--', '/': '-..-.', '(': '-.--.', ')': '-.--.-',
  '&': '.-...', ':': '---...', ';': '-.-.-.', '=': '-...-',
  '+': '.-.-.', '-': '-....-', '_': '..--.-', '"': '.-..-.',
  '$': '...-..-', '@': '.--.-.',
};

// Orden de aprendizaje Koch: introduce los caracteres en un orden que maximiza
// el contraste sonoro, empezando por K y M.
export const KOCH_ORDER = [
  'K', 'M', 'R', 'S', 'U', 'A', 'P', 'T', 'L', 'O', 'W', 'I',
  '.', 'N', 'J', 'E', 'F', '0', 'Y', 'V', ',', 'G', '5', '/',
  'Q', '9', 'Z', 'H', '3', '8', 'B', '?', '4', '2', '7', 'C',
  '1', 'D', '6', 'X',
];

// Grupos de caracteres para selección manual
export const GROUPS = {
  letras: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split(''),
  numeros: '0123456789'.split(''),
  puntuacion: ['.', ',', '?', '/', '=', '+', '-', '(', ')', ':', ';', '"', "'"],
};

// Abreviaturas y código Q habituales en CW
export const ABBREVIATIONS = [
  'CQ', 'DE', 'K', 'KN', 'AR', 'SK', 'BK', 'R', 'RR', 'TU', '73', '88',
  'GM', 'GA', 'GE', 'GN', 'OM', 'YL', 'XYL', 'ES', 'PSE', 'TNX', 'FB',
  'HR', 'HW', 'UR', 'RST', 'WX', 'ANT', 'PWR', 'RIG', 'NAME', 'QTH',
  'QRZ', 'QRM', 'QRN', 'QRP', 'QRO', 'QRT', 'QRS', 'QRQ', 'QSB', 'QSL',
  'QSO', 'QSY', 'QTC', 'QRL', 'WPM', 'AGN', 'CUL', 'DX', 'OP',
];

/**
 * Calcula las duraciones (en segundos) de los elementos Morse usando la
 * técnica Farnsworth, siguiendo el estándar ARRL.
 *
 * @param {number} charWpm  Velocidad de carácter (WPM). Cada letra se envía a esta velocidad.
 * @param {number} effWpm   Velocidad efectiva/global (WPM). <= charWpm.
 * @returns {{dit:number, dah:number, symGap:number, charGap:number, wordGap:number}}
 */
export function timing(charWpm, effWpm) {
  const c = Math.max(1, charWpm);
  const s = Math.min(Math.max(1, effWpm), c); // la efectiva nunca supera la de carácter

  const dit = 1.2 / c;        // duración del punto a velocidad de carácter
  const dah = 3 * dit;        // raya = 3 puntos
  const symGap = dit;         // hueco entre símbolos del mismo carácter

  // Unidad de espaciado Farnsworth: reparte el tiempo extra sobre 19 unidades
  // (PARIS = 50 unidades; 31 de elementos + 19 de espaciado).
  let td = (60 / s - 37.2 / c) / 19;
  if (td < dit) td = dit; // sin Farnsworth: espaciado normal

  return {
    dit,
    dah,
    symGap,
    charGap: 3 * td,  // hueco entre caracteres
    wordGap: 7 * td,  // hueco entre palabras
  };
}

/**
 * Convierte un texto a una secuencia de eventos de audio (tono/silencio).
 * @returns {Array<{on:boolean, dur:number}>} on=true suena, on=false silencio.
 */
export function textToEvents(text, t) {
  const events = [];
  const chars = text.toUpperCase().split('');

  chars.forEach((ch, i) => {
    if (ch === ' ') {
      events.push({ on: false, dur: t.wordGap });
      return;
    }
    const pattern = MORSE[ch];
    if (!pattern) return;

    pattern.split('').forEach((sym, j) => {
      events.push({ on: true, dur: sym === '-' ? t.dah : t.dit });
      if (j < pattern.length - 1) events.push({ on: false, dur: t.symGap });
    });

    // Hueco tras el carácter (salvo el último o si el siguiente es espacio)
    const next = chars[i + 1];
    if (i < chars.length - 1 && next !== ' ') {
      events.push({ on: false, dur: t.charGap });
    }
  });

  return events;
}

// Duración total (segundos) de un texto a la temporización dada
export function durationOf(text, t) {
  return textToEvents(text, t).reduce((acc, e) => acc + e.dur, 0);
}
