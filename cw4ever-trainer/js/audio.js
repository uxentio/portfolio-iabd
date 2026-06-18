// audio.js — Generación de tono CW (sidetone) con la Web Audio API

export class CWPlayer {
  constructor() {
    this.ctx = null;
    this.osc = null;
    this.gain = null;
    this.freq = 600;       // Hz
    this.rampMs = 5;       // envolvente para evitar clicks
    this._stopFlag = false;
    this._timers = [];
  }

  _ensureContext() {
    if (!this.ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      this.ctx = new AC();
      this.osc = this.ctx.createOscillator();
      this.gain = this.ctx.createGain();
      this.gain.gain.value = 0;
      this.osc.type = 'sine';
      this.osc.frequency.value = this.freq;
      this.osc.connect(this.gain);
      this.gain.connect(this.ctx.destination);
      this.osc.start();
    }
  }

  // Algunos navegadores exigen un gesto del usuario para arrancar el audio.
  async resume() {
    this._ensureContext();
    if (this.ctx.state === 'suspended') await this.ctx.resume();
  }

  setFrequency(hz) {
    this.freq = hz;
    if (this.osc) this.osc.frequency.setValueAtTime(hz, this.ctx.currentTime);
  }

  /**
   * Reproduce una secuencia de eventos {on, dur(segundos)}.
   * @returns {Promise<boolean>} resuelve true si terminó, false si se detuvo.
   */
  async play(events, { onSymbol } = {}) {
    await this.resume();
    this._stopFlag = false;
    this._clearTimers();

    const t0 = this.ctx.currentTime + 0.05;
    let cursor = t0;
    const r = this.rampMs / 1000;

    for (const ev of events) {
      if (ev.on) {
        this.gain.gain.setValueAtTime(0, cursor);
        this.gain.gain.linearRampToValueAtTime(0.9, cursor + r);
        this.gain.gain.setValueAtTime(0.9, cursor + ev.dur - r);
        this.gain.gain.linearRampToValueAtTime(0, cursor + ev.dur);
      }
      cursor += ev.dur;
    }

    // Callback opcional de progreso visual a mitad de cada elemento sonoro
    if (onSymbol) {
      let c2 = t0;
      for (const ev of events) {
        if (ev.on) {
          const delay = (c2 - this.ctx.currentTime) * 1000;
          this._timers.push(setTimeout(() => onSymbol(), Math.max(0, delay)));
        }
        c2 += ev.dur;
      }
    }

    const totalMs = (cursor - this.ctx.currentTime) * 1000;
    return new Promise((resolve) => {
      const id = setTimeout(() => resolve(!this._stopFlag), totalMs + 30);
      this._timers.push(id);
    });
  }

  // Tono manual (para el modo "key" / pulsador)
  toneOn() {
    this._ensureContext();
    const now = this.ctx.currentTime;
    this.gain.gain.cancelScheduledValues(now);
    this.gain.gain.setValueAtTime(this.gain.gain.value, now);
    this.gain.gain.linearRampToValueAtTime(0.9, now + this.rampMs / 1000);
  }

  toneOff() {
    if (!this.ctx) return;
    const now = this.ctx.currentTime;
    this.gain.gain.cancelScheduledValues(now);
    this.gain.gain.setValueAtTime(this.gain.gain.value, now);
    this.gain.gain.linearRampToValueAtTime(0, now + this.rampMs / 1000);
  }

  stop() {
    this._stopFlag = true;
    this._clearTimers();
    if (this.gain && this.ctx) {
      const now = this.ctx.currentTime;
      this.gain.gain.cancelScheduledValues(now);
      this.gain.gain.setValueAtTime(0, now);
    }
  }

  _clearTimers() {
    this._timers.forEach(clearTimeout);
    this._timers = [];
  }
}
