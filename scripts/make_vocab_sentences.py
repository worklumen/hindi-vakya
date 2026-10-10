import json, re, glob
from pathlib import Path

ROOT = Path('.')
norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')
tok = lambda t: re.findall(r'[\u0900-\u097F]+', t)

# Load missing words
md = open('VAKYA.md').read().splitlines()
used = set()
for f in sorted(glob.glob('data/phrases*.json')):
    for s in json.load(open(f)):
        used.update(norm(w) for w in tok(s['hi']))

i = next(k for k,l in enumerate(md) if l.startswith('## 4.'))
vocab = []
for l in md[i+1:]:
    if l.startswith('#'): continue
    vocab.extend(norm(w) for w in re.findall(r'[ऀ-ॿ]+', l))

missing = [w for w in vocab if w not in used]
print("Missing:", len(missing))

# Group words into sentences of 2-3 words each
# We will create semantic context frames that embed each target word accurately in natural Hindi.
