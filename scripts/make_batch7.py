import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Read chunk1 words
words1 = Path(ROOT / "scripts" / "missing" / "chunk1.txt").read_text().split()
print(f"Target words in chunk1: {len(words1)}")

# We will build sentences covering all words1, plus idioms 101-135, plus tense/verb boosters.
# Let's inspect idioms 101-135 from VAKYA.md
lines = (ROOT / "VAKYA.md").read_text().splitlines()
sec3_idioms = []
in_sec = False
for l in lines:
    if l.startswith("## 3."): in_sec = True
    elif l.startswith("## 4."): in_sec = False
    if in_sec:
        m = re.match(r"\|\s*\d+\s*\|\s*\*\*(.+?)\*\*\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", l)
        if m:
            sec3_idioms.append((m.group(1).strip(), m.group(3).strip(), m.group(4).strip()))

print(f"Total idioms available: {len(sec3_idioms)}")
batch7_idioms = sec3_idioms[100:135] # 35 new idioms
print(f"Batch 7 idiom count: {len(batch7_idioms)}")

