import json, re, glob
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent

# Load alignment generator
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')
tok = lambda t: re.findall(r'[\u0900-\u097F]+', t)

# Get current used words
used = set()
for f in sorted(glob.glob(str(ROOT / 'data' / 'phrases*.json'))):
    for s in json.load(open(f)):
        used.update(norm(w) for w in tok(s['hi']))

# Get VAKYA words
md = (ROOT / 'VAKYA.md').read_text().splitlines()
i = next(k for k,l in enumerate(md) if l.startswith('## 4.'))
vocab = []
for l in md[i+1:]:
    if l.startswith('#'): continue
    vocab.extend(norm(w) for w in re.findall(r'[ऀ-ॿ]+', l))

missing = [w for w in vocab if w not in used]
print(f"Total words missing: {len(missing)}")

# Load the 100 new idioms (indices 100 to 199)
all_idioms = []
in_sec = False
for l in md:
    if l.startswith("## 3."): in_sec = True
    elif l.startswith("## 4."): in_sec = False
    if in_sec:
        m = re.match(r"\|\s*\d+\s*\|\s*\*\*(.+?)\*\*\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", l)
        if m:
            all_idioms.append((m.group(1).strip(), m.group(3).strip(), m.group(4).strip()))

new_idioms = all_idioms[100:]
print(f"New idioms to embed: {len(new_idioms)}")

# Split missing words into 3 chunks: 300, 300, 263
c1 = missing[:300]
c2 = missing[300:600]
c3 = missing[600:]

# Split idioms into 35, 35, 30
id1 = new_idioms[:35]
id2 = new_idioms[35:70]
id3 = new_idioms[70:]

print(f"Chunk 1: {len(c1)} words, {len(id1)} idioms")
print(f"Chunk 2: {len(c2)} words, {len(id2)} idioms")
print(f"Chunk 3: {len(c3)} words, {len(id3)} idioms")
