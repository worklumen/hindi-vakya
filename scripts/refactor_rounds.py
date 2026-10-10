import re
R = "/home/zenhall/Projects/hindi-vakya/"


def rd(p):
    return open(R + p, encoding="utf-8").read()


def wr(p, s):
    open(R + p, "w", encoding="utf-8").write(s)


def rep(s, a, b):
    assert a in s, "missing: " + a[:70]
    return s.replace(a, b, 1)


# ---------------- engine.js ----------------
e = rd("assets/engine.js")
e = rep(e, "    streak: 0,\n", "    round: null,\n    hintEls: [],\n")
i = e.index("    addScore(points = 10) {")
j = e.index("    showToast(text) {")
e = e[:i] + '''    /** Called by the hub every time a game (re)starts a round. */
    beginRound() {
      this.round = { touched: false, done: false };
      this.clearHint();
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

''' + e[j:]

i = e.index("    showHint() {")
j = e.index("    stopTimer() {")
e = e[:i] + '''    clearHint() {
      if (this.hintTimer) {
        clearTimeout(this.hintTimer);
        this.hintTimer = null;
      }
      this.hintEls.forEach(el => el.classList.remove("arcade-hint-pulse"));
      this.hintEls = [];
    },

    /** Highlights what is already on screen (no toast, no speech) for 1.5s. */
    showHint() {
      playSound("tap");
      this.clearHint();
      const arena = document.getElementById("arcade-arena-board");
      if (!arena) return;

      const targetWord = this.currentHintWord;
      const targets = arena.querySelectorAll(
        "button, .arcade-chip, .bubble-btn, .auditor-chip, .odd-option-btn, .bridge-slot, .reveal-slot, .snake-food, .slot-reel, .anagram-btn, .plinko-slot-btn, .ws-cell, .domino-tile, .memory-card, .sorter-bucket, .syntax-hi-word, .mole-btn"
      );
      const hits = [];
      if (targetWord) {
        targets.forEach(el => {
          const txt = (el.textContent || "").trim();
          const d = el.dataset || {};
          const dw = d.word || d.choice || d.c || d.hi || d.part || d.text || d.en;
          if (txt === targetWord || dw === targetWord) hits.push(el);
        });
      }
      // alignment: the English partner of the hinted Hindi word, if shown on screen
      if (this.currentSentence && targetWord) {
        const pair = getSentenceWordPairs(this.currentSentence).find(p => p.hiWord === targetWord);
        if (pair && pair.enWord) {
          targets.forEach(el => {
            const txt = (el.textContent || "").trim();
            if (txt === pair.enWord && !hits.includes(el)) hits.push(el);
          });
        }
      }
      // fallback: nudge the prompt that is already on screen
      if (hits.length === 0) {
        const prompt = arena.querySelector(".arcade-prompt-box, .arcade-sentence-display, .arcade-card");
        if (prompt) hits.push(prompt);
      }
      hits.forEach(el => el.classList.add("arcade-hint-pulse"));
      this.hintEls = hits;
      this.hintTimer = setTimeout(() => this.clearHint(), 1500);
    },

''' + e[j:]
wr("assets/engine.js", e)

# ---------------- hub.js ----------------
h = rd("assets/hub.js")
h = rep(h, "  const GAMES = (window.__VakyaGamesPart1 || []).concat(window.__VakyaGamesPart2 || []);\n",
"""  const GAMES = (window.__VakyaGamesPart1 || []).concat(window.__VakyaGamesPart2 || []);

  // Every (re)start of a round resets the touched/done tracking.
  GAMES.forEach(g => {
    const original = g.start;
    g.start = function (board) {
      engine.beginRound();
      return original.call(this, board);
    };
  });
""")
h = rep(h, """        hintBtn.onclick = () => engine.showHint();
      }
""", """        hintBtn.onclick = () => engine.showHint();
      }
      const nextBtn = document.getElementById("btn-arcade-next");
      if (nextBtn) {
        nextBtn.onclick = () => {
          const board = document.getElementById("arcade-arena-board");
          if (engine.activeGame && board) engine.activeGame.start(board);
        };
      }
      const arenaBoard = document.getElementById("arcade-arena-board");
      if (arenaBoard) {
        // capture phase: runs before the game's own handler sees the click
        arenaBoard.addEventListener("click", e => {
          if (e.target.closest("button, .memory-card, .syntax-hi-word")) engine.markTouched();
        }, true);
      }
""")
h = rep(h, "      engine.score = 0;\n      engine.streak = 0;\n", "")
h = rep(h, """      if (window.recordGamePlay) {
        window.recordGamePlay(g.id);
      }

""", "")
h = rep(h, "      engine.updateHud();\n", "")
wr("assets/hub.js", h)

# ---------------- index.html ----------------
x = rd("index.html")
x = rep(x, '''              <span class="arcade-stat score"><span class="stat-lbl">PTS</span> <strong id="arcade-hud-score">0</strong></span>
              <span class="arcade-stat streak"><span class="stat-lbl">STREAK</span> <strong id="arcade-hud-streak">0</strong></span>
''', '''              <button id="btn-arcade-next" class="icon-btn arcade-next-btn" type="button" aria-label="Next round" title="Next">&#x23ED;</button>
''')
x = rep(x, '<span class="kpi-label">Arcade Points</span>', '<span class="kpi-label">Play Rating</span>')
x = rep(x, '<small id="kpi-arcade-sub" class="kpi-sub">total score</small>', '<small id="kpi-arcade-sub" class="kpi-sub">out of 10</small>')
x = rep(x, '''                    <th scope="col" class="num">Streak</th>
                    <th scope="col" class="num">High</th>
''', '''                    <th scope="col" class="num">Done</th>
''')
wr("index.html", x)

# ---------------- base.css ----------------
c = rd("assets/base.css")
c = rep(c, '''
#games-stats-table th:nth-child(4),
#games-stats-table td:nth-child(4) {
  width: 68px;
}''', "")
wr("assets/base.css", c)

# ---------------- app.js ----------------
a = rd("assets/app.js")
a = rep(a, "        cleanStreak: 0,\n        arcadePoints: 0,\n        games: {} // { [gameId]: { plays: number, bestStreak: number, highScore: number } }",
        "        games: {} // { [gameId]: { plays: number, done: number } }")
a = rep(a, "      p.cleanStreak = p.cleanStreak || 0;\n", "")
a = rep(a, "      p.arcadePoints = p.arcadePoints || 0;\n      p.games = p.games || {};\n",
"""      delete p.arcadePoints;
      delete p.cleanStreak;
      p.games = p.games || {};
      for (const g of Object.values(p.games)) {
        g.plays = g.plays || 0;
        g.done = g.done || 0;
        delete g.bestStreak;
        delete g.highScore;
      }
""")
i = a.index("    // Expose helpers for games.js")
j = a.index("    function sentenceState(id) {")
a = a[:i] + '''    // Called by the arcade engine: "touch" = first interaction, "done" = solved.
    window.recordGameEvent = function(gameId, sentence, kind) {
      if (!progress) return;
      if (!progress.games) progress.games = {};
      if (!progress.games[gameId]) progress.games[gameId] = { plays: 0, done: 0 };
      const g = progress.games[gameId];
      const isDone = kind === "done";
      g[isDone ? "done" : "plays"]++;
      if (sentence) {
        sentenceState(sentence.id)[isDone ? "done" : "seen"]++;
        for (const w of (sentence.words || sentence.hi.split(/\\s+/))) {
          wordState(w)[isDone ? "done" : "enc"]++;
        }
      }
      saveProgress();
    };

''' + a[j:]
a = rep(a, "progress.words[w] = { enc: 0, done: 0, streak: 0, target: CONFIG.learnThreshold, learnt: false };",
        "progress.words[w] = { enc: 0, done: 0 };")
a = rep(a, "        if (clean) { wSt.done++; wSt.streak++; }\n        if (!wSt.learnt && wSt.streak >= wSt.target) wSt.learnt = true;\n",
        "        if (clean) wSt.done++;\n")
a = rep(a, "      progress.cleanStreak++; // streak badge only — levels no longer auto-advance\n      if (slips > 0) progress.cleanStreak = 0;\n\n", "")
# sentence builder: count seen on first placement, not on load
a = rep(a, "      session.lastPlayedId = sentence.id;\n      sentenceState(sentence.id).seen++;\n", "      session.lastPlayedId = sentence.id;\n")
a = rep(a, "        hintsUsed: 0,\n", "        touched: false,\n        hintsUsed: 0,\n")
a = rep(a, "      const tile = round.bank[bankIndex];\n      const used",
        "      if (!round.touched) {\n        round.touched = true;\n        sentenceState(round.sentence.id).seen++;\n      }\n      const tile = round.bank[bankIndex];\n      const used")
a = rep(a, "arcade points, and game streaks", "play counts and game ratings")
a = rep(a, "      if (dom.kpiArcadePts) dom.kpiArcadePts.textContent = String(progress.arcadePoints || 0);\n      if (dom.kpiArcadeSub) dom.kpiArcadeSub.textContent = `from all game drills`;\n",
"""      let gamePlays = 0, gameDone = 0;
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
""")
a = rep(a, "{ plays: 0, bestStreak: 0, highScore: 0 };\n          const tr", "{ plays: 0, done: 0 };\n          const tr")
a = rep(a, '''          const tdStreak = el("td", "num", String(gData.bestStreak || 0));
          const tdScore = el("td", "num", String(gData.highScore || 0));
          tr.append(tdTitle, tdPlays, tdStreak, tdScore);''', '''          const tdDone = el("td", "num", String(gData.done || 0));
          tr.append(tdTitle, tdPlays, tdDone);''')
wr("assets/app.js", a)

# ---------------- suite.js ----------------
s = rd("assets/suite.js")
# multi-score games: move the single completion to the true end of the round
s = rep(s, "            engine.addScore(10);\n            wordIdx++;", '            playSound("pop");\n            wordIdx++;')
s = rep(s, "speakHindi(sentence.hi);\n              setTimeout(() => this.start(board), 700);",
        "engine.completeRound();\n              setTimeout(() => this.start(board), 700);")
s = rep(s, "              engine.addScore(15);\n              setTimeout(() => {\n                c1.classList",
        '              playSound("pop");\n              setTimeout(() => {\n                c1.classList')
s = rep(s, "                if (clearedCount === activePairs.length) {",
        "                if (clearedCount === activePairs.length) {\n                  engine.completeRound();")
s = re.sub(r"engine\.addScore\([^)]*\)", "engine.completeRound()", s)
s = s.replace("engine.resetStreak()", "engine.wrong()")
# post-completion speech (statement-only lines)
s = re.sub(r"^[ \t]*speakHindi\([^\n]*\);[ \t]*\n", "", s, flags=re.M)
wr("assets/suite.js", s)
print("ok")
