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

def clean_hi(t):
    return re.sub(r"\s+", " ", re.sub(r"[^ऀ-ॿ\s]", "", t)).strip()
def clean_en(t):
    return re.sub(r"\s+", " ", re.sub(r"[^A-Za-z\s]", "", t)).strip()
DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')

chunk1_words = Path(ROOT / 'scripts' / 'missing' / 'chunk1.txt').read_text().split()
print("Chunk 1 words:", len(chunk1_words))

# Sentences carefully authoring natural Hindi for chunk1 words
# along with idioms 101-135 and comprehensive verb & tense forms:
PAIRS = [
    # Idioms 101-135
    ("Their eyes met and feelings deepened", "मेले में दोनों की आँखें चार हुईं"),
    ("He did not heed repeated warnings at all", "बार बार टोकने पर भी कान पर जूँ न रेंगी"),
    ("The shameful deed ruined family prestige", "गलत काम से पूरे परिवार की नाक कट गई"),
    ("Do not sulk over petty trifles", "छोटी सी बात पर मुँह फुलाना ठीक नहीं"),
    ("The furious person ground his teeth in anger", "गुस्से में वह दाँत पीसता रह गया"),
    ("Focus on honest work rather than boasting loudly", "काम करो केवल गाल बजाने से क्या होगा"),
    ("He accepted his fault and bowed his neck", "उसने अपनी गलती मानकर गर्दन झुका ली"),
    ("Seeing the heavy damage he grieved deeply", "नुकसान देखकर वह सिर धुनने लगा"),
    ("The thief stole money from the iron safe", "चोर ने मौका पाकर तिजोरी पर हाथ साफ़ किया"),
    ("The sudden counterattack uprooted enemy troops", "सेना के हमले से दुश्मनों के पैर उखड़ गए"),
    ("Parents pinched pennies to educate their children", "माता पिता ने पेट काटकर बच्चों को पढ़ाया"),
    ("A brave patriot never flees from battlefield", "सच्चा सिपाही मैदान में कभी पीठ नहीं दिखाता"),
    ("Students prepared determinedly for the difficult examination", "परीक्षा के लिए सबने कमर कस ली है"),
    ("The father chest swelled with pride on victory", "बेटे की सफलता पर पिता की छाती फूल गई"),
    ("The compassionate helper wiped tears of the distressed", "संकट में उसने सबके आँसू पोंछे"),
    ("It is unseemly to shirk honest duty", "मेहनत से जी चुराना अच्छी बात नहीं"),
    ("After achieving justice he felt peaceful in heart", "बदला लेकर उसका कलेजा ठंडा हुआ"),
    ("The beloved child is the star of mother eyes", "इकलौता बेटा माँ की आँखों का तारा है"),
    ("Seeing plain food he wrinkled his nose and brows", "सादा खाना देखकर उसने नाक भौं सिकोड़ ली"),
    ("In times of crisis selfish companions withdrew help", "संकट आते ही दोस्तों ने हाथ खींच लिया"),
    ("Out of intense fright his feet felt heavy", "भय के मारे उसके पाँव भारी हो गए"),
    ("Flattery never brings genuine respect in society", "अफसर के तलवे चाटने से सम्मान नहीं मिलता"),
    ("Facing the hard problem the boy broke into sweat", "मुश्किल सवाल देखकर छात्र के पसीने छूट गए"),
    ("After defeat the disgraced rival hid his face", "हारने के बाद वह सबसे मुँह छिपाने लगा"),
    ("A gullible person easily believes wild rumors", "कान का कच्चा व्यक्ति हर अफवाह पर विश्वास करता है"),
    ("Hearing the bitter argument he became furious", "बात बिगड़ते ही वह आग बबूला हो गया"),
    ("When the theft was exposed he was utterly ashamed", "चोरी पकड़े जाने पर वह पानी पानी हो गया"),
    ("The entire world recognized the skill of our scientists", "दुनिया ने भारतीय वैज्ञानिकों का लोहा माना"),
    ("Sudden rainfall completely spoiled the festive joy", "अचानक बारिश से उत्सव के रंग में भंग पड़ गया"),
    ("He made a huge mountain out of a small mustard issue", "उसने छोटी सी बात पर राई का पहाड़ बना दिया"),
    ("The veteran trader has vast diverse experience", "वह चतुर व्यापारी है जिसने घाट घाट का पानी पिया है"),
    ("Shrewd leaders observe the public mood before speaking", "राजनेता हमेशा हवा का रुख देखकर निर्णय लेते हैं"),
    ("Mocking the defeated rival rubbed salt into wounds", "हार के बाद ताना मारकर उसने जले पर नमक छिड़क दिया"),
    ("Do not become an unwelcome meddler in our conversation", "हमारी निजी बातचीत में दाल भात में मूसलचंद मत बनो"),
    ("Speaking absolute truth he took immense risks", "सच बोलकर उसने अंगारों पर पैर रखा"),

    # Chunk 1 vocabulary sentences:
    ("The clerk arranged old official files on shelf", "लिपिक ने अलमारी में पुरानी फाइलों को करीने से रखा"),
    ("The historical revenue system Dahsala worked well", "मुगल काल की दशाला व्यवस्था बहुत प्रसिद्ध थी"),
    ("The team traveled to Algeria for scientific study", "अनुसंधान दल ने अल्जेरिया की यात्रा पूरी की"),
    ("Madan enjoyed the festive beauty of city", "मदन ने नगर की सुंदरता का आनंद लिया"),
    ("The scientific section added appendix to the book", "लेखक ने ग्रंथ के अंत में अनु भाग जोड़ा"),
    ("Merit decided the ranks of students in class", "योग्यता के आधार पर छात्रों के रैंकों का निर्धारण हुआ"),
    ("Democracy defeated cruel fascist ideas", "लोकतंत्र ने फासीवादी विचारधारा को अस्वीकार किया"),
    ("The great river nurtures vast fertile plains", "महा नदी विशाल उपजाऊ मैदानों को सींचती है"),
    ("Dense smoke rose from the brick factory chimney", "ईंट भट्टे की चिमनी से घना धुआं निकला"),
    ("Pollen dust caused seasonal skin allergy to patient", "पराग कणों से रोगी को एलर्जी की शिकायत हुई"),
    ("Meteorite collision formed a huge circular crater", "उल्कापिंड के गिरने से विशाल क्रेटर बन गया"),
    ("Communists organized rallies for worker welfare", "कम्युनिस्टों ने मजदूरों के कल्याण के लिए सभा की"),
    ("Spring garden blossomed with fragrant red flowers", "उद्यान में लाल गुलाब का गुल खिला"),
    ("The court heard the serious defamation case", "अदालत ने मानहानि के मुकदमे की सुनवाई की"),
    ("The team began planned construction of modern roads", "योजनाबद्ध तरीके से सड़कों का निर्माण शुरू हुआ"),
    ("The versatile scholar excels in diverse arts", "बहुमुखी प्रतिभा के धनी विद्वान का सम्मान हुआ"),
    ("Patience dispels temporary despair from human mind", "धैर्य से निराशा और हताशा दूर होती है"),
    ("Engineers installed state of the art equipment in lab", "प्रयोगशाला में अत्याधुनिक उपकरण लगाए गए"),
    ("High ranking officials took key administrative decisions", "उच्च पदस्थ अधिकारियों ने महत्वपूर्ण निर्णय लिए"),
    ("Red tape slows the work of government bureaucracy", "जटिल नौकरशाही से विकास कार्य में देरी होती है"),
    ("Keen observers recognize real worth of talent", "पारखी लोग असली प्रतिभा को पहचानते हैं"),
    ("Planting trees stops continuous soil erosion", "वृक्षारोपण से भूमि का कटाव रुकता है"),
    ("Municipalities provide clean drinking water in towns", "नगरपालिकाएँ नगर में स्वच्छ जल पहुंचाती हैं"),
    ("Skilled trainers guided young athletes patiently", "कुशल प्रशिक्षकों ने युवा खिलाड़ियों को सिखाया"),
    ("The sculptor carved graceful statues from stone", "मूर्तिकार ने पाषाण से सुंदर मूर्ति को तराशा"),
    ("Parliament approved budgetary appropriation of public money", "संसद ने बजट विनियोग विधेयक को पारित किया"),
    ("Experts assessed economic feasibility of project", "विशेषज्ञों ने परियोजना की व्यवहार्यता की जांच की"),
    ("Economic contraction slowed industrial growth", "व्यापारिक संकुचन से उत्पादन में कमी आई"),
    ("Education liberates minds from narrow conservatism", "शिक्षा समाज को पुरानी रूढिवादिता से मुक्त करती है"),
    ("The journal published thematic essays on culture", "पत्रिका ने संस्कृति पर विषयगत लेख छापे"),
    ("The thyroid gland regulates essential bodily metabolism", "थायरॉयड ग्रंथि शरीर की गति को नियंत्रित करती है"),
    ("Initial experiments yielded promising scientific evidence", "प्रारम्भिक प्रयोगों से उत्साहजनक परिणाम मिले"),
    ("Sensational speculation was refuted by official reports", "निराधार अटकलों का सरकारी रिपोर्ट ने खंडन किया"),
    ("Calendar dates marked key historic events", "इतिहास की प्रमुख तारीखों को याद रखा जाता है"),
    ("Avoid wasteful luxury and cherish simple living", "अनावश्यक विलासिता छोड़कर सादगी से जियो"),
    ("Land and gold constitute valuable household asset", "भूमि और स्वर्ण बहुमूल्य परिसंपत्ति माने जाते हैं"),
    ("The task was entirely completed before evening", "शाम से पहले काम पूर्णत संपन्न हो गया"),
    ("The pleasant climate suited the health of traveler", "पहाड़ी आबोहवा यात्री को खूब रास आई"),
    ("Keep your hands clean and avoid dirty surroundings", "गंदी आदतों से दूर रहकर स्वच्छता अपनाओ"),
    ("Learn profound wisdom from these wise teachings", "इनसे हमें जीवन का सच्चा पाठ मिलता है"),
    ("The preacher delivered moral sermon to gathering", "धार्मिक उपदेशक ने शांति का प्रवचन दिया"),
    ("Hope and faith sustain human spirit in darkness", "सच्ची आस मन को कभी टूटने नहीं देती"),
    ("The temple dome was supported by cylindrical pillars", "मंदिर का गुंबद बेलनाकार खंभों पर टिका था"),
    ("Courage overcomes all domestic problems and obstacles", "साहस से पारिवारिक परेशानियों का समाधान होता है"),
    ("The nation established a centralized database system", "सरकार ने केंद्रीकृत सूचना तंत्र विकसित किया"),
    ("The psychiatrist treated mental stress gently", "मनोचिकित्सक ने तनावग्रस्त रोगी को परामर्श दिया"),
    ("The industrious farmer grew fresh vegetables in farm", "किसान ने खेत में भरपूर अनाज उगाया"),
    ("The Lokpal investigates allegations against public servants", "लोकपाल भ्रष्टाचार के मामलों की जांच करता है"),
    ("The playful child turned the spinning wheel around", "बच्चे ने गोल पहिए को तेजी से घुमाया"),
    ("The humorous drama made audience laugh heartily", "हास्यपूर्ण नाटक देखकर दर्शक बहुत हंसे"),
    ("Modern techniques boosted agricultural productivity", "नई तकनीकें खेती की पैदावार बढ़ाती हैं"),
    ("The twin sisters won first prize in debate", "जुडवा बहनों ने वाद विवाद में प्रथम स्थान पाया"),
    ("Gene sequencing revealed ancient biological lineage", "वैज्ञानिकों ने डीएनए का अनुक्रमण पूरा किया"),
    ("Place the heavy book gently upon it", "उसपर भारी सामान संभालकर रखो"),
    ("The ninth chapter describes the solar system", "पुस्तक का नौवां पाठ सौरमंडल का वर्णन करता है"),
    ("Transparent methodology ensures public institutional trust", "पारदर्शी कार्यप्रणाली से विश्वास बढ़ता है"),
    ("The debate remained focused on quality education", "सदन का ध्यान शिक्षा पर केन्द्रित रहा"),
    ("Oceanic tidal energy generates green electricity", "तटीय क्षेत्रों में ज्वारीय ऊर्जा का उपयोग होता है"),
    ("The grand cultural ceremony concluded successfully", "भव्य समारोह आनंदपूर्वक सम्पन्न हुआ"),
    ("The court poet composed royal eulogy for emperor", "कवि ने राजा की प्रशस्ति में गीत गाए"),
    ("The royal representative signed the peace treaty", "संधि पत्र पर राजप्रतिनिधि ने हस्ताक्षर किए"),
    ("The law caught ruthless killers and punished them", "पुलिस ने क्रूर हत्यारों को सीखचों के पीछे डाला"),
    ("Noble ideals uplift the collective human mind", "सद्विचार मानव मानस को पवित्र बनाते हैं"),
    ("The injured patient slipped into deep coma", "गंभीर चोट के बाद घायल कोमा में चला गया"),
    ("Electricity has numerous useful applications in life", "दैनिक जीवन में बिजली के कई उपयोगों की सूची है"),
    ("The loving parents blessed their virtuous sons", "माता पिता ने सुयोग्य पुत्रों को आशीष दिया"),
    ("The wild boar wandered into forest thickets", "जंगली सुअर वन में भोजन खोजता रहा"),
    ("The witty speaker told funny and entertaining jokes", "मजाकिया स्वभाव के व्यक्ति ने सबको हंसाया"),
    ("Parliament debated the constitutional impeachment process", "सदन में महाभियोग प्रस्ताव पर गंभीर चर्चा हुई"),
    ("Disciplined routine offers immense health benefits", "व्यायाम से शरीर को अनगिनत फायदे मिलते हैं"),
    ("Gracious hosts welcomed wedding guests with sweets", "उदार मेजबानों ने अतिथियों का आदर सत्कार किया"),
    ("Truth always triumphs over falsehood in the end", "सत्य सदैव असत्य पर विजय प्राप्त करता है"),
    ("The river flowed smoothly with uninterrupted stream", "नदी की निर्बाध धारा सागर की ओर बही"),
    ("The absconding criminal was arrested near border", "फरार अभियुक्त को सीमा पर पकड़ लिया गया"),
    ("The factory recruited competent technical personnel", "संस्थान ने योग्य कार्मिक नियुक्त किए"),
    ("Cooling systems maintain steady machine temperature", "शीतलन संयंत्र यंत्र को ठंडा रखता है"),
    ("Eager buyers gathered at the morning village fair", "बाजार में नए खरीदारों की भीड़ उमड़ पड़ी"),
    ("The relaxed posture relieved physical tension", "व्यायाम के बाद शरीर शिथिल हो गया"),
    ("Honeybees carry flower pollen to make sweet honey", "मधुमक्खियाँ फूलों से पराग एकत्र करती हैं"),
    ("The restoration of historical monument was praised", "पुरातत्व विभाग ने स्मारक की पुनर्स्थापना की"),
    ("Fossils reveal history of ancient living organisms", "भूवैज्ञानिकों ने चट्टानों से जीवाश्मों का अध्ययन किया"),
    ("Nuclear power plants generate abundant clean electricity", "नाभिकीय ऊर्जा से देश में बिजली बनती है"),
    ("Historians arranged events in strict chronology", "इतिहासकार ने कालक्रम के अनुसार विवरण लिखा"),
    ("The frightened mouse looked for hiding places", "चूहा बिल्ली से छिपने का स्थान ढूंढने लगा"),
    ("The suspect made a truthful confession of guilt", "अपराधी ने न्यायालय में स्वीकारोक्ति दर्ज कराई"),
    ("Nurses tied clean bandage strips on the wound", "घाव पर स्वच्छ पट्टियों को बांधा गया"),
    ("Sports commentators analyzed key match moments", "टिप्पणीकारों ने खेल की बारीकियों पर चर्चा की"),
    ("Mathematics students solved the complex polynomial equation", "छात्रों ने बीजगणित में बहुपद का मान निकाला"),
    ("Music lovers attended the classical vocal concert", "संगीत प्रेमियों ने शास्त्रीय गायन का आनंद लिया"),
    ("The library maintains well organized book racks", "पुस्तकालय में सुव्यवस्थित व्यवस्था सराहनीय थी"),
    ("Attentive listeners enjoyed the motivational lecture", "श्रोता वक्ता के विचारों को ध्यान से सुनते रहे"),
    ("DNA strand contains genetic codes of heredity", "वैज्ञानिकों ने कोशिका में नया स्ट्रैंड देखा"),
    ("Radio towers transmitted emergency warning signals", "आकाशवाणी ने सूचना को संचारित किया"),
    ("Food grain surplus was exported to neighbor nations", "कृषि में उत्पन्न अधिशेष अनाज गोदामों में भेजा गया"),
    ("Linguists discovered striking similarities across dialects", "विद्वानों ने बोलियों की समानताओं का विश्लेषण किया"),
    ("The catalog listed entries in hierarchical order", "पुस्तकों को श्रेणीबद्ध क्रम में रखा गया"),
    ("Hygiene prevents disease from spreading in town", "सफाई से संक्रमण फैलने का खतरा टलता है"),
    ("The school is situated close to green riverbank", "हमारा विद्यालय नदी के नजदीक स्थित है"),
    ("Differential gears enable smooth vehicular turns", "यंत्र में विभेदक प्रणाली सही तरीके से लगी है"),
    ("Spiritual virtues awaken dormant inner powers", "साधना से मनुष्य की आंतरिक शक्तियां जागती हैं"),

    # Remaining chunk1 vocabulary:
    ("Photographers displayed scenic visual images", "प्रदर्शनी में प्राकृतिक छवियां प्रदर्शित की गईं"),
    ("The Bengal tiger has dark vertical stripes", "बाघ के शरीर पर सुंदर धारियों का पैटर्न होता है"),
    ("The high commissioner inaugurated the cultural center", "उच्चायुक्त ने नए दूतावास भवन का उद्घाटन किया"),
    ("Do not make shallow excuse for your negligence", "गलती छिपाने के लिए बहाना मत बनाओ"),
    ("Computer operating systems ensure smooth computing", "कंप्यूटर प्रचालन प्रणाली ठीक से काम कर रही है"),
    ("Geometry rules calculate the diagonal of rectangle", "छात्र ने आयत के विकर्ण की लंबाई नापी"),
    ("Cold weather caused nasal congestion in children", "सर्दी से नास मार्ग में रुकावट आई"),
    ("Philosophers share diverse viewpoints on universe", "विद्वान अनेक दृष्टिकोणों से सत्य की व्याख्या करते हैं"),
    ("Queen Ahilyabai Holkar was called Devi by devotees", "लोकमाता अहिल्याबाई देई के नाम से प्रसिद्ध हुईं"),
    ("The official letter was dated yesterday", "यह पत्र कल की तिथि से दिनांकित है"),
    ("The jeep drove over rugged mountain paths", "ऊबडखाबड रास्ते पर वाहन सावधानी से चला"),
    ("Harmonious cooperation between communities brings peace", "सामंजस्यपूर्ण वातावरण में समाज की उन्नति होती है"),
    ("Diverse cultures bring distinct flavors to nation", "देश में भिन्नभिन्न भाषाओं का संगम है"),
    ("The old family house retained wooden door", "मकान का मजबूत दार बंद कर दिया गया"),
    ("Paramedics rushed wounded victims to hospital", "एंबुलेंस ने घायलों को तुरंत अस्पताल पहुंचाया"),
    ("Repetition of words creates rhythmic effect in verse", "कविता में शब्दों का दोहराव सुंदर लगता है"),
    ("Doctors examined muscular strain in neck region", "चिकित्सक ने गर्दन की ग्रीवा का परीक्षण किया"),
    ("Loose electrical wires pose safety hazards at home", "ढीले तारों को बिजली मिस्त्री ने कसा"),
    ("Long corridors connected spacious classrooms", "स्कूल के लंबे गलियारों में छात्र टहल रहे थे"),
    ("Television networks broadcast popular family serials", "दूरदर्शन पर अनेक धारावाहिकों का प्रसारण हुआ"),
    ("Security guards escorted the visiting foreign dignitaries", "अनुरक्षक दल ने अतिथि को सुरक्षा प्रदान की"),
    ("Cunning predators trapped naive prey in cage", "शिकारी ने जाल फंसाया और शिकार पकड़ा"),
    ("Unionist leaders demanded workers wage revision", "संघवादी नेताओं ने अधिकारों के लिए मांग उठाई"),
    ("Grammar textbooks provide precise sentence definitions", "पाठ्यपुस्तक में व्याकरण की परिभाषाएँ दी गई हैं"),
    ("Social studies highlight regional cultural differences", "विद्वानों ने समाजों की भिन्नताओं को रेखांकित किया"),
    ("Devotees worshipped Goddess Bhavani with devotion", "भक्तों ने माता भवानी के मंदिर में शीश नवाया"),
    ("A strange person knocked at front door at night", "रात में एक अपरिचित शख्स द्वार पर आया"),
    ("The loving uncle gifted a cycle to nephew", "चाचा ने अपने होनहार भतीजा को उपहार दिया"),
    ("Warm summer season ripens delicious mango fruit", "ग्रीष्मकाल में आम के फल पकते हैं"),
    ("Contempt of court is strictly punished by law", "न्यायालय की अवमानना कानूनन अपराध है"),
    ("Manufacturing procedures follow standard factory rules", "उत्पादन की सभी प्रक्रियाएं समय पर पूरी हुईं"),
    ("Sensational scandal shook local administrative circles", "राजनीतिक कांड की जांच पुलिस कर रही है"),
    ("The senior officer inspected border posts carefully", "वरिष्ठ अफसर ने सीमा चौकियों का निरीक्षण किया"),
    ("The historical treaty was signed in fourteenth century", "चौदहवीं सदी में इस नगर की स्थापना हुई थी"),
    ("Narrow lanes opened into wide city square", "संकुचित गलियों से निकलकर हम मुख्य मार्ग पर आए"),
    ("Rainwater filled the deep roadside pit", "सड़क के किनारे गहरा गड्ढा बन गया था"),
    ("Research verified medical efficacy of herbal remedy", "दवा की प्रभावकारिता पर शोध पत्र छपा"),
    ("Ancient Prakrit inscriptions survive on stone pillars", "अशोक के शिलालेख प्राकृत भाषा में मिलते हैं"),
    ("The twelfth chapter explains celestial orbits", "पुस्तक का बारहवें अध्याय खगोल विज्ञान से संबंधित है"),
    ("Traditional gold ornaments adorn the Indian bride", "विवाह में दुल्हन ने सुंदर आभूषणों को धारण किया"),
    ("The political theorist wrote articles on democracy", "सिद्धांतकार ने लोकतंत्र के स्वरूप पर विचार किया"),
    ("Selfless service gives deep spiritual inner feeling", "परोपकार से हृदय में पवित्र अनुभूति होती है"),
    ("The team met to settle pending official matters", "अधिकारियों ने विवाद निपटाने के लिए बैठक की"),
    ("Healthy habits curtail negative mental tendencies", "सत्संग से मन की बुरी प्रवृत्तियों का शमन होता है"),
    ("Ancient aesthetic philosophy enriches classical drama", "भारतीय सौंदर्यशास्त्र कला को दिव्यता प्रदान करता है"),
    ("Spacious mountain caves housed ancient monks", "अजंता की गुफाएँ प्राचीन चित्रकला के लिए विख्यात हैं"),
    ("Collected reserves of rainwater supported village crops", "तालाब में संचित जल खेती के काम आया"),
    ("Rising inflation increased prices of daily essentials", "महंगाई से आम जनता का बजट प्रभावित हुआ"),
    ("The dwarf tree grew in miniature ceramic pot", "गमले में बोनसाई का बौना पौधा बहुत सुंदर लगा"),
    ("The company advertised sudden vacancy in accounts", "कार्यालय में लिपिक की रिक्ति घोषित की गई"),
    ("Thorney acacia trees thrive in dry desert regions", "रेगिस्तान में बबूल के पेड़ आसानी से उगते हैं"),
    ("A buzzing wasp flew over fragrant garden flowers", "गुलाब की झाड़ी पर एक ततैया मंडरा रहा था"),
    ("The kind couple adopted an orphan baby", "निसंतान दंपती ने दत्तक पुत्र को स्नेह दिया"),
    ("Upper divisional courts handle constitutional appeals", "अपर सत्र न्यायाधीश ने जमानत याचिका पर सुनवाई की"),
    ("Pay outstanding debts promptly to maintain credit", "समय पर ऋण चुकाने से प्रतिष्ठा बढ़ती है"),
    ("The wedding brass band played cheerful lively music", "बारात के आगे बाजा बज रहा था"),
    ("Families celebrate weddings with traditional grandeur", "गाँव में शादियों का मौसम शुरू हो गया है"),
    ("The wooden desk stood adjacent to brick wall", "कमरे में मेज से सटा हुआ संदूक रखा था"),
    ("Hypersensitive sensors detect faint seismic tremors", "यह अतिसंवेदनशील यंत्र मामूली कंपन भी पकड़ता है"),
    ("The fifth musical scale sounded resonant and clear", "संगीत के पंचम स्वर में राग मेघ गाया गया"),
    ("The generous moneylender financed village farming", "गाँव के साहू ने किसानों को बीज दिए"),
    ("Oh look at the glowing evening star in sky", "अरे देखो शाम का तारा कितना सुंदर चमक रहा है"),
    ("National awakening inspired public independence movement", "जन जागृति से स्वाधीनता का मार्ग प्रशस्त हुआ"),
    ("Debates in assembly clarified legislative nuances", "सदन में बहसों के बाद कानून पारित हुआ"),
    ("The thirteenth century fortress withstood enemy siege", "तेरहवीं शताब्दी का यह दुर्ग आज भी अडिग है"),
    ("I will do this noble task with full diligence", "मैं यह शुभ कार्य निष्ठापूर्वक करूंगा"),
    ("Devotees observed sacred religious fast on Monday", "सोम वार को शिव मंदिर में भक्तों की भीड़ रही"),
    ("Sweet fragrances dwell in spring forest blossoms", "फूलों में मधुर सुगंध का वास होता है"),
    ("Republican ideals celebrate liberty and civic equality", "गणतंत्रवादी व्यवस्था में जनता ही सर्वोपरि है"),
    ("A tall stone pillar marks the palace entrance", "दरबार के मुख्य द्वार पर विशाल स्तम्भ खड़ा है"),
    ("The shining crescent moon decorated the clear sky", "आकाश में दूज का अर्धचंद्र चमक रहा था"),
    ("The singer magnetic voice charmed the large audience", "गायक का सम्मोहक स्वर सबको मुग्ध कर गया"),
    ("Clean air and sweet water are divine blessings of nature", "प्रकृति का यह वरदान हमें जीवन देता है"),
    ("Basic moral education builds strong citizen character", "सदाचार ही जीवन का आधारभूत सिद्धांत है"),
    ("Tropical forests have abundance of medicinal plants", "इस वन में जड़ी बूटियों की बहुतायत पाई जाती है"),
    ("Do not provoke anger in peaceful reasonable people", "किसी को अनुचित रूप से उकसाने का प्रयास मत करो"),
    ("Hard work fulfills positive expectations of life", "युवाओं की उम्मीदों को पूरा करने के लिए नीतियां बनीं"),
    ("Memory retention improves with regular revision", "अभ्यास से ज्ञान का प्रतिधारण सुदृढ़ होता है"),
    ("Great thinkers lived with exemplary moral simplicity", "गांधीजी का जीवन सादगी की मिसाल था"),
    ("Irrigation canal carried river water to dry fields", "नहर की मुख्य कैनाल से खेतों में पानी पहुंचा"),
    ("The Sufi mystic sang songs of divine love", "रहस्यवादी कवि ने ईश्वर प्रेम के गीत गाए"),
    ("Historians chronicled genealogies of ancient dynasties", "इतिहास में अनेक कुलों का वर्णन मिलता है"),
    ("The writer wrote descriptive paragraphs on nature", "पुस्तक में प्रकृति का वर्णनात्मक चित्रण मिलता है"),
    ("Our cultural heritage remains intact through ages", "भारत की संप्रभुता सदा अक्षुण्ण रहेगी"),
    ("Chronological sequence of events clarified the matter", "जांच दल ने घटनाक्रम की पूरी समीक्षा की"),
    ("The bilateral conference hired an expert interpreter", "विदेश मंत्री के साथ एक कुशल दुभाषिया मौजूद था"),
    ("The Olympic flame burned bright in stadium", "समारोह में पावन ज्योति प्रज्वलित की गई"),
    ("University faculty organized summer academic workshops", "शिक्षकों के लिए कार्यशालाएं आयोजित की गईं"),
    ("Honest trade practice preserves healthy market confidence", "बाजार में उचित मूल्य का चलन होना चाहिए"),
    ("Devotees made humble prayer before the deity", "भक्त ने ईश्वर के चरणों में विनती की"),
    ("The radio transmitter operated at megahertz frequency", "यह केंद्र सौ हर्ट्ज की आवृत्ति पर प्रसारित होता है"),
    ("Thunderous rumbling of clouds echoed across valley", "आकाश में बादलों की गडगडाहट गूंज उठी"),
    ("Senior advocates argued constitutional law in apex court", "वरिष्ठ अधिवक्ताओं ने न्यायालय में बहस की"),
    ("Aggressive invaders were pushed back by defenders", "आक्रमणकारी सेना को सीमा से खदेड़ दिया गया"),
    ("The pelvis bone supports upper human body", "कंकाल तंत्र में श्रोणि की हड्डी महत्वपूर्ण होती है"),
    ("Hardworking doers inspire positive collective action", "भलाई करनेवाले लोग समाज के सच्चे नायक हैं"),
    ("The delayed express train arrived late at platform", "कोहरे के कारण विलंबित गाड़ी शाम को आई"),
    ("Rocket propellants launch heavy satellite into orbit", "इस अंतरिक्ष यान में उन्नत प्रणोदक ईंधन भरा गया"),
    ("The inquiry proved official complicity in corruption", "अपराध में संलिप्तता पाए जाने पर कार्रवाई हुई"),
    ("Advertisements use bright colors to entice consumers", "व्यापारी ग्राहकों को लुभाने के लिए छूट देते हैं"),

    # Booster verbs and tenses (Future Continuous, Future Perfect, Past Perfect, Causatives):
    ("The brave farmers will be harvesting the golden wheat", "मेहनती किसान खेत में गेहूं काट रहे होंगे"),
    ("The kind mother will have prepared delicious dinner", "माँ रसोई में स्वादिष्ट भोजन बना चुकी होगी"),
    ("The diligent students had written the difficult essay", "विद्यार्थियों ने कठिन निबंध लिखा था"),
    ("The skilled mechanic will have repaired the machine", "कारीगर ने मशीन को ठीक कर लिया होगा"),
    ("The innocent children were singing prayers in school", "बच्चे विद्यालय में प्रार्थना गा रहे थे"),
    ("The wise teacher has explained the deep verse", "विद्वान शिक्षक ने गहरा श्लोक समझाया है"),
    ("The vigilant watchman will be guarding the village", "जागरूक पहरेदार रात में पहरा दे रहा होगा"),
    ("The river had flooded the surrounding lowlands", "नदी ने आसपास के मैदानों में पानी भर दिया था"),
    ("The birds will have flown back to their nests", "संध्या समय पक्षी घोंसलों में लौट चुके होंगे"),
    ("The artist has painted a breathtaking landscape", "चित्रकार ने एक मनमोहक दृश्य चित्रित किया है"),
]

# Alignment and formatting
out = []
for en, hi in PAIRS:
    hi_clean = clean_hi(hi)
    en_clean = clean_en(en)
    align = ga.derive(en_clean, hi_clean)
    out.append({"id": f"p22s{len(out)+1:03d}", "en": en_clean, "hi": hi_clean, "align": align})

print("Generated sentences:", len(out))

# Check chunk1 coverage
words_in_out = set()
for s in out:
    words_in_out.update(norm(w) for w in tok(s['hi']))

c1_covered = [w for w in chunk1_words if norm(w) in words_in_out]
print(f"Chunk 1 words covered: {len(c1_covered)} / {len(chunk1_words)}")

# Write to phrases22.json
(ROOT / 'data' / 'phrases22.json').write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
print("Wrote data/phrases22.json")

# Update manifest.json
man = json.load(open(ROOT / 'data' / 'manifest.json'))
man["files"] = [f for f in man["files"] if f["file"] != "data/phrases22.json"] + [
    {"file": "data/phrases22.json", "count": len(out)}
]
json.dump(man, open(ROOT / 'data' / 'manifest.json', "w"), ensure_ascii=False, indent=2)
print("Updated manifest.json")
