from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
suite_path = ROOT / "assets" / "suite.js"
code = suite_path.read_text()

new_game_code = """
    // -----------------------------------------------------------------------
    // Game: Target Slot Lock (Predefined Word Anchors)
    // -----------------------------------------------------------------------
    {
      id: "slot-anchor",
      title: "Target Slot Lock",
      tagline: "Tap Hindi words to lock them into their exact predefined sentence positions",
      icon: "pin",
      start(board) {
        const sentence = engine.getRandomSentence(s => {
          const c = s.hi.split(/\\s+/).length;
          return c >= 3 && c <= 7;
        });
        const words = sentence.hi.split(/\\s+/);
        let filledCount = 0;

        engine.currentSentence = sentence;
        // Hint highlights any currently unplaced word in the bank
        const pickHint = () => {
          const unplaced = [];
          words.forEach((w, idx) => {
            const slot = board.querySelector(`.anchor-slot[data-pos="${idx}"]`);
            if (slot && slot.classList.contains("empty")) unplaced.push(w);
          });
          engine.currentHintWord = unplaced.length ? sample(unplaced) : null;
        };
        engine.onHint = pickHint;

        // Shuffle tiles in bank, associating each correct tile with its fixed target index
        const tilePool = shuffle(words.map((w, idx) => ({ word: w, targetPos: idx })));

        board.innerHTML = `
          <div class="arcade-card">
            <div class="arcade-prompt-box">
              <span class="arcade-sub">Target English Sentence:</span>
              <p class="arcade-sentence-display">${sentence.en}</p>
            </div>
            <div class="arcade-sub" style="margin-bottom: 0.5rem; text-align: center;">
              Sentence Placeholders (tap matching words to anchor into position):
            </div>
            <div class="anchor-slots-container" id="anchor-slots">
              ${words.map((_, idx) => `
                <div class="anchor-slot empty" data-pos="${idx}">
                  <span class="anchor-slot-num">#${idx + 1}</span>
                  <span class="anchor-slot-word">____</span>
                </div>
              `).join("")}
            </div>
            <div class="anchor-tile-bank" id="anchor-bank">
              ${tilePool.map((item, tIdx) => `
                <button type="button" class="anchor-word-btn" data-word="${item.word}" data-target-pos="${item.targetPos}" data-tile-id="${tIdx}">
                  ${item.word}
                </button>
              `).join("")}
            </div>
          </div>
        `;

        pickHint();

        board.querySelector("#anchor-bank").addEventListener("click", e => {
          const btn = e.target.closest(".anchor-word-btn");
          if (!btn || btn.disabled) return;

          const targetPos = parseInt(btn.dataset.targetPos, 10);
          const word = btn.dataset.word;
          const slot = board.querySelector(`.anchor-slot[data-pos="${targetPos}"]`);

          if (slot && slot.classList.contains("empty")) {
            playSound("pop");
            slot.classList.remove("empty");
            slot.classList.add("filled");
            slot.querySelector(".anchor-slot-word").textContent = word;
            btn.disabled = true;
            filledCount++;

            pickHint();

            if (filledCount === words.length) {
              playSound("tap");
              engine.completeRound();
              setTimeout(() => this.start(board), 700);
            }
          } else {
            playSound("error");
            engine.wrong();
            btn.classList.add("shake-bad");
            setTimeout(() => btn.classList.remove("shake-bad"), 400);
          }
        });
      }
    }
"""

marker = "    // Game 31: The Sentence Dominoes (Chain Reaction)\n    // -----------------------------------------------------------------------\n    // Game 32: Cloze Fill Challenge\n    ];"
if marker in code:
    code = code.replace(marker, new_game_code + "\n  ];")
else:
    # Replace before closing ];
    idx = code.rindex("];\n\n  window.__VakyaGamesPart2")
    code = code[:idx] + new_game_code + "\n  " + code[idx:]

suite_path.write_text(code)
print("Added Target Slot Lock to suite.js")
