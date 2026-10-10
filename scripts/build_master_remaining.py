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

DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')

def clean_hi(t):
    return re.sub(r"\s+", " ", re.sub(r"[^\u0900-\u097F\s]", "", t)).strip()

def clean_en(t):
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z\s]", "", t)).strip()

# Check what words remain missing right now
used = set()
for f in sorted(glob.glob(str(ROOT / 'data' / 'phrases*.json'))):
    for s in json.load(open(f)):
        used.update(norm(w) for w in tok(s['hi']))

md = (ROOT / 'VAKYA.md').read_text().splitlines()
i = next(k for k,l in enumerate(md) if l.startswith('## 4.'))
vocab = []
for l in md[i+1:]:
    if l.startswith('#'): continue
    vocab.extend(norm(w) for w in re.findall(r'[ऀ-ॿ]+', l))

missing = [w for w in vocab if w not in used]
print(f"Remaining missing words across entire corpus: {len(missing)}")

# Check idioms remaining
all_idioms = []
in_sec = False
for l in md:
    if l.startswith("## 3."): in_sec = True
    elif l.startswith("## 4."): in_sec = False
    if in_sec:
        m = re.match(r"\|\s*\d+\s*\|\s*\*\*(.+?)\*\*\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", l)
        if m:
            all_idioms.append((m.group(1).strip(), m.group(3).strip(), m.group(4).strip()))

print(f"Total idioms in VAKYA: {len(all_idioms)}")
# Find which idioms are already covered
text_blob = " ".join(s['hi'] for f in sorted(glob.glob(str(ROOT / 'data' / 'phrases*.json'))) for s in json.load(open(f)))
uncovered_idioms = []
for idiom_tuple in all_idioms:
    id_name = idiom_tuple[0]
    id_ex = idiom_tuple[2]
    # check if ex sentence or words exist
    id_words = [norm(w) for w in tok(id_name) if len(w) > 1]
    hit = all(w in text_blob for w in id_words)
    if not hit:
        uncovered_idioms.append(idiom_tuple)

print(f"Uncovered idioms count: {len(uncovered_idioms)}")
