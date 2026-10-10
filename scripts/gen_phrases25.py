#!/usr/bin/env python3
"""Batch ID-01: Anatomy & Sensations I (आँख, कान, नाक, मुँह/जीभ).

Generates data/phrases25.json (250 sentences) and updates data/manifest.json.
Validates charset, bounds, and alignment.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 250 bilingual pairs for Anatomy & Sensations I
# Eyes: 1-65, Ears: 66-125, Nose: 126-185, Mouth/Tongue/Teeth/Lips: 186-250
PAIRS = [
    # 1-65: आँख, नज़र, नयन
    ("The student opened his eyes to the truth after reading history", "इतिहास पढ़कर छात्र की आँखें सच्चाई के प्रति खुल गईं"),
    ("Ignorance had cast a dark veil over his eyes", "अज्ञानता के कारण उसकी आँखों पर गहरा पर्दा पड़ा था"),
    ("The mother longed with eager eyes to see her beloved son", "माँ अपने प्यारे बेटे को देखने के लिए आँखें तरसती रही"),
    ("The villagers spread their eyes in warm welcome for the guest", "ग्रामीणों ने आदरणीय अतिथि के स्वागत में आँखें बिछा दीं"),
    ("The corrupt officer was an eyesore to the entire village", "भ्रष्ट अधिकारी पूरे गाँव के लोगों की आँखों में खटकता था"),
    ("Her eyes turned to stone waiting for the traveller to return", "यात्री के लौटने की प्रतीक्षा में उसकी आँखें पथरा गईं"),
    ("The guilty boy tried to avoid eyes after his secret was out", "भेद खुल जाने पर दोषी लड़का सबसे आँखें चुराने लगा"),
    ("Selfishness had tied a blindfold over the eyes of the greedy man", "स्वार्थ ने लालची व्यक्ति की आँखों पर पट्टी बाँध दी थी"),
    ("The wicked enemy remained a painful thorn in their eye", "दुष्ट शत्रु हमेशा उनके लिए आँख का काँटा बना रहा"),
    ("The dishonest servant lowered his eyes in deep shame", "बेईमान नौकर ने गहरी लज्जा से अपनी आँखें नीची कर लीं"),
    ("Her eyes welled up with tears upon hearing the sad story", "दुखद कहानी सुनकर उसकी आँखें आँसुओं से भर आईं"),
    ("The young prince dared not look up before the venerable king", "युवा राजकुमार ने आदरणीय राजा के सामने आँख उठाकर नहीं देखा"),
    ("The shameless thief had lost all sense of shame in his eyes", "बेशर्म चोर की आँखों का सारा पानी मर चुका था"),
    ("The worried father spent the entire dark night with open eyes", "चिंतित पिता ने पूरी अंधेरी रात आँखों में काट दी"),
    ("The brave soldiers never closed their eyes to danger", "बहादुर सैनिकों ने कभी किसी खतरे से आँखें नहीं मूँदीं"),
    ("The clever thief stole the collyrium from eyes without any sound", "चतुर चोर ने बिना आवाज़ किए आँख का काजल चुरा लिया"),
    ("The distant boat vanished from their eyes into the evening mist", "दूर जाती नाव शाम के कोहरे में आँखों से ओझल हो गई"),
    ("The loyal citizens placed the kind king upon their eyes", "वफादार नागरिकों ने दयालु राजा को अपनी आँखों पर बिठाया"),
    ("The amazed children stared with wide eyes at the giant elephant", "हैरान बच्चों ने आँखें फाड़कर विशाल हाथी की ओर देखा"),
    ("The little boy was the star of the eyes of his grandmother", "छोटा बालक अपनी प्यारी दादी की आँखों का तारा था"),
    ("The con man threw dust in the eyes of innocent travelers", "धूर्त व्यक्ति ने भोले यात्रियों की आँखों में धूल झोंकी"),
    ("The angry master turned red and yellow in fierce wrath", "गुस्सैल मालिक क्रोध के मारे आँखें लाल पीली करने लगा"),
    ("The tired farmer dozed off under the cool shade of the banyan", "थका हुआ किसान बरगद की शीतल छाया में आँख लगा बैठा"),
    ("The two friends communicated their secret plan solely through eyes", "दोनों मित्रों ने आँखों ही आँखों में अपनी गुप्त योजना बना ली"),
    ("Her eyes shone with great joy after passing the difficult exam", "कठिन परीक्षा पास करके उसकी आँखों में अनोखी चमक आ गई"),
    ("The strict guard showed sharp eyes to the noisy crowd", "सख्त पहरेदार ने शोर मचाती भीड़ को गुस्से में आँखें दिखाईं"),
    ("The golden image of the temple remained forever in his eyes", "मंदिर की स्वर्णिम छवि हमेशा उसकी आँखों में बसी रही"),
    ("The witness presented a vivid eyewitness account of the event", "गवाह ने सभा में पूरी घटना का आँखों देखा हाल सुनाया"),
    ("The proud merchant refused even to glance at the poor beggar", "घमंडी व्यापारी ने गरीब भिखारी की ओर आँख उठाकर भी न देखा"),
    ("The idle youth kept dreaming with open eyes without doing work", "आलसी युवक बिना कोई काम किए खुली आँखों से सपने देखता रहा"),
    ("Her eyes became moist with deep emotion upon meeting an old friend", "पुराने मित्र से मिलकर उसकी आँखें गहरी भावना से तर हो गईं"),
    ("The hungry vulture sat with eyes fixed upon the distant meat", "भूखा गिद्ध दूर रखे मांस पर आँख गड़ाए बैठा रहा"),
    ("Darkness spread before his eyes when he heard the sudden news", "अचानक बुरी खबर सुनकर उसकी आँखों के आगे अंधेरा छा गया"),
    ("The rude behavior of the stranger did not please his eyes", "अपरिचित व्यक्ति का बुरा व्यवहार उसकी आँखों को बिल्कुल न सुहाया"),
    ("The watchful mother did not let the little child out of sight", "सतर्क माँ ने छोटे बच्चे को अपनी आँख से ओझल न होने दिया"),
    ("True knowledge removed the heavy blindfold from the young minds", "सच्चे ज्ञान ने युवाओं की आँखों पर पड़ा भारी पर्दा हटा दिया"),
    ("The grandmother cast off the evil eye with dry red chilies", "दादी ने सूखी लाल मिर्च जलाकर छोटे बच्चे की नज़र उतारी"),
    ("The fearful witness avoided the eyes of the stern judge", "डरे हुए गवाह ने कठोर न्यायाधीश से अपनी नज़रें चुरा लीं"),
    ("The honest leader met the eyes of the gathered crowd fearlessly", "ईमानदार नेता ने निर्भय होकर उपस्थित भीड़ से नज़रें मिलाईं"),
    ("The noble artist gained a high place in the royal eyes", "सदाचारी कलाकार राजा की पारखी नज़र में बहुत ऊँचा बैठ गया"),
    ("The traitor fell from respect in the eyes of all countrymen", "गद्दार सभी देशवासियों की नज़र से हमेशा के लिए गिर गया"),
    ("The watchman kept strict surveillance over the palace gates at night", "चौकीदार ने रात भर महल के मुख्य द्वार पर कड़ी नज़र रखी"),
    ("The wise elder overlooked the minor mistake of the young boy", "बुद्धिमान बुज़ुर्ग ने छोटे बालक की सामान्य भूल को नज़र अंदाज़ किया"),
    ("The envious neighbor looked askance at the prosperous new house", "ईर्ष्यालु पड़ोसी ने नए सुंदर घर को तिरछी नज़र से देखा"),
    ("The royal hunter possessed keen vision in the deep jungle", "शाही शिकारी घने जंगल में बहुत तेज़ नज़र रखता था"),
    ("The scientist scrutinized the ancient manuscript with deep eyes", "वैज्ञानिक ने प्राचीन पांडुलिपि को अत्यंत गहरी नज़र से देखा"),
    ("The tired traveler cast a quick glance across the green valley", "थके हुए यात्री ने हरी भरी घाटी पर एक नज़र दौड़ाई"),
    ("The kind doctor cast an attentive glance upon the patient", "दयालु चिकित्सक ने बीमार व्यक्ति पर एक सहानुभूतिपूर्ण नज़र डाली"),
    ("His steady eyes rested upon the beautiful marble palace", "उसकी स्थिर नज़र सुंदर संगमरमर के राजमहल पर टिक गई"),
    ("The eagle kept a sharp eye on the moving fish below", "चील ने पानी में तैरती मछली पर पैनी नज़र रखी"),
    ("The brave deed brought the young soldier into royal favor", "साहसिक कार्य से युवा सिपाही सेनापति की अच्छी नज़र में चढ़ा"),
    ("The kind words awakened fresh hope in the eyes of laborers", "सहानुभूति भरे शब्दों ने मजदूरों की आँखों में नई उम्मीद जगाई"),
    ("The continuous injustice rankled like a particle in the public eyes", "लगातार होता अन्याय जनता की आँखों में तिनके की तरह चुभता था"),
    ("The two leaders exchanged glances of mutual understanding across table", "दोनों नेताओं ने मेज़ के पार आपसी समझ से आँखें मिलाईं"),
    ("The curious child stared with wide eyes at the spinning wheel", "जिज्ञासु बालक ने घूमते हुए पहिये को फटी आँखों से देखा"),
    ("Greed made the cunning broker fix covetous eyes on the land", "लालच के कारण चालाक दलाल ने उपजाऊ भूमि पर आँख गड़ा दी"),
    ("The pure devotion brought tears of gratitude into her eyes", "सच्ची भक्ति ने उसकी आँखों में कृतज्ञता के आँसू ला दिए"),
    ("The old poet remembered the sacred sights with closed eyes", "बूढ़े कवि ने बंद आँखों से पवित्र दृश्यों को याद किया"),
    ("The village remained safe under the watchful eyes of the guard", "पहरेदार की सजग आँखों की देखरेख में गाँव सुरक्षित रहा"),
    ("A gleam of confidence shone in the eyes of the winner", "विजेता खिलाड़ी की आँखों में गहरे आत्मविश्वास की चमक दिखाई दी"),
    ("The guilty servant could not raise his eyes before the master", "अपराधी नौकर स्वामी के सामने अपनी आँखें न उठा सका"),
    ("The mother washed the dust from the eyes of the child", "माँ ने स्वच्छ जल से बालक की आँखों की धूल धोई"),
    ("The beauty of the sunrise filled their eyes with wonder", "सूर्योदय के अनुपम सौंदर्य ने उनकी आँखों को विस्मय से भर दिया"),
    ("The honest clerk never cast a greedy eye on public wealth", "ईमानदार मुंशी ने सरकारी धन पर कभी लालची नज़र नहीं डाली"),
    ("The true friend never looked away during times of sorrow", "सच्चे मित्र ने विपत्ति के समय कभी अपनी आँखें नहीं फेरीं"),

    # 66-125: कान
    ("The naughty student held his ears and promised never to lie", "शरारती छात्र ने कान पकड़कर फिर कभी झूठ न बोलने का वादा किया"),
    ("The deceitful minister poisoned the ears of the ruler against the general", "कपटी मंत्री ने सेनापति के विरुद्ध शासक के कान भर दिए"),
    ("The deer perked up its ears upon hearing the twig snap", "टहनी टूटने की आवाज़ सुनकर हिरण के कान खड़े हो गए"),
    ("Not a louse crawled on his ear despite repeated warnings", "बार बार चेतावनी देने पर भी लापरवाह लड़के के कान पर जूँ न रेंगी"),
    ("The credulous officer believed every rumor because he was soft of ear", "अफसर कान का कच्चा था इसलिए उसने हर उड़ती अफवाह मान ली"),
    ("The attentive disciple listened intently to every word of the sage", "जिज्ञासु शिष्य ने ऋषि के प्रत्येक वचन पर कान लगाया"),
    ("Listen carefully to the instructions of the experienced guide", "अनुभवी मार्गदर्शक के महत्वपूर्ण निर्देशों को कान खोलकर सुनो"),
    ("The secret plan succeeded without the slightest whisper reaching anyone", "किसी को कानों कान खबर हुए बिना ही गुप्त योजना सफल हो गई"),
    ("The arrogant landlord sat pouring oil into his ears ignoring pleas", "घमंडी ज़मींदार गरीबों की पुकार सुनकर भी कान में तेल डाले बैठा रहा"),
    ("Her ears yearned to hear the sweet voice of her daughter", "माँ के कान अपनी परदेसी बेटी की मीठी आवाज़ सुनने को तरस गए"),
    ("The strict master twisted the ear of the negligent apprentice", "कठोर उस्ताद ने लापरवाह कारीगर का कान मरोड़कर काम सिखाया"),
    ("The talkative passenger talked the ear off of everyone on the journey", "बातूनी सहयात्री ने पूरे सफर में बोल बोलकर सबके कान खा लिए"),
    ("Lend an ear to the grievances of the working people", "मेहनतकश जनता की गंभीर समस्याओं पर भी थोड़ा कान दीजिए"),
    ("The melodious flute poured sweet nectar into the ears of villagers", "मधुर बाँसुरी की धुन ने ग्रामीणों के कानों में रस घोल दिया"),
    ("The righteous man placed hands on his ears hearing wicked slander", "सज्जन पुरुष ने दुष्टों की निंदा सुनकर अपने कानों पर हाथ रख लिए"),
    ("The spiritual guru whispered sacred wisdom into the ear of the initiate", "आध्यात्मिक गुरु ने नए शिष्य के कान में पवित्र ज्ञान फूँका"),
    ("A strange piece of news fell upon the ears of the villagers", "गाँव वालों के कान में एक बहुत ही विचित्र समाचार पड़ा"),
    ("Loud thunder made the ears of the frightened animals ring", "बादलों की भीषण गर्जना से भयभीत पशुओं के कान बजने लगे"),
    ("The wise father pulled the ear of his son with love", "बुद्धिमान पिता ने अपने भटके हुए पुत्र का कान उमठ दिया"),
    ("The fair judge kept his ears clean of all false rumors", "न्यायप्रिय हाकिम ने झूठी अफवाहों से अपने कान हमेशा साफ़ रखे"),
    ("The fearful wolf flattened its ears and fled into the dark forest", "डरपोक भेड़िया कान दबाकर घने अंधेरे जंगल की ओर भाग गया"),
    ("The terrible explosion deafened the ears of all nearby villagers", "भीषण विस्फोट की तेज़ गूँज से आसपास के लोगों के कान फट गए"),
    ("The freezing mountain wind made the ears of the climbers numb", "बर्फ़ीली पहाड़ी हवा से पर्वतारोहियों के कान पूरी तरह सुन्न हो गए"),
    ("The truth of the conspiracy finally reached the ears of the king", "षड्यंत्र की पूरी सच्चाई आखिरकार प्रजापालक राजा के कान तक पहुँची"),
    ("The sound of evening bells sounded pleasing to the weary ears", "शाम के घंटों की पवित्र ध्वनि थके हुए कानों को बहुत भली लगी"),
    ("The faithful guard stood with perked ears through the quiet night", "वफादार संतरी पूरी शांत रात कान खड़े करके पहरा देता रहा"),
    ("The trusted minister dropped a quiet word into the royal ear", "विश्वस्त मंत्री ने एकांत में राजा के कान में आवश्यक बात डाली"),
    ("The pious woman shut her ears to malicious village gossip", "धर्मपरायण महिला ने गाँव की निंदनीय बातों पर कान बंद कर लिए"),
    ("The stern teacher opened the ears of the careless scholars", "कड़े अध्यापक ने लापरवाह छात्रों के कान खोलकर उन्हें सच समझाया"),
    ("The foolish orator bored the audience to exhaustion with endless words", "मूर्ख वक्ता ने लंबी बातों से उपस्थित श्रोताओं के कान पका दिए"),
    ("The violent roar of the waterfall shook the ears of travelers", "झरने की प्रचंड आवाज़ से सभी यात्रियों के कानों के पर्दे हिल गए"),
    ("The final advice of the grandmother echoed constantly in his ears", "दादी की अंतिम सीख उस युवक के कानों में लगातार गूँजती रही"),
    ("Open the window of your ears to beneficial ancient learning", "हितकारी प्राचीन ज्ञान को ग्रहण करने के लिए अपने कान की खिड़की खोलो"),
    ("The two conspirators whispered closely ear to ear in the dark corner", "दोनों षड्यंत्रकारियों ने अंधेरे कोने में कान से कान सटाकर फुसफुसाया"),
    ("The contrite boy touched his ears in genuine remorse", "पछताते हुए लड़के ने अपनी भूल पर दोनों कान छूकर क्षमा माँगी"),
    ("The faint whisper failed to reach the distant ears of the crowd", "धीमी फुसफुसाहट दूर खड़ी विशाल भीड़ के कानों तक नहीं पहुँच सकी"),
    ("The annoying insect buzzed constantly near the sleeping man ear", "परेशान करने वाला कीड़ा सोते हुए व्यक्ति के कान के पास भिनभिनाया"),
    ("Her gentle words dissolved like sugar candy in the ears of listeners", "उसके कोमल शब्दों ने सुनने वालों के कानों में मिश्री घोल दी"),
    ("The sudden thunderous bang nearly burst the eardrums of the soldiers", "अचानक हुए भयंकर धमाके से सैनिकों के कान के पर्दे फटने लगे"),
    ("Their ears marvelled at the miraculous victory of the small army", "छोटी सेना की अद्भुत विजय सुनकर सभी के कानों को अचरज हुआ"),
    ("The sneaky spy listened at the doorway with attentive ears", "धूर्त गुप्तचर ने दरवाज़े पर कान लगाकर सभी गुप्त बातें जान लीं"),
    ("The sister whispered the delightful surprise into the ear of her brother", "बहन ने भाई के कान में चुपके से सुखद समाचार फुसफुसाया"),
    ("The reformed delinquent held his ears and did sit ups before the assembly", "सुधरे हुए युवक ने सबके सामने कान पकड़कर उठक बैठक की"),
    ("The indifferent landlord sat with closed ears amid cries for help", "बेपरवाह सेठ सहायता की गुहार के बीच कान मूँदकर बैठा रहा"),
    ("The sublime song poured divine nectar into the ears of pilgrims", "भक्तिमय संगीत ने तीर्थयात्रियों के कानों में दिव्य अमृत बरसा दिया"),
    ("The classical performance gave complete fulfillment to musical ears", "शास्त्रीय गायन ने संगीत प्रेमियों के कानों को सच्ची तृप्ति दी"),
    ("The loyal horse shook its ears upon spotting its master afar", "वफादार घोड़े ने दूर से स्वामी को देखकर अपने कान हिलाए"),
    ("The watchdog kept guard with perked ears outside the courtyard gate", "चौकस कुत्ते ने आँगन के फाटक पर कान खड़े रखकर पहरा दिया"),
    ("The harsh screech of the rusty wheels grated upon tender ears", "जंग लगे पहियों की तीखी आवाज़ सुकुमार कानों में बुरी तरह चुभी"),
    ("The medicine cleared the blocked eardrum of the aged scholar", "दवा के प्रभाव से वृद्ध विद्वान के बंद कान का पर्दा साफ़ हो गया"),
    ("A joyful shout reverberated through the ears of the excited villagers", "उत्साहित ग्रामीणों के कानों में विजय का आनंदमय जयघोष गूँज उठा"),
    ("The wicked jealous relative poured deadly poison into their ears", "ईर्ष्यालु संबंधी ने परिवार के सदस्यों के कान में ज़हर घोल दिया"),
    ("The merchant rubbed his ears in bitter regret over the foolish bargain", "व्यापारी ने घाटे के सौदे पर पछतावे से अपने कान मले"),
    ("The profound teaching of the mentor finally settled into his ear", "गुरु का गंभीर उपदेश आखिरकार उस शिष्य के कान में बैठ गया"),
    ("Their ears refused to believe the shocking news of defeat", "पराजय का दुखद समाचार सुनकर लोगों के कानों को विश्वास न हुआ"),
    ("The old blacksmith became slightly hard of hearing from hammer blows", "हथौड़े की निरंतर चोटों से बूढ़ा लोहार कान से थोड़ा बहरा हो गया"),
    ("The respectful nephew held his earlobes asking for affectionate pardon", "आज्ञाकारी भतीजे ने बड़ों के आगे कान की लोली पकड़कर क्षमा माँगी"),
    ("A strange whistling sensation rang in his ear after the blast", "विस्फोट के बाद काफी देर तक उसके कान में सीटी बजती रही"),
    ("The headstrong youth paid no attention to valuable parental counsel", "हठीले युवक ने माता पिता के हितकारी परामर्श पर कान न दिया"),
    ("Listening to divine hymns cleared all stale thoughts from their ears", "पवित्र भजन सुनकर भक्तों के कानों के सारे विकार दूर हो गए"),

    # 126-185: नाक
    ("The shameful act cut the nose of the honorable family in society", "शर्मनाक काम ने समाज में प्रतिष्ठित परिवार की नाक काट दी"),
    ("The devoted son saved the nose and dignity of his ancestors", "सच्चे सपूत ने पूर्वजों की नाक और मान मर्यादा बचा ली"),
    ("The honest clerk became the hair of the nose of the officer through loyalty", "ईमानदार मुंशी अपनी निष्ठा से बड़े साहब की नाक का बाल बन गया"),
    ("The mischievous monkeys harassed and annoyed the fruit vendors endlessly", "शरारती बंदरों ने फल विक्रेताओं की नाक में दम कर दिया"),
    ("The defeated opponent rubbed his nose on the ground pleading for mercy", "पराजित शत्रु ने ज़मीन पर नाक रगड़कर दया की भीख माँगी"),
    ("The haughty guest wrinkled her nose in disdain at simple food", "घमंडी मेहमान ने सादे भोजन को देखकर नाक भौं सिकोड़ ली"),
    ("The proud officer flared his nostrils in hot anger at insolence", "गुस्सैल अफसर ने धृष्टता देखकर क्रोध में अपनी नाक फुला ली"),
    ("The dignified gentleman never let a fly sit on his proud nose", "स्वाभिमानी सज्जन अपनी इज़्ज़त की नाक पर कभी मक्खी न बैठने देता था"),
    ("The clever detective made the arrogant criminal grovel in the dust", "चतुर जासूस ने घमंडी अपराधी से अदालत में नाक रगड़वा दी"),
    ("The brave daughter held the nose of the village high by winning", "जीत हासिल करके बहादुर बेटी ने पूरे गाँव की नाक ऊँची रखी"),
    ("The disgraced merchant sat with a cut nose in the marketplace", "अपमानित व्यापारी बाज़ार के बीच कटी नाक लेकर लज्जित बैठा रहा"),
    ("The strict mother put a tight rein on the unruly child", "सख्त माँ ने उद्दंड बालक की नाक में नकेल डाल दी"),
    ("Anger always sat on the very tip of his impatient nose", "उस अधीर व्यक्ति की नाक पर हमेशा बेवजह गुस्सा सवार रहता था"),
    ("The snobbish lady looked down with wrinkled nose upon the village cottage", "नखरेबाज महिला ने गाँव की कुटिया को नाक सिकोड़कर देखा"),
    ("The floods rose until water reached up to the nose of cottages", "बाढ़ इतनी बढ़ी कि झोपड़ियों की नाक तक पानी आ गया"),
    ("The foolish thinker was unable to see beyond his own nose", "संकीर्ण सोच वाला व्यक्ति अपनी नाक से आगे कुछ न देख सका"),
    ("The speaker spoke through his nose with an unusual tone", "वक्ता ने अजीब लहजे में अपनी नाक के सुर से बात की"),
    ("The constant interference brought everyone to the point of suffocation", "लगातार हस्तक्षेप से घर के सदस्यों की नाक में दम आ गया"),
    ("The arrogant prince raised his nose and turned away from commoners", "अभिमानी राजकुमार ने नाक चढ़ाकर साधारण प्रजा से मुँह मोड़ लिया"),
    ("Winning the tournament became an ultimate question of nose for the team", "प्रतियोगिता जीतना दोनों टीमों के लिए प्रतिष्ठा और नाक का सवाल बन गया"),
    ("The honest effort saved the nose of the organization from scandal", "ईमानदार प्रयास ने संस्था की नाक बदनामी से बचा ली"),
    ("The audacious theft occurred right under the nose of royal guards", "दुस्साहसी चोरी शाही संतरियों की नाक के नीचे घटित हुई"),
    ("The teacher stopped the student from the bad habit of poking nose", "अध्यापक ने छात्र को नाक में उँगली डालने से मना किया"),
    ("The honest traveler walked straight in the line of his nose", "सीधा सादा पथिक बिना भटके अपनी नाक की सीध में चलता रहा"),
    ("The nervous witness wiped his nose before answering the hard query", "घबराए गवाह ने कठिन सवाल सुनकर अपनी नाक पर हाथ फेरा"),
    ("Pressing the nose made the stubborn thief open his mouth", "दबाव बनाकर नाक दबाने से हठी चोर का मुँह खुल गया"),
    ("The haughty minister could not bear the slightest fly on his nose", "अभिमानी मंत्री अपनी नाक पर बैठी मक्खी भी सहन न कर पाता था"),
    ("The weeping child sniffled his nose during the chilly winter morning", "रोता हुआ बालक ठंडी सुबह में अपनी नाक सुड़कता रहा"),
    ("The golden nose ring of the bride sparkled under the festival lamps", "विवाह के दीयों में दुल्हन की सोने की नथ खूब चमकी"),
    ("The strict law tightened the rein on illegal trade across the border", "कठोर कानून ने सीमा पार अवैध व्यापार की नाक में नकेल कसी"),
    ("The swindler sat disgraced after his fraudulent scheme collapsed", "धोखेबाज़ अपनी पोल खुलने के बाद नाक कटाकर बैठ गया"),
    ("The playful bee perched right on the tip of the nose of the tiger", "चंचल मधुमक्खी सोते हुए बाघ की नाक की नोक पर बैठ गई"),
    ("The foul odor from the sewer offended the nose of passersby", "नाली की सड़ी बदबू ने राहगीरों की नाक में बेचैनी पैदा की"),
    ("The pungent spice caused an itch inside his sensitive nose", "तीखे मसाले के कारण उसकी संवेदनशील नाक में खुजली होने लगी"),
    ("The people walked past the garbage dump holding their nose tightly", "लोग कूड़े के ढेर के पास से नाक सिकोड़कर तेज़ी से निकले"),
    ("The noble family strove hard to preserve the prestige of their nose", "कुलीन घराने ने अपनी खानदानी नाक की प्रतिष्ठा बनाए रखने को संघर्ष किया"),
    ("The guilty merchant feared the bitter shame of having his nose cut", "दोषी व्यापारी समाज में अपनी नाक कटने के भय से काँपता रहा"),
    ("The boxer took an accidental blow upon his nose during practice", "अभ्यास के दौरान मुक्केबाज़ की नाक पर अचानक भारी चोट लगी"),
    ("The clever thief slipped right past under the nose of the watchmen", "शातिर चोर पहरेदारों की नाक के नीचे से चुपचाप निकल गया"),
    ("Bright red blood began to flow from his nose after heatstroke", "लू लगने के कारण उसकी नाक से लाल खून बहने लगा"),
    ("The furious stallion flared its nostrils before galloping away", "क्रोधित घोड़े ने दौड़ने से पहले अपनी नाक फड़फड़ाई"),
    ("The determined runner looked straight in the line of her nose", "दृढ़निश्चयी धाविका अपनी नाक की सीध में देखते हुए दौड़ी"),
    ("The sweet scent of fragrant sandalwood filled the nostrils of devotees", "सुगंधित चंदन की महक ने श्रद्धालुओं की नाक को आनंदित किया"),
    ("The remorseful servant apologized on his knees rubbing his nose", "पश्चाताप करते हुए नौकर ने नाक रगड़कर अपने अपराध की माफ़ी माँगी"),
    ("The village girl lost her precious silver nose jewel in the river", "गाँव की किशोरी ने नदी में अपनी प्यारी नाक की नथ खो दी"),
    ("Dense smoke from the burning furnace choked the nostrils of workers", "जलती भट्टी के घने धुएँ ने मजदूरों की नाक में जलन भर दी"),
    ("Hot anger did not stay long on the nose of the gentle saint", "शांत साधु की नाक पर क्रोध कभी देर तक नहीं ठहरता था"),
    ("The victorious general walked through the streets holding his nose high", "विजयी सेनापति अपनी नाक ऊँची करके नगर के मार्ग पर चला"),
    ("The reckless fall broke the delicate bone of his nose", "असावधानी से गिरने के कारण उसकी नाक की पतली हड्डी टूट गई"),
    ("The pungent smell of crushed mustard stung the nose of the cook", "पिसी हुई राई की तीखी गंध ने रसोइए की नाक में तीखापन भर दिया"),
    ("The little girl held her nose and drank the bitter herbal tonic", "छोटी बच्ची ने नाक बंद करके कड़वा काढ़ा पी लिया"),
    ("The tired yogi breathed deeply and calmly through his nose", "थके हुए योगी ने अपनी नाक से गहरी और शांत सांस ली"),
    ("Fright made everything turn completely dark before his nose", "तीव्र भय के कारण उसकी नाक के आगे घोर अंधकार छा गया"),
    ("Small drops of sweat beaded upon the nose of the hardworking blacksmith", "परिश्रमी लोहार की नाक पर पसीने की नन्हीं बूँदें छलक आईं"),
    ("The constant nagging caused extreme annoyance in his nose", "लगातार टोकाटोकी से उसके नाक में असहनीय दम भर गया"),
    ("The righteous man always followed the straight line of his nose", "सच्चे इंसान ने हमेशा अपनी नाक की सीध पकड़कर जीवन बिताया"),
    ("The proud clan vowed never to let the nose of the family fall", "स्वाभिमानी कुल ने अपनी पारिवारिक नाक कभी नीची न होने दी"),
    ("The wise diplomat never showed sudden irritation on his nose", "कुशल राजनयिक ने अपनी नाक पर कभी अचानक गुस्सा न आने दिया"),
    ("The perfume vendor offered fragrant oils pleasing to the royal nose", "इत्र बेचने वाले ने राजा की नाक को भाने वाला सुगंधित तेल दिया"),
    ("The farmer protected the nose of his hard won honor from disgrace", "किसान ने अपनी कठिन कमाई की नाक को अपमान से बचाया"),

    # 186-250: मुँह, जीभ, दाँत, होंठ
    ("The boastful wrestler suffered humiliating defeat and bit the dust", "डींग हाँकने वाले पहलवान को दंगल में मुँह की खानी पड़ी"),
    ("The spoiled boy sulked and puffed his mouth over small trifles", "जिद्दी बालक छोटी छोटी बातों पर अपना मुँह फुला लेता था"),
    ("Fresh hot sweets made delicious water rise into every mouth", "गरमा गरम मिठाइयाँ देखकर हर किसी के मुँह में पानी आ गया"),
    ("The disgraced gambler hid his face in deep shame after defeat", "पराजित जुआरी अपमान के कारण सबसे अपना मुँह छिपाने लगा"),
    ("It is great wisdom to keep mouth shut during angry quarrels", "क्रोध भरे विवाद में अपना मुँह बंद रखना ही सच्ची समझदारी है"),
    ("The clever advocate gave a crushing retort to the false claim", "कुशल वकील ने झूठे आरोप का मुँह तोड़ जवाब दिया"),
    ("Fear placed a heavy lock upon the mouth of the silent witness", "भय के कारण मूक गवाह के मुँह पर ताला लग गया"),
    ("The dejected candidate hung his mouth after failing the interview", "असफल उम्मीदवार साक्षात्कार के बाद उदास होकर मुँह लटकाए बैठा रहा"),
    ("The selfish fair weather friend turned his face away during crisis", "स्वार्थी मित्र ने विपत्ति आते ही मुँह फेर लिया"),
    ("The courageous elder opened his mouth to defend the oppressed peasants", "साहसी बुज़ुर्ग ने पीड़ित किसानों के पक्ष में अपना मुँह खोला"),
    ("Sweet honey drooled from the mouth of the greedy bear", "लालची भालू के मुँह से मीठे शहद की लार टपकने लगी"),
    ("Gentle and sweet flowers dropped from the mouth of the poetess", "विदुषी कवयित्री के मुँह से ज्ञान और प्रेम के फूल झड़ते थे"),
    ("The deceitful hypocrite had sweet words on mouth and dagger in heart", "कपटपूर्ण ढोंगी के मुँह में राम और बगल में छुरी थी"),
    ("The devoted disciple received his longed wish from the holy guru", "सच्चे शिष्य को कृपालु गुरु से मुँह माँगी मुराद मिल गई"),
    ("The fearless critic spoke bitter truths directly to the face of tyrant", "निडर आलोचक ने तानाशाह के मुँह पर कड़वी सच्चाई बोल दी"),
    ("The corrupt traitor blackened his mouth and brought disgrace upon the city", "भ्रष्ट देशद्रोही ने अपने कुकर्मों से अपना मुँह काला कर लिया"),
    ("The bright face of the young bride fell upon hearing the sad parting", "विदाई की बात सुनकर युवा वधू का सुंदर मुँह उतर गया"),
    ("Colors of terror flew from his face when police arrived suddenly", "अचानक पुलिस को देखकर अपराधी के मुँह पर हवाइयाँ उड़ने लगीं"),
    ("Curd seemed frozen in his mouth when asked to explain the mistake", "गलती पूछे जाने पर डरपोक लड़के के मुँह में दही जम गया"),
    ("Wash your mouth if you expect unearned wealth without honest effort", "बिना मेहनत धन पाने की आशा हो तो मुँह धो रखो"),
    ("The helpless orphan kept looking at the faces of passersby for bread", "असहाय अनाथ बालक रोटी के लिए राहगीरों का मुँह ताकता रहा"),
    ("The faithful spy sewed his mouth and revealed no secret under torture", "वफादार गुप्तचर ने अपना मुँह सी लिया और कोई भेद न दिया"),
    ("The naughty monkey made funny faces to amuse the small children", "शरारती बंदर ने छोटे बच्चों को हँसाने के लिए मुँह बनाया"),
    ("Parched thirst dried the mouth of the wanderer in the sandy desert", "रेतीले मरुस्थल में प्यास के मारे पथिक का मुँह सूख गया"),
    ("The aroma of spicy feast made mouth fill with water in excitement", "स्वादिष्ट दावत की सुगंध से सभी का मुँह पानी से भर आया"),
    ("The happy grandfather sweetened the mouth of everyone with fresh sweets", "प्रसन्न दादाजी ने ताज़े लड्डू खिलाकर सबका मुँह मीठा कराया"),
    ("The bitter argument spoiled the taste of food in his mouth", "कड़वे झगड़े ने भोजन के समय उसके मुँह का स्वाद बिगाड़ दिया"),
    ("Wise elders advise that one should not quarrel with foul mouths", "बुज़ुर्ग सिखाते हैं कि ओछे लोगों के मुँह नहीं लगना चाहिए"),
    ("The talkative merchant kept running his mouth throughout the meeting", "बातूनी व्यापारी पूरी बैठक के दौरान लगातार अपना मुँह चलाता रहा"),
    ("The mother held the mouth of her child before he blurted the secret", "भेद खुलने से पहले ही माँ ने अपने चंचल बालक का मुँह पकड़ लिया"),
    ("The goddess of speech sat upon her tongue when the prophecy came true", "भविष्यवाणी सच होने पर लगा कि उसकी जीभ पर सरस्वती बैठी थीं"),
    ("The modest speaker bit his tongue upon uttering an unintended word", "अनजाने में कड़वा शब्द निकलते ही विनम्र वक्ता ने अपनी जीभ काट ली"),
    ("Speak with a restrained tongue before the assembly of scholars", "विद्वानों की सभा में अपनी जीभ संभालकर बोलना आवश्यक होता है"),
    ("His bold tongue ran without hesitation during the royal debate", "शाही शास्त्रार्थ में उस प्रतिभाशाली युवक की जीभ बिना रुके चली"),
    ("A loose tongue without reins brings ruin to peaceful homes", "लगाम के बिना बेकाबू जीभ सुखद परिवारों को तबाह कर देती है"),
    ("The hungry tiger licked its tongue anticipating the fat deer", "भूखे बाघ ने मोटे हिरण को देखकर अपनी जीभ लपलपाई"),
    ("Hot ginger tea scalded the tender tongue of the hasty drinker", "गरम अदरक वाली चाय से उतावले व्यक्ति की कोमल जीभ जल गई"),
    ("Simple home cooked food gave true delight to the tired tongue", "घर के सादे भोजन ने थकी हुई जीभ को सच्चा स्वाद दिया"),
    ("The forgotten ancient name was lingering right upon his tongue", "भूला हुआ पुराना नाम ठीक उसकी जीभ की नोक पर था"),
    ("A sudden slip of the tongue created confusion in the court", "अचानक जीभ फिसलने से राजदरबार में भारी भ्रम पैदा हो गया"),
    ("The fierce warrior threatened to pull out the tongue of insolent spies", "क्रोधित योद्धा ने ढीठ जासूसों की जीभ खींच लेने की धमकी दी"),
    ("Nervous stage fright made the tongue of the young actor stutter", "मंच के भय से नए अभिनेता की जीभ घबराहट में ऐंठने लगी"),
    ("The sharp tongue of the envious neighbour wounded many innocent hearts", "ईर्ष्यालु पड़ोसी की तीखी जीभ ने कई मासूम दिलों को ठेस पहुँचाई"),
    ("A prick of thorn troubled his swollen tongue after eating wild berry", "जंगली फल खाने के बाद उसकी सूजी जीभ में काँटा चुभने लगा"),
    ("Folklore says that a black mole upon the tongue speaks prophetic truth", "लोकमान्यता है कि जीभ पर काला तिल होने से वचन सच होता है"),
    ("The brave defense made the teeth of the enemy army turn sour", "बहादुर सेना ने आक्रमणकारी शत्रु के दाँत पूरी तरह खट्टे कर दिए"),
    ("The furious giant gnashed his teeth in terrible rage", "भीषण क्रोध में आकर विशालकाय राक्षस अपने दाँत पीसने लगा"),
    ("The audience pressed finger under teeth in astonishment at the magic", "जादू का कमाल देखकर दर्शकों ने दाँतों तले उँगली दबा ली"),
    ("The freezing mountain cold made their teeth chatter through the night", "कड़ाके की बर्फीली ठंड से रात भर उनके दाँत किटकिटाते रहे"),
    ("The shameless jester grinned his teeth despite repeated reprimands", "बार बार डांट खाने पर भी निर्लज्ज विदूषक दाँत दिखाता रहा"),
    ("The hungry hound sank its sharp teeth into the meat bone", "भूखे शिकारी कुत्ते ने मांस की हड्डी पर अपने दाँत गड़ा दिए"),
    ("The boxer broke the loose tooth of his boastful challenger", "मुक्केबाज़ ने डींग मारने वाले प्रतिद्वंद्वी का हिलता दाँत तोड़ दिया"),
    ("The clumsy porter smiled sheepishly showing teeth after dropping bundle", "गठरी गिराने के बाद अनाड़ी कुली शर्मिंदा होकर दाँत निपोरने लगा"),
    ("The milk tooth of the growing boy was shaking before falling out", "बढ़ते हुए बालक का दूध का दाँत गिरने से पहले हिल रहा था"),
    ("A hard grain of rice got stuck between his back teeth", "कठोर चावल का दाना उसके पीछे वाले दाँतों में फँस गया"),
    ("The faithful captive sealed his lips and revealed not a word", "स्वाभिमानी बंदी ने अपने होंठ सिल लिए और एक शब्द न बोला"),
    ("The anxious student bit her lip awaiting the exam results", "परीक्षा परिणाम की प्रतीक्षा में चिंतित छात्रा ने अपना होंठ काटा"),
    ("Impatient frustration made the driver chew his lip in the traffic jam", "भीड़ में फँसकर अधीर चालक गुस्से से अपना होंठ चबाने लगा"),
    ("A gentle smile of serene peace played upon the lips of the sage", "भगवान बुद्ध के होंठों पर शांत शांति की कोमल मुस्कान खेलती रही"),
    ("Dry desert winds caused the lips of the nomads to crack", "रेगिस्तान की शुष्क हवाओं से खानाबदोश लोगों के होंठ सूखने लगे"),
    ("Suppressed indignation made the lips of the honest citizen twitch", "दबे हुए गुस्से से ईमानदार नागरिक के होंठ फड़कने लगे"),
    ("The confidential confession reached the lips but stopped before speaking", "महत्वपूर्ण बात होंठों तक आकर रुक गई और वह कुछ न बोला"),
    ("The timid girl parted her lips softly to sing the prayer", "संकोची बालिका ने प्रार्थना गाने के लिए धीरे से होंठ खोले"),
    ("The astonished spectators stood with open mouth watching the meteor fall", "उल्कापिंड को गिरते देखकर चकित दर्शक मुँह बाए खड़े रह गए"),
    ("The caring mother fed a nourishing morsel into the child mouth", "स्नेहमयी माँ ने अपने नन्हें शिशु के मुँह में पौष्टिक निवाला डाला"),
]

# Set up alignment derivation
import importlib.util
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

# Extend ga.DICT with batch-specific vocabulary mappings for high-quality alignments
ANATOMY_DICT = {
    'आँख': ['eye', 'eyes', 'glance'], 'आँखें': ['eyes', 'gaze'], 'आँखों': ['eyes', 'sight'],
    'नज़र': ['sight', 'vision', 'eye', 'glance', 'surveillance'], 'नज़रें': ['eyes', 'glances'],
    'कान': ['ear', 'ears'], 'कानों': ['ears'],
    'नाक': ['nose', 'nostril'], 'नथ': ['nose', 'ring'],
    'मुँह': ['mouth', 'face'], 'जीभ': ['tongue'], 'दाँत': ['tooth', 'teeth'], 'दाँतों': ['teeth'],
    'होंठ': ['lip', 'lips'], 'होंठों': ['lips'],
    'छात्र': ['student'], 'इतिहास': ['history'], 'सच्चाई': ['truth'], 'अज्ञानता': ['ignorance'],
    'पर्दा': ['veil', 'blindfold'], 'माँ': ['mother'], 'बेटे': ['son'], 'अतिथि': ['guest'],
    'ग्रामीणों': ['villagers'], 'अधिकारी': ['officer'], 'गाँव': ['village'], 'यात्री': ['traveller'],
    'लड़का': ['boy'], 'स्वार्थ': ['selfishness'], 'शत्रु': ['enemy'], 'नौकर': ['servant'],
    'कहानी': ['story'], 'राजकुमार': ['prince'], 'राजा': ['king'], 'चोर': ['thief'],
    'पिता': ['father'], 'रात': ['night'], 'सैनिकों': ['soldiers'], 'नाव': ['boat'],
    'नागरिकों': ['citizens'], 'बच्चों': ['children'], 'बालक': ['boy', 'child'],
    'यात्रियों': ['travelers'], 'मालिक': ['master'], 'किसान': ['farmer'], 'मित्रों': ['friends'],
    'परीक्षा': ['exam'], 'पहरेदार': ['guard'], 'भीड़': ['crowd'], 'मंदिर': ['temple'],
    'गवाह': ['witness'], 'व्यापारी': ['merchant'], 'भिखारी': ['beggar'], 'युवक': ['youth'],
    'मित्र': ['friend'], 'गिद्ध': ['vulture'], 'मांस': ['meat'], 'खबर': ['news'],
    'व्यवहार': ['behavior'], 'दादी': ['grandmother'], 'न्यायाधीश': ['judge'], 'नेता': ['leader'],
    'कलाकार': ['artist'], 'गद्दार': ['traitor'], 'चौकीदार': ['watchman'], 'बुज़ुर्ग': ['elder'],
    'पड़ोसी': ['neighbor'], 'शिकारी': ['hunter'], 'जंगल': ['jungle'], 'वैज्ञानिक': ['scientist'],
    'घाटी': ['valley'], 'चिकित्सक': ['doctor'], 'महल': ['palace'], 'चील': ['eagle'],
    'मछली': ['fish'], 'सिपाही': ['soldier'], 'मजदूरों': ['laborers'], 'जनता': ['public'],
    'नेताओं': ['leaders'], 'दलाल': ['broker'], 'भक्ति': ['devotion'], 'कवि': ['poet'],
    'खिलाड़ी': ['winner', 'player'], 'स्वामी': ['master'], 'जल': ['water'], 'सूर्योदय': ['sunrise'],
    'मुंशी': ['clerk'], 'वादा': ['promised'], 'मंत्री': ['minister'], 'सेनापति': ['general'],
    'हिरण': ['deer'], 'आवाज़': ['sound'], 'लड़के': ['boy'], 'अफसर': ['officer'],
    'शिष्य': ['disciple'], 'ऋषि': ['sage'], 'मार्गदर्शक': ['guide'], 'ज़मींदार': ['landlord'],
    'उस्ताद': ['master'], 'कारीगर': ['apprentice'], 'सहयात्री': ['passenger'], 'बाँसुरी': ['flute'],
    'सज्जन': ['righteous'], 'गुरु': ['guru'], 'पशुओं': ['animals'], 'हाकिम': ['judge'],
    'भेड़िया': ['wolf'], 'विस्फोट': ['explosion'], 'पर्वतारोहियों': ['climbers'], 'घंटों': ['bells'],
    'संतरी': ['guard'], 'महिला': ['woman'], 'अध्यापक': ['teacher'], 'वक्ता': ['orator'],
    'झरने': ['waterfall'], 'यात्रियों': ['travelers'], 'गुप्तचर': ['spy'], 'बहन': ['sister'],
    'भाई': ['brother'], 'घोड़े': ['horse'], 'कुत्ते': ['watchdog'], 'पहियों': ['wheels'],
    'लोहार': ['blacksmith'], 'परिवार': ['family'], 'सपूत': ['son'], 'बंदरों': ['monkeys'],
    'जासूस': ['detective'], 'बेटी': ['daughter'], 'दुल्हन': ['bride'], 'मधुमक्खी': ['bee'],
    'नाली': ['sewer'], 'कुकर्मों': ['deeds'], 'वकील': ['advocate'], 'पहलवान': ['wrestler'],
    'भालू': ['bear'], 'कवयित्री': ['poetess'], 'जुआरी': ['gambler'], 'बुद्ध': ['buddha'],
}
ga.DICT.update(ANATOMY_DICT)

def validate_all(corpus_pairs):
    DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
    ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')

    # Load existing hi sentences
    existing_hi = {}
    for p in sorted((ROOT / "data").glob("phrases*.json")):
        if p.name == "phrases25.json":
            continue
        data = json.load(open(p))
        for item in data:
            existing_hi[item["hi"]] = (p.name, item["id"])

    errors = []
    seen_hi = set()
    out = []

    if len(corpus_pairs) != 250:
        errors.append(f"Expected 250 pairs, got {len(corpus_pairs)}")

    for idx, (en, hi) in enumerate(corpus_pairs, start=1):
        sid = f"p25s{idx:03d}"
        if not ASC.match(en):
            errors.append(f"{sid}: English failed regex: {en!r}")
        if not DEV.match(hi):
            errors.append(f"{sid}: Hindi failed regex: {hi!r}")
        if hi in seen_hi:
            errors.append(f"{sid}: Duplicate Hindi within batch: {hi}")
        seen_hi.add(hi)
        if hi in existing_hi:
            orig_f, orig_id = existing_hi[hi]
            errors.append(f"{sid}: Duplicate Hindi exists in {orig_f} ({orig_id}): {hi}")

        align = ga.derive(en, hi)
        toks = align.split()
        hiw = hi.split()
        enw = en.split()

        if len(toks) != len(hiw):
            errors.append(f"{sid}: Align length {len(toks)} != hi length {len(hiw)}")
        for t in toks:
            for part in re.split(r'[-,]', t):
                if not (part.isdigit() and int(part) < len(enw)):
                    errors.append(f"{sid}: Invalid align token {t!r} for en len {len(enw)}")

        out.append({
            "id": sid,
            "en": en,
            "hi": hi,
            "align": align
        })

    return out, errors

def main():
    print(f"Validating {len(PAIRS)} sentence pairs for Batch ID-01...")
    out, errors = validate_all(PAIRS)
    if errors:
        print(f"FOUND {len(errors)} ERRORS:")
        for e in errors[:20]:
            print("  ", e)
        sys.exit(1)

    out_file = ROOT / "data" / "phrases25.json"
    out_file.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"Successfully generated {out_file} with {len(out)} sentences.")

    # Update manifest.json
    manifest_file = ROOT / "data" / "manifest.json"
    manifest = json.load(open(manifest_file))
    manifest["files"] = [f for f in manifest["files"] if f["file"] != "data/phrases25.json"]
    manifest["files"].append({
        "file": "data/phrases25.json",
        "count": len(out)
    })
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated {manifest_file} with data/phrases25.json (count: {len(out)}).")

if __name__ == "__main__":
    main()
