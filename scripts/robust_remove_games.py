import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
suite_path = ROOT / "assets" / "suite.js"
code = suite_path.read_text()

games_to_remove = ['Connect the Threads', 'Classic Builder', 'Sentence Anagram Hunt', 'Bilingual Word Search', 'Odd-One-Out', 'Sentence Slot Machine', 'Sentence Tile Snap', 'Spot the Mistake', 'Color-Coded Syntax Highlighting', 'The Grammar Sorter', 
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
    'Contextual Tap-Tap'
]

# Each game in GAMES_PART1 / GAMES_PART2 starts with `{ \n id: "...", \n title: "..."`
# and ends with ` }` followed by comma or array end.
# We can find each game object precisely by tracking matching braces `{` and `}` starting from `{` before `title: "..."`.

for g in games_to_remove:
    needle = f'title: "{g}"'
    if needle not in code:
        print(f"NOT FOUND: {g}")
        continue
    pos = code.index(needle)
    # Scan backward to the opening `{` of this game object
    start_brace = code.rindex("{", 0, pos)
    
    # Also find any preceding comment like `// ------\n // Game ...\n`
    prev_sep = code.rfind("// -----------------------------------------------------------------------", 0, start_brace)
    if prev_sep != -1 and code[prev_sep:start_brace].strip().startswith("//"):
        remove_start = prev_sep
    else:
        remove_start = start_brace
        
    # Scan forward from start_brace counting braces to find the matching closing `}`
    depth = 0
    i = start_brace
    while i < len(code):
        if code[i] == "{":
            depth += 1
        elif code[i] == "}":
            depth -= 1
            if depth == 0:
                end_brace = i
                break
        i += 1
    
    # Check if there is a trailing comma
    remove_end = end_brace + 1
    while remove_end < len(code) and code[remove_end] in " \t\r\n":
        remove_end += 1
    if remove_end < len(code) and code[remove_end] == ",":
        remove_end += 1
    while remove_end < len(code) and code[remove_end] in " \t\r\n":
        remove_end += 1
        
    code = code[:remove_start] + code[remove_end:]
    print(f"Removed: {g}")

# If trailing comma before array end `];`, clean it up:
import re
code = re.sub(r',\s*\];', '\n  ];', code)

suite_path.write_text(code)
print("All requested games removed successfully.")
