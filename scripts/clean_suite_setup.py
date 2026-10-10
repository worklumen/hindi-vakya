import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
suite_path = ROOT / "assets" / "suite.js"

# Let's inspect the entire original suite.js to extract each game block cleanly as a dict
code = suite_path.read_text()

# Target Slot Lock code:
anchor_game = """    // -----------------------------------------------------------------------
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
        const pickHint = () => {
          const unplaced = [];
          words.forEach((w, idx) => {
            const slot = board.querySelector(`.anchor-slot[data-pos="${idx}"]`);
            if (slot && slot.classList.contains("empty")) unplaced.push(w);
          });
          engine.currentHintWord = unplaced.length ? sample(unplaced) : null;
        };
        engine.onHint = pickHint;

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
    }"""

# Games to eliminate completely:
ELIMINATE = [
    'Cloze Fill Challenge',
    'The Sentence Dominoes',
    'Pair Plinko',
    'The Sentence Detective',
    'Word Drop Puzzle',
    'The Word Pyramid',
    'Speed Verb Conjugator',
    'The Mirror Match',
    'Bilingual Crossword Clues',
    'The Sentence Snake',
    'Type-Ahead Reverse Translate',
    'The Codebreaker',
    'Translation Match Quiz',
    'Contextual Tap-Tap',
    'Color-Coded Syntax Highlighting',
    'The Grammar Sorter',
    'Sentence Jumble & Reveal'
]

# We want:
# 1. Classic Builder
# 2. The Word Bridge
# 3. Target Slot Lock
# 4. Flashcard Swipes
# 5. The Word Link Matcher
# ... and remaining games

# Remove all eliminated games
for g in ELIMINATE:
    needle = f'title: "{g}"'
    if needle not in code: continue
    pos = code.index(needle)
    start_brace = code.rindex("{", 0, pos)
    prev_sep = code.rfind("// -----------------------------------------------------------------------", 0, start_brace)
    if prev_sep != -1 and code[prev_sep:start_brace].strip().startswith("//"):
        remove_start = prev_sep
    else:
        remove_start = start_brace
    depth = 0
    i = start_brace
    while i < len(code):
        if code[i] == "{": depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                end_brace = i
                break
        i += 1
    remove_end = end_brace + 1
    while remove_end < len(code) and code[remove_end] in " \t\r\n": remove_end += 1
    if remove_end < len(code) and code[remove_end] == ",": remove_end += 1
    while remove_end < len(code) and code[remove_end] in " \t\r\n": remove_end += 1
    code = code[:remove_start] + code[remove_end:]
    print(f"Removed: {g}")

# Now insert anchor_game right after The Word Bridge!
bridge_needle = 'title: "The Word Bridge"'
pos_b = code.index(bridge_needle)
start_b = code.rindex("{", 0, pos_b)
depth = 0
i = start_b
while i < len(code):
    if code[i] == "{": depth += 1
    elif code[i] == "}":
        depth -= 1
        if depth == 0:
            end_bridge = i
            break
    i += 1

# Insert immediately after end_bridge
insert_pos = end_bridge + 1
# Check if comma follows
while insert_pos < len(code) and code[insert_pos] in " \t\r\n": insert_pos += 1
if code[insert_pos] == ",": insert_pos += 1

insertion = "\n\n" + anchor_game + ",\n"
code = code[:insert_pos] + insertion + code[insert_pos:]

# Update Anagram Hunt to show full sentence if needed
code = re.sub(r'span class="arcade-sub">Sentence: "\$\{sentence\.en\}"</span>\s*<div class="anagram-target-slot"',
              'div class="arcade-prompt-box"><span class="arcade-sub">English Reference:</span><p class="arcade-sentence-display">${sentence.en}</p></div><div class="hi-large" style="margin-bottom: 1.25rem;">${words.map(w => w === targetWord ? \'<span class="type-slot-active">[ ___ ]</span>\' : w).join(" ")}</div><div class="anagram-target-slot"', code)

# Clean up trailing commas in array
code = re.sub(r',\s*\];', '\n  ];', code)

suite_path.write_text(code)
print("Configured suite.js with Target Slot Lock as 3rd game!")
