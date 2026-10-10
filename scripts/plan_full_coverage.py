import json, re, glob
from pathlib import Path

ROOT = Path('.')
tok = lambda t: re.findall(r'[\u0900-\u097F]+', t)
norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')

used = set()
for f in sorted(glob.glob('data/phrases*.json')):
    for s in json.load(open(f)):
        used.update(norm(w) for w in tok(s['hi']))

md = open('VAKYA.md').read().splitlines()
i = next(k for k,l in enumerate(md) if l.startswith('## 4.'))
vocab = []
for l in md[i+1:]:
    if l.startswith('#'): continue
    vocab.extend(norm(w) for w in re.findall(r'[ऀ-ॿ]+', l))

missing = [w for w in vocab if w not in used]
print(f"Total missing vocabulary: {len(missing)}")

# Group into 3 clean tranches:
# Chunk 1: 300 words -> phrases22.json (Batch 7)
# Chunk 2: 300 words -> phrases23.json (Batch 8)
# Chunk 3: 263 words -> phrases24.json (Batch 9)
Path('scripts/missing/chunk1.txt').write_text(' '.join(missing[:300]))
Path('scripts/missing/chunk2.txt').write_text(' '.join(missing[300:600]))
Path('scripts/missing/chunk3.txt').write_text(' '.join(missing[600:]))
print("Split into chunk1 (300), chunk2 (300), chunk3 (263)")
