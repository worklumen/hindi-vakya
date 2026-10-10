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
    let vocabTotal = 0;     // total words in the vocabulary, from data/vocab-manifest.json
    /** @type {{sentences:Object, words:Object, plays:number, level:number, cleanStreak:number}} */
    let progress = null;

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
      vocabTotal = all.length;
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

    const randomItem = arr => arr[Math.floor(Math.random() * arr.length)];

    function pickSentence() {
      if (sentences.length === 0) return null;
      const lvl = session.playLevel !== null ? session.playLevel : 0;
      // Only sentences inside the active band; an empty band means no content
      // exists for that level yet — never fall back to other levels.
      let pool = sentences.filter(s => inLevel(s, lvl));
      if (pool.length === 0) return null;

      // avoid repeating the sentence just played, when possible
      const noRepeat = pool.filter(s => s.id !== session.lastPlayedId);
      if (noRepeat.length > 0) pool = noRepeat;

      return randomItem(pool);
    }

    /* ---------------------------------------------------------------------
     * 6. Round (game logic)
     * ------------------------------------------------------------------- */
    function vibrate(pattern) {
      try { if (navigator.vibrate) navigator.vibrate(pattern); } catch (e) { /* unsupported */ }
    }



    function buildBank(sentence) {
      // distractors: unique words from other sentences
      const targetSet = new Set(sentence.words);
      const candidates = shuffle(
        [...new Set(sentences.flatMap(s => (s.id === sentence.id ? [] : s.words)))]
        .filter(w => !targetSet.has(w))
      );
      const count = Math.max(2, Math.round(sentence.words.length * CONFIG.distractorRatio));
      return shuffle(
        sentence.words.map(word => ({ word, distract: false }))
        .concat(candidates.slice(0, count).map(word => ({ word, distract: true })))
      );
    }

    function startGame() {
      const picked = pickSentence();
      if (!picked) {
        session.playLevel = null;
        renderHome();
        showDialog({
          title: "No sentences yet",
          message: "There are no sentences for this level yet — more are being added soon."
        });
        return;
      }
      showSection("game");
      progress.plays++;
      newRound(picked);
    }

    function renderEnSentence() {
      const frag = document.createDocumentFragment();
      round.sentence.en.split(" ").forEach((word, j) => {
        if (j > 0) frag.appendChild(document.createTextNode(" "));
        const span = el("span", "en-word", word);
        span.dataset.enIndex = String(j);
        frag.appendChild(span);
      });
      dom.enSentence.replaceChildren(frag);
    }

    function newRound(sentence) {
      session.lastPlayedId = sentence.id;

      round = {
        sentence,
        // one predefined slot per word; taps fill the matching slot
        answer: new Array(sentence.words.length).fill(null), // null | { word, bankIndex }
        bank: buildBank(sentence),                           // { word, distract }[]
        locked: false,        // true once the sentence is fully correct
        touched: false,
        wrongTaps: 0
      };

      renderEnSentence();
      dom.actionsPlay.hidden = false;
      dom.actionsDone.hidden = true;
      renderBank();
      renderRound();
    }

    function placeTile(bankIndex, chipEl) {
      if (!round || round.locked) return;
      if (!round.touched) {
        round.touched = true;
        sentenceState(round.sentence.id).seen++;
      }
      const tile = round.bank[bankIndex];
      const used = round.answer.some(a => a && a.bankIndex === bankIndex);
      if (used) return;

      // The word snaps to its designated place, so words can be filled in any
      // order; an incorrect word flashes red and stays in the bank.
      const spot = round.sentence.words.findIndex((w, j) => w === tile.word && !round.answer[j]);
      if (spot === -1) {
        round.wrongTaps++;
        chipEl.classList.add("reject");
        setTimeout(() => chipEl.classList.remove("reject"), CONFIG.rejectFlashMs);
        vibrate(60);
        return;
      }
      round.answer[spot] = { word: tile.word, bankIndex };
      renderRound();
    }

    function removeTile(slotIndex) {
      if (!round || round.locked) return;
      round.answer[slotIndex] = null;
      renderRound();
    }

    function clearAnswer() {
      if (!round || round.locked) return;
      round.answer = new Array(round.sentence.words.length).fill(null);
      renderRound();
    }

    function checkAnswer() {
      if (!round || round.locked || !round.answer.every(Boolean)) return;

      // The game only ever rewards the correct sentence. Until the tiles match,
      // the round stays open — rearranging carries no penalty.
      const words = round.sentence.words;
      if (!round.answer.every((a, i) => a.word === words[i])) return;

      round.locked = true;

      // slips: wrong picks — only a spotless round earns credit
      const slips = round.wrongTaps;
      const clean = slips === 0;
      sentenceState(round.sentence.id).done++;

      for (const w of words) {
        const wSt = wordState(w);
        wSt.enc++;
        if (clean) wSt.done++;
      }

      vibrate(50);
      dom.actionsPlay.hidden = true;
      dom.actionsDone.hidden = false;
      saveProgress();
      renderRound();
      renderHome();
    }

    function exitGame() {
      round = null;
      session.playLevel = null; // leaving the game returns to adaptive level
      showSection("home");
    }

    /* ---------------------------------------------------------------------
     * 7. Views
     * ------------------------------------------------------------------- */
    const dom = {};
    const $ = id => document.getElementById(id);

    function cacheDom() {
      [
        "section-home", "section-game", "section-stats",
        "nav-home", "nav-stats", "bottom-nav",
        "btn-quick-play",
        "btn-exit", "game-count", "en-sentence",
        "answer-row", "place-track", "place-progress", "tile-bank",
        "actions-play", "actions-done",
        "btn-check", "btn-clear", "btn-done", "btn-next",
        "btn-reset",
        "dialog", "dialog-title", "dialog-message", "dialog-confirm", "dialog-cancel",
        "btn-arcade-exit",
        // KPI & Stats
        "kpi-sentences-seen", "kpi-sentences-sub", "kpi-sentences-done", "kpi-sentences-rate",
        "kpi-words-seen", "kpi-words-sub", "kpi-arcade-pts", "kpi-arcade-sub",
        "games-stats-tbody"
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
      for (const s of ["home", "game", "stats"]) {
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
      if (!sentences || sentences.length === 0) return;

      // 1. KPI Cards
      let totalSeen = 0, totalDone = 0;
      for (const s of sentences) {
        const st = progress.sentences[s.id];
        if (st) {
          if (st.seen > 0) totalSeen++;
          if (st.done > 0) totalDone++;
        }
      }

      const activeWords = [...new Set(sentences.flatMap(s => s.words))]
        .filter(w => progress.words[w] && progress.words[w].enc > 0);
      const totalWordsDone = activeWords.reduce((n, w) => n + (progress.words[w].done || 0), 0);

      if (dom.kpiSentencesSeen) dom.kpiSentencesSeen.textContent = String(totalSeen);
      if (dom.kpiSentencesSub) dom.kpiSentencesSub.textContent = `of ${sentences.length} total`;
      if (dom.kpiSentencesDone) dom.kpiSentencesDone.textContent = String(totalDone);
      if (dom.kpiSentencesRate) {
        const pct = sentences.length ? Math.round((totalDone / sentences.length) * 100) : 0;
        dom.kpiSentencesRate.textContent = `${pct}% done`;
      }
      if (dom.kpiWordsSeen) dom.kpiWordsSeen.textContent = String(activeWords.length);
      if (dom.kpiWordsSub) dom.kpiWordsSub.textContent = `${totalWordsDone} done`;
      let gamePlays = 0, gameDone = 0;
      for (const v of Object.values(progress.games || {})) {
        gamePlays += v.plays || 0;
        gameDone += v.done || 0;
      }
      if (dom.kpiArcadePts) {
        dom.kpiArcadePts.textContent = gamePlays ? (Math.min(gameDone / gamePlays, 1) * 10).toFixed(1) : "-";
      }
      if (dom.kpiArcadeSub) {
        dom.kpiArcadeSub.textContent = gamePlays ? `${gameDone} done of ${gamePlays} played` : "out of 10";
      }

      // 2. Games Performance Table
      if (dom.gamesStatsTbody) {
        const gamesList = window.VakyaArcade ? window.VakyaArcade.games : [];
        const frag = document.createDocumentFragment();
        gamesList.forEach(g => {
          const gData = (progress.games && progress.games[g.id]) || { plays: 0, done: 0 };
          const tr = el("tr");
          const tdTitle = el("td", "", g.title);
          const tdPlays = el("td", "num", String(gData.plays || 0));
          const tdDone = el("td", "num", String(gData.done || 0));
          tr.append(tdTitle, tdPlays, tdDone);
          frag.appendChild(tr);
        });
        dom.gamesStatsTbody.replaceChildren(frag);
      }
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

      // Quick play / Sentence Builder button
      if (dom.btnQuickPlay) {
        dom.btnQuickPlay.addEventListener("click", () => {
          session.playLevel = Math.floor(Math.random() * LEVELS.length);
          startGame();
        });
      }


      // game
      dom.btnExit.addEventListener("click", exitGame);
      dom.btnDone.addEventListener("click", exitGame);
      dom.btnNext.addEventListener("click", startGame);
      dom.btnCheck.addEventListener("click", checkAnswer);
      dom.btnClear.addEventListener("click", clearAnswer);

      dom.tileBank.addEventListener("click", e => {
        const chip = e.target.closest("[data-index]");
        if (chip) placeTile(Number(chip.dataset.index), chip);
      });
      dom.answerRow.addEventListener("click", e => {
        const chip = e.target.closest("[data-slot]");
        if (chip) removeTile(Number(chip.dataset.slot));
      });

      // Reset
      dom.btnReset.addEventListener("click", async () => {
        const ok = await showDialog({
          title: "Reset all progress?",
          message: "This permanently clears your sentence and word counts, play counts and game ratings. It cannot be undone.",
          confirmLabel: "Reset all",
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
