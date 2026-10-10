"""Generate data/phrases17.json — Batch 2 of full-coverage drive.

Targets: first ~168 missing words of scripts/missing/missing1.txt (rank 5001+),
skipping फ़ाइलों (English-origin, flagged exception) and दशाला (unclear
headword, deferred). Plus tense boosters matching coverage_vakya.py regexes:
ने..किया/दिया/लिया/गया/आए..है/था, रहा/रहे/रही..होंगे.

Aligns hand-authored; auto-repair via gen_align.derive on structural failure.
Run once; idempotent.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

N = [
    ("The members of parliament discussed the budget", "सांसदों ने बजट पर चर्चा की", "0-3 4 6 6 4 4"),
    ("The commentator wrote about the game", "टिप्पणीकार ने खेल के बारे में लिखा", "1 2 5 3 3 3 2"),
    ("The brother and sister study together", "भाईबहन साथ पढ़ते हैं", "1-3 5 4 4"),
    ("The blockade of the road continued", "सड़क का अवरोधन जारी रहा", "3-4 2 1 5 5"),
    ("Many deaths occurred in the flood", "बाढ़ में कई मौतें हुईं", "5 3 0 1 2"),
    ("Clouds of many shapes are in the sky", "आकाश में कई आकारों के बादल हैं", "7 5 2 3 1 0 4"),
    ("The village was afflicted by drought", "गाँव सूखे से ग्रस्त था", "1 5 4 3 2"),
    ("An accident happened at the workplace", "कार्यस्थल पर दुर्घटना हुई", "5 3 1 2"),
    ("The waste of the factories pollutes the river", "संयंत्रों का कचरा नदी को दूषित करता है", "4 2 1 7 7 5 5 5"),
    ("Two factions arose in the party", "दल में दो गुटों का जन्म हुआ", "5 3 0 1 2 2 2"),
    ("The government brought an ordinance", "सरकार ने अध्यादेश लाया", "1 2 4 2"),
    ("The drafts of the law were amended", "कानून के प्रारूपों में संशोधन हुआ", "4 2 1 5 6 6"),
    ("The priests performed the ritual", "पुजारियों ने अनुष्ठान किया", "1 2 4 2"),
    ("The full length of the road is two kilometers", "सड़क की पूर्णलंबाई दो किलोमीटर है", "5 3 1-2 7 8 6"),
    ("The student drew a diagram in the book", "छात्र ने पुस्तक में आरेख बनाया", "1 2 6 5 4 2"),
    ("The guests were shown the preview of the program", "मेहमानों को कार्यक्रम का पूर्वावलोकन दिखाया गया", "9 7 4 2 1 6 6"),
    ("This word is a synonym of that word", "यह शब्द उस शब्द का पर्याय है", "0 1 6 7 5 4 2"),
    ("The bat is counted among mammals", "चमगादड़ स्तनधारियों में गिना जाता है", "1 5 4 3 3 2"),
    ("The panel of advisors met", "सलाहकारों की सभा हुई", "3 2 1 4"),
    ("The importance of education is evident", "शिक्षा का महत्त्व स्पष्ट है", "3 2 1 5 4"),
    ("The waves hit the coastline", "लहरें तटरेखा से टकराती हैं", "1 4 3 2 2"),
    ("He is the coauthor of this book", "वह इस पुस्तक के सहलेखक हैं", "0 5 6 4 3 1"),
    ("The leaders made false promises", "नेताओं ने झूठे वादे किए", "1 2 3 4 2"),
    ("A tremendous storm came last night", "कल रात जबरदस्त तूफ़ान आया", "4 5 1 2 3"),
    ("Her eyes were moist", "उसकी आंखें नम थीं", "0 1 3 2"),
    ("The crowd raised a slogan", "भीड़ ने नारा लगाया", "1 2 4 2"),
    ("Gardening is a good hobby", "बागवानी अच्छा शौक़ है", "0 4 3 2"),
    ("Shaking makes an emulsion of oil and water", "हिलाने से तेल और पानी का पायस बनता है", "0 1 5 6 7 4 3 1 1"),
    ("The two countries have friendly relations", "दोनों देशों के संबंध मैत्रीपूर्ण हैं", "1 2 3 5 4 3"),
    ("The meeting of the directors was called", "निर्देशकों की बैठक बुलाई गई", "4 2 1 6 6"),
    ("The northern hemisphere remains cold", "उत्तरी गोलार्ध ठंडा रहता है", "0-1 2 4 3"),
    ("We learn from the teachings of the elders", "हम बुज़ुर्गों की शिक्षाओं से सीखते हैं", "0 7 5 4 2 1 1"),
    ("Classroom studies improved", "कक्षीय अध्ययन सुधरा", "0 1 2"),
    ("A one day workshop was held", "एकदिवसीय कार्यशाला हुई", "1-2 3 5"),
    ("The strike caused obstruction in traffic", "हड़ताल से यातायात में अवरोध हुआ", "1 2 5 4 3 2"),
    ("Inability to walk made him sad", "चलने की अक्षमता ने उसे दुखी किया", "2 1 0 3 4 5 3"),
    ("The sage lived in a hut", "साधु कुटीर में रहता था", "1 5 4 2 2"),
    ("The rights of the minorities were protected", "अल्पसंख्यकों के अधिकारों की रक्षा हुई", "4 2 1 5 6 6"),
    ("She is editing the magazine", "वह पत्रिका का सम्पादन करती है", "0 4 3 2 2 1"),
    ("Every figure was checked", "हर आंकड़ा जाँचा गया", "0 1 3 3"),
    ("The boys went to fly kites", "लड़के पतंग उड़ाने गए", "1 5 4 2"),
    ("The block chief heard the complaints", "प्रखंड प्रमुख ने शिकायतें सुनीं", "1 2 3 5 3"),
    ("The treasure was found in the excavations", "खोजों में ख़ज़ाना मिला", "6 4 1 3"),
    ("His application got refusal", "उसके आवेदन को अस्वीकृति मिली", "0 1 2 3 2"),
    ("The pigeon carried messages", "कबूतर संदेशों को ले जाता था", "1 3 2 2 2 2"),
    ("The benign guru forgave everyone", "शुभंकर गुरु ने सबको क्षमा कर दी", "1 2 3 4 3 3 3"),
    ("The baby stays in the womb for nine months", "शिशु नौ महीने गर्भ में रहता है", "1 7 8 5 3 2 2"),
    ("The kin of the deceased reached the hospital", "मृतक के परिजन अस्पताल पहुंचे", "4 2 1 7 5"),
    ("The chromosome carries the traits", "गुणसूत्र लक्षणों को ले जाता है", "1 4 3 2 2 2"),
    ("The retired teacher helps the students", "सेवामुक्त शिक्षक छात्रों की मदद करते हैं", "1 2 5 4 3 3 3"),
    ("Farming is the livelihood of the village", "खेती गाँव की आजीविका है", "0 6 4 3 1"),
    ("The book shows history in a new perspective", "पुस्तक इतिहास को नए परिप्रेक्ष्य में दिखाती है", "1 3 3 6 7 4 2 2"),
    ("The body gains resistant power against disease", "शरीर रोग के प्रति प्रतिरोधी शक्ति पाता है", "1 7 5 5 3 4 2 2"),
    ("The stepmother also loved the child", "सौतेली माँ ने भी बच्चे से प्रेम किया", "1 1 3 2 5 3 3 3"),
    ("The student has an analytical mind", "छात्र का विश्लेषणात्मक मन है", "1 3 4 5 2"),
    ("Fruits grew in plenty in the orchard", "बगीचे में विपुल मात्रा में फल लगे", "6 4 3 3 4 0 1"),
    ("The old man cleaned the spectacles", "बूढ़े ने चश्मे साफ़ किए", "1-2 3 5 3 3"),
    ("The ear hears many sounds", "कान बहुत सी ध्वनियों को सुनता है", "1 3 3 4 2 2 2"),
    ("All fruits especially mangoes are sold in summer", "सभी फल विशेषकर आम गर्मी में बिकते हैं", "0 1 2 3 7 6 5 4"),
    ("The stories of the vampire frighten children", "पिशाच की कहानियाँ बच्चों को डराती हैं", "4 2 1 6 6 5 5"),
    ("The organizer managed the whole program", "आयोजक ने पूरा कार्यक्रम संभाला", "1 2 4 5 2"),
    ("The banquet continued until late at night", "रात्रिभोज देर रात तक चला", "1 4 6 3 2"),
    ("The monasteries of the hill have ancient history", "पहाड़ के मठों का इतिहास प्राचीन है", "4 2 1 5 7 6 5"),
    ("The services of the providers are costly", "प्रदाताओं की सेवाएँ महँगी हैं", "4 2 1 6 5"),
    ("The guard stayed alert all night", "चौकीदार पूरी रात सतर्क रहा", "1 4 5 3 2"),
    ("The wings of the butterfly are symmetric", "तितली के पंख सममित होते हैं", "4 2 1 6 5 5"),
    ("The rotten fruits were thrown away", "सड़े फल फेंक दिए गए", "1 2 4 4 5"),
    ("The city was surrounded by problems", "नगरी समस्याओं से घिरी थी", "1 5 4 3 2"),
    ("The mother gave a kiss to the child", "माँ ने बच्चे को चुंबन दिया", "1 2 7 5 4 2"),
    ("The soul takes rebirth", "आत्मा का पुनर्जन्म होता है", "1 3 3 2 2"),
    ("The snails move slowly", "घोंघे धीरे चलते हैं", "1 3 2"),
    ("The origin of the river is the glacier", "नदी का उद्भव हिमनदी से होता है", "4 2 1 7 5 5 5"),
    ("That medicine works as a stimulant", "वह औषधि उत्तेजक का काम करती है", "0 1 5 4 2 2 2"),
    ("The proof went against the notions", "प्रमाण धारणाओं के विरुद्ध गया", "1 5 3 3 2"),
    ("The diamond shines in the light", "हीरा रोशनी में चमकता है", "1 5 4 2 2"),
    ("It rained heavily therefore the crops grew well", "मूसलाधार बारिश हुई इसलिये फसल अच्छी हुई", "2 1 1 3 5 7 6"),
    ("The poet writes ghazals", "वह शायर ग़ज़लें लिखता है", "0 1 3 2"),
    ("Trade goes on in the border areas", "सीमावर्ती क्षेत्रों में व्यापार होता है", "4 5 3 0 1 2"),
    ("The phonetic structure of the language changed", "भाषा का ध्वन्यात्मक ढाँचा बदल गया", "5 3 1 2 6 6"),
    ("The student solved all the equations", "छात्र ने सभी समीकरणों को हल किया", "1 2 3 5 2 2 2"),
    ("The child pointed a finger at the sky", "बच्चे ने आकाश की ओर उंगली उठाई", "1 2 7 5 5 4 2"),
    ("Fundamental rights were suspended in the emergency", "आपातकाल में मौलिक अधिकार रोक दिए गए", "6 4 0 1 3 3 3"),
    ("He withdrew his candidacy", "उसने अपनी उम्मीदवारी वापस ले ली", "0 2 3 1 1 1"),
    ("The minister talked to the journalists", "मंत्री ने संवाददाताओं से बात की", "1 2 5 4 3 2"),
    ("The temple is decorated with carvings", "मंदिर नक्काशी से अलंकृत है", "1 5 4 3 2"),
    ("The whole market lit up brightly", "पूरा बाज़ार जगमग उठा", "0 1 3 2"),
    ("The ointment healed the wound", "मरहम ने घाव भर दिया", "1 2 4 2 2"),
    ("She knows how to scrub utensils", "वह बर्तन माँजना जानती है", "0 4 3 1 1"),
    ("The grain was stored in the granary", "अनाज कोठार में भरा था", "1 6 4 3 2"),
    ("The exam was extremely hard", "परीक्षा अत्यन्त कठिन थी", "1 3 4 2"),
    ("Deer live in the forest", "मृग वान में रहते हैं", "0 4 2 1 1"),
    ("The court declared the evidence invalid", "न्यायालय ने सबूत अमान्य घोषित किया", "1 2 4 5 2 2"),
    ("The names are written in order", "नाम क्रमबद्ध लिखे हैं", "1 5 3 2"),
    ("The weaver weaves with skill", "बुनकर कुशलता से बुनता है", "1 4 3 2 2"),
    ("The children dislike the bitter medicine", "बच्चों को कड़वी दवा नापसंद है", "1 2 4 5 2 2"),
    ("Write the sums in brackets", "जोड़ कोष्ठक में लिखो", "2 4 3 0"),
    ("The measurement of land takes time", "भूमि के मापन में समय लगता है", "3 2 1 4 5 4 4"),
    ("Cells together make up the tissues", "कोशिकाएं मिलकर ऊतकों का निर्माण करती हैं", "0 1 5 4 2 2 2"),
    ("The custom of dowry is prevalent in society", "दहेज का प्रचलन समाज में है", "3 2 1 7 6 4"),
    ("The king performed a sacrifice", "राजा ने यज्ञ किया", "1 2 4 2"),
    ("Silk is cloth of high grade", "रेशम उच्च दर्जे का कपड़ा है", "0 4 5 3 2 1"),
    ("The postman went to deliver the letter", "डाकिया चिट्ठी पहुंचाने गया", "1 6 4 2"),
    ("The parts of machines are standardized", "मशीनों के पुर्ज़े मानकीकृत होते हैं", "3 2 1 5 4 4"),
    ("The police surrounded the dacoits", "पुलिस ने डाकुओं को घेर लिया", "1 2 4 2 2 2"),
    ("Small things matter in friendship", "दोस्ती में छोटी बातें मायने रखती हैं", "4 3 0 1 2 2 2"),
    ("The boy stood fourth in the class", "लड़का कक्षा में चतुर्थ स्थान पर रहा", "1 6 4 3 3 4 2"),
    ("Heat comes from the compression of air", "हवा के संपीड़न से गर्मी पैदा होती है", "6 5 4 2 0 1 1 1"),
    ("For a soldier duty is supreme", "सैनिक के लिए कर्तव्य सर्वोपरि होता है", "2 0 0 3 5 4 4"),
    ("The freedom struggle awakened patriotism", "स्वतंत्रता संग्राम ने देशभक्ति जगाई", "1 2 3 4 3"),
    ("Every voter cast a vote", "हर निर्वाचक ने मत दिया", "0 1 2 4 2"),
    ("The defeat demotivated the team", "हार ने टीम को हतोत्साहित किया", "1 2 4 3 2 2"),
    ("The people have faith in the court", "जनता को न्यायालय में आस्था है", "1 2 6 4 3 2"),
    ("The titles of the chapters make the topic clear", "अध्यायों के शीर्षकों से विषय स्पष्ट होते हैं", "4 2 1 5 7 8 5 5"),
    ("The mines closed after the explosions", "विस्फोटों के बाद खानें बंद हुईं", "5 3 3 1 2 2"),
    ("The members disagreed with the proposal", "सदस्य प्रस्ताव पर असहमत रहे", "1 5 3 2 2"),
    ("With use the meanings of words change", "प्रयोग के साथ शब्दों के अर्थों में बदलाव आता है", "1 0 0 5 4 3 6 6 6 6"),
    ("The festival brings joys", "त्यौहार खुशियाँ लाता है", "1 3 2 2"),
    ("The students were admitted to the college", "छात्र महाविद्यालय में दाखिल हुए", "1 6 4 3 2"),
    ("The tropical climate stays humid", "उपोष्णकटिबंधीय जलवायु नम रहती है", "0-1 2 4 3"),
    ("The villagers gathered under the tree", "गाँव वाले पेड़ के नीचे एकत्रित हुए", "1 1 5 3 3 2 2"),
    ("Good magazines increase knowledge", "अच्छी पत्रिकाएँ ज्ञान बढ़ाती हैं", "0 1 3 2 2"),
    ("Life is full of ups and downs", "जीवन उतारचढ़ाव से भरा है", "0 4-6 3 2 1"),
    ("The inventor made a new machine", "आविष्कारक ने नई मशीन बनाई", "1 2 4 5 2"),
    ("Wear protective clothes in the sun", "धूप में सुरक्षात्मक कपड़े पहनो", "5 3 1 2 0"),
    ("The new law expanded the dimensions of rights", "नए कानून ने अधिकारों के आयामों को बढ़ाया", "1 2 3 7 6 5 3 3"),
    ("The nation is rich in natural wealth", "राष्ट्र प्राकृतिक संपदा से समृद्ध है", "1 5 6 4 3 2"),
    ("The faces were not recognized in the dark", "अंधेरे में चेहरे नहीं पहचाने गए", "7 5 1 3 4 2"),
    ("Forestry conserves the forests", "वानिकी वनों का संरक्षण करती है", "0 3 2 1 1 1"),
    ("His birthday falls on the sixteenth", "उसका जन्मदिन सोलहवीं को आता है", "0 1 5 3 2 2"),
    ("Irrigation increased the productivity of the fields", "सिंचाई ने खेतों की उत्पादकता बढ़ाई", "0 1 6 4 3 1"),
    ("The operator pays attention to the machine", "प्रचालक मशीन पर ध्यान देता है", "1 6 4 3 2 2"),
    ("The reformers clashed with the conservatives", "सुधारक रूढ़िवादियों से टकराए", "1 5 3 2"),
    ("The body got legal status", "संस्था को वैधानिक दर्जा मिला", "1 2 3 4 2"),
    ("The data is stored in an array", "आँकड़े सरणी में संग्रहित होते हैं", "1 6 4 3 2 2"),
    ("He drank water to cool the throat", "उसने गला ठंडा करने के लिए पानी पिया", "0 6 4 3 3 3 2 1"),
    ("The child drew a line with chalk", "बच्चे ने चाक से लकीर खींची", "1 2 6 5 4 2"),
    ("Transcription of the speech took hours", "प्रतिलेखन भाषण के में घंटे लगे", "0 3 1 4 5 4"),
    ("The king sent a message", "राजा ने सन्देश भेजा", "1 2 4 2"),
    ("The serpent is counted in the reptile class", "साँप सरीसृप योनि में आता है", "1 6 7 4 2 2"),
    ("Training workshops were held in the districts", "जिलों में प्रशिक्षण कार्यशालाओं का आयोजन हुआ", "6 4 0 1 3 3 3"),
    ("The optimal use of resources is necessary", "साधनों का इष्टतम उपयोग आवश्यक है", "4 3 1 2 6 5"),
    ("The storyteller narrated the tale", "कथाकार ने कहानी सुनाई", "1 2 4 2"),
    ("The entries in the register were checked", "रजिस्टर की प्रविष्टियों की जाँच हुई", "4 2 1 5 6 6"),
    ("The soldiers bid farewell to their wives", "सैनिकों ने अपनी पत्नियों को विदा किया", "1 2 5 6 4 3 2"),
    ("The tehsil office remains open all day", "तालुका कार्यालय सारा दिन खुला रहता है", "1 2 5 6 4 3 3"),
    ("The family lives in unity", "परिवार एकजुटता से रहता है", "1 4 3 2 2"),
    ("The lawyer did advocacy for the poor", "वकील ने गरीबों की पैरवी की", "1 2 6 4 3 2"),
    ("The swimmer crossed the river", "तैराक नदी पार कर गया", "1 4 2 2"),
    ("The inner room stays cool", "भीतरी कमरा ठंडा रहता है", "0 2 4 3"),
    ("The researcher is methodical", "शोधकर्ता पद्धतिवादी है", "1 3 2"),
    ("The instability of the government increased", "सरकार की अस्थिरता बढ़ गई", "4 2 1 5 5"),
    ("Time heals old wounds", "समय पुराने घावों को भर देता है", "0 2 3 3 1 1 1"),
    ("The travelers were surrounded by the forest", "यात्री जंगल से घिरे थे", "1 6 4 3 2"),
    ("The students collected money for the trip", "छात्रों ने यात्रा के लिए पैसे जुटाए", "1 2 6 4 4 3 2"),
    ("The binary system has only two digits", "द्विआधारी पद्धति में केवल दो अंक होते हैं", "1 2 3 4 5 6 3 3"),
    ("Manure is made from the droppings of animals", "पशुओं के मल से खाद बनती है", "7 6 5 3 0 2 1"),
    ("The students fear exams", "छात्र परीक्षाओं से डरते हैं", "1 3 2 2 2"),
    ("Mosquitoes spread malaria", "मच्छर मलेरिया फैलाते हैं", "0 2 1"),
    ("The municipality approved the plan", "पालिका ने योजना स्वीकार की", "1 2 4 2"),
    ("The village joins the city by the road", "सड़क से गाँव शहर से जुड़ता है", "7 5 1 4 5 2 2"),
    ("Tertiary education is costly", "तृतीयक शिक्षा महँगी है", "0 1 3 2"),
    ("Tolerance keeps society together", "सहिष्णुता समाज को जोड़े रखती है", "0 2 2 3 1 1"),
    ("Gravel was filled in the pit", "गड्ढे में बजरी भरी गई", "1 2 5 3 3"),
    ("The chief entrusted the keys to the guard", "प्रमुख ने चौकीदार को चाबियाँ सौंपे", "1 2 7 5 4 2"),
    ("The errors in the book were corrected", "पुस्तक की त्रुटियों को सुधारा गया", "4 2 1 6 6 6"),
    ("The movement of the battalions continued", "बटालियनों की आवाजाही जारी रही", "4 2 1 5 5"),
    ("The sensor detected the smoke", "संवेदक ने धुएँ को पहचाना", "1 2 4 3 2"),
]

# tense boosters (constructions match coverage_vakya.py regexes)
T = [
    # present perfect: ne + kiya/diya/liya/gaya/aae + hai
    ("The officer has done the inspection", "अधिकारी ने निरीक्षण किया है", "1 2 5 3 2"),
    ("The gardener has given water to the plants", "माली ने पौधों को पानी दिया है", "1 2 7 5 4 3 2"),
    ("The girl has taken the letter", "लड़की ने पत्र लिया है", "1 2 5 3 2"),
    ("The servant has cleaned the courtyard", "नौकर ने आँगन साफ़ किया है", "1 2 5 3 2"),
    ("The thief has run away", "चोर भाग गया है", "1 3 4 2"),
    ("The guests have come home", "मेहमान घर आए हैं", "1 4 3 2"),
    ("The farmer has finished the harvest", "किसान फसल काट चुका है", "1 5 3 3 2"),
    ("The results have gone in favor of the students", "परिणाम छात्रों के पक्ष में गए हैं", "1 8 5 5 4 3 2"),
    # past perfect: ne + kiya/diya/liya/gaya/aae + tha
    ("The carpenter had done the work", "बढ़ई ने काम किया था", "1 2 5 3 2"),
    ("The teacher had given the prize", "शिक्षक ने पुरस्कार दिया था", "1 2 5 3 2"),
    ("The boy had taken the letter", "लड़के ने पत्र लिया था", "1 2 5 3 2"),
    ("The bird had flown away", "पक्षी उड़ गया था", "1 3 4 2"),
    ("The players had come on the field", "खिलाड़ी मैदान पर आए थे", "1 6 4 3 2"),
    ("The lion had hunted the prey", "शेर ने शिकार किया था", "1 2 5 3 2"),
    ("By then the sun had set", "तब तक सूरज डूब चुका था", "1 0 3 5 5 4"),
    # future continuous: raha/rahe/rahi + honga/hongi/honge
    ("The children will be bathing in the river", "बच्चे नदी में नहा रहे होंगे", "1 7 5 4 3 2"),
    ("At noon the women will be cooking food", "दोपहर औरतें खाना पका रही होंगी", "1 3 7 6 5 4"),
    ("In the evening the birds will be returning home", "शाम को पक्षी घर लौट रहे होंगे", "2 0 4 8 7 6 5"),
    ("The oxen will be grazing in the field", "बैल खेत में चर रहे होंगे", "1 7 5 4 3 2"),
    ("The child will be sleeping in the cradle", "बच्चा पालने में सो रहा होगा", "1 7 5 4 3 2"),
    ("The washerman will be beating the clothes", "धोबी कपड़े पीट रहा होगा", "1 6 4 3 2"),
    # present continuous top-up
    ("The calf is drinking milk", "बछड़ा दूध पी रहा है", "1 4 3 2 2"),
    ("The hens are pecking grain", "मुर्गियाँ दाना चुग रही हैं", "1 4 3 2 2"),
    ("The goats are grazing grass", "बकरियाँ घास चर रही हैं", "1 4 3 2 2"),
    ("The potter is kneading the clay", "कुम्हार मिट्टी गूँध रहा है", "1 5 3 2 2"),
    # past continuous top-up
    ("The oxen were pulling the cart", "बैल गाड़ी खींच रहे थे", "1 5 3 2 2"),
    ("Grandma was telling a story", "दादी कहानी सुना रही थीं", "0 4 2 1 1"),
    ("The girl was grinding the grain", "लड़की अनाज पीस रही थी", "1 5 3 2 2"),
    ("The cattle were grazing near the pond", "मवेशी तालाब के पास चर रहे थे", "1 6 4 4 3 2 2"),
    ("The baby was crying in the lap", "शिशु गोद में रो रहा था", "1 6 4 3 2 2"),
    ("The men were unloading the sacks", "आदमी बोरियाँ उतार रहे थे", "1 5 3 2 2"),
    ("The kite was flying in the sky", "पतंग आकाश में उड़ रही थी", "1 6 4 3 2 2"),
]

out = []
def add(en, hi, align):
    out.append({"id": f"j{len(out)+1:03d}", "en": en, "hi": hi, "align": align})
for e, h, a in N:
    add(e, h, a)
for e, h, a in T:
    add(e, h, a)

# structural check + auto-repair (same as gen_phrases15/16)
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

bad = []
for s in out:
    if not ok(s):
        bad.append(s["id"])
        s["align"] = ga.derive(s["en"], s["hi"])
print(f"repaired to valid: {sum(ok(s) for s in out)}/{len(out)} (derived for: {' '.join(bad) or 'none'})")

(ROOT / "data" / "phrases17.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
man = json.load(open(ROOT / "data" / "manifest.json"))
man["files"] = [f for f in man["files"] if f["file"] != "data/phrases17.json"] + [
    {"file": "data/phrases17.json", "count": len(out)}]
json.dump(man, open(ROOT / "data" / "manifest.json", "w"), ensure_ascii=False, indent=2)
print(f"wrote {len(out)} sentences -> data/phrases17.json")
