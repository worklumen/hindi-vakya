"use strict";

/* ==========================================================================
 H i*ndi Vakya — application script
 Sections: 1 Config · 2 State · 3 Storage · 4 Data · 5 Selection engine
 6 Round (game logic) · 7 Views · 8 Dialog · 9 Wiring
 ========================================================================== */

(() => {
  /* ---------------------------------------------------------------------
   * 1. Config
   * ------------------------------------------------------------------- */
  const CONFIG = Object.freeze({
    storeKey: "hindi-vakya-state"
  });

  /* ---------------------------------------------------------------------
   * 2. State
   * ------------------------------------------------------------------- */
  /** @type {{id:string|number, en:string, hi:string, freq:number, words:string[]}[]} */
  let sentences = [];
  let manifestSentenceTotal = 0;
  let manifestWordTotal = 0;
  let dictionary = {};    // { [hiWord]: string (en meaning) }
  /** @type {{sentences:Object, words:Object, games:Object}} */
  let progress = null;

  window.__getWordMeaning = function (w) {
    if (!w) return "";
    const clean = w.replace(/[^\w\u0900-\u097F]/g, "");
    return dictionary[clean] || dictionary[w] || "";
  };

  /* ---------------------------------------------------------------------
   * 3. Storage
   * ------------------------------------------------------------------- */

    function freshProgress() {
      return {
        sentences: {},
        words: {},
        games: {} // { [gameId]: { plays: number, done: number } }
      };
    }

    /** Upgrades state saved by older versions of the app. */
    function migrate(p) {
      p.games = p.games || {};
      for (const g of Object.values(p.games)) {
        g.plays = g.plays || 0;
        g.done = g.done || 0;
      }

      if (!p.words) p.words = {};
      for (const w of Object.values(p.words)) {
        if (w.enc === undefined) w.enc = 0;
        if (w.done === undefined) w.done = 0;
      }
      if (!p.sentences) p.sentences = {};
      for (const [id, st] of Object.entries(p.sentences)) {
        const seen = st.seen !== undefined ? st.seen : (st.plays || 0);
        const done = st.done !== undefined
          ? st.done
          : (st.mastered ? Math.max(5, st.clean || 0) : (st.clean || 0));
        p.sentences[id] = { seen, done };
      }
      return p;
    }



    function loadProgress() {
      try {
        const raw = localStorage.getItem(CONFIG.storeKey);
        if (raw) {
          const p = JSON.parse(raw);
          if (p) return migrate(p);
        }
      } catch (e) { /* corrupted state: start fresh */ }
      return freshProgress();
    }

    function saveProgress() {
      try {
        localStorage.setItem(CONFIG.storeKey, JSON.stringify(progress));
      } catch (e) { /* storage unavailable: game still playable this session */ }
    }

    // Called by the arcade engine: "touch" = first interaction, "done" = solved.
    window.recordGameEvent = function(gameId, sentence, kind) {
      if (!progress) return;
      if (!progress.games) progress.games = {};
      if (!progress.games[gameId]) progress.games[gameId] = { plays: 0, done: 0 };
      const g = progress.games[gameId];
      const isDone = kind === "done";
      g[isDone ? "done" : "plays"]++;
      if (sentence) {
        sentenceState(sentence.id)[isDone ? "done" : "seen"]++;
        for (const w of (sentence.words || sentence.hi.split(/\s+/))) {
          wordState(w)[isDone ? "done" : "enc"]++;
        }
      }
      saveProgress();
      renderStats();
    };

    function sentenceState(id) {
      if (!progress.sentences[id]) {
        progress.sentences[id] = { seen: 0, done: 0 };
      }
      return progress.sentences[id];
    }

    function wordState(w) {
      if (!progress.words[w]) {
        progress.words[w] = { enc: 0, done: 0 };
      }
      return progress.words[w];
    }

    /* ---------------------------------------------------------------------
     * 4. Data
     * ------------------------------------------------------------------- */
    // bump when data level files change so browsers drop cached chunks
    const DATA_V = 56;

    async function fetchJson(url) {
      const res = await fetch(url + "?v=" + DATA_V);
      if (!res.ok) throw new Error(`${url} not found`);
      return res.json();
    }

    async function loadData() {
      const manifest = await fetchJson("data/manifest.json");
      manifestSentenceTotal = manifest.total_sentences || 0;
      manifestWordTotal = manifest.total_words || 0;
      try {
        dictionary = await fetchJson("data/dictionary.json");
      } catch (e) {
        console.warn("Could not load dictionary.json", e);
      }
      const all = [];
      for (const entry of manifest.files) {
        const items = await fetchJson(entry.file);
        for (const s of items) {
          all.push({
            id: s.id,
            en: s.en,
            hi: s.hi,
            freq: s.freq || 0,
            words: s.hi.split(/\s+/)
          });
        }
      }
      if (!manifestSentenceTotal) manifestSentenceTotal = all.length;
      return all;
    }

    /* ---------------------------------------------------------------------
     * 4. Views & UI Controller
     * ------------------------------------------------------------------- */
    const dom = {};
    const $ = id => document.getElementById(id);

    function cacheDom() {
      [
        "section-home",
        "btn-reset",
        "dialog", "dialog-title", "dialog-message", "dialog-confirm", "dialog-cancel",
        "btn-arcade-exit",
        // Simple Stats
        "stat-sentences-seen", "stat-sentences-total",
        "stat-words-seen", "stat-words-total"
      ].forEach(id => {
        dom[id.replace(/-(\w)/g, (_, c) => c.toUpperCase())] = $(id);
      });
    }

    /* --- Home (Games Hub & Stats) --- */
    function renderHome() {
      renderStats();
      if (window.VakyaArcade) {
        window.VakyaArcade.exitArena();
        window.VakyaArcade.renderHub();
      }
    }

    /* --- Stats Section --- */
    function renderStats() {
      // 1. Unique Sentences seen
      let totalSeen = 0;
      if (progress && progress.sentences) {
        for (const st of Object.values(progress.sentences)) {
          if (st && (st.seen > 0 || st.done > 0)) totalSeen++;
        }
      }

      // 2. Unique Words seen
      let wordsSeenCount = 0;
      if (progress && progress.words) {
        for (const wt of Object.values(progress.words)) {
          if (wt && (wt.enc > 0 || wt.done > 0)) wordsSeenCount++;
        }
      }

      const totalSentences = manifestSentenceTotal || (sentences ? sentences.length : 0);
      const totalWords = manifestWordTotal || 0;

      if (dom.statSentencesSeen) dom.statSentencesSeen.textContent = String(totalSeen);
      if (dom.statSentencesTotal) dom.statSentencesTotal.textContent = String(totalSentences);
      if (dom.statWordsSeen) dom.statWordsSeen.textContent = String(wordsSeenCount);
      if (dom.statWordsTotal) dom.statWordsTotal.textContent = String(totalWords);
    }

    /* ---------------------------------------------------------------------
     * 8. Dialog (replaces alert / confirm)
     * ------------------------------------------------------------------- */
    /**
     * @param {{title:string, message:string, confirmLabel?:string, cancelLabel?:string, danger?:boolean}} opts
     * @returns {Promise<boolean>} true when confirmed
     */
    function showDialog({ title, message, confirmLabel = "OK", cancelLabel = null, danger = false }) {
      return new Promise(resolve => {
        const d = dom.dialog;
        if (typeof d.showModal !== "function") {
          // very old browsers: fall back to native dialogs
          if (cancelLabel) resolve(window.confirm(message));
          else { window.alert(message); resolve(true); }
          return;
        }
        dom.dialogTitle.textContent = title;
        dom.dialogMessage.textContent = message;
        dom.dialogConfirm.textContent = confirmLabel;
        dom.dialogConfirm.classList.toggle("btn-danger-fill", danger);
        dom.dialogCancel.hidden = !cancelLabel;
        if (cancelLabel) dom.dialogCancel.textContent = cancelLabel;

        d.addEventListener("close", () => resolve(d.returnValue === "confirm"), { once: true });
        d.returnValue = "";
        d.showModal();
      });
    }

    /* ---------------------------------------------------------------------
     * 9. Wiring
     * ------------------------------------------------------------------- */
    function bindEvents() {
      if (dom.btnArcadeExit) dom.btnArcadeExit.addEventListener("click", () => {
        if (window.VakyaArcade) window.VakyaArcade.exitArena();
      });

      // Reset
      dom.btnReset.addEventListener("click", async () => {
        const ok = await showDialog({
          title: "Reset progress?",
          message: "This will reset your sentences and words seen counters back to zero.",
          confirmLabel: "Reset",
          cancelLabel: "Cancel",
          danger: true
        });
        if (!ok) return;
        progress = freshProgress();
        saveProgress();
        renderStats();
        renderHome();
      });

      // dialog: clicking the backdrop dismisses it
      dom.dialog.addEventListener("click", e => {
        if (e.target === dom.dialog) dom.dialog.close("cancel");
      });
    }

    function init() {
      cacheDom();
      bindEvents();

      progress = loadProgress();
      renderHome();

      loadData()
      .then(data => {
        sentences = data;
        renderHome();
        if (window.VakyaArcade) {
          window.VakyaArcade.init(sentences);
        }
      })
      .catch(err => {
        console.error(err);
        showDialog({
          title: "Couldn't load sentences",
          message: "Serve this folder over HTTP (for example, run `python3 -m http.server`) and reload the page."
        });
      });
    }

    document.addEventListener("DOMContentLoaded", init);
     })();
