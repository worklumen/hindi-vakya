"""Phase B2: read-only swap-candidate finder.

For each missing vocab word, find existing corpus sentences where a covered
word with the same stem (inflection variant of the same lemma) sits — swapping
that word for the missing form is often a natural in-place coverage fix.
Writes scripts/missing/swap_candidates.md for manual review; changes nothing.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
tok = lambda t: re.findall(r"[ऀ-ॿ]+", t)
n = lambda w: w.replace("\u095c","\u0921").replace("\u095d","\u0922").replace("़", "")

S = []
for f in sorted((ROOT / "data").glob("phrases*.json")):
    for s in json.load(open(f)):
        S.append((f.name, s["id"], s["hi"].split()))
used = {}
for fn, sid, ws in S:
    for w in ws:
        used.setdefault(n(w), []).append((fn, sid))

miss = []
md = (ROOT / "VAKYA.md").read_text().splitlines()
i = next(k for k, l in enumerate(md) if l.startswith("## 4."))
for l in md[i + 1:]:
    if l.startswith("#"):
        continue
    miss += re.findall(r"[ऀ-ॿ]+", l)
miss = [w for w in miss if n(w) not in used]

SUF = ("ना", "नी", "ने", "ता", "ती", "ते", "ा", "ी", "े", "ों", "ें", "ूँ", "ो", "या", "यी", "ये")
def stem(w):
    for s in sorted(SUF, key=len, reverse=True):
        if w.endswith(s) and len(w) - len(s) >= 3:
            return w[: -len(s)]
    return w

out = ["# Swap candidates for missing vocab (stems/variants)", "",
       "Same-stem hits = the missing word is likely an inflectional variant of a",
       "word already used in that sentence; a hand-checked swap covers it in place.", ""]
n_cand = 0
for w in miss:
    st = stem(w)
    hits = []
    for s in (st, st[:-1], w[:-2], w[:-1]):
        if len(s) < 3 or s == w:
            continue
        for c, locs in used.items():
            if c != w and (c.startswith(s) or w.startswith(stem(c) or "\0")) and abs(len(c) - len(w)) <= 3:
                hits.extend(locs[:2])
        if hits:
            break
    if hits:
        n_cand += 1
        seen = set()
        uniq = [h for h in hits if not (h in seen or seen.add(h))][:3]
        sents = [f"`{fn}:{sid}` {' '.join(next(x[2] for x in S if x[0]==fn and x[1]==sid))}" for fn, sid in uniq]
        out.append(f"- **{w}** (stem {st}): " + " | ".join(sents))
out += ["", f"{n_cand}/{len(miss)} missing words have same-stem candidates."]
(ROOT / "scripts" / "missing" / "swap_candidates.md").write_text("\n".join(out) + "\n")
print(f"{n_cand}/{len(miss)} missing words have candidates -> scripts/missing/swap_candidates.md")
