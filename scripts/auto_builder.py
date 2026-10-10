import json, re, glob
from pathlib import Path

ROOT = Path('.')

def load_all_used():
    tok = lambda t: re.findall(r'[\u0900-\u097F]+', t)
    norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')
    used = set()
    for f in sorted(glob.glob('data/phrases*.json')):
        for s in json.load(open(f)):
            used.update(norm(w) for w in tok(s['hi']))
    return used

def get_missing_words():
    used = load_all_used()
    norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')
    md = open('VAKYA.md').read().splitlines()
    i = next(k for k,l in enumerate(md) if l.startswith('## 4.'))
    vocab = []
    for l in md[i+1:]:
        if l.startswith('#'): continue
        vocab.extend(norm(w) for w in re.findall(r'[ऀ-ॿ]+', l))
    missing = [w for w in vocab if w not in used]
    return missing

print("Uncovered vocabulary count:", len(get_missing_words()))
