"use strict";
/**
 * games-engine.js — Core Audio FX & Gameplay Engine
 */
(() => {
  /* =========================================================================
   * 1. Audio & Sound FX (Web Audio API Synthesizer)
   * ========================================================================= */
  let audioCtx = null;
  function getAudioCtx() {
    if (!audioCtx) {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (AudioContext) audioCtx = new AudioContext();
    }
    if (audioCtx && audioCtx.state === "suspended") {
      audioCtx.resume();
    }
    return audioCtx;
  }

  function playSound(type) {
    try {
      const ctx = getAudioCtx();
      if (!ctx) return;
      const now = ctx.currentTime;
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.connect(gain);
      gain.connect(ctx.destination);

      if (type === "pop" || type === "tap") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.08);
        gain.gain.setValueAtTime(0.15, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.08);
        osc.start(now);
        osc.stop(now + 0.08);
      } else if (type === "success") {
        osc.type = "triangle";
        osc.frequency.setValueAtTime(523.25, now); // C5
        osc.frequency.setValueAtTime(659.25, now + 0.08); // E5
        osc.frequency.setValueAtTime(783.99, now + 0.16); // G5
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.32);
        osc.start(now);
        osc.stop(now + 0.32);
      } else if (type === "error") {
        osc.type = "sawtooth";
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.exponentialRampToValueAtTime(110, now + 0.18);
        gain.gain.setValueAtTime(0.2, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
        osc.start(now);
        osc.stop(now + 0.18);
      } else if (type === "complete") {
        osc.type = "sine";
        osc.frequency.setValueAtTime(440, now);
        osc.frequency.exponentialRampToValueAtTime(880, now + 0.12);
        osc.frequency.exponentialRampToValueAtTime(1320, now + 0.28);
        gain.gain.setValueAtTime(0.22, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.4);
        osc.start(now);
        osc.stop(now + 0.4);
      }
    } catch (e) {
      // Audio autoplay or web audio context blocked
    }
  }

  function shuffle(arr) {
    const a = arr.slice();
    for (let i = a.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [a[i], a[j]] = [a[j], a[i]];
    }
    return a;
  }

  function sample(arr) {
    return arr[Math.floor(Math.random() * arr.length)];
  }

  /* =========================================================================
   * 2. Arcade Engine & Session
   * ========================================================================= */
  const engine = {
    allSentences: [],
    activeGame: null,
    score: 0,
    round: null,
    timerId: null,
    timeLeft: 0,

    init(sentences) {
      this.allSentences = sentences;
    },

    getRandomSentence(filterFn) {
      const pool = filterFn ? this.allSentences.filter(filterFn) : this.allSentences;
      if (!pool || pool.length === 0) return sample(this.allSentences);
      return sample(pool);
    },

    getRandomSentences(count, filterFn) {
      const pool = filterFn ? this.allSentences.filter(filterFn) : this.allSentences;
      const sh = shuffle(pool || this.allSentences);
      return sh.slice(0, count);
    },

    /** Called by the hub every time a game (re)starts a round. */
    beginRound() {
      this.round = { touched: false, done: false };
    },

    /** First real interaction: only now is the round counted as played/seen. */
    markTouched() {
      const r = this.round;
      if (!r || r.touched || !this.activeGame) return;
      r.touched = true;
      if (window.recordGameEvent) window.recordGameEvent(this.activeGame.id, this.currentSentence, "touch");
    },

    /** Round solved: counts once as done. */
    completeRound() {
      this.markTouched();
      const r = this.round;
      if (!r || r.done) return;
      r.done = true;
      playSound("success");
      if (this.activeGame && window.recordGameEvent) {
        window.recordGameEvent(this.activeGame.id, this.currentSentence, "done");
      }
    },

    wrong() {
      playSound("error");
    },

    updateHud() {},

    showToast(text) {
      const toast = document.createElement("div");
      toast.className = "arcade-float-toast";
      toast.textContent = text;
      const arena = document.getElementById("arcade-arena-board");
      if (arena) {
        arena.appendChild(toast);
        setTimeout(() => toast.remove(), 1200);
      }
    },

    startTimer(seconds, onTick, onExpire) {
      this.stopTimer();
      this.timeLeft = seconds;
      const bar = document.getElementById("arcade-timer-bar");
      if (bar) {
        bar.style.width = "100%";
        bar.parentElement.hidden = false;
      }
      this.timerId = setInterval(() => {
        this.timeLeft--;
        if (bar) bar.style.width = `${Math.max(0, (this.timeLeft / seconds) * 100)}%`;
        if (onTick) onTick(this.timeLeft);
        if (this.timeLeft <= 0) {
          this.stopTimer();
          if (onExpire) onExpire();
        }
      }, 1000);
    },

    stopTimer() {
      if (this.timerId) {
        clearInterval(this.timerId);
        this.timerId = null;
      }
      const bar = document.getElementById("arcade-timer-bar");
      if (bar) {
        bar.parentElement.hidden = true;
      }
    }
  };

  window.__VakyaArcadeEngine = engine;
  window.__shuffle = shuffle;
  window.__sample = sample;
  window.__playSound = playSound;
})();
