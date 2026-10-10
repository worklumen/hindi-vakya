import json, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
S = []
for f in sorted((ROOT/"data").glob("phrases*.json")): S += json.load(open(f))
tok = lambda t: re.findall(r"[\u0900-\u097F]+", t)
n = lambda w: w.replace("\u095c","\u0921").replace("\u095d","\u0922").replace("\u093c","")
toks = [[n(w) for w in tok(s["hi"])] for s in S]
allw = collections.Counter(w for t in toks for w in t)
md = (ROOT/"VAKYA.md").read_text().splitlines()
i = next(k for k,l in enumerate(md) if l.startswith("## 4."))
# compact format: plain Devanagari word lists, rank = position (1-based)
vocab=[]
for l in md[i+1:]:
    if l.startswith("#"): continue
    vocab.extend((r, n(w)) for r, w in enumerate(
        re.findall(r"[ऀ-ॿ]+", l), len(vocab)+1))
verbs = [(r,w) for r,w in vocab if w.endswith("ना") and len(w)>3 and " " not in w]
print("infinitive verbs in vocab:", len(verbs))
def forms(stem):
    if stem.endswith("ा"): # खा, जा, आ, पा -> irregular endings
        return None
    return stem
tenseSuffix = {
 "infinitive":["ना","नी","ने"],
 "habitual":["ता","ती","ते"],
 "perfective":["ा","ी","े","ीं","या","यी","ये"],
 "future":["ेगा","ेगी","ेंगे","ेंगी","ूँगा","ूँगी","ोगे","ोगी","ेगें"],
 "continuous":["रहा","रहे","रही"],
 "imperative":["ो","िए","िये","ें"],
 "conjunctive":["कर"],
}
covered=0; zero=[]; per_tense=collections.Counter(); tcount=collections.Counter()
rows=[]
for r,v in verbs:
    st=v[:-2]
    hits=[w for w in allw if w.startswith(st) and len(w)<=len(st)+4]
    if hits or v in allw: covered+=1
    else: zero.append((r,v))
    seen=set()
    for t in toks:
        for j,w in enumerate(t):
            if w.startswith(st) and len(w)<=len(st)+4:
                suf=w[len(st):]
                if suf in ("ना","नी","ने"): seen.add("infinitive")
                if suf in ("ता","ती","ते"): seen.add("habitual")
                if suf in ("ा","ी","े","ीं","या","यी","ये","ई","ए"): seen.add("perfective")
                if re.search(r"(ेगा|ेगी|ेंगे|ेंगी|ूँगा|ूँगी|ोगे|ोगी|ेगें|ंगा|ंगी)$",suf): seen.add("future")
                if j+1<len(t) and t[j+1] in {"रहा","रहे","रही"}: seen.add("continuous")
                if suf in ("ो","िए","िये","ें","ओ","इए"): seen.add("imperative")
    for x in seen: per_tense[x]+=1
    rows.append((r,v,len(seen)))
print(f"verbs with any form in phrases: {covered}/{len(verbs)}")
print("verbs by number of distinct form-types seen (of 6):", dict(collections.Counter(c for _,_,c in rows)))
print("form-type coverage across verbs:", dict(per_tense))
print("top-frequency verbs missing entirely:", " ".join(f"{v}({r})" for r,v in zero[:40]))
print("top-500 verbs w/ <4 form types:", " ".join(v for r,v,c in rows if r<2000 and c<4)[:600])
# core verb check
core="होना करना जाना आना देना लेना खाना पीना देखना सुनना बोलना कहना पढ़ना लिखना सोना चलना रहना मिलना बनना रखना समझना सीखना खेलना उठना बैठना पूछना भेजना लाना बुलाना खरीदना बेचना धोना पहनना गाना नाचना हँसना रोना डरना भूलना याद करना".split()
print("\ncore verbs:")
for v in core:
    st=n(v)[:-2]
    c=sum(1 for t in toks if any(w.startswith(st) for w in t))
    print(f"{v}:{c}", end="  ")
print()
