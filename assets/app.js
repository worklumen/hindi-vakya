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
    storeKey: "hindi-vakya-state",
    learnThreshold: 10,    // consecutive spotless rounds needed to learn a word
    distractorRatio: 0.4,  // extra wrong tiles relative to sentence length
    rejectFlashMs: 600
  });

  // Word-count range per level (index 0-2, shown as Level 1-3)
  const LEVELS = Object.freeze([
    [2, 8],
    [9, 16],
    [17, 24]
  ]);

    /* ---------------------------------------------------------------------
     * 2. State
     * ------------------------------------------------------------------- */
    /** @type {{id:string|number, en:string, hi:string, freq:number, words:string[]}[]} */
    let sentences = [];
    let manifestSentenceTotal = 0;
    let manifestWordTotal = 0;
    let dictionary = {};    // { [hiWord]: string (en meaning) }
    /** @type {{sentences:Object, words:Object, plays:number, level:number, cleanStreak:number}} */
    let progress = null;

    window.__getWordMeaning = function (w) {
      if (!w) return "";
      const clean = w.replace(/[^\w\u0900-\u097F]/g, "");
      return dictionary[clean] || dictionary[w] || "";
    };

    const session = {
      playLevel: null,   // level entered via Random / level button; sticky until exit
 lastPlayedId: null
    };

    /** Active round; null when not in a game. */
    let round = null;

    /* ---------------------------------------------------------------------
     * 3. Storage
     * ------------------------------------------------------------------- */
    const clampLevel = l => Math.min(LEVELS.length - 1, Math.max(0, l || 0));

    const levelOfLength = n => (n <= LEVELS[0][1] ? 0 : n <= LEVELS[1][1] ? 1 : LEVELS.length - 1);

    const inLevel = (s, lvl) => {
      const [lo, hi] = LEVELS[clampLevel(lvl)];
      return s.words.length >= lo && s.words.length <= hi;
    };

    function freshProgress() {
      return {
        sentences: {},
        words: {},
        plays: 0,
        level: 0,
        games: {} // { [gameId]: { plays: number, done: number } }
      };
    }

    /** Upgrades state saved by older versions of the app. */
    function migrate(p) {
      if (typeof p.level === "number" && p.level > LEVELS.length - 1) {
        p.level = Math.max(0, levelOfLength(p.level));
      }
      p.level = clampLevel(p.level);
      p.plays = p.plays || 0;
      delete p.arcadePoints;
      delete p.cleanStreak;
      p.games = p.games || {};
      for (const g of Object.values(p.games)) {
        g.plays = g.plays || 0;
        g.done = g.done || 0;
        delete g.bestStreak;
        delete g.highScore;
      }

      if (!p.words) p.words = {};
      for (const w of Object.values(p.words)) {
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
     * 5. Selection engine
     * Pure random: the active level's band is the only filter. Every
     * sentence in the band is equally likely — no weighting by seen, done
     * or frequency; only the immediately-previous sentence is skipped
     * when alternatives exist.
     * ------------------------------------------------------------------- */
    function shuffle(arr) {
      const a = arr.slice();
      for (let i = a.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [a[i], a[j]] = [a[j], a[i]];
      }
      return a;
    }

    /* ---------------------------------------------------------------------
     * 5. Views & UI Controller
     * ------------------------------------------------------------------- */
    const dom = {};
    const $ = id => document.getElementById(id);

    function cacheDom() {
      [
        "section-home", "section-stats",
        "nav-home", "nav-stats", "bottom-nav",
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

    function el(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }

    function icon(name) {
      const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
      svg.setAttribute("class", "icon");
      svg.setAttribute("aria-hidden", "true");
      const use = document.createElementNS("http://www.w3.org/2000/svg", "use");
      use.setAttribute("href", `#i-${name}`);
      svg.appendChild(use);
      return svg;
    }

    function showSection(name) {
      if (window.VakyaArcade) {
        window.VakyaArcade.exitArena();
      }
      for (const s of ["home", "stats"]) {
        const secEl = dom["section" + s[0].toUpperCase() + s.slice(1)];
        if (secEl) {
          secEl.classList.toggle("active", s === name);
          secEl.hidden = s !== name;
        }
      }
      dom.navHome.classList.toggle("active", name === "home");
      dom.navStats.classList.toggle("active", name === "stats");

      const navButtons = [[dom.navHome, "home"], [dom.navStats, "stats"]];
      for (const [btn, key] of navButtons) {
        if (!btn) continue;
        if (key === name) btn.setAttribute("aria-current", "page");
        else btn.removeAttribute("aria-current");
      }

      // bottom nav remains always present across all sections
      if (dom.bottomNav) dom.bottomNav.classList.remove("hidden");

      if (name === "home") renderHome();
      if (name === "stats") renderStats();
      window.scrollTo(0, 0);
    }

    /* --- Home (Games Hub) --- */
    function renderHome() {
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
      // navigation
      dom.navHome.addEventListener("click", () => showSection("home"));
      dom.navStats.addEventListener("click", () => showSection("stats"));
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
