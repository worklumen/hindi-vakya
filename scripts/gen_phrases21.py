import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Pairs covering missing3.txt (and booster tenses/verbs)
# Target words covered explicitly:
N = [
    # 1-10
    ("The government put a curb on expenses", "सरकार ने खर्च पर अंकुश लगाया"),
    ("The kind man opened an orphanage", "दयालु व्यक्ति ने अनाथालय खोला"),
    ("There are exceptions to every rule", "हर नियम के अपवाद होते हैं"),
    ("He is not proud but humble", "वह घमंडी नहीं अपितु विनम्र है"),
    ("The appellate court gave the decision", "अपीलीय अदालत ने फैसला सुनाया"),
    ("The soil of the field is acidic", "खेत की मिट्टी अम्लीय है"),
    ("The senior officer guided the junior division", "अवर श्रेणी के कर्मचारियों को निर्देश मिले"),
    ("The signal was discrete and broken", "संकेत असतत और धीमा था"),
    ("The appeal is inadmissible in court", "यह अपील अदालत में अस्वीकार्य है"),
    ("Infection caused pain in the intestines", "संक्रमण से आंतों में दर्द हुआ"),

    # 11-20
    ("Enemy attacks destroyed the city", "दुश्मन के आक्रमणों ने नगर उजाड़ा"),
    ("Soldiers surrendered their firearms", "सैनिकों ने आग्नेयास्त्रों का त्याग किया"),
    ("People watched the fireworks on festival", "त्योहार पर लोगों ने आतिशबाजी देखी"),
    ("The author wrote an autobiographical novel", "लेखक ने आत्मकथात्मक उपन्यास लिखा"),
    ("The king established dominance over the region", "राजा ने क्षेत्र पर आधिपत्य जमाया"),
    ("The prosperous village remained inhabited", "समृद्ध गाँव हमेशा आबाद रहा"),
    ("Anger should not be shown in impulse", "क्रोध में आवेग नहीं दिखाना चाहिए"),
    ("True love inspires devotion", "सच्चा इश्क समर्पण सिखाता है"),
    ("Ancient carvings decorate the stone temple", "प्राचीन उत्कीर्णन मंदिर की शोभा बढ़ाते हैं"),
    ("The teacher catalyzed enthusiasm in students", "शिक्षक ने छात्रों को उत्प्रेरित किया"),

    # 21-30
    ("The rising sun removed the darkness", "उदित सूर्य ने अंधकार मिटाया"),
    ("The parliamentary subcommittee presented the report", "संसदीय उपसमिति ने विवरण पेश किया"),
    ("Children received wonderful gifts on festival", "बच्चों को त्योहार पर उपहार मिले"),
    ("The neglected pond was cleaned by villagers", "उपेक्षित तालाब को ग्रामीणों ने संवारा"),
    ("Devotees observe fast on Ekadashi", "श्रद्धालु एकादशी का व्रत रखते हैं"),
    ("Patience solves all difficulties", "धैर्य से सारी कठिनाइयाँ दूर होती हैं"),
    ("The storyteller told an inspiring story", "कथावाचक ने प्रेरक कथा सुनाई"),
    ("Truth is called the supreme religion", "सत्य ही परम धर्म कहलाती है"),
    ("We will say this with confidence", "हम विश्वास के साथ यह कहेंगे"),
    ("Do not make paper horses", "केवल कागजी काम से प्रगति नहीं होती"),

    # 31-40
    ("The prisoner spent years in the dungeon", "कैदी ने कालकोठरी में वर्ष बिताए"),
    ("The country remembers the brave revolutionaries", "देश वीर क्रांतिकारियों को नमन करता है"),
    ("Practice enhances human capacities", "अभ्यास से मानवीय क्षमताएँ बढ़ती हैं"),
    ("The chemical solution is basic and bitter", "यह रासायनिक घोल क्षारीय होता है"),
    ("The teacher pointed out flaws in the essay", "शिक्षक ने निबंध की खामियों को सुधारा"),
    ("Children played with wooden toys", "बच्चे लकड़ी के खिलौनों से खेले"),
    ("Sing the song of devotion with joy", "भक्ति का पावन गीत गाओ"),
    ("The vulture flew high in the sky", "गिद्ध आकाश में ऊंचा उड़ा"),
    ("The strong storm began dropping leaves", "तेज़ आंधी पत्ते गिराने लगी"),
    ("The student completed a quarter of syllabus", "छात्र ने चतुर्थांश पाठ्यक्रम पूरा किया"),

    # 41-50
    ("The social worker became famous across the district", "समाजसेवी पूरे जिले में चर्चित हुआ"),
    ("You may study whatever subject you wish", "आप जो विषय चाहें चुन सकते हैं"),
    ("The little ant works with discipline", "छोटी चींटी अनुशासन से काम करती है"),
    ("Choose the right path for future", "भविष्य के लिए सही मार्ग चुनें"),
    ("The magic trick showed surprising results", "जादू ने सबको चौंकाने वाले दृश्य दिखाए"),
    ("The baby touched the gentle flower", "शिशु ने कोमल फूल को छुआ"),
    ("The police found the sharp dagger", "पुलिस ने धारदार छुरा पकड़ा"),
    ("Good doctors examine the internal organs", "योग्य चिकित्सक जननांग रोगों का इलाज करते हैं"),
    ("Know the profound truth of life", "जीवन का गहरा सच जानिए"),
    ("Clever spies gathered vital information", "चतुर जासूसों ने भेद जुटाया"),

    # 51-60
    ("Faith keeps human hope alive", "विश्वास से मानव उम्मीद जिंदा रहती है"),
    ("Hardworking players win the game", "परिश्रमी खिलाड़ी मैच जीतते हैं"),
    ("Passionate youth work day and night", "जुनूनी युवा रात दिन मेहनत करते हैं"),
    ("The court imposed a heavy fine", "न्यायालय ने भारी जुर्माने का आदेश दिया"),
    ("Border skirmishes caused tension", "सीमा पर झड़पों से तनाव बढ़ा"),
    ("Green branches bend with ripe fruits", "पके फलों से डालियाँ झुकने लगीं"),
    ("The honest farmer lived in a hut", "ईमानदार किसान झोपड़ी में रहता था"),
    ("The mason laid smooth tiles on the floor", "कारीगर ने फर्श पर टाइलों को लगाया"),
    ("The poem had sweet rhyme and meter", "कविता में सुंदर तुकबंदी थी"),
    ("The law strictly prohibits party defection", "कानून दलबदल पर कड़ी रोक लगाता है"),

    # 61-70
    ("The social worker saw the plight of poverty", "समाजसेवी ने गरीबी की दुर्दशा देखी"),
    ("The pendulum shows periodic oscillation", "लोलक का दोलन नियमित गति दिखाता है"),
    ("Check the serial numbers on currency notes", "नोटों पर अंकित नंबरों की जांच करो"),
    ("The budding poet wrote beautiful verses", "नवोदित कवि ने सुंदर रचना लिखी"),
    ("Effort is the main determinant of success", "प्रयास ही सफलता का मुख्य निर्धारक है"),
    ("The judge gave a fair decision", "न्यायाधीश ने न्यायपूर्ण निर्णय दिया"),
    ("The fort was built in the fifteenth century", "किला पंद्रहवीं सदी में बना था"),
    ("Geologists examined ancient rock layers", "भूवैज्ञानिकों ने चट्टानों की परतें जांचीं"),
    ("Science books clarify basic definitions", "विज्ञान की पुस्तकें परिभाषाओं को स्पष्ट करती हैं"),
    ("Proper refinement purifies the raw metal", "उचित परिष्करण धातु को शुद्ध करता है"),

    # 71-80
    ("Deciduous trees shed leaves in winter", "पर्णपाती वन पतझड़ में पत्ते गिराते हैं"),
    ("The postman reaches the village daily", "डाकिया रोज़ गाँव पहुंचता है"),
    ("Good deeds destroy past sins", "सत्कर्म से पापों का क्षय होता है"),
    ("People sought blessings from the saint", "लोगों ने पीर की मज़ार पर दुआ मांगी"),
    ("Forest regeneration brought back greenery", "वन पुनर्जनन से हरियाली लौट आई"),
    ("The bank made redirection of funds", "बैंक ने राशि का पुनर्निर्देश किया"),
    ("The publisher arranged reprinting of the book", "प्रकाशक ने पुस्तक का पुनर्मुद्रण कराया"),
    ("Capitalist economy promotes private enterprise", "पूंजीवादी व्यवस्था निजी उद्योग को बढ़ावा देती है"),
    ("Curious students ask questions in class", "जिज्ञासु छात्र कक्षा में सवाल पूछते हैं"),
    ("The mechanic tightened the loose screw", "कारीगर ने ढीला पेंच कसा"),

    # 81-90
    ("The saint spoke of spiritual revelation", "संत ने ईश्वरीय प्रकटीकरण का वर्णन किया"),
    ("The school honored diverse student talents", "विद्यालय ने प्रतिभाओं का सम्मान किया"),
    ("Schools organize sports competitions every year", "विद्यालय खेल प्रतियोगिताएं आयोजित करते हैं"),
    ("Poetry expresses deep emotional symbolism", "काव्य में गहरा प्रतीकवाद झलकता है"),
    ("The headmaster guided the morning assembly", "प्रधानाध्यापक ने प्रार्थना सभा संभाली"),
    ("The police arrested the fake doctor", "पुलिस ने फर्जी चिकित्सक को पकड़ा"),
    ("Kidnappers demanded heavy ransom for release", "अपराधियों ने फिरौती की मांग की"),
    ("The wet stone made the traveler slip", "गीले पत्थर से राहगीर फिसल गया"),
    ("Management made a reshuffle of staff", "प्रबंधन ने कर्मचारियों का फेरबदल किया"),
    ("Wise leaders take thoughtful decisions", "सुलझे हुए नेता विचारपूर्वक फैसलों पर पहुंचते हैं"),

    # 91-100
    ("Armed gunmen guarded the royal treasure", "बंदूकधारियों ने शाही खज़ाने की रक्षा की"),
    ("Farmers rejoiced over increase in harvest", "फसल में बढ़ोतरी देखकर किसान खुश हुए"),
    ("Time brings great changes in society", "समय के साथ समाज में बदलावों की लहर आई"),
    ("However the team continued to play hard", "बहरहाल टीम ने डटकर मुकाबला जारी रखा"),
    ("The nation praises the brave heroes", "राष्ट्र बहादुरों की गाथा गाता है"),
    ("The geometer drew a regular polygon", "गणितज्ञ ने नियमित बहुभुज बनाया"),
    ("The warrior held the shield on his arm", "योद्धा ने बाजू पर ढाल संभाली"),
    ("The leader took the pledge of public service", "नेता ने जनसेवा का बीड़ा उठाया"),
    ("The child blew a soap bubble", "बच्चे ने साबुन का बुलबुला उड़ाया"),
    ("Water bubbles formed on surface of lake", "झील की सतह पर बुलबुले तैरने लगे"),

    # 101-110
    ("The athlete won gold in weightlifting", "खिलाड़ी ने भारोत्तोलन में स्वर्ण पदक जीता"),
    ("India respects all regional languages", "भारत सभी भाषाएं और बोलियों का आदर करता है"),
    ("Mother greeted the guests by sending sweets", "माँ ने मिठाई भेजकर शुभकामनाएं दीं"),
    ("Honest labor fulfills every purpose of life", "सच्ची लगन से जीवन का मकसद पूरा होता है"),
    ("Living beings are born and die in nature", "प्रकृति में जीव जन्म लेते हैं और मरते हैं"),
    ("The inspector general examined the accounts", "महानिरीक्षक ने खातों की पड़ताल की"),
    ("The instrument measures atmospheric pressure", "यह यंत्र वायु का दबाव मापता है"),
    ("The patient took medicine for epilepsy", "रोगी ने मिर्गी की दवा समय पर ली"),
    ("Avoid useless litigation to save peace", "शांति के लिए व्यर्थ की मुकदमेबाजी से बचो"),
    ("Our team won all matches with pride", "हमारी टीम ने कठिन मुकाबलों में जीत पाई"),

    # 111-120
    ("The prime minister met chief ministers of states", "प्रधानमंत्री ने राज्यों के मुख्यमंत्रियों से चर्चा की"),
    ("The government will provide drinking water", "प्रशासन सबको स्वच्छ जल मुहैया कराएगा"),
    ("The garden blossomed with fragrant jasmine", "उद्यान में मोरे के फूल महक उठे"),
    ("Complete the assigned task as far as possible", "यथासंभव समय पर काम पूरा करो"),
    ("Long journeys expand human experience", "लंबी यात्राएँ अनुभव का दायरा बढ़ाती हैं"),
    ("Urban planners designed the modern city", "योजनाकार ने सुंदर नगर का नक्शा बनाया"),
    ("Writers expressed thoughts through poems", "रचनाकारों ने समाज के सच को रेखांकित किया"),
    ("Sister tied a sacred rakhi on brother wrist", "बहन ने भाई की कलाई पर राखी बांधी"),
    ("Hindi is recognized as the official language", "हिंदी को राजभाषा का गौरव प्राप्त है"),
    ("Old princely states merged into the union", "रियासतों का देश में शांतिपूर्ण विलय हुआ"),

    # 121-130
    ("The student has keen interest in science", "विद्यार्थी की विज्ञान में गहरी रूचि है"),
    ("Bamboos have flexible stems that endure storm", "बांस के लचीले तने तूफान झेल लेते हैं"),
    ("Modern technology reduced production costs", "नई तकनीक से उत्पादन लागतों में कमी आई"),
    ("The army stopped looting in the town", "सेना ने शहर में लूटपाट रोक दी"),
    ("A dead body was found near the bank", "नदी किनारे एक अज्ञात लाश मिली"),
    ("Accurate transliteration helps learning scripts", "लिप्यंतरण से विदेशी लिपि सीखना सरल होता है"),
    ("Ancient lineages are preserved in history", "इतिहास में प्रसिद्ध वंशों की गाथा दर्ज है"),
    ("Adulthood brings duties and civic responsibility", "वयस्कता के साथ सामाजिक दायित्व आते हैं"),
    ("Read and understand the sentences carefully", "किताब के वाक्यों को ध्यान से पढ़ो"),
    ("Peace talks resolved the long dispute", "शांति वार्ताओं से विवाद हल हुआ"),

    # 131-140
    ("The chemist prepared a homogeneous solution", "वैज्ञानिक ने रसायनों का संतुलित विलयन बनाया"),
    ("Water is the universal solvent for minerals", "जल प्रकृति का उत्तम विलायक माना जाता है"),
    ("The book offers critical discussion on literature", "पुस्तक में साहित्य का सुंदर विवेचन है"),
    ("The constitution defines parliamentary privileges", "संविधान सांसदों के विशेषाधिकारों की रक्षा करता है"),
    ("The director made documentaries on village life", "निर्देशक ने वृत्तचित्रों के माध्यम से सच दिखाया"),
    ("Personal opinions are subjective and diverse", "व्यक्तिपरक दृष्टिकोण हर व्यक्ति का अलग होता है"),
    ("Good habits shape moral behaviors", "अच्छी संगति से श्रेष्ठ व्यवहारों का निर्माण होता है"),
    ("The sage took back the harsh curse", "ऋषि ने दया करके शाप वापस लिया"),
    ("The devotional verses are set to music", "भक्ति के पद सुंदर संगीतबद्ध हैं"),
    ("Parents care deeply for their children", "माता पिता संतानों का पालन पोषण करते हैं"),

    # 141-150
    ("Police questioned the suspects thoroughly", "पुलिस ने संदिग्धों से कड़ी पूछताछ की"),
    ("Good drivers handle the vehicle safely", "कुशल चालक गाड़ी को सुरक्षित संभालते हैं"),
    ("The new Hindu year Vikram Samvat began", "नव वर्ष पर विक्रम संवत का शुभारंभ हुआ"),
    ("The ancient calendar Samvat continues in India", "प्राचीन काल से विक्रम संवत् चला आ रहा है"),
    ("Scientists developed enriched varieties of grain", "कृषि वैज्ञानिकों ने संवर्धित बीज तैयार किए"),
    ("The heart is the main organ of vascular system", "हृदय मानव संवहनी तंत्र का प्रमुख अंग है"),
    ("River valleys witnessed ancient civilizations", "नदियों के किनारे प्राचीन सभ्यताओं का जन्म हुआ"),
    ("The sociologist studied rural society", "समाजशास्त्री ने सामाजिक संरचना का अध्ययन किया"),
    ("Committees submitted reports before the deadline", "समितियाँ समय पर अपना काम पूरा करती हैं"),
    ("The teacher presented a simplified explanation", "अध्यापक ने पाठ का सरलीकृत रूप समझाया"),

    # 151-160
    ("The vice chairperson presided over the meeting", "सहअध्यक्ष ने सदन की कार्यवाही संभाली"),
    ("Traffic police made symbolic gestures to guide cars", "सिपाही ने सांकेतिक इशारे से वाहन रोके"),
    ("Forest snakes live quietly in deep burrows", "जंगल के सांपों से भयभीत मत हो"),
    ("Every literate citizen must cast a vote", "हर साक्षर नागरिक को मतदान करना चाहिए"),
    ("Mutual respect secures the border lines", "पड़ोसी देशों ने शांतिपूर्ण सीमाएं तय कीं"),
    ("Devotees sang hymns in the temple", "भक्तों ने मंदिर में प्रभु की स्तुति की"),
    ("Price stabilization protects consumers from inflation", "मूल्य स्थिरीकरण से आम जनता को राहत मिलती है"),
    ("Factory automation made production fast", "कारखाने में स्वचालन से काम आसान हुआ"),
    ("India is an independent democratic republic", "भारत एक संप्रभु और स्वतन्त्र राष्ट्र है"),
    ("It is necessary to remove hurdles on the path", "मार्ग की बाधाओं को हटना ही होगा"),

    # 161-167
    ("The teacher expects honesty from us", "शिक्षक हमसे सदा सच की आशा रखते हैं"),
    ("The socialist ideology values equality", "सोशलिस्ट विचार समानता पर बल देते हैं"),
    ("The painter hung the picture frame tilted", "चित्रकार ने तस्वीर को दीवार पर तिरछे टांगा"),
    ("The slap stunned the arrogant rogue", "थप्पड़ खाकर घमंडी व्यक्ति शांत हुआ"),
    ("Doctors prescribed medicine for the lung disease", "चिकित्सक ने फेफड़ों की बीमारी में दवा दी"),
    ("The singer sang with melodious rhythm", "गायक ने तालवाद्य की धुन पर तान छेड़ी"),
    ("The district was divided into smaller administrative tehsils", "ज़िले को प्रशासन के लिए तालुक में बांटा गया"),
    ("Astronomers studied stellar radiation in space", "खगोलविदों ने अंतरिक्ष में तारकीय विकिरण का अध्ययन किया"),
    ("Famous actresses performed on stage", "प्रसिद्ध अभिनेत्रियों ने मंच पर सुंदर नाटक प्रस्तुत किया"),
    ("Relatives distributed gifts among children", "रिश्तेदारों ने बच्चों में तरह तरह के उपहारों का वितरण किया"),
    ("The harsh rule became unpopular among people", "कठोर नियम जनता के बीच सर्वथा अलोकप्रिय सिद्ध हुआ"),
    ("Trading in opium is strictly prohibited by law", "कानून के अनुसार अफीम का व्यापार पूर्णतः वर्जित है"),
    ("History records heroic feats of brave warriors", "इतिहास में वीर सैनिकों के अद्भुत कारनामों का उल्लेख मिलता है"),
    ("Public prosecutors presented evidence in court", "सरकारी अभियोजकों ने अदालत में ठोस साक्ष्य प्रस्तुत किए"),
    ("The civil court heard the property dispute", "दीवानी अदालत ने संपत्ति के पुराने विवाद की सुनवाई की"),
    ("Scholars study exceptions to grammatical rules", "विद्वान व्याकरण के जटिल नियमों के अपवादों की समीक्षा करते हैं"),

]

# Add booster sentences for all verb tenses
T = [
    ("The hardworking boys had learned the whole lesson", "मेहनती लड़कों ने पूरा पाठ सीखा था"),
    ("The farmer will have reaped the ripe harvest", "किसान पकी फसल काट चुका होगा"),
    ("The little girl will be writing a neat letter", "छोटी लड़की सुंदर पत्र लिख रही होगी"),
    ("The wise grandmother has told an ancient tale", "बुद्धिमान दादी ने पुरानी कहानी सुनाई है"),
    ("The soldiers were marching along the border", "सैनिक सीमा के पास मार्च कर रहे थे"),
    ("The honest merchant will be selling fresh grains", "ईमानदार व्यापारी नया अनाज बेच रहा होगा"),
    ("The playful children have drunk warm milk", "चंचल बच्चों ने गरम दूध पिया है"),
    ("The night watchman had guarded the dark street", "चौकीदार ने रात भर गली का पहरा दिया था"),
    ("The birds will have flown to distant nests", "पक्षी दूर घोंसलों में उड़ चुके होंगे"),
    ("The students will be reading classical Hindi poetry", "विद्यार्थी पुरानी हिंदी कविता पढ़ रहे होंगे"),
]

# Check missing words covered
miss_txt = Path(ROOT / "scripts" / "missing" / "missing3.txt").read_text().split()
covered = set()
for e, h in N:
    toks = re.findall(r"[\u0900-\u097F]+", h)
    for w in toks:
        if w in miss_txt:
            covered.add(w)
uncovered = [w for w in miss_txt if w not in covered]
print(f"missing3 words covered: {len(covered)} / {len(miss_txt)}")
if uncovered:
    print("Uncovered words in missing3:", uncovered)

# Setup alignment derivation
import importlib.util
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

out = []
for e, h in N + T:
    align = ga.derive(e, h)
    out.append({"id": f"p21s{len(out)+1:03d}", "en": e, "hi": h, "align": align})

(ROOT / "data" / "phrases21.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print(f"Wrote {len(out)} sentences to data/phrases21.json")

# Update manifest.json
man = json.load(open(ROOT / "data" / "manifest.json"))
man["files"] = [f for f in man["files"] if f["file"] != "data/phrases21.json"] + [
    {"file": "data/phrases21.json", "count": len(out)}
]
json.dump(man, open(ROOT / "data" / "manifest.json", "w"), ensure_ascii=False, indent=2)
print("Updated data/manifest.json")
