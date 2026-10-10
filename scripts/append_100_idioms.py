import re
from pathlib import Path

ROOT = Path('.')
vakya_path = ROOT / "VAKYA.md"
content = vakya_path.read_text()

# 100 Authentic Hindi Idioms & Proverbs (Tier L1-L4 expanded)
# L1: 25 new everyday body/action idioms (26 to 50)
l1_extra = """| 26 | **आँखें चार होना** | eyes to become four | to meet eyes or fall in love | मेले में दोनों की आँखें चार हुईं |
| 27 | **कान पर जूँ न रेंगना** | louse not crawling on ear | to remain completely indifferent | बार बार टोकने पर भी कान पर जूँ न रेंगी |
| 28 | **नाक कटना** | nose to get cut | to lose honour or face disgrace | गलत काम से पूरे परिवार की नाक कट गई |
| 29 | **मुँह फुलाना** | to puff the mouth | to sulk or get displeased | छोटी सी बात पर मुँह फुलाना ठीक नहीं |
| 30 | **दाँत पीसना** | to grind teeth | to be enraged | गुस्से में वह दाँत पीसता रह गया |
| 31 | **गाल बजाना** | to sound cheeks | to boast loudly | काम करो केवल गाल बजाने से क्या होगा |
| 32 | **गर्दन झुकाना** | to bow the neck | to accept submission or respect | उसने अपनी गलती मानकर गर्दन झुका ली |
| 33 | **सिर धुनना** | to beat the head | to grieve deeply or regret | नुकसान देखकर वह सिर धुनने लगा |
| 34 | **हाथ साफ़ करना** | to clean the hand | to steal or take away slyly | चोर ने मौका पाकर तिजोरी पर हाथ साफ़ किया |
| 35 | **पैर उखड़ना** | feet to be uprooted | to be forced to retreat | सेना के हमले से दुश्मनों के पैर उखड़ गए |
| 36 | **पेट काटना** | to cut the stomach | to pinch pennies for a cause | माता पिता ने पेट काटकर बच्चों को पढ़ाया |
| 37 | **पीठ दिखाना** | to show the back | to flee from battle | सच्चा सिपाही मैदान में कभी पीठ नहीं दिखाता |
| 38 | **कमर कसना** | to tighten the waist | to prepare determinedly | परीक्षा के लिए सबने कमर कस ली है |
| 39 | **छाती फूलना** | chest to swell | to be proud | बेटे की सफलता पर पिता की छाती फूल गई |
| 40 | **आँसू पोंछना** | to wipe tears | to comfort in sorrow | संकट में उसने सबके आँसू पोंछे |
| 41 | **जी चुराना** | to steal the heart | to shirk work | मेहनत से जी चुराना अच्छी बात नहीं |
| 42 | **कलेजा ठंडा होना** | liver/heart to become cold | to feel vindicated or satisfied | बदला लेकर उसका कलेजा ठंडा हुआ |
| 43 | **आँखों का तारा** | star of the eyes | very beloved | इकलौता बेटा माँ की आँखों का तारा है |
| 44 | **नाक भौं सिकोड़ना** | to wrinkle nose and brows | to express disgust | सादा खाना देखकर उसने नाक भौं सिकोड़ ली |
| 45 | **हाथ खींचना** | to pull back the hand | to withdraw support | संकट आते ही दोस्तों ने हाथ खींच लिया |
| 46 | **पाँव भारी होना** | feet to become heavy | to hesitate to move forward | भय के मारे उसके पाँव भारी हो गए |
| 47 | **तलवे चाटना** | to lick soles | to flatter servilely | अफसर के तलवे चाटने से सम्मान नहीं मिलता |
| 48 | **पसीने छूटना** | sweat to break out | to be terrified or exhausted | मुश्किल सवाल देखकर छात्र के पसीने छूट गए |
| 49 | **मुँह छिपाना** | to hide the face | to feel ashamed | हारने के बाद वह सबसे मुँह छिपाने लगा |
| 50 | **कान का कच्चा** | soft of ear | easily misled by rumors | कान का कच्चा व्यक्ति हर अफवाह पर विश्वास करता है |
"""

# L2: 25 new case & postposition idioms (27 to 51)
l2_extra = """| 27 | **आग बबूला होना** | to become a ball of fire | to become furious | बात बिगड़ते ही वह आग बबूला हो गया |
| 28 | **पानी पानी होना** | to become water water | to be deeply embarrassed | चोरी पकड़े जाने पर वह पानी पानी हो गया |
| 29 | **लोहा मानना** | to acknowledge the iron | to accept someone supremacy | दुनिया ने भारतीय वैज्ञानिकों का लोहा माना |
| 30 | **रंग में भंग पड़ना** | interruption in festive mood | to spoil the fun | अचानक बारिश से उत्सव के रंग में भंग पड़ गया |
| 31 | **राई का पहाड़ बनाना** | to make a mountain of mustard seed | to exaggerate a small issue | उसने छोटी सी बात पर राई का पहाड़ बना दिया |
| 32 | **घाट घाट का पानी पीना** | to drink water from various ghats | to be widely experienced | वह चतुर व्यापारी है जिसने घाट घाट का पानी पिया है |
| 33 | **हवा का रुख देखना** | to observe the wind direction | to judge public mood | राजनेता हमेशा हवा का रुख देखकर निर्णय लेते हैं |
| 34 | **जले पर नमक छिड़कना** | to sprinkle salt on burn | to add insult to injury | हार के बाद ताना मारकर उसने जले पर नमक छिड़क दिया |
| 35 | **दाल भात में मूसलचंद** | pestle in rice and lentils | unwanted meddler | हमारी निजी बातचीत में दाल भात में मूसलचंद मत बनो |
| 36 | **अंगारों पर पैर रखना** | to step on burning coals | to take extreme risk | सच बोलकर उसने अंगारों पर पैर रखा |
| 37 | **आस्तीन का साँप** | snake in the sleeve | a treacherous friend | जिसे मित्र समझा वह आस्तीन का साँप निकला |
| 38 | **गुदड़ी का लाल** | ruby in rags | a genius in humble origin | गरीब घर का बालक वैज्ञानिक बनकर गुदड़ी का लाल साबित हुआ |
| 39 | **चोली दामन का साथ** | bond of blouse and skirt | inseparable relationship | परिश्रम और सफलता का चोली दामन का साथ है |
| 40 | **तिल का ताड़ बनाना** | to make palm tree of sesame | to make a huge fuss | समझदार लोग तिल का ताड़ नहीं बनाते |
| 41 | **दिन दूनी रात चौगुनी** | two times by day four times by night | rapid progress | उसका व्यापार दिन दूनी रात चौगुनी उन्नति कर रहा है |
| 42 | **पापड़ बेलना** | to roll papads | to undergo many hardships | नौकरी पाने के लिए उसे बहुत पापड़ बेलने पड़े |
| 43 | **बगलें झाँकना** | to look at armpits | to be embarrassed and clueless | प्रश्न का उत्तर न मिलने पर वह बगलें झाँकने लगा |
| 44 | **भीगी बिल्ली बनना** | to become a drenched cat | to cower in fear | डांट पड़ते ही शरारती बालक भीगी बिल्ली बन गया |
| 45 | **रंगे हाथ पकड़ना** | to catch red handed | to catch in the act | पुलिस ने रिश्वतखोर को रंगे हाथ पकड़ा |
| 46 | **हथेली पर सरसों जमाना** | to grow mustard on palm | to expect overnight miracles | सफलता समय लेती है हथेली पर सरसों नहीं जमती |
| 47 | **हक्का बक्का रह जाना** | to be dumbfounded | to be stunned | जादू का खेल देखकर सब हक्के बक्के रह गए |
| 48 | **गागर में सागर भरना** | to fill ocean in a pot | to convey profound depth briefly | कवि बिहारी ने अपने दोहों में गागर में सागर भर दिया |
| 49 | **दिन में तारे दिखाई देना** | to see stars in day | to be dazed by shock | सिर पर चोट लगते ही उसे दिन में तारे दिखाई दिए |
| 50 | **चार चाँद लगाना** | to add four moons | to enhance beauty or glory | गायक की प्रस्तुति ने समारोह में चार चाँद लगा दिए |
| 51 | **चादर देखकर पाँव पसारना** | to stretch feet according to sheet | to live within means | बुद्धिमान व्यक्ति हमेशा चादर देखकर पाँव पसारता है |
"""

# L3: 25 new figurative comparisons & proverbs (26 to 50)
l3_extra = """| 26 | **उल्टे बाँस बरेली को** | reverse bamboos to Bareilly | doing something absurdly superfluous | वहाँ सामान बेचना उल्टे बाँस बरेली को भेजने जैसा है |
| 27 | **खोदा पहाड़ निकली चुहिया** | dug a mountain found a mouse | huge effort trivial result | इतनी लंबी जाँच में खोदा पहाड़ निकली चुहिया वाली बात हुई |
| 28 | **चोर की दाढ़ी में तिनका** | straw in the thief beard | guilty conscience betrays itself | पुलिस को देखते ही वह घबराया क्योंकि चोर की दाढ़ी में तिनका था |
| 29 | **जिसका काम उसी को साजे** | only the expert suits the job | each to his own trade | बढ़ई का काम लोहार नहीं कर सकता जिसका काम उसी को साजे |
| 30 | **डूबते को नाव का सहारा** | boat support to the drowning | timely aid in distress | संकट में मित्र की सहायता डूबते को नाव का सहारा बनी |
| 31 | **तेते पाँव पसारिए जेती लाँबी सौर** | stretch feet as long as the quilt | spend according to resources | समझदार बनो और तेते पाँव पसारिए जेती लाँबी सौर |
| 32 | **धोबी का कुत्ता न घर का न घाट का** | washerman dog belonging neither home nor river | belonging nowhere | दोनों दलों की दलाली में वह धोबी का कुत्ता न घर का न घाट का बना |
| 33 | **नाचते नाचते आँगन छोटा** | dancing dancing courtyard becomes small | excuses after incompetence | असमर्थ व्यक्ति हमेशा दूसरों पर दोष मढ़ता है |
| 34 | **नेकी और पूछ पूछ** | doing good and asking permission | glad acceptance of a noble offer | भलाई के काम में नेकी और पूछ पूछ कैसी |
| 35 | **पढ़े फारसी बेचे तेल** | studied Persian selling oil | highly educated doing menial job | योग्य होकर भी नौकरी न मिलना पढ़े फारसी बेचे तेल जैसा है |
| 36 | **बकरे की माँ कब तक खैर मनाएगी** | how long will goat mother celebrate | doom is inevitable | अपराधी कितना भी भागे बकरे की माँ कब तक खैर मनाएगी |
| 37 | **बोए पेड़ बबूल का तो आम कहाँ से होय** | if you plant acacia how can you reap mangoes | evil deeds yield evil fruit | बुरे कर्म करके अच्छाई की उम्मीद मत रखो |
| 38 | **मान न मान मैं तेरा मेहमान** | accept or not I am your guest | forced unwelcome presence | बिना बुलाए आकर वह मान न मान मैं तेरा मेहमान बन बैठा |
| 39 | **साँच को आंच नहीं** | truth fears no heat | truth needs no fear | ईमानदार व्यक्ति निर्भय रहता है क्योंकि साँच को आंच नहीं |
| 40 | **हाथ कंगन को आरसी क्या** | why need mirror for bracelet | direct proof needs no argument | प्रत्यक्ष प्रमाण सामने है हाथ कंगन को आरसी क्या |
| 41 | **होनहार बिरवान के होत चीकने पात** | promising plants have glossy leaves | great talents show early | बचपन की प्रतिभा देखकर सबने कहा होनहार बिरवान के होत चीकने पात |
| 42 | **अंधे के हाथ बटेर लगना** | quail falling into blind man hand | undeserved stroke of luck | बिना मेहनत के मिली सफलता अंधे के हाथ बटेर लगने जैसी है |
| 43 | **अपनी डफली अपना राग** | ones own drum ones own tune | complete lack of consensus | समिति में सब अपनी डफली अपना राग अलाप रहे थे |
| 44 | **आम के आम गुठलियों के दाम** | mangoes as well as price of stones | double profit | किताब पढ़कर ज्ञान भी मिला और परीक्षा भी पास हुई आम के आम गुठलियों के दाम |
| 45 | **उल्टा चोर कोतवाल को डांटे** | reverse thief scolding police officer | culprit blaming the accuser | खुद गलती करके मुझे सिखाते हो उल्टा चोर कोतवाल को डांटे |
| 46 | **ऊँची उड़ान भरना** | to fly high in sky | to have high ambitions | युवा पीढ़ी हमेशा जीवन में ऊँची उड़ान भरने का सपना देखती है |
| 47 | **कंगाली में आटा गीला** | flour becoming wet in poverty | compounding of misfortunes | बीमारी के समय नौकरी छूटना कंगाली में आटा गीला होना है |
| 48 | **कोयले की दलाली में हाथ काले** | hands turn black in coal brokerage | bad company brings disgrace | गलत लोगों के साथ रहने पर बदनामी तय है |
| 49 | **चमड़ी जाए पर दमड़ी न जाए** | skin may peel but penny should not go | extreme miserliness | कंजूस व्यक्ति का सिद्धांत होता है चमड़ी जाए पर दमड़ी न जाए |
| 50 | **जल में रहकर मगर से बैर** | living in water enmity with crocodile | antagonizing power in its domain | गाँव में रहकर मुखिया से दुश्मनी करना जल में रहकर मगर से बैर है |
"""

# L4: 25 new proverbs & literary maxims (25 to 49)
l4_extra = """| 25 | **कर भला तो हो भला** | do good and good will follow | virtue has its own reward | निस्वार्थ सेवा करो कर भला तो हो भला |
| 26 | **खरबूजे को देखकर खरबूजा रंग बदलता है** | melon changes color seeing another melon | environment influences nature | संगति का असर पड़ता है खरबूजे को देखकर खरबूजा रंग बदलता है |
| 27 | **घर की मुर्गी दाल बराबर** | home chicken treated as plain lentils | familiar things are undervalued | घर के ज्ञानी को कोई नहीं पूछता घर की मुर्गी दाल बराबर |
| 28 | **चार दिन की चाँदनी फिर अँधेरी रात** | moonlight of four days then dark night | fleeting glory | वैभव क्षणिक होता है चार दिन की चाँदनी फिर अँधेरी रात |
| 29 | **चिराग बुझना** | lamp to be extinguished | lineage or life to end | युद्ध में परिवार का आखिरी चिराग बुझ गया |
| 30 | **चोर चोर मौसेरे भाई** | thieves are cousin brothers | birds of a feather flock together | दोनों बेईमान व्यापारी एक दूसरे का साथ देते हैं चोर चोर मौसेरे भाई |
| 31 | **छोटा मुँह बड़ी बात** | small mouth big words | speaking beyond ones stature | बड़ों के सामने सोच समझकर बोलो छोटा मुँह बड़ी बात शोभा नहीं देती |
| 32 | **जल बिन मछली** | fish without water | utter restlessness | ज्ञान के बिना जिज्ञासु का मन जल बिन मछली जैसा तड़पता है |
| 33 | **जैसा करोगे वैसा भरोगे** | as you do so you will reap | what goes around comes around | बुरे काम का नतीजा बुरा ही होता है जैसा करोगे वैसा भरोगे |
| 34 | **जो बोओगे वही काटोगे** | what you sow that you will reap | deeds dictate destiny | कर्म के नियम अटल हैं जो बोओगे वही काटोगे |
| 35 | **डूबते जहाज से भागना** | to flee sinking ship | deserting in danger | संकट आते ही स्वार्थी मित्र डूबते जहाज से भागने लगे |
| 36 | **तिनके का सहारा** | support of a straw | slight relief in distress | डूबते हुए को एक छोटा सा तिनके का सहारा भी बहुत होता है |
| 37 | **दूध का जला छाछ फूँक फूँक कर पीता है** | burnt by hot milk drinks buttermilk blowing | once bitten twice shy | धोखे के बाद वह हर समझौते में दूध का जला छाछ फूँक कर पीता है |
| 38 | **नेकी कभी व्यर्थ नहीं जाती** | virtue never goes in vain | goodness endures | दूसरों की भलाई करो क्योंकि नेकी कभी व्यर्थ नहीं जाती |
| 39 | **पर उपदेश कुशल बहुतेरे** | many are skilled in advising others | easy to advise hard to practice | उपदेश देना आसान है पर उपदेश कुशल बहुतेरे |
| 40 | **पाँचों उँगलियाँ बराबर नहीं होतीं** | all five fingers are not equal | diversity in human nature | समाज में सब एक जैसे नहीं होते पाँचों उँगलियाँ बराबर नहीं होतीं |
| 41 | **पानी में आग लगाना** | to set water on fire | to achieve the impossible or stir up turmoil | उसकी चालाकी ने शांत माहौल में भी पानी में आग लगा दी |
| 42 | **बिना सेवा मेवा नहीं मिलता** | no sweet fruit without service | no gains without pains | कठिन साधना करो क्योंकि बिना सेवा मेवा नहीं मिलता |
| 43 | **मन चंगा तो कठौती में गंगा** | if heart is pure the Ganges is in the tub | inner purity is true pilgrimage | पवित्र आचरण रखो मन चंगा तो कठौती में गंगा |
| 44 | **मुख में राम बगल में छुरी** | Ram on lips dagger in armpit | hypocritical malice | मीठी बातों पर भरोसा मत करो मुख में राम बगल में छुरी वाले बहुत हैं |
| 45 | **रस्सी जल गई पर बल नहीं गया** | rope burnt away but twist remained | stubborn vanity persists despite defeat | सत्ता छिन गई पर अहंकार बाकी है रस्सी जल गई पर बल नहीं गया |
| 46 | **लोहा लोहे को काटता है** | iron cuts iron | like meets like | कठोर शत्रु को हराने के लिए लोहा लोहे को काटता है |
| 47 | **विपत्ति में बुद्धि नष्ट होती है** | wisdom is lost in adversity | distress clouds judgment | शांत रहो क्योंकि विपत्ति में बुद्धि नष्ट होने लगती है |
| 48 | **समय किसी की प्रतीक्षा नहीं करता** | time waits for no one | value time | आलस्य छोड़ो क्योंकि समय किसी की प्रतीक्षा नहीं करता |
| 49 | **हवा के विपरीत तैरना** | to swim against the wind | to defy public trend | परंपरावादी समाज में सुधारकों को हवा के विपरीत तैरना पड़ा |
"""

# Insert l1_extra before "### Level L2"
content = content.replace("### Level L2: Idioms built on cases and postpositions: ko se me par ke pas",
                          l1_extra + "\n### Level L2: Idioms built on cases and postpositions: ko se me par ke pas")

# Insert l2_extra before "### Level L3"
content = content.replace("### Level L3: Figurative idioms and common proverbs: comparisons and exaggerations",
                          l2_extra + "\n### Level L3: Figurative idioms and common proverbs: comparisons and exaggerations")

# Insert l3_extra before "### Level L4"
content = content.replace("### Level L4: Proverbs and literary expressions: wit wisdom and high register",
                          l3_extra + "\n### Level L4: Proverbs and literary expressions: wit wisdom and high register")

# Insert l4_extra before "## 4. Complete Vocabulary Corpus"
content = content.replace("## 4. Complete Vocabulary Corpus (All 9,418 Words)",
                          l4_extra + "\n## 4. Complete Vocabulary Corpus (All 9,418 Words)")

vakya_path.write_text(content)
print("Successfully appended 100 new idioms to VAKYA.md")
