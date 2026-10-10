import json, glob, re, collections
from pathlib import Path
D = Path(__file__).resolve().parent.parent / "data"
S = []
for f in sorted(D.glob("phrases*.json")): S += json.load(open(f))
print("sentences", len(S), "unique ids", len({s["id"] for s in S}), "unique hi", len({s["hi"] for s in S}))
words = collections.Counter(w for s in S for w in re.findall(r"[\u0900-\u097F]+", s["hi"]))
print("unique hindi words", len(words), "seen once:", sum(1 for c in words.values() if c == 1))
# tense / grammar patterns on Hindi text
AUX = r"(है|हैं|हूँ|हो|था|थे|थी|थीं|होगा|होगी|होंगे|होंगी)"
pat = {
 "present simple (verb ta/te/ti + hai)": r"(ता|ते|ती)\s+" + AUX + r"\b",
 "present continuous (raha/rahe/rahi + hai)": r"(रहा|रहे|रही)\s+(है|हैं|हूँ|हो)\b",
 "past continuous (raha + tha)": r"(रहा|रहे|रही)\s+(था|थे|थी|थीं)\b",
 "future continuous (raha + hoga)": r"(रहा|रहे|रही)\s+(होगा|होगी|होंगे|होंगी)\b",
 "past habitual (ta + tha)": r"(ता|ते|ती)\s+(था|थे|थी|थीं)\b",
 "future simple (ega/enge/egi)": r"\w+(ेगा|ेगी|ेंगे|ेंगी|ूँगा|ूँगी|ोगे|ोगी)\b",
 "simple past (a/e/i/ya)": r"\b\w+(ा|े|ी|ीं|या|ये|यी)\s*[।?.]?$",
 "present perfect (chuka/liya/kiya hai)": r"(चुका|चुके|चुकी|लिया|किया|दिया|गया|आया|गई|गए|आए)\s+(है|हैं|हूँ)\b",
 "past perfect (.. tha)": r"(चुका|चुके|चुकी|लिया|किया|दिया|गया|आया|गई|गए|आए|खाया|पिया)\s+(था|थे|थी|थीं)\b",
 "future perfect (chuka hoga)": r"(चुका|चुके|चुकी)\s+(होगा|होगी|होंगे|होंगी)\b",
 "subjunctive (e/o/un)": r"\b(मैं|वह|वो|हम|तुम|आप)\s+\w+(ूँ|ें|े|ो)\s*[।?]?$",
 "imperative polite (iye/iyega/ie)": r"\w+(िए|िये|ियेगा|िएगा)\b",
 "imperative (verb-o/ na)": r"\b\w+ो\b",
 "ne ergative": r"\bने\b",
 "ko (dative/accusative)": r"\bको\b",
 "se (instrumental/ablative)": r"\bसे\b",
 "mein/par locative": r"\b(में|पर)\b",
 "ka/ki/ke possessive": r"\b(का|की|के)\b",
 "passive (jaata/jaana)": r"जा(ता|ती|ते|या|एगा|एगी)?\s+(है|हैं|था|थी|थे|गया|गई|गए)|जाता है",
 "causative (-aa/-vaa)": r"\w+(वा|ला|खा)ना?\b",
 "conditional (agar..toh)": r"(अगर|यदि).*(तो)",
 "compound verb (uth/pad/baith/dena/lena)": r"(उठा|पड़ा|बैठा|देना|लेना|दिया|लिया)",
 "relative (jo..vo/ jab..tab)": r"(जो|जब|जहाँ|जैसे).*(वो|वह|तब|वहाँ|वैसे)",
 "negation (nahin/mat/na)": r"\b(नहीं|मत|न)\b",
 "question word": r"\b(क्या|कौन|कब|कहाँ|क्यों|कैसे|कितना|कितने|कितनी|कौनसा|किसे|किसका|कौन सा)\b",
 "comparison (se zyada/sabse)": r"(से\s+(ज़्यादा|ज्यादा|कम|अच्छा|बड़ा|छोटा)|सबसे)",
 "obligation (chahiye/padega/hona)": r"(चाहिए|पड़ेगा|पड़ता|पड़ा|होगा|ना होगा|ना पड़ेगा)",
 "ability (sakta/pata)": r"(सकता|सकती|सकते|पाता|पाती|पाते|पाया)",
 "conjunct (kar/ke)": r"\bकर\b|\bके\b",
 "reported / ki-clause": r"\bकि\b",
 "reflexive (apna/khud)": r"(अपना|अपनी|अपने|खुद)",
 "numbers": r"\b(एक|दो|तीन|चार|पाँच|छह|सात|आठ|नौ|दस|सौ|हज़ार|हजार)\b",
 "time (baje/bajkar)": r"बजे",
 "honorific (aap)": r"\bआप\b",
 "vocative/exclam": r"(अरे|वाह|हाय|ओह)",
}
tot = len(S)
print("\nGrammar pattern coverage (sentences matching):")
for k, p in pat.items():
    n = sum(1 for s in S if re.search(p, s["hi"]))
    print(f"  {k:48s}{n:5d}  {'MISSING' if n==0 else ('THIN' if n<30 else '')}")
# idioms / muhavare
idioms = ["आँखें","आँख","नाक","कान","हाथ","पैर","दिल","सिर","मुँह","पानी","घी","उँगली","दाँत","खून","पसीना","मक्खी","गधा","उल्लू","बिल्ली","कुत्ता","साँप","तारे","चाँद","दिन में","नौ दो ग्यारह","ईंट","सोना","आसमान","ज़मीन","जमीन","तिल का ताड़","ऊँट","हवा","आग","काला","दाल"]
print("\nIdiom-ish keyword hits:")
for k in idioms:
    print(f"  {k}: {sum(1 for s in S if k in s['hi'])}", end=";")
print()
mu = [s for s in S if re.search(r"(लगाना|उड़ाना|खोलना|डालना|चढ़ना|उतरना|मारना|बनाना|खाना|पीना|लेना|देना)\b", s["hi"])]
print("verb-phrasal sentences", len(mu))
# vocab categories
cats = {
 "pronouns": "मैं तुम आप वह यह हम वे ये मुझे तुम्हें उसे हमें",
 "family": "माँ पिता भाई बहन दादा दादी नाना नानी बेटा बेटी पति पत्नी चाचा मामा",
 "body": "सिर आँख नाक कान मुँह हाथ पैर दिल पेट बाल दाँत",
 "food": "रोटी चावल दाल सब्ज़ी सब्जी दूध चाय पानी फल आम सेब केला नमक चीनी",
 "colors": "लाल नीला हरा पीला काला सफेद सफ़ेद",
 "days": "सोमवार मंगलवार बुधवार गुरुवार शुक्रवार शनिवार रविवार",
 "months/season": "जनवरी फरवरी मार्च अप्रैल मई जून जुलाई अगस्त सितंबर अक्टूबर नवंबर दिसंबर गर्मी सर्दी बारिश बरसात",
 "places": "घर स्कूल बाजार अस्पताल दफ्तर शहर गाँव स्टेशन दुकान बैंक सड़क",
 "common verbs": "जाना आना खाना पीना करना होना देखना सुनना बोलना पढ़ना लिखना सोना चलना रहना देना लेना",
 "adjectives": "अच्छा बुरा बड़ा छोटा नया पुराना सुंदर गर्म ठंडा तेज़ धीरे",
 "directions": "दाएँ बाएँ ऊपर नीचे आगे पीछे अंदर बाहर",
 "time": "आज कल अभी सुबह शाम रात दोपहर हफ्ते महीना साल घंटा",
}
print("\nVocab category coverage (word stems found as substring):")
blob = " ".join(s["hi"] for s in S)
for c, ws in cats.items():
    ws = ws.split(); miss = [w for w in ws if w not in blob]
    print(f"  {c:14s}{len(ws)-len(miss)}/{len(ws)}  missing: {' '.join(miss)}")
