from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
suite_path = ROOT / "assets" / "suite.js"
code = suite_path.read_text()

# 1. Extract Target Slot Lock definition
# It is located around the end of GAMES_PART2
m_anchor = re.search(r'(\s*//[ -]+\n\s*// Game: Target Slot Lock.*?\n\s*\{.*?\n\s*id:\s*"slot-anchor",.*?\n\s*\},?)', code, re.DOTALL)
if not m_anchor:
    print("FAILED to find slot-anchor")
    exit(1)

slot_anchor_code = m_anchor.group(1).rstrip(",").strip()
# Remove slot-anchor from its current location
code = code[:m_anchor.start()] + code[m_anchor.end():]

# Clean any trailing comma issues in GAMES_PART2
code = re.sub(r',\s*\];', '\n  ];', code)

# 2. Remove Sentence Jumble & Reveal
# Locate Sentence Jumble & Reveal
needle = 'title: "Sentence Jumble & Reveal"'
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

# Replace Sentence Jumble & Reveal with Target Slot Lock!
replacement = f"\n    // -----------------------------------------------------------------------\n    // Game 3: Target Slot Lock (Predefined Word Anchors)\n    // -----------------------------------------------------------------------\n    {slot_anchor_code},\n\n"

code = code[:remove_start] + replacement + code[remove_end:]

suite_path.write_text(code)
print("Successfully replaced Sentence Jumble & Reveal with Target Slot Lock as 3rd game.")
