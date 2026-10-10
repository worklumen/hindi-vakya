"""Generate data/phrases16.json — Batch 1 of full-coverage drive.

- SWAPS: in-place edits to existing sentences (inflection/orthographic variants)
  covering 5 missing words; each swapped-out twin verified covered elsewhere.
- NEW: sentences for the remaining 83 missing words in rank 1-5000.
- TENSE: first booster tranche (present/past/future continuous + perfect).

Aligns hand-authored; auto-repair via gen_align.derive on structural failure.
Run once; re-running rewrites the file and re-applies swaps (idempotent).
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------- SWAPS: (file, id) -> new en/hi/align (None = unchanged)
SWAPS = {
    ("phrases06.json", "b038s015"): {"hi": None},  # पहुंचा -> पहुंची (fem subject) below
    ("phrases03.json", "v02144"): {"hi": None},
    ("phrases06.json", "b050-004"): {"hi": None},
    ("phrases01.json", "s012"): {"hi": None},
    ("phrases15.json", "h535"): {
        "en": "The warrior guarded the gate",
        "hi": "सेनानी द्वार की रखवाली करता था",
        "align": "1 4 3 2 2 2",
    },
}
# precise word-level replacements: (file, id, old, new)
REPL = [
    ("phrases06.json", "b038s015", "कब पहुंचा वह", "कब पहुंची वह"),
    ("phrases03.json", "v02144", "आ जाएँ", "आ जाएं"),
    ("phrases06.json", "b050-004", "बाईं तरफ", "बाई तरफ"),
    ("phrases01.json", "s012", "कहाँ है", "कहां है"),
]

# ---------------- NEW sentences (rank 1-5000 gap words, >=1 target per sentence)
N = [
    # कुमार अर्थात् उपयोगकर्ताओं प्रायोजित इन्होंने राजनीतिज्ञ गुजरता प्रक्षेपण
    ("The prince performed penance in the forest", "कुमार ने वन में तपस्या की", "0-1 1 4 4 2 3"),
    ("The cow that is the milch animal is worshipped", "गाय अर्थात् धेनु पूजी जाती है", "0 3 1 4 5 4"),
    ("The complaints of the users were registered", "उपयोगकर्ताओं की शिकायतें दर्ज हुईं", "0-1 4 2 5 4"),
    ("Artists came to the sponsored program", "कलाकार प्रायोजित कार्यक्रम में आए", "0 1 2 3 3 4"),
    ("Together these people completed the work", "इन्होंने मिलकर काम पूरा किया", "0 1 3 3 2"),
    ("The senior politician gave a speech", "वरिष्ठ राजनीतिज्ञ ने भाषण दिया", "0-1 1 1 3 2"),
    ("Time keeps passing", "समय गुजरता रहता है", "0 1 1 1"),
    ("The scientists succeeded in the launch of the satellite", "उपग्रह के प्रक्षेपण में वैज्ञानिक सफल हुए", "0-1 1 3 3 4 5 6"),
    # उपविजेता महाद्वीपीय विशेषताएँ पनडुब्बी मानवाधिकार उत्सर्जन गतिशील बिंदुओं महासंघ
    ("She remained the runner up of the tournament", "वह टूर्नामेंट की उपविजेता रही", "0 1 3 4 5"),
    ("Big changes come in the continental climate", "महाद्वीपीय जलवायु में बड़े बदलाव आते हैं", "0-2 2 4 4-5 5 6"),
    ("The features of the mountains are unique", "पहाड़ों की विशेषताएँ अनूठी हैं", "0 1 3 4 5"),
    ("The submarine descended into the sea", "पनडुब्बी समुद्र में उतरी", "0 3 3 2"),
    ("Protection of human rights is necessary", "मानवाधिकार की रक्षा आवश्यक है", "0-1 4 3 5 6"),
    ("The emission of the factories decreased", "कारखानों का उत्सर्जन घटा", "0 3 2 4"),
    ("The market became dynamic with the new scheme", "नई योजना से बाज़ार गतिशील हुआ", "0-1 1 3 2 4"),
    ("Pay attention to these points", "इन बिंदुओं पर ध्यान दें", "0 1 3 2 2"),
    ("The federation issued a notification", "महासंघ ने अधिसूचना जारी की", "0-1 1 3 4 5"),
    # विधायी गेंदबाजी अल्पकालिक गर्भपात दक्षिणपूर्वी धारक निर्णायक राष्ट्रवादी प्रतिबिंबित
    ("The legislative process went on long", "विधायी प्रक्रिया लंबी चली", "0-1 2 3 3"),
    ("His bowling was brilliant", "उसकी गेंदबाजी शानदार थी", "0-1 2 3 4"),
    ("Short term training was given", "अल्पकालिक प्रशिक्षण दिया गया", "0-1 2 3 3"),
    ("The issue of abortion is discussed in health services", "स्वास्थ्य सेवाओं में गर्भपात की चर्चा होती है", "0-1 1 3 4 4 5 5"),
    ("Rain came from the southeastern winds", "दक्षिणपूर्वी हवाओं से बारिश आई", "0 1 4 2 5"),
    ("The holder of the land got rights", "भूमि के धारक को अधिकार मिले", "0 1 3 4 5"),
    ("The goal proved decisive", "गोल निर्णायक साबित हुई", "0 1 2 2"),
    ("Nationalist thoughts spread among the youth", "युवाओं में राष्ट्रवादी विचार फैले", "0 1 2 3 4"),
    ("The picture of society is reflected in literature", "समाज की तस्वीर साहित्य में प्रतिबिंबित होती है", "0 1 4 2 5 5 6"),
    # विधायिका बौद्धिक सैद्धांतिक धोखाधड़ी प्रतियां विकलांग अग्रभाग कुटुंब विध्वंसक कार्यात्मक
    ("The legislature passed the law", "विधायिका ने कानून पारित किया", "0-1 1 2 3 3"),
    ("Books are necessary for intellectual growth", "बौद्धिक विकास के लिए पुस्तकें आवश्यक हैं", "0 1 3 4 5 6"),
    ("This is only theoretical knowledge", "यह केवल सैद्धांतिक ज्ञान है", "0 1 2 3 4"),
    ("Rules were framed to stop fraud in the market", "बाज़ार में धोखाधड़ी रोकने के नियम बने", "0 1 2 3 4 5 6"),
    ("The copies will have to be submitted", "प्रतियां जमा करानी होंगी", "0 3 2 2"),
    ("The disabled student got a discount", "विकलांग छात्र को छूट मिली", "0-1 1 3 4 5"),
    ("The front part of the ship struck the waves", "जहाज़ का अग्रभाग लहरों से टकराया", "0 1 3 5 4 6"),
    ("The whole family came to the ceremony", "पूरा कुटुंब समारोह में आया", "0-1 2 4 3 5"),
    ("The flood proved destructive", "बाढ़ विध्वंसक साबित हुई", "0 1 2 2"),
    ("A functional committee was formed", "कार्यात्मक समिति बनाई गई", "0-1 2 3 3"),
    # प्रस्तुतियों अनुमोदन संरेखित विन्यास पे भूमध्यसागरीय अनुसूचित व्याख्याता सांख्यिकी कही
    ("The level of the presentations was high", "प्रस्तुतियों का स्तर ऊँचा था", "0 1 3 4 5"),
    ("The parliament gave approval to the scheme", "संसद ने योजना को अनुमोदन दिया", "0-1 1 3 3 4 5"),
    ("Both armies got aligned", "दोनों सेनाएँ संरेखित हो गईं", "0-1 2 3 3 3"),
    ("The layout of the stage was attractive", "मंच का विन्यास आकर्षक था", "0 1 3 4 5"),
    ("I will stay at home today", "मैं आज घर पे रहूँगा", "0 2 1 3 3"),
    ("The mediterranean climate stays humid", "भूमध्यसागरीय जलवायु नम रहती है", "0-2 2 3 4 5"),
    ("The scheduled castes got reservation", "अनुसूचित जातियों को आरक्षण मिला", "0-1 2 3 4 5"),
    ("The lecturer managed the stage", "व्याख्याता ने मंच संभाला", "0-1 1 3 3"),
    ("Statistics is the science of figures", "सांख्यिकी आँकड़ों की विद्या है", "0 2 2 4 5"),
    ("The little sister spoke the truth", "छोटी बहन ने सच कही", "0-1 2 1 4 3"),
    # स्तन धकेल गर्भावस्था जोड़ते फंस पादप बढ़ाना खेद शरणार्थी सदस्यीय डेढ़
    ("The child drinks milk from the breast of the mother", "बच्चा माँ के स्तन से दूध पीता है", "0 1 4 5 4 3 6 7"),
    ("He could not push the stone up the hill", "वह पहाड़ी पत्थर को धकेल नहीं पाया", "0 1 3 3 4 2 2"),
    ("Take care of diet in pregnancy", "गर्भावस्था में आहार का ध्यान रखें", "0 1 3 3 3 4"),
    ("He makes nets joining the ropes", "वह डोरियाँ जोड़ते हुए जाल बनाता है", "0 1 2 2 3 4 4 5"),
    ("The wheel got stuck in the mud", "पहिया कीचड़ में फंस गया", "0 3 3 2 4"),
    ("The green plant is the base of the food chain", "हरा पादप खाद्य श्रृंखला का आधार है", "0-1 2 3-4 4-5 6 7 8"),
    ("Emphasis was laid on increasing production", "उत्पादन बढ़ाने पर ज़ोर दिया गया", "0 1 3 4 4 5"),
    ("Grief was expressed at the death of the village elder", "गाँव के बुज़ुर्ग के निधन का खेद व्यक्त हुआ", "0 1 2 2 4 5 6 7 8"),
    ("Food reached the refugee camp", "भोजन शरणार्थी शिविर पहुँचा", "0 1 2 3 4"),
    ("The member countries signed the treaty", "सदस्यीय देशों ने संधि पर हस्ताक्षर किए", "0-1 2 1 4 5 6"),
    ("It is a path of one and a half hours", "डेढ़ घंटे का रास्ता है", "0-2 1 2 3 4"),
    # नाते प्रतिकृति कप्तानी पौ सामान्यत संरचनाएँ नौसैनिक झंडा जाहिर दलित
    ("The relations of both families are old", "दोनों परिवारों के नाते पुराने हैं", "0-1 2 2 4 5 6"),
    ("The replica of the manuscript was made", "ग्रंथ की प्रतिकृति बनाई गई", "0 1 3 3 3"),
    ("He took up the captaincy of the team", "उसने टीम की कप्तानी संभाली", "0 1 3 4 5"),
    ("The sprout of hard work shot up", "कठिन परिश्रम की पौ फूटी", "0-1 2 3 4"),
    ("He generally stays calm", "वह सामान्यत शांत रहता है", "0 1 2 2 2"),
    ("The old structures were strong", "पुरानी संरचनाएँ मज़बूत थीं", "0-1 2 3 4"),
    ("The naval exercise took place", "नौसैनिक अभ्यास हुआ", "0-1 2 3"),
    ("The flag was hoisted on the fort", "किले पर झंडा फहराया गया", "0 2 1 3 3"),
    ("The matter is evident", "बात जाहिर है", "0 1 2"),
    ("The progress of the oppressed society is necessary", "दलित समाज की उन्नति ज़रूरी है", "0-1 2 3 4 5 6"),
    # परिसंपत्तियों अन्दर क्षतिपूर्ति सह योजनाएं संप्रभुता संभोग बिहारी मानती उपज़िला
    ("The assets were auctioned", "परिसंपत्तियों की नीलामी हुई", "0 2 3 4"),
    ("The children came inside", "बच्चे अन्दर आ गए", "0 1 2 3"),
    ("The farmers got compensation", "किसानों को क्षतिपूर्ति मिली", "0 1 3 4"),
    ("He quietly endured the insult", "वह अपमान चुपचाप सह गया", "0 1 3 3 2 4"),
    ("New schemes were implemented", "नई योजनाएं लागू हुईं", "0-1 1 2 3"),
    ("The sovereignty of the parliament was accepted", "संसद की संप्रभुता स्वीकार की गई", "0 1 3 4 5 6"),
    ("Information about intercourse was given in the health class", "स्वास्थ्य कक्षा में संभोग की जानकारी दी गई", "0 1 3 4 4 5 6"),
    ("The peacocks become playful in the rains", "बरसात में मोर बिहारी हो उठते हैं", "0 1 2 3 3 4 5"),
    ("The mother believes the truth", "माँ सच मानती है", "0 1 2 3"),
    ("The sub district chief called a meeting", "उपज़िला प्रधान ने सभा बुलाई", "0-1 2 1 3 4 5"),
    # पहुंचती गान जातियाँ स्वप्न वस्तुत
    ("The mail arrives daily", "डाक प्रतिदिन पहुंचती है", "0 1 1 2 3"),
    ("His singing sounded sweet", "उसका गान मधुर लगा", "0-1 2 3 4"),
    ("The castes divide the society", "जातियाँ समाज को बाँटती हैं", "0 1 2 3 3"),
    ("The dreams came true", "स्वप्न सच हो गए", "0 1 1 2 3"),
    ("In fact this matter is right", "वस्तुत यह बात सही है", "0 1 2 3 4"),
    ("Where did you keep my book", "तुमने मेरी किताब कहां रखी", "0 2 1 3 4 5"),
]

# ---------------- TENSE boosters, tranche 1
T = [
    # present continuous (raha + hai)
    ("The girls are plucking flowers in the garden", "बच्चियाँ बगीचे में फूल तोड़ रही हैं", "0-1 5 4 3 3 2"),
    ("The cow is grazing by the river", "गाय नदी के पास चर रही है", "0 3 3 3 3 2"),
    ("The old man is sitting at the door", "बूढ़ा द्वार पर बैठ रहा है", "0-1 5 4 3 3 2"),
    ("The women are carrying water pots on their heads", "औरतें मटके सिर पर उठा रही हैं", "0-1 3 4 4 3 3 2"),
    ("The tailors are stitching clothes", "दर्ज़ी कपड़े सिल रहे हैं", "0 3 3 3 2"),
    ("The children are bathing in the pond", "बच्चे तालाब में नहा रहे हैं", "0-1 5 4 3 3 2"),
    ("The spark is burning the straw", "चिंगारी पुआल को जला रही है", "0 1 3 3 3 2"),
    # past continuous (raha + tha)
    ("The farmers were sowing seeds in the field", "किसान खेत में बीज बो रहे थे", "0-1 6 4 3 3 2"),
    ("The birds were flying in the sky", "पक्षी आकाश में उड़ रहे थे", "0-1 5 4 3 3 2"),
    ("The mother was cooking vegetables in the kitchen", "माँ रसोई में सब्ज़ी पका रही थी", "0 5 4 3 3 2"),
    ("The workers were breaking stones on the hill", "मज़दूर पहाड़ पर पत्थर तोड़ रहे थे", "0-1 5 5 3 3 3 2"),
    ("The girls were drawing water from the well", "लड़कियाँ कुएँ से पानी खींच रही थीं", "0-1 9-10 8 7 7 5-6"),
    ("The sheep were grazing on the meadow", "भेड़ें चरागाह में चर रही थीं", "0 5 4 3 3 2"),
    # future continuous (raha + hoga)
    ("Tomorrow the farmers will be harvesting the crop", "कल किसान फसल काट रहे होंगे", "0 1 4 4 4 2-3"),
    ("In the evening the children will be playing in the courtyard", "शाम को बच्चे आँगन में खेल रहे होंगे", "0-1 1 2-3 8 6 6 4-5"),
    ("The washerman will be washing clothes at the river", "धोबी नदी पर कपड़े धो रहा होगा", "0 6 6 3 3 3 2"),
    ("The women will be grinding spices at that time", "उस समय औरतें मसाले पीस रही होंगी", "0-2 0-2 3-4 7 7 7 5-6"),
    ("The travelers will be walking on the road by night", "रात तक यात्री सड़क पर चल रहे होंगे", "0-1 1 2-3 6 5 5 5 3-4"),
    ("The teacher will be checking the copies in the morning", "सुबह शिक्षक कॉपियाँ देख रहा होगा", "0-2 3-4 8 7 7 5-6"),
    # present perfect
    ("I have written the letter", "मैंने पत्र लिखा है", "0 1 1 1"),
    ("The girl has learned the song", "लड़की ने गीत सीखा है", "0-1 1 3 2 2"),
    ("The gardener has planted saplings", "माली ने पौधे लगाए हैं", "0-1 1 3 2 2"),
    ("The cat has drunk the milk", "बिल्ली ने दूध पी लिया है", "0-1 1 3 2 2 2"),
    ("The boys have broken the window", "लड़कों ने खिड़की तोड़ी है", "0-1 1 3 2 2"),
    ("The mother has cooked the food", "माँ ने खाना पकाया है", "0-1 1 3 2 2"),
    ("The farmer has sold the grain", "किसान ने अनाज बेचा है", "0-1 1 3 2 2"),
    ("The painter has made a picture", "चित्रकार ने चित्र बनाया है", "0-1 1 3 2 2"),
    ("The clerk has opened the register", "लिपिक ने रजिस्टर खोला है", "0-1 1 3 2 2"),
    # past perfect
    ("The boys had flown kites", "लड़कों ने पतंग उड़ाई थी", "0-1 1 3 2 2"),
    ("The potter had made pots", "कुम्हार ने घड़े बनाए थे", "0-1 1 3 2 2"),
    ("The shepherd had taken the sheep to the hill", "चरवाहा भेड़ें पहाड़ ले गया था", "0 1 4 3 3 2 2"),
    ("The mother had fed the child", "माँ ने बच्चे को खिलाया था", "0-1 1 3 3 2 2"),
    ("The women had fetched water from the river", "औरतों ने नदी से पानी लाया था", "0-1 1 3 5 4 2 2"),
    ("The farmer had plowed the field", "किसान ने खेत जोता था", "0-1 1 3 2 2"),
    ("The students had read the lesson", "छात्रों ने पाठ पढ़ा था", "0-1 1 3 2 2"),
    # future perfect (chuka hoga)
    ("The guests will have eaten by evening", "शाम तक मेहमान खा चुके होंगे", "0-1 1 2-3 3 3 2"),
    ("The train will have left the station", "रेलगाड़ी स्टेशन से निकल चुकी होगी", "0-1 1 2 3 3 3 2"),
    ("The farmer will have sown the field", "किसान खेत बो चुका होगा", "0 1 3 3 3 2"),
    ("The children will have slept by midnight", "आधी रात तक बच्चे सो चुके होंगे", "0-1 1 1 2-3 3 3 2"),
    ("The washerman will have washed the clothes", "धोबी कपड़े धो चुका होगा", "0 3 3 3 3 2"),
    ("The girls will have plucked the flowers", "लड़कियाँ फूल तोड़ चुकी होंगी", "0-1 3 3 3 2-3"),
]

# ---------------- apply swaps
swap_log = []
for fname in sorted({f for f, _ in SWAPS} | {f for f, _, _, _ in REPL}):
    p = ROOT / "data" / fname
    data = json.load(open(p))
    for s in data:
        key = (fname, s["id"])
        if key in SWAPS and SWAPS[key].get("en"):
            s.update(SWAPS[key])
            swap_log.append(f"{fname}:{s['id']} rewritten")
        for rf, rid, old, new in REPL:
            if rf == fname and s["id"] == rid:
                assert old in s["hi"], f"swap pattern missing: {fname}:{rid} {old}"
                s["hi"] = s["hi"].replace(old, new)
                swap_log.append(f"{fname}:{rid} {old} -> {new}")
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(f"swaps applied: {len(swap_log)}")

# ---------------- build new chunk
out = []
def add(en, hi, align):
    out.append({"id": f"i{len(out)+1:03d}", "en": en, "hi": hi, "align": align})
for e, h, a in N:
    add(e, h, a)
for e, h, a in T:
    add(e, h, a)

# structural check + auto-repair (same as gen_phrases15)
import importlib.util
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec); spec.loader.exec_module(ga)

def ok(s):
    a = s.get("align")
    if not a:
        return False
    toks = a.split(); en = s["en"].split(); hi = s["hi"].split()
    if len(toks) != len(hi):
        return False
    return all(pp.isdigit() and int(pp) < len(en)
               for t in toks for pp in re.split(r"[-,]", t))

for s in out:
    if not ok(s):
        s["align"] = ga.derive(s["en"], s["hi"])
print(f"repaired to valid: {sum(ok(s) for s in out)}/{len(out)}")

(ROOT / "data" / "phrases16.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
man = json.load(open(ROOT / "data" / "manifest.json"))
man["files"] = [f for f in man["files"] if f["file"] != "data/phrases16.json"] + [
    {"file": "data/phrases16.json", "count": len(out)}]
json.dump(man, open(ROOT / "data" / "manifest.json", "w"), ensure_ascii=False, indent=2)
print(f"wrote {len(out)} sentences -> data/phrases16.json")
