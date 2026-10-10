import json, re, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
S = []
for f in sorted((ROOT/"data").glob("phrases*.json")): S += json.load(open(f))
tok = lambda t: re.findall(r"[\u0900-\u097F]+", t)
norm = lambda w: w.replace("\u095c","\u0921").replace("\u095d","\u0922").replace("\u093c", "")  # drop nukta
toks = [[norm(w) for w in tok(s["hi"])] for s in S]
used = collections.Counter(w for t in toks for w in t)
text = [" ".join(t) for t in toks]
md = (ROOT/"VAKYA.md").read_text().splitlines()

# ---- vocab
i = next(k for k,l in enumerate(md) if l.startswith("## 4."))
# compact format: plain Devanagari word lists under tier headings, rank = position
vocab = []
for l in md[i+1:]:
    if l.startswith("#"): continue
    vocab.extend(norm(w) for w in re.findall(r"[ऀ-ॿ]+", l))
miss = [w for w in vocab if w not in used]
print(f"VOCAB: {len(vocab)-len(miss)}/{len(vocab)} exact-token covered ({100*(len(vocab)-len(miss))/len(vocab):.1f}%)")
for a,b in [(0,500),(500,2000),(2000,5000),(5000,len(vocab))]:
    seg=vocab[a:b]; print(f"  rank {a+1}-{b}: {sum(w in used for w in seg)}/{len(seg)}")
print("  top missing:", " ".join(miss[:40]))

# ---- idioms
a = next(k for k,l in enumerate(md) if l.startswith("## 3."))
idioms = []
lvl = None
for l in md[a:i]:
    if l.startswith("### Level"): lvl = l[9:11]
    m = re.match(r"\|\s*\d+\s*\|\s*\*\*(.+?)\*\*", l)
    if m: idioms.append((lvl, norm(m.group(1))))
def idiom_hit(p):
    ws = [w for w in tok(p) if len(w) > 1]
    if not ws: return False
    if " ".join(ws) in " ".join(text): return True
    if any(all(w in t for w in ws) for t in toks): return True
    # stem match: allow inflected forms (लगना -> लगी, खाना -> खाया)
    stems = [w[:-2] if w.endswith(("ना", "नी")) and len(w) >= 4 else w for w in ws]
    def stem_hit(sent):
        return all(any(t.startswith(st) for t in sent) for st in stems)
    if any(stem_hit(sent) for sent in toks): return True
    # final verb may inflect irregularly (लेना->लिया, आना->आ, ढाए->ढाता):
    # accept if all preceding stems co-occur in one sentence
    if len(stems) > 2:
        head = stems[:-1]
        return any(all(any(t.startswith(st) for t in sent) for st in head)
                   for sent in toks)
    return False
byl = collections.defaultdict(lambda:[0,0])
for lv,p in idioms:
    byl[lv][1]+=1; byl[lv][0]+=idiom_hit(p)
print(f"\nIDIOMS: {sum(v[0] for v in byl.values())}/{len(idioms)}", dict(byl))

# ---- grammar (token level; Devanagari-safe)
AUX = {"है","हैं","हूँ","हो","था","थे","थी","थीं","होगा","होगी","होंगे","होंगी"}
def has(t, pred): return any(pred(t,i) for i in range(len(t)))
G = {
 "present habitual (-ta/ti/te + hai/ho)": lambda t,i: re.search(r"(ता|ती|ते)$",t[i]) and i+1<len(t) and t[i+1] in {"है","हैं","हूँ","हो"},
 "present continuous (raha + hai)": lambda t,i: t[i] in {"रहा","रहे","रही"} and i+1<len(t) and t[i+1] in {"है","हैं","हूँ","हो"},
 "past continuous (raha + tha)": lambda t,i: t[i] in {"रहा","रहे","रही"} and i+1<len(t) and t[i+1] in {"था","थे","थी","थीं"},
 "future continuous (raha + hoga)": lambda t,i: t[i] in {"रहा","रहे","रही"} and i+1<len(t) and t[i+1].startswith("होंग") or (t[i] in {"रहा","रहे","रही"} and i+1<len(t) and t[i+1] in {"होगा","होगी"}),
 "past habitual (-ta + tha)": lambda t,i: re.search(r"(ता|ती|ते)$",t[i]) and i+1<len(t) and t[i+1] in {"था","थे","थी","थीं"},
 "simple future (-ega/egi/enge/ungaa)": lambda t,i: re.search(r"(ेगा|ेगी|ेंगे|ेंगी|ूँगा|ूँगी|ोगे|ोगी|ंगा|ंगी|ंगे)$",t[i]),
 "present perfect (kiya hai ...)": lambda t,i: t[i] in {"किया","लिया","दिया","गया","आया","गई","गए","आए","चुका","चुके","चुकी"} and i+1<len(t) and t[i+1] in {"है","हैं","हूँ","हो"},
 "past perfect (... tha)": lambda t,i: t[i] in {"किया","लिया","दिया","गया","आया","गई","गए","आए","चुका","चुके","चुकी"} and i+1<len(t) and t[i+1] in {"था","थे","थी","थीं"},
 "future perfect (chuka hoga)": lambda t,i: t[i] in {"चुका","चुके","चुकी"} and i+1<len(t) and t[i+1] in {"होगा","होगी","होंगे","होंगी"},
 "hona copula (hai/tha/hoga)": lambda t,i: t[i] in AUX,
 "ne ergative": lambda t,i: t[i]=="ने",
 "ko / se / mein / par": lambda t,i: t[i] in {"को","से","में","पर"},
 "ka/ki/ke": lambda t,i: t[i] in {"का","की","के"},
 "compound postpositions (ke paas/saath/bina)": lambda t,i: t[i]=="के" and i+1<len(t) and t[i+1] in {"पास","साथ","बिना","लिए","बाद","पहले","बारे","ऊपर","नीचे","सामने","अंदर","बाहर","कारण"},
 "modal sakna": lambda t,i: re.match(r"सक",t[i]) is not None,
 "obligation (chahiye/padna)": lambda t,i: t[i] in {"चाहिए","चाहिये"} or re.match(r"पड़(ा|ेगा|ती|ता|ना|ी|े)$",t[i]) is not None,
 "permission (sakte/dena + dijiye)": lambda t,i: t[i] in {"दीजिए","दीजिये","दो","दें"} or re.match(r"देना",t[i]) is not None,
 "passive jaana": lambda t,i: re.match(r"जा(ता|ती|ते|या|एगा|एगी|ए|ना|नी)$",t[i]) is not None or t[i] in {"गया","गई","गए","गयी"} and i>0,
 "causative -aa/-vaa": lambda t,i: re.search(r"(वा(ता|ती|ते|या|ना|ई|ए|ओ|एगा)|ाना|ाता|ाती|ाते|ाया|ाई|ाओ)$",t[i]) is not None and len(t[i])>4,
 "compound verbs (vector)": lambda t,i: t[i] in {"उठा","उठी","उठे","पड़ा","पड़ी","पड़े","बैठा","बैठी","बैठे","डाला","डाली","डालो","लिया","दिया","जाओ"} and i>0,
 "relative-correlative (jo..vo, jab..tab)": lambda t,i: t[i] in {"जो","जब","जहाँ","जैसा","जितना","जिसने","जिसे","जिन","जिस"},
 "conditional (agar..to)": lambda t,i: t[i] in {"अगर","यदि","जो"} ,
 "conjunctive (kar/ke)": lambda t,i: t[i] in {"कर","के"} and i>0,
 "negation (nahin/mat)": lambda t,i: t[i] in {"नहीं","मत","न"},
 "interrogatives": lambda t,i: t[i] in {"क्या","कौन","कब","कहाँ","क्यों","कैसे","कितना","कितने","कितनी","कैसा","कैसी","किस","किसे","किसका"},
 "imperative polite (-iye)": lambda t,i: re.search(r"(िए|िये|ियेगा|िएगा)$",t[i]) is not None,
 "subjunctive (-e/-oon with agar/shaayad)": lambda t,i: t[i] in {"शायद","चाहे","काश"},
 "comparison (se + adj / sabse)": lambda t,i: t[i] in {"सबसे","ज़्यादा","ज्यादा","अधिक","कम","बेहतर"},
 "emphatic particles (hi/bhi/to)": lambda t,i: t[i] in {"ही","भी","तो","तक","भर","मात्र"},
 "bhavavachya impersonal (se ho)": lambda t,i: t[i] in {"सकना","पाना"} or re.match(r"पा(ता|ती|ते|या)$",t[i]) is not None,
 "samas/sandhi/alankar vocabulary": lambda t,i: t[i] in {"जैसे","मानो","समान","सा","सी","से"} ,
}
print("\nGRAMMAR (sentences matching, token-based):")
for k,p in G.items():
    n = sum(1 for t in toks if has(t,lambda tt,j:bool(p(tt,j))))
    print(f"  {k:52s}{n:5d} {'MISSING' if n==0 else 'THIN' if n<40 else ''}")
nums=sum(1 for t in toks if any(w in {"एक","दो","तीन","चार","पाँच","सात","दस","सौ"} for w in t))
months=[m for m in "जनवरी फरवरी मार्च अप्रैल मई जून जुलाई अगस्त सितंबर अक्टूबर नवंबर दिसंबर".split() if m not in used]
print("\nnumber sentences:", nums, "| months missing:", months)
