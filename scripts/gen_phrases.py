"""Generate data/phrases14.json: missing/thin tenses, months, causatives, idioms. Run once; re-running rewrites the file."""
import json, re, random
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
random.seed(14)
out = []

def add(en, hi, align=None):
    d = {"id": f"g{len(out)+1:03d}", "en": en, "hi": hi}
    if align: d["align"] = align
    out.append(d)

# ---------------- subjects: (en, hi, person, gender, number, en_be_past, en_have)
SUBJ = [
 ("I","मैं",1,"m","s","was","have"), ("I","मैं",1,"f","s","was","have"),
 ("you","तुम",2,"m","p","were","have"), ("you","तुम",2,"f","p","were","have"),
 ("he","वह",3,"m","s","was","has"), ("she","वह",3,"f","s","was","has"),
 ("we","हम",1,"m","p","were","have"), ("they","वे",3,"m","p","were","have"),
 ("they","वे",3,"f","p","were","have"), ("the boy","लड़का",3,"m","s","was","has"),
 ("the girl","लड़की",3,"f","s","was","has"), ("the children","बच्चे",3,"m","p","were","have"),
 ("the women","औरतें",3,"f","p","were","have"), ("you","आप",3,"m","p","were","have"),
]
# verbs: hi stem, en base, ing, past, pp, perfective-type
VERBS = [
 ("खेल","play","playing","played","played"), ("चल","walk","walking","walked","walked"),
 ("सो","sleep","sleeping","slept","slept"), ("हँस","laugh","laughing","laughed","laughed"),
 ("रो","cry","crying","cried","cried"), ("दौड़","run","running","ran","run"),
 ("नाच","dance","dancing","danced","danced"), ("बैठ","sit","sitting","sat","sat"),
 ("उठ","get up","getting up","got up","got up"), ("पहुँच","arrive","arriving","arrived","arrived"),
]
def perf(stem, g, n):
    v = stem.endswith(("ो",))
    if v:  # सो रो
        return stem + {("m","s"):"या",("m","p"):"ए",("f","s"):"ई",("f","p"):"ईं"}[(g,n)]
    return stem + {("m","s"):"ा",("m","p"):"े",("f","s"):"ी",("f","p"):"ीं"}[(g,n)]
def ragh(g,n): return {("m","s"):"रहा",("m","p"):"रहे",("f","s"):"रही",("f","p"):"रहीं"}[(g,n)]
def chuka(g,n): return {("m","s"):"चुका",("m","p"):"चुके",("f","s"):"चुकी",("f","p"):"चुकीं"}[(g,n)]
def pres_aux(p,n,sub):
    if p==1: return "हूँ" if n=="s" else "हैं"
    if sub=="तुम": return "हो"
    return "है" if n=="s" else "हैं"
def past_aux(g,n): return {("m","s"):"था",("m","p"):"थे",("f","s"):"थी",("f","p"):"थीं"}[(g,n)]
def fut_aux(sub,p,g,n):
    if sub=="मैं": return "होऊँगा" if g=="m" else "होऊँगी"
    if sub=="तुम": return "होगे" if g=="m" else "होगी"
    return {("m","s"):"होगा",("m","p"):"होंगे",("f","s"):"होगी",("f","p"):"होंगी"}[(g,n)]
def pn(sub,p,g,n):
    # number for agreement (तुम/आप/हम/वे plural-masc forms; आप honorific uses plural)
    if sub in ("मैं","लड़का","लड़की","वह"): return g,"s"
    return g,"p"
SUBJ_FIX=[]
for e,h,p,g,n,bp,hv in SUBJ:
    SUBJ_FIX.append((e,h,p,g,pn(h,p,g,n)[1],bp,hv))
def cap(s): return s[0].upper()+s[1:]
def gen(tense, subj, verb, adv):
    e,h,p,g,n,bp,hv = subj; st,base,ing,past,pp = verb
    if tense=="pc":   # past continuous
        hi=[adv[0],h,st,ragh(g,n),past_aux(g,n)]; en=f"{cap(e)} {bp} {ing} {adv[1]}"
    elif tense=="fc":
        hi=[adv[0],h,st,ragh(g,n),fut_aux(h,p,g,n)]; en=f"{cap(e)} will be {ing} {adv[1]}"
    elif tense=="pp":
        hi=[adv[0],h,perf(st,g,n),pres_aux(p,n,h)]; en=f"{cap(e)} {hv} {pp} {adv[1]}"
    elif tense=="pap":
        hi=[adv[0],h,perf(st,g,n),past_aux(g,n)]; en=f"{cap(e)} had {pp} {adv[1]}"
    elif tense=="fp":
        hi=[adv[0],h,st,chuka(g,n),fut_aux(h,p,g,n)]; en=f"{cap(e)} will have {pp} {adv[1]}"
    elif tense=="sj":
        suf = {"मैं":"ूँ","तुम":"ो"}.get(h, "े" if (n=="s") else "ें")
        s2 = st[:-1]+"ऊँ" if False else st
        if st.endswith("ो"): form = st + {"ूँ":"ऊँ","ो":"ओ","े":"ए","ें":"एँ"}[suf]
        else: form = st + suf
        hi=["शायद",h,form]; en=f"Perhaps {e} {base if not (p==3 and n=='s') else base+'s'}"
        return en, " ".join(hi)
    return en.strip(), " ".join(hi)
ADV = {
 "pc":[("कल रात","last night"),("तब","then"),("उस समय","at that time")],
 "fc":[("कल सुबह","tomorrow morning"),("शाम को","in the evening"),("उस समय","at that time")],
 "pp":[("अब तक","so far"),("अभी","just now"),("आज","today")],
 "pap":[("तब तक","by then"),("पहले","before"),("उस दिन तक","by that day")],
 "fp":[("शाम तक","by evening"),("कल तक","by tomorrow"),("रात तक","by night")],
 "sj":[("","")],
}
ENG_FIX = lambda s: re.sub(r"\s+"," ",s).strip()
seen=set()
for t,count in [("pc",70),("fc",70),("pp",70),("pap",70),("fp",70),("sj",50)]:
    combos=[(s,v,a) for s in SUBJ_FIX for v in VERBS for a in ADV[t]]
    random.shuffle(combos); k=0
    for s,v,a in combos:
        en,hi = gen(t,s,v,a); hi=hi.strip()
        if hi in seen: continue
        seen.add(hi); add(ENG_FIX(en), hi); k+=1
        if k>=count: break

# ---------------- months (aligned: "hi_en_index" pairs)
MONTHS=[("जनवरी","January"),("फरवरी","February"),("मार्च","March"),("अप्रैल","April"),("मई","May"),("जून","June"),("जुलाई","July"),("अगस्त","August"),("सितंबर","September"),("अक्टूबर","October"),("नवंबर","November"),("दिसंबर","December")]
for hm,em in MONTHS:
    add(f"School starts in {em}", f"स्कूल {hm} में शुरू होता है", "0 3 1-2")  # स्कूल, month, में->placeholder fixed below
    out[-1]["align"]="0 3 2 1 1"
    add(f"My birthday is in {em}", f"मेरा जन्मदिन {hm} में है", "0-1 2 3")
    out[-1]["align"]="0 1 4 3 2"
# ---------------- causatives / thin verbs
HAND=[
 ("The teacher makes the child read a book","शिक्षक बच्चे से किताब पढ़वाता है"),
 ("She got the dress washed","उसने कपड़े धुलवाए"),
 ("I will have the food made","मैं खाना बनवाऊँगा"),
 ("He will make me meet his friend","वह मुझे अपने दोस्त से मिलवाएगा"),
 ("Do not let the glass fall","गिलास को गिरवाना मत"),
 ("We got the house bought through an agent","हमने एजेंट से घर खरीदवाया"),
 ("She made her old furniture sold","उसने अपना पुराना सामान बेचवाया"),
 ("The mother is teaching the girl to sing","माँ लड़की को गाना सिखला रही है"),
 ("Please push the door","कृपया दरवाज़ा धकेलिए"),
 ("The wind scattered the papers","हवा ने कागज़ बिखेर दिए"),
 ("Why did you ask him","तुमने उससे क्यों पूछा"),
 ("Do not be afraid of the dark","अँधेरे से मत डरो"),
 ("I forgot my keys at home","मैं अपनी चाबी घर पर भूल गया"),
 ("Please call the doctor","कृपया डॉक्टर को बुलाइए"),
 ("He sells vegetables in the market","वह बाज़ार में सब्ज़ियाँ बेचता है"),
 ("I sent a letter to my mother","मैंने माँ को चिट्ठी भेजी"),
 ("Do you understand what I am saying","क्या तुम समझ रहे हो मैं क्या कह रहा हूँ"),
 ("She dances very well","वह बहुत अच्छा नाचती है"),
 ("Will you ask the teacher tomorrow","क्या तुम कल शिक्षक से पूछोगे"),
 ("They are calling us from the station","वे हमें स्टेशन से बुला रहे हैं"),
]
for en,hi in HAND: add(en,hi)

# ---------------- idioms from VAKYA.md
md=(ROOT/"VAKYA.md").read_text().splitlines()
a=next(k for k,l in enumerate(md) if l.startswith("## 3.")); b=next(k for k,l in enumerate(md) if l.startswith("## 4."))
for l in md[a:b]:
    c=[x.strip() for x in l.strip().strip("|").split("|")]
    if len(c)>=5 and re.match(r"\d+$",c[0]):
        idiom=c[1].strip("*"); gloss=c[3]; lit=c[2]; ex=c[4]
        add(f"{cap(gloss)} (idiom, literally: {lit})", ex)

(ROOT/"data"/"phrases14.json").write_text(json.dumps(out,ensure_ascii=False,indent=2))
man=json.load(open(ROOT/"data"/"manifest.json"))
man["files"]=[f for f in man["files"] if f["file"]!="data/phrases14.json"]+[{"file":"data/phrases14.json","count":len(out)}]
json.dump(man,open(ROOT/"data"/"manifest.json","w"),ensure_ascii=False,indent=2)
print(len(out))
