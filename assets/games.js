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
      this.meaningsActive = false;
      const dictBtn = document.getElementById("btn-arcade-dict");
      if (dictBtn) {
        dictBtn.hidden = true;
        dictBtn.classList.remove("active");
      }
      const board = document.getElementById("arcade-arena-board");
      if (board) {
        board.classList.remove("show-meanings");
      }
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
      playSound("complete");
      const dictBtn = document.getElementById("btn-arcade-dict");
      if (dictBtn) dictBtn.hidden = false;
      if (this.onRoundComplete) this.onRoundComplete();
      if (this.activeGame && window.recordGameEvent) {
        window.recordGameEvent(this.activeGame.id, this.currentSentence, "done");
      }
    },

    toggleMeanings() {
      if (!this.round || !this.round.done) return;
      this.meaningsActive = !this.meaningsActive;
      const dictBtn = document.getElementById("btn-arcade-dict");
      if (dictBtn) dictBtn.classList.toggle("active", this.meaningsActive);
      const board = document.getElementById("arcade-arena-board");
      if (board) board.classList.toggle("show-meanings", this.meaningsActive);
      if (this.onToggleMeanings) this.onToggleMeanings(this.meaningsActive);
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
"use strict";
/**
 * games-suite-1.js — Interactive Games 1 to 16
 */
(() => {
  const engine = window.__VakyaArcadeEngine;
  const shuffle = window.__shuffle;
  const sample = window.__sample;
  const playSound = window.__playSound;

  const GAMES = [

    {
      id: "word-bridge",
      title: "Word Bridge",
      tagline: "Sequential Word-Matching with SVO ➔ SOV Visual Bridge",
      icon: "game-bridge",
      start(board) {
        const sentence = engine.getRandomSentence(s => {
          const count = s.hi.split(/\s+/).length;
          return count >= 4 && count <= 8;
        });
        const words = sentence.hi.split(/\s+/);
        let placed = [];

        engine.currentSentence = sentence;

        board.innerHTML = `
          <div class="arcade-card">
            <div class="game-bridge-ref">
              <div class="bridge-en-box">
                <p class="bridge-sentence-en">${sentence.en.trim().split(/\s+/).map((w, idx) => `<span class="en-word" data-en-index="${idx}">${w}</span>`).join(" ")}</p>
              </div>
              <div class="bridge-hi-box">
                <div class="bridge-slots" id="bridge-slots">
                  ${words.map((_, i) => `<div class="bridge-slot" data-slot="${i}">?</div>`).join("")}
                </div>
              </div>
            </div>
            <div class="bridge-tiles" id="bridge-tiles"></div>
          </div>
        `;

        const tilesCont = board.querySelector("#bridge-tiles");
        const slotsCont = board.querySelector("#bridge-slots");
        // Introduce 1-2 distractor words from other sentences to slightly increase difficulty
        const otherSent = engine.getRandomSentence(s => s.id !== sentence.id && s.hi.split(/\s+/).length >= 3);
        const distractors = otherSent
          ? shuffle(otherSent.hi.split(/\s+/).filter(w => !words.includes(w))).slice(0, 2)
          : [];
        const poolItems = words.map((w, idx) => ({ word: w, origIndex: idx, isDistractor: false }))
          .concat(distractors.map((w, dIdx) => ({ word: w, origIndex: -1 - dIdx, isDistractor: true })));
        const shuffled = shuffle(poolItems);

        function renderTiles() {
          tilesCont.innerHTML = shuffled.map((item, i) => {
            const meaning = window.__getWordMeaning ? window.__getWordMeaning(item.word) : "";
            return `
            <button type="button" class="arcade-chip ${placed.includes(item.origIndex) ? "used" : ""}" data-tile-idx="${i}" data-word="${item.word}">
              <span class="slot-hi-text">${item.word}</span>
              <span class="slot-en-gloss">${meaning}</span>
            </button>
          `;}).join("");
        }

        renderTiles();

        tilesCont.addEventListener("click", e => {
          const btn = e.target.closest(".arcade-chip");
          if (!btn || btn.classList.contains("used")) return;
          const tIdx = Number(btn.dataset.tileIdx);
          const item = shuffled[tIdx];

          const nextSlotIdx = placed.length;
          if (!item.isDistractor && item.origIndex === nextSlotIdx) {
            placed.push(item.origIndex);
            playSound("tap");
            const slotEl = slotsCont.querySelector(`[data-slot="${nextSlotIdx}"]`);
            if (slotEl) {
              const meaning = window.__getWordMeaning ? window.__getWordMeaning(item.word) : "";
              slotEl.setAttribute("data-word", item.word);
              slotEl.innerHTML = `<span class="slot-hi-text">${item.word}</span><span class="slot-en-gloss">${meaning}</span>`;
              slotEl.classList.add("filled", "good");
            }
            renderTiles();

            if (placed.length === words.length) {
              const hiBox = board.querySelector(".bridge-hi-box");
              if (hiBox) hiBox.classList.add("completed");
              engine.completeRound();
            }
          } else {
            playSound("error");
            engine.wrong();
            btn.classList.add("shake-bad");
            setTimeout(() => btn.classList.remove("shake-bad"), 400);
          }
        });
      }
    },

    {
      id: "word-swap",
      title: "Word Swap",
      tagline: "Two words are swapped out of order. Tap both to switch them back",
      icon: "game-swap",
      start(board) {
        const sentence = engine.getRandomSentence(s => {
          const c = s.hi.split(/\s+/).length;
          return c >= 4 && c <= 8;
        });
        const words = sentence.hi.split(/\s+/);

        // Pick two distinct indices with different words to swap
        let i1 = 0, i2 = 1;
        const distinctPairs = [];
        for (let i = 0; i < words.length; i++) {
          for (let j = i + 1; j < words.length; j++) {
            if (words[i] !== words[j]) distinctPairs.push([i, j]);
          }
        }
        if (distinctPairs.length > 0) {
          [i1, i2] = sample(distinctPairs);
        }
        const currentWords = words.slice();
        currentWords[i1] = words[i2];
        currentWords[i2] = words[i1];

        engine.currentSentence = sentence;

        function renderSwap() {
          board.innerHTML = `
            <div class="arcade-card">
              <div class="arcade-prompt-box">
                <p class="arcade-sentence-display">${sentence.en}</p>
              </div>
              <div class="swap-display" id="swap-display">
                ${currentWords.map((w, idx) => {
                  const meaning = window.__getWordMeaning ? window.__getWordMeaning(w) : "";
                  return `
                  <button type="button" class="swap-word-btn" data-idx="${idx}" data-word="${w}">
                    <span class="slot-hi-text">${w}</span>
                    <span class="slot-en-gloss">${meaning}</span>
                  </button>
                `;}).join("")}
              </div>
            </div>
          `;
          setupHandlers();
        }

        let selectedBtn = null;
        let finished = false;

        function setupHandlers() {
          const displayEl = board.querySelector("#swap-display");
          displayEl.addEventListener("click", e => {
            if (finished) return;
            const btn = e.target.closest(".swap-word-btn");
            if (!btn) return;

            if (!selectedBtn) {
              selectedBtn = btn;
              btn.classList.add("selected-swap");
              playSound("tap");
            } else if (selectedBtn === btn) {
              selectedBtn.classList.remove("selected-swap");
              selectedBtn = null;
            } else {
              // Perform swap
              const idxA = parseInt(selectedBtn.dataset.idx, 10);
              const idxB = parseInt(btn.dataset.idx, 10);
              const temp = currentWords[idxA];
              currentWords[idxA] = currentWords[idxB];
              currentWords[idxB] = temp;

              // Check if restored
              const isCorrect = currentWords.every((w, idx) => w === words[idx]);
              if (isCorrect) {
                finished = true;
                playSound("pop");
                renderSwap();
                const d = board.querySelector("#swap-display");
                if (d) d.classList.add("completed");
                engine.completeRound();
              } else {
                playSound("error");
                engine.wrong();
                renderSwap();
              }
              selectedBtn = null;
            }
          });
        }

        renderSwap();
      }
    },

    {
      id: "word-doctor",
      title: "Word Doctor",
      tagline: "Diagnose the grammatically incorrect word and prescribe the cure",
      icon: "game-doctor",
      start(board) {
        const sentence = engine.getRandomSentence(s => s.hi.split(/\s+/).length >= 3)
          || engine.getRandomSentence();

        const words = sentence.hi.split(/\s+/);
        // Purely random: any word position in the sentence can be selected
        const targetIdx = Math.floor(Math.random() * words.length);
        const correctWord = words[targetIdx];

        // Gather candidate replacement words from other sentences in the curriculum
        const otherSentences = engine.getRandomSentences ? engine.getRandomSentences(5, s => s.id !== sentence.id) : [];
        const candidatePool = new Set();
        otherSentences.forEach(s => {
          s.hi.split(/\s+/).forEach(w => {
            if (w && w !== correctWord && !words.includes(w)) {
              candidatePool.add(w);
            }
          });
        });

        // Fallback candidates if pool is small
        ["नहीं", "बहुत", "यहाँ", "वहाँ", "सब", "कल", "आज", "घर"].forEach(w => {
          if (w !== correctWord && !words.includes(w)) candidatePool.add(w);
        });

        const alternativeOptions = shuffle(Array.from(candidatePool));
        const sickReplacement = alternativeOptions[0] || "नहीं";
        const remedies = shuffle([correctWord, alternativeOptions[1] || "बहुत", alternativeOptions[2] || "यहाँ"]);

        const displayedWords = words.slice();
        displayedWords[targetIdx] = sickReplacement;

        engine.currentSentence = sentence;

        board.innerHTML = `
          <div class="arcade-card">
            <div class="arcade-prompt-box">
              <p class="arcade-sentence-display">${sentence.en}</p>
            </div>
            <div class="doctor-display" id="doctor-display">
              ${displayedWords.map((w, idx) => {
                const meaning = window.__getWordMeaning ? window.__getWordMeaning(w) : "";
                return `
                <button type="button" class="doctor-word-btn" data-idx="${idx}" data-word="${w}">
                  <span class="slot-hi-text">${w}</span>
                  <span class="slot-en-gloss">${meaning}</span>
                </button>
              `;}).join("")}
            </div>
            <div id="doctor-remedy-container" hidden>
              <div class="doctor-remedy-bank" id="doctor-remedies">
                ${remedies.map(r => `
                  <button type="button" class="doctor-pill-btn" data-remedy="${r}">
                    ${r}
                  </button>
                `).join("")}
              </div>
            </div>
          </div>
        `;

        const displayEl = board.querySelector("#doctor-display");
        const remedyCont = board.querySelector("#doctor-remedy-container");
        const remedyBank = board.querySelector("#doctor-remedies");
        let diagnosed = false;
        let cured = false;

        displayEl.addEventListener("click", e => {
          if (cured) return;
          const btn = e.target.closest(".doctor-word-btn");
          if (!btn) return;
          const idx = parseInt(btn.dataset.idx, 10);

          if (idx === targetIdx) {
            diagnosed = true;
            playSound("tap");
            btn.classList.add("sick-word");
            remedyCont.hidden = false;
          } else {
            playSound("error");
            engine.wrong();
            btn.classList.add("shake-bad");
            setTimeout(() => btn.classList.remove("shake-bad"), 400);
          }
        });

        remedyBank.addEventListener("click", e => {
          if (cured || !diagnosed) return;
          const pill = e.target.closest(".doctor-pill-btn");
          if (!pill) return;
          const chosen = pill.dataset.remedy;

          if (chosen === correctWord) {
            cured = true;
            playSound("pop");
            const targetBtn = displayEl.querySelector(`[data-idx="${targetIdx}"]`);
            if (targetBtn) {
              const meaning = window.__getWordMeaning ? window.__getWordMeaning(correctWord) : "";
              targetBtn.innerHTML = `<span class="slot-hi-text">${correctWord}</span><span class="slot-en-gloss">${meaning}</span>`;
              targetBtn.setAttribute("data-word", correctWord);
              targetBtn.classList.remove("sick-word");
              targetBtn.classList.add("cured-word");
            }
            remedyCont.hidden = true;
            displayEl.classList.add("completed");
            engine.completeRound();
          } else {
            playSound("error");
            engine.wrong();
            pill.classList.add("shake-bad");
            setTimeout(() => pill.classList.remove("shake-bad"), 400);
          }
        });
      }
    }
  ];

  window.__VakyaGames = GAMES;
})();
"use strict";
/**
 * games-hub.js — Games Hub Card Grid & Arena Controller
 */
(() => {
  const engine = window.__VakyaArcadeEngine;
  const GAMES = window.__VakyaGames || window.__VakyaGamesPart1 || [];

  // Every (re)start of a round resets the touched/done tracking.
  GAMES.forEach(g => {
    const original = g.start;
    g.start = function (board) {
      engine.beginRound();
      return original.call(this, board);
    };
  });

  /* =========================================================================
   * 5. Public Arcade Interface
   * ========================================================================= */
  window.VakyaArcade = {
    games: GAMES,

    init(sentences) {
      engine.init(sentences);
      this.renderHub();
      const nextBtn = document.getElementById("btn-arcade-next");
      if (nextBtn) {
        nextBtn.onclick = () => {
          const board = document.getElementById("arcade-arena-board");
          if (engine.activeGame && board) engine.activeGame.start(board);
        };
      }
      const dictBtn = document.getElementById("btn-arcade-dict");
      if (dictBtn) {
        dictBtn.onclick = () => {
          engine.toggleMeanings();
        };
      }
      const arenaBoard = document.getElementById("arcade-arena-board");
      if (arenaBoard) {
        // capture phase: runs before the game's own handler sees the click
        arenaBoard.addEventListener("click", e => {
          if (e.target.closest("button, .memory-card, .syntax-hi-word")) engine.markTouched();
        }, true);
      }
    },

    renderHub() {
      const grid = document.getElementById("arcade-games-grid");
      if (!grid) return;
      grid.innerHTML = GAMES.map(g => `
        <article class="arcade-game-card" data-game-id="${g.id}">
          <div class="arcade-card-icon-wrap" aria-hidden="true">
            <svg class="arcade-game-icon"><use href="#i-${g.icon || 'arcade'}"/></svg>
          </div>
          <div class="arcade-card-body">
            <h3 class="arcade-game-title">${g.title}</h3>
          </div>
          <div class="arcade-card-arrow" aria-hidden="true">
            <svg class="arcade-arrow-icon" viewBox="0 0 24 24"><path d="M9 6l6 6-6 6" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
        </article>
      `).join("");

      grid.onclick = e => {
        const card = e.target.closest(".arcade-game-card");
        if (card) {
          const gameId = card.dataset.gameId;
          this.launchGame(gameId);
        }
      };
    },

    launchGame(gameId) {
      const g = GAMES.find(x => x.id === gameId);
      if (!g) return;
      engine.activeGame = g;
      engine.stopTimer();

      // Show Arena Section
      const hubSec = document.getElementById("section-arcade-hub");
      const arenaSec = document.getElementById("section-arcade-arena");
      if (hubSec) hubSec.hidden = true;
      if (arenaSec) arenaSec.hidden = false;

      const titleEl = document.getElementById("arcade-arena-title");
      if (titleEl) titleEl.textContent = g.title;

      const board = document.getElementById("arcade-arena-board");
      if (board) g.start(board);
    },

    exitArena() {
      engine.stopTimer();
      engine.activeGame = null;
      engine.meaningsActive = false;
      const dictBtn = document.getElementById("btn-arcade-dict");
      if (dictBtn) {
        dictBtn.hidden = true;
        dictBtn.classList.remove("active");
      }
      const board = document.getElementById("arcade-arena-board");
      if (board) {
        board.classList.remove("show-meanings");
        board.innerHTML = "";
      }
      const hubSec = document.getElementById("section-arcade-hub");
      const arenaSec = document.getElementById("section-arcade-arena");
      if (arenaSec) arenaSec.hidden = true;
      if (hubSec) hubSec.hidden = false;
    }
  };
})();
