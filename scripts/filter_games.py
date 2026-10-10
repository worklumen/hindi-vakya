import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
suite_path = ROOT / "assets" / "suite.js"
code = suite_path.read_text()

games_to_remove = [
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
    'Contextual Tap-Tap'
]

# We will remove them using regex matching each game object block
# Let's inspect each game block structure
for g in games_to_remove:
    # Match from // --- or { id: ... title: g ...
    pat = re.compile(r'(\s*//[ -]+\n\s*\{\s*\n\s*id:\s*"[^"]+",\s*\n\s*title:\s*"' + re.escape(g) + r'",.*?\n\s*\},?)', re.DOTALL)
    m = pat.search(code)
    if m:
        code = code[:m.start()] + code[m.end():]
        print(f"Removed '{g}'")
    else:
        # Check without trailing comma
        pat2 = re.compile(r'(\s*//[ -]+\n\s*\{\s*\n\s*id:\s*"[^"]+",\s*\n\s*title:\s*"' + re.escape(g) + r'",.*?\n\s*\})', re.DOTALL)
        m2 = pat2.search(code)
        if m2:
            code = code[:m2.start()] + code[m2.end():]
            print(f"Removed '{g}' (alt)")
        else:
            print(f"FAILED to match '{g}'")

suite_path.write_text(code)
print("Filter pass complete.")
