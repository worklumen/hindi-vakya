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
          tilesCont.innerHTML = shuffled.map((item, i) => `
            <button type="button" class="arcade-chip ${placed.includes(item.origIndex) ? "used" : ""}" data-tile-idx="${i}">
              ${item.word}
            </button>
          `).join("");
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
              slotEl.textContent = item.word;
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
                ${currentWords.map((w, idx) => `
                  <button type="button" class="swap-word-btn" data-idx="${idx}">
                    ${w}
                  </button>
                `).join("")}
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
        // Find a sentence that contains postpositions or common inflected words
        const inflections = [
          { group: ["का", "के", "की"] },
          { group: ["रहा", "रही", "रहे"] },
          { group: ["था", "थी", "थे"] },
          { group: ["गया", "गई", "गए"] },
          { group: ["करता", "करती", "करते"] },
          { group: ["जाता", "जाती", "जाते"] },
          { group: ["होता", "होती", "होते"] },
          { group: ["सकता", "सकती", "सकते"] },
          { group: ["आता", "आती", "आते"] },
          { group: ["ने", "को", "से", "में", "पर"] }
        ];

        const sentence = engine.getRandomSentence(s => {
          const wList = s.hi.split(/\s+/);
          return wList.length >= 3 && inflections.some(inf => wList.some(w => inf.group.includes(w)));
        }) || engine.getRandomSentence(s => s.hi.split(/\s+/).length >= 3);

        const words = sentence.hi.split(/\s+/);

        // Find candidate words in sentence that match our inflection groups
        let targetIdx = -1;
        let matchedGroup = null;
        for (let i = 0; i < words.length; i++) {
          const found = inflections.find(inf => inf.group.includes(words[i]));
          if (found) {
            targetIdx = i;
            matchedGroup = found.group;
            break;
          }
        }

        // Fallback if no specific inflection matched
        if (targetIdx === -1) {
          targetIdx = Math.floor(Math.random() * words.length);
          const other = engine.getRandomSentence(s => s.id !== sentence.id);
          const otherWord = other ? sample(other.hi.split(/\s+/)) : "नहीं";
          matchedGroup = [words[targetIdx], otherWord];
        }

        const correctWord = words[targetIdx];
        const alternativeOptions = matchedGroup.filter(w => w !== correctWord);
        const sickReplacement = sample(alternativeOptions) || "का";
        const remedies = shuffle([correctWord, ...alternativeOptions.slice(0, 2)]);

        const displayedWords = words.slice();
        displayedWords[targetIdx] = sickReplacement;

        engine.currentSentence = sentence;

        board.innerHTML = `
          <div class="arcade-card">
            <div class="arcade-prompt-box">
              <p class="arcade-sentence-display">${sentence.en}</p>
            </div>
            <div class="doctor-display" id="doctor-display">
              ${displayedWords.map((w, idx) => `
                <button type="button" class="doctor-word-btn" data-idx="${idx}" data-word="${w}">
                  ${w}
                </button>
              `).join("")}
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
              targetBtn.textContent = correctWord;
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

  window.__VakyaGamesPart1 = GAMES;
})();
"use strict";
/**
 * games-suite-2.js — Interactive Games 17 to 32
 */
(() => {
  const engine = window.__VakyaArcadeEngine;
  const shuffle = window.__shuffle;
  const sample = window.__sample;
  const playSound = window.__playSound;

  const GAMES_PART2 = [];

  window.__VakyaGamesPart2 = GAMES_PART2;
})();
