import re, json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
tok = lambda t: re.findall(r"[\u0900-\u097F]+", t)
n = lambda w: w.replace("\u095c","\u0921").replace("\u095d","\u0922").replace("\u093c","")
used=set()
for f in (ROOT/"data").glob("phrases*.json"):
    for s in json.load(open(f)): used.update(n(w) for w in tok(s["hi"]))
md=(ROOT/"VAKYA.md").read_text().splitlines()
i=next(k for k,l in enumerate(md) if l.startswith("## 4."))
miss=[]
for l in md[i+1:]:
    if l.startswith("#"): continue
    for w in re.findall(r"[ऀ-ॿ]+", l):
        if n(w) not in used: miss.append(w)
K=6; size=-(-len(miss)//K)
for k in range(K):
    (ROOT/"scripts"/"missing"/f"missing{k+1}.txt").write_text(" ".join(miss[k*size:(k+1)*size]))
print(len(miss), size)
