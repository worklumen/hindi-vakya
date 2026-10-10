#!/usr/bin/env python3
"""Batch ID-03: Fauna & Animals (घोड़ा, ऊँट, बिल्ली, गधा, बंदर, साँप, चींटी, चिड़िया, शेर, कुत्ता, मछली, उल्लू).

Generates data/phrases27.json (250 sentences) with explicit AI semantic alignments.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# 250 bilingual pairs for Fauna & Animals
PAIRS = [
    # 1-40: घोड़ा, गधा, खच्चर (Horses, donkeys, mules)
    ("The tired farmer slept soundly as if selling off his horses", "थका हुआ किसान निश्चिंत होकर घोड़े बेचकर सो गया"),
    ("The cunning flatterer called the donkey father to get his work done", "काम निकालने के लिए धूर्त चापलूस ने गधे को बाप बनाया"),
    ("The impatient rider always rode upon a horse in immense hurry", "अधीर घुड़सवार हमेशा जल्दी में घोड़े पर सवार रहता था"),
    ("The strict king tightened the rein upon the rebellious chieftains", "कड़े राजा ने विद्रोही सामंतों की ढीली लगाम कस दी"),
    ("The skillful general won the field after a hard fought battle", "कुशल सेनापति ने कठिन युद्ध के बाद मैदान मार लिया"),
    ("The spirited stallion galloped fast across the wide green valley", "उत्साही घोड़ा विशाल हरी घाटी में सरपट दौड़ा"),
    ("The stubborn mule stopped near the cliff and refused to budge", "हठी खच्चर चट्टान के पास रुक गया और आगे न बढ़ा"),
    ("The careless servant left the horse reins loose on the highway", "लापरवाह सेवक ने राजमार्ग पर घोड़े की लगाम ढीली छोड़ दी"),
    ("The poor potter loaded heavy bags of clay upon his donkey", "गरीब कुम्हार ने अपने गधे पर मिट्टी के भारी बोरे लादे"),
    ("The brave cavalier urged his horse into the thick of battle", "साहसी घुड़सवार ने अपने घोड़े को भीषण युद्ध में आगे बढ़ाया"),
    ("The old donkey carried wet clothes of the washerman to river", "बूढ़ा गधा धोबी के गीले कपड़े नदी तक ले गया"),
    ("The runaway horse leaped across the stone wall with great ease", "भागे हुए घोड़े ने पत्थर की दीवार को आसानी से लांघ लिया"),
    ("The proud noble bought an Arabian mare from the famous fair", "अमीर रईस ने प्रसिद्ध मेले से अरबी घोड़ी खरीदी"),
    ("The weary donkey rested under the banyan shade during hot noon", "थके गधे ने दोपहरी में बरगद की छाया में विश्राम किया"),
    ("The swift horse carried the royal message to the distant fort", "तेज़ घोड़े ने शाही संदेश दूर के किले तक पहुँचाया"),
    ("The foolish servant treated the precious jewel like fodder for donkey", "मूर्ख सेवक ने अनमोल रत्न को गधे की घास समझ लिया"),
    ("The royal stable housed a hundred magnificent white horses", "शाही अस्तबल में सौ भव्य सफेद घोड़े रखे गए थे"),
    ("The young colt kicked its hind legs playfully in the meadow", "छोटे बछेड़े ने मैदान में चंचलता से अपनी पिछली टांगें चलाईं"),
    ("The kind veterinarian healed the sprained ankle of the race horse", "दयालु पशु चिकित्सक ने दौड़ के घोड़े का मोच लगा पैर ठीक किया"),
    ("The tired soldier tied his horse to the wooden railing outside", "थके सैनिक ने अपने घोड़े को बाहर लकड़ी की बाड़ से बाँध दिया"),
    ("The hungry donkey grazed peacefully upon the green grass of hill", "भूखा गधा पहाड़ी की हरी घास पर शांति से चरता रहा"),
    ("The wild horses ran freely across the endless sandy plains", "जंगली घोड़े अनंत रेतीले मैदानों में आज़ादी से दौड़े"),
    ("The stubborn donkey sat in the middle of road blocking traffic", "हठी गधा सड़क के बीच बैठकर रास्ता रोकने लगा"),
    ("The skilled jockey guided the spirited mare to victory in race", "कुशल सवार ने चंचल घोड़ी को दौड़ में जीत की ओर बढ़ाया"),
    ("The brave commander rode a black horse into the frontline", "बहादुर सेनापति काले घोड़े पर सवार होकर आगे बढ़ा"),
    ("The frightened donkey brayed loudly hearing the distant thunder", "बादलों की गर्जना सुनकर डरे हुए गधे ने ज़ोर से ढेंचू ढेंचू किया"),
    ("The loyal horse did not leave the side of its wounded master", "वफादार घोड़े ने अपने घायल स्वामी का साथ नहीं छोड़ा"),
    ("The old carriage was drawn by two sturdy brown horses", "पुराना रथ दो मज़बूत भूरे घोड़ों द्वारा खींचा जाता था"),
    ("The weary traveler dismounted from his horse at the roadside inn", "थके मुसाफिर ने सराय के पास अपने घोड़े से उतरकर विश्राम किया"),
    ("The kind farmer gave fresh oats and clean water to his horse", "दयालु किसान ने अपने घोड़े को ताज़ा दाना और स्वच्छ पानी दिया"),
    ("The agile horse jumped over the wide muddy ditch without effort", "फुर्तीले घोड़े ने बिना प्रयास के चौड़े कीचड़ भरे नाले को पार किया"),
    ("The stubborn mule resisted every pull of the leather rope", "हठी खच्चर ने चमड़े की रस्सी के हर खिंचाव का विरोध किया"),
    ("The royal guard patted the neck of his trusted steed warmly", "शाही रक्षक ने अपने विश्वस्त घोड़े की गर्दन प्यार से थपथपाई"),
    ("The energetic colt sprinted across the pasture alongside its mother", "उत्साही बछेड़ा अपनी माँ के साथ चारागाह में तेज़ी से दौड़ा"),
    ("The poor peasant walked beside his donkey carrying dry firewood", "गरीब किसान सूखी लकड़ियाँ लादे अपने गधे के साथ चला"),
    ("The magnificent white mare stood proudly inside the palace courtyard", "भव्य सफेद घोड़ी महल के आँगन में गर्व से खड़ी रही"),
    ("The noisy donkey woke up the entire sleepy village at dawn", "शोर मचाते गधे ने सुबह सवेरे पूरे सोते हुए गाँव को जगा दिया"),
    ("The tired cavalry rested their horses beside the flowing stream", "थकी सेना ने बहती नदी के किनारे अपने घोड़ों को विश्राम दिया"),
    ("The blacksmith fitted new iron shoes to the hooves of horse", "लोहार ने घोड़े के खुरों में लोहे की नई नाल लगाई"),
    ("The brave scout galloped through the night carrying news of attack", "बहादुर दूत ने हमले की खबर लेकर रात भर घोड़ा दौड़ाया"),

    # 41-80: ऊँट, हाथी, गाय, बैल, भैंस (Camels, elephants, cattle, buffaloes)
    ("A single spoonful was like a cumin seed in the mouth of camel", "विशाल दावत में इतना सा भोजन ऊँट के मुँह में जीरा था"),
    ("The crowd waited tensely to see which side the camel sits", "सब बेसब्री से देखने लगे कि ऊँट किस करवट बैठता है"),
    ("Might is right was the brutal law of the ancient jungle", "जंगल का क्रूर नियम था कि जिसकी लाठी उसकी भैंस"),
    ("The hardworking clerk toiled like an oil mill bullock without rest", "मेहनती मुंशी कोल्हू के बैल की तरह बिना रुके काम करता रहा"),
    ("The double dealer had different teeth for showing and for eating", "धूर्त व्यक्ति के हाथी के दाँत खाने के और दिखाने के और थे"),
    ("The reckless fool invited trouble upon himself without any reason", "लापरवाह युवक ने आ बैल मुझे मार वाली मुसीबत मोल ली"),
    ("Even a kick from a milch cow is accepted with smiling patience", "दूध देने वाली गाय की लात भी लोग खुशी से सह लेते हैं"),
    ("The desert caravan moved slowly with twenty heavily loaded camels", "रेगिस्तानी काफिला बीस लदे हुए ऊँटों के साथ धीरे धीरे बढ़ा"),
    ("The giant temple elephant bowed before the deity during festival", "विशाल मंदिर का हाथी उत्सव में देवता के आगे झुक गया"),
    ("The faithful bullock pulled the heavy wooden plow through clay", "वफादार बैल ने गीली मिट्टी में भारी लकड़ी का हल खींचा"),
    ("The gentle cow gave sweet milk every morning to the village family", "सीधी गाय हर सुबह गाँव के परिवार को मीठा दूध देती थी"),
    ("The stray buffalo wallowed with delight in the muddy village pond", "भैंस गाँव के कीचड़ भरे तालाब में आनंद से लोटती रही"),
    ("The angry bull snorted and pawed the dry dirt with fury", "क्रोधित बैल ने फुंकार मारकर अपने खुरों से सूखी धूल उड़ाई"),
    ("The king rode a majestic elephant covered with embroidered velvet", "राजा कशीदाकारी वाले मखमल से सजे भव्य हाथी पर सवार हुआ"),
    ("The thirsty camel drank water after walking across the arid dunes", "प्यासे ऊँट ने सूखे टीलों को पार करके खूब पानी पिया"),
    ("The little calf gamboled with pure joy around its mother cow", "छोटा बछड़ा अपनी गऊ माता के चारों ओर खुशी से उछलकूद करने लगा"),
    ("The massive elephant cleared the fallen timber from the jungle track", "विशाल हाथी ने जंगल के रास्ते से गिरे हुए लट्ठे हटाए"),
    ("The patient camel knelt down on the hot sand to receive baggage", "धैर्यवान ऊँट सामान लादने के लिए गरम रेत पर बैठ गया"),
    ("The fierce bull chased the red clad intruder out of the meadow", "खूँखार सांड ने लाल कपड़े पहने घुसपैठिए को मैदान से खदेड़ दिया"),
    ("The holy cow rested peacefully outside the village Shiva temple", "गौ माता गाँव के शिव मंदिर के बाहर शांति से बैठी रही"),
    ("The wild buffalo defended its young calf against the prowling tiger", "जंगली भैंसे ने घात लगाए बाघ से अपने छोटे बछड़े की रक्षा की"),
    ("The royal mahout guided the huge elephant with an iron goad", "शाही महावत ने लोहे के अंकुश से विशाल हाथी को दिशा दिखाई"),
    ("The camel train crossed the scorching desert under the starry sky", "ऊँटों का काफिला तारों भरी रात में तपते रेगिस्तान से गुज़रा"),
    ("The gentle cow chewed the cud under the cool shade of neem", "सीधी गाय नीम की ठंडी छाया में आराम से जुगाली करती रही"),
    ("The strong bullocks carried golden grain sheaves to the threshing floor", "मज़बूत बैलों ने सुनहरी फसल के गट्ठर खलिहान तक पहुँचाए"),
    ("The wild elephant herd trumpeted loudly near the mountain river", "जंगली हाथियों के झुंड ने पहाड़ी नदी के पास चिंघाड़ लगाई"),
    ("The tall camel stretched its long neck to pluck thorny acacia leaves", "लंबे ऊँट ने बबूल की कांटेदार पत्तियाँ खाने के लिए गर्दन बढ़ाई"),
    ("The loving mother compared her innocent child to a holy cow", "स्नेहमयी माँ ने अपने सीधे बालक की तुलना गौ माता से की"),
    ("The muddy water buffalo submerged itself to escape the humid heat", "भैंस उमस भरी गर्मी से बचने के लिए पानी में डूबकर बैठ गई"),
    ("The elderly farmer stroked the horns of his loyal companion bullock", "बूढ़े किसान ने अपने वफादार साथी बैल के सींगों को सहलाया"),
    ("The decorated elephant led the magnificent royal procession with dignity", "सजे हुए हाथी ने शान से शाही शोभायात्रा की अगुवाई की"),
    ("The baby camel followed the footsteps of its mother across sand", "ऊँट का छोटा बच्चा रेत पर अपनी माँ के पदचिह्नों पर चला"),
    ("The gentle cow licked the head of her newborn calf with affection", "दयालु गाय ने अपने नवजात बछड़े के सिर को प्यार से चाटा"),
    ("The raging bull broke through the wooden fence into the garden", "मस्त सांड ने लकड़ी की बाड़ तोड़कर बगीचे में उपद्रव मचाया"),
    ("The patient camel carried heavy loads across hundred miles of desert", "सहनशील ऊँट ने सौ मील लंबे रेगिस्तान में भारी बोझ ढोया"),
    ("The temple elephant blessed the pilgrims by placing its trunk gently", "मंदिर के हाथी ने अपनी सूंड रखकर श्रद्धालुओं को आशीर्वाद दिया"),
    ("The hardworking pair of bullocks ploughed the fertile field before rain", "बैलों की मेहनती जोड़ी ने बारिश से पहले उपजाऊ खेत को जोता"),
    ("The herd of black buffaloes grazed beside the shallow swamp waters", "काली भैंसों का झुंड दलदल के उथले पानी के पास चरता रहा"),
    ("The wild bull challenged the rival male with deep guttural roars", "जंगली सांड ने भारी गर्जना के साथ विरोधी नर को ललकारा"),
    ("The friendly cow recognized the familiar voice of the milkmaid", "सीधी गाय ने ग्वालिन की जानी पहचानी आवाज़ तुरंत पहचान ली"),

    # 81-125: बिल्ली, कुत्ता, लोमड़ी, भेड़िया (Cats, dogs, foxes, wolves)
    ("The naughty boy turned into a drenched cat after the scolding", "कड़ी डांट सुनकर शरारती बालक भीगी बिल्ली बन गया"),
    ("The lucky fellow got an unexpected feast like a broken pot for cat", "भाग्यशाली युवक के आगे बिल्ली के भागों छींका टूट पड़ा"),
    ("The fearful mice held a meeting to bell the dangerous cat", "डरपोक चूहों ने खतरनाक बिल्ली के गले में घंटी बाँधने की सोची"),
    ("The double agent belonged nowhere like the dog of the washerman", "दोगला व्यक्ति धोबी के कुत्ते की तरह न घर का रहा न घाट का"),
    ("The crooked nature of the wicked man never straightened like dog tail", "कुत्ते की दुम की तरह दुष्ट व्यक्ति का स्वभाव कभी सीधा न हुआ"),
    ("The hungry hound grabbed a dry crust of bread from the gutter", "भूखे शिकारी कुत्ते ने नाली के पास से सूखी रोटी झपट ली"),
    ("The cunning fox declared the sweet grapes sour after failing to reach", "पहुँच न पाने पर चतुर लोमड़ी ने अंगूर खट्टे हैं कहकर पीछा छुड़ाया"),
    ("The hungry wolf disguised in sheep clothing entered the peaceful flock", "भेड़ की खाल में छिपे भूखे भेड़िए ने शांत रेवड़ में प्रवेश किया"),
    ("The watchful dog barked furiously at the shadow of the thief", "चौकस कुत्ते ने चोर की परछाईं पर ज़ोर से भौंकना शुरू किया"),
    ("The pampered Persian cat purred softly upon the velvet cushion", "लाड़ली बिल्ली मखमली गद्दे पर बैठकर धीरे धीरे म्याऊँ करने लगी"),
    ("The deceitful flatterer was known for the sly tricks of a fox", "धूर्त चापलूस लोमड़ी जैसी चालाकियों के लिए पूरे शहर में कुख्यात था"),
    ("The ferocious wolf pack howled together under the cold full moon", "खूँखार भेड़ियों के झुंड ने पूर्णिमा की रात एक साथ हावभाव किया"),
    ("The stray dog wagged its tail happily upon getting a warm roti", "आवारा कुत्ते ने गरम रोटी पाकर खुशी से अपनी पूँछ हिलाई"),
    ("The nimble cat caught the scurrying mouse with a swift pounce", "फुर्तीली बिल्ली ने तेज़ झपट्टे से भागते हुए चूहे को दबोच लिया"),
    ("The sly fox tricked the vain crow into dropping the cheese piece", "चालाक लोमड़ी ने घमंडी कौए को फुसलाकर पनीर का टुकड़ा गिरा दिया"),
    ("The lonely wolf prowled silently through the snow covered pine forest", "अकेला भेड़िया बर्फ़ से ढके चीड़ के जंगल में चुपचाप घूमता रहा"),
    ("The loyal watchdog guarded the farmyard against thieves and wild beasts", "वफादार कुत्ते ने चोरों और जंगली जानवरों से खेत की रखवाली की"),
    ("The playful kitten chased a round ball of woolen yarn everywhere", "चंचल बिल्ली के बच्चे ने ऊन के गोल गोले का पीछा किया"),
    ("The greedy fox fell into the indigo vat and changed its color", "लालची लोमड़ी नील के हौज में गिरकर अपना रंग बदल बैठी"),
    ("The fierce wolf bared its sharp white fangs at the hunters", "खूँखार भेड़िए ने शिकारियों को अपने नुकीले सफेद दाँत दिखाए"),
    ("The wounded dog whimpered softly in the cold corner of street", "घायल कुत्ता गली के ठंडे कोने में बैठकर धीमे धीमे कराहता रहा"),
    ("The white cat drank the spilled milk quietly without making sound", "सफेद बिल्ली ने बिना आवाज़ किए गिरा हुआ सारा दूध पी लिया"),
    ("The cunning fox escaped through the narrow hedge leaving no trace", "चालाक लोमड़ी घनी झाड़ियों से बिना कोई सुराग छोड़े भाग निकली"),
    ("The pack of gray wolves hunted the wounded reindeer across tundra", "सलेटी भेड़ियों के झुंड ने घायल हिरण का दूर तक पीछा किया"),
    ("The faithful dog followed its master to the end of the world", "वफादार कुत्ता अपने स्वामी के पीछे दुनिया के अंत तक चला"),
    ("The sleepy cat stretched its claws upon the rough wooden pillar", "अलसाई बिल्ली ने लकड़ी के खंभे पर अपने पंजे फैलाए"),
    ("The crafty fox pretended to be dead to catch the foolish hen", "मक्कार लोमड़ी ने मूर्ख मुर्गी को पकड़ने के लिए मरने का ढोंग किया"),
    ("The hungry wolf stalked the lonely traveler through the mountain pass", "भूखे भेड़िए ने पहाड़ी दर्रे में अकेले यात्री का पीछा किया"),
    ("The brave hound pinned the vicious burglar to the floor firmly", "बहादुर कुत्ते ने खतरनाक चोर को ज़मीन पर मज़बूती से दबा लिया"),
    ("The clever cat waited patiently near the small mouse hole for hours", "चतुर बिल्ली घंटों चूहे के बिल के पास धीरज से बैठी रही"),
    ("The cowardly fox retreated into its underground den when dogs approached", "कुत्तों के आते ही डरपोक लोमड़ी अपने भूमिगत बिल में छिप गई"),
    ("The savage wolves encircled the burning campfire of the fearful campers", "जंगली भेड़ियों ने डरे हुए यात्रियों के जलते अलाव को घेर लिया"),
    ("The joyful puppy jumped into the arms of the returning child", "खुश पिल्ला लौटते हुए बालक की बाहों में उछलकर चढ़ गया"),
    ("The black cat crossed the path causing superstitious fears in travelers", "काली बिल्ली के रास्ता काटने से अंधविश्वासी यात्री सहम गए"),
    ("The sly fox flattered the foolish goat into jumping down the well", "धूर्त लोमड़ी ने मूर्ख बकरी को कुएँ में कूदने के लिए बहका दिया"),
    ("The starving wolf scavenged for leftover bones in the frozen valley", "भूखा भेड़िया जमी हुई घाटी में बची हड्डियों की तलाश करता रहा"),
    ("The loyal shepherd dog rounded up the wandering sheep before dark", "वफादार चरवाहे के कुत्ते ने शाम होने से पहले भटकी भेड़ें इकट्ठी कीं"),
    ("The curious cat climbed up the tall roof chasing a green cricket", "जिज्ञासु बिल्ली हरे झींगुर का पीछा करते हुए ऊँची छत पर चढ़ गई"),
    ("The cunning fox stole a fat rooster from the village poultry farm", "चालाक लोमड़ी ने गाँव के बाड़े से एक मोटा मुर्गा चुरा लिया"),
    ("The aggressive wolf snarled and defended its rocky den against intruders", "आक्रामक भेड़िए ने गुर्राते हुए चट्टानी मांद की घुसपैठियों से रक्षा की"),
    ("The rescued dog licked the grateful hand of the young savior", "बचाए गए कुत्ते ने प्यार से अपने रक्षक का हाथ चाटा"),
    ("The sleek tabby cat basked under the warm rays of morning sun", "धारीदार बिल्ली सुबह की धूप की गुनगुनी किरणों में सुस्ताती रही"),
    ("The treacherous fox misled the royal hounds into the thorny thicket", "धूर्त लोमड़ी ने शाही शिकारी कुत्तों को काँटेदार झाड़ियों में भटका दिया"),
    ("The timber wolf howled mournfully over the loss of its mate", "जंगली भेड़िए ने अपनी संगिनी के वियोग में दर्दनाक हूक भरी"),
    ("The obedient dog sat quietly waiting for the permission of its trainer", "आज्ञाकारी कुत्ता प्रशिक्षक की अनुमति की प्रतीक्षा में चुपचाप बैठा रहा"),

    # 126-160: बंदर, लंगूर, रीछ/भालू, हिरण (Monkeys, apes, bears, deer)
    ("The crude fool could never appreciate the refined flavor of ginger", "मूर्ख व्यक्ति कभी अदरक के असली स्वाद और महत्व को न समझ सका"),
    ("The empty threat of the coward was like the grimace of monkey", "डरपोक की खोखली धमकी केवल बंदर घुड़की साबित हुई"),
    ("The foolish flatterer sang his own praises like a pampered parrot", "अहंकारी व्यक्ति अपने मुँह मियाँ मिट्ठू बनकर डींगें हाँकता रहा"),
    ("The musk deer searched the forest in vain for the inner scent", "कस्तूरी मृग अपनी ही नाभि की सुगंध पूरे जंगल में ढूंढता रहा"),
    ("The greedy usurer made the poor debtors dance like performing monkeys", "लालची साहूकार ने गरीब कर्ज़दारों को बंदर की तरह नचाया"),
    ("The mischievous monkey snatched spectacles from the nose of the scholar", "शरारती बंदर ने विद्वान की नाक से चश्मा झपट लिया"),
    ("The black faced langur sat majestically upon the temple dome", "काले मुँह वाला लंगूर मंदिर के गुंबद पर शान से बैठा रहा"),
    ("The giant Himalayan bear searched for wild honey inside hollow tree", "विशाल भालू ने खोखले पेड़ के भीतर जंगली शहद की खोज की"),
    ("The graceful spotted deer leaped across the gurgling mountain brook", "सुंदर चित्तीदार हिरण कलकल बहते पहाड़ी नाले को लांघ गया"),
    ("The playful monkeys chattered loudly and shook the mango tree branches", "चंचल बंदरों ने शोर मचाते हुए आम के पेड़ की डालियाँ हिलाईं"),
    ("The clever monkey dropped ripe guavas to confuse the village dogs", "चतुर बंदर ने गाँव के कुत्तों को भटकाने के लिए पके अमरूद गिराए"),
    ("The mother ape held her tiny infant clinging tightly to her chest", "मादा वानर ने अपने छोटे बच्चे को छाती से चिपकाए रखा"),
    ("The lazy brown bear slept throughout the harsh winter in its cave", "सुस्त भूरा भालू कड़ाके की ठंड में अपनी गुफा में सोता रहा"),
    ("The swift golden deer vanished like an illusion into deep forest", "तेज़ सुनहरी हिरण माया की तरह घने जंगल में ओझल हो गया"),
    ("The troop of monkeys raided the vegetable garden of the monastery", "बंदरों के झुंड ने आश्रम के सब्ज़ी के बगीचे पर धावा बोला"),
    ("The elderly baboon warned the troop with sharp alarm barks", "बूढ़े वानर ने चेतावनी भरी आवाज़ से पूरे दल को सावधान किया"),
    ("The shaggy bear caught a slippery salmon with its broad paws", "रोएंदार भालू ने अपने चौड़े पंजों से फिसलती मछली पकड़ ली"),
    ("The gentle doe guided her spotted fawn to the quiet watering hole", "सीधी हिरणी अपने चितकबरे बच्चे को शांत तालाब तक ले गई"),
    ("The naughty monkey mimicked the gestures of the turbaned fruit seller", "नटखट बंदर ने पगड़ी वाले फल विक्रेता की हरकतों की नकल उतारी"),
    ("The wise old langur observed the humans from the ancient banyan branch", "समझदार बूढ़े लंगूर ने प्राचीन बरगद की डाल से मनुष्यों को देखा"),
    ("The angry black bear stood on two hind legs roaring in defense", "क्रोधित काला भालू रक्षा के लिए पिछली टांगों पर खड़ा होकर गरजा"),
    ("The timid gazelle fled into the high grasslands upon spotting tiger", "डरपोक मृग बाघ को देखते ही ऊँची घास में भाग गया"),
    ("The mischievous ape untied the ropes of the docked pleasure boat", "शरारती बंदर ने घाट पर बंधी नाव की रस्सियाँ खोल दीं"),
    ("The hungry bear dug up nutritious roots beneath the damp forest moss", "भूखे भालू ने जंगल की नम काई के नीचे से पौष्टिक जड़ें खोदीं"),
    ("The fleet footed stag showed magnificent antlers against the sunset sky", "चपल हिरण ने ढलते सूरज के आगे अपने भव्य सींग दिखाए"),
    ("The baby monkey swung merrily from the hanging aerial roots of banyan", "छोटा बंदर बरगद की लटकती दाढ़ियों से मजे से झूलने लगा"),
    ("The cunning monkey tricked the two cats and ate all the butter", "चालाक बंदर ने दोनों बिल्लियों को उल्लू बनाकर सारा मक्खन खा लिया"),
    ("The mother bear defended her cubs fiercely against the hungry wolves", "भालू माता ने भूखे भेड़ियों से अपने बच्चों की बहादुरी से रक्षा की"),
    ("The frightened herd of deer scattered in all directions at the gunshot", "बंदूक की आवाज़ सुनते ही हिरणों का झुंड दसों दिशाओं में बिखर गया"),
    ("The aggressive male baboon bared long canine teeth to display dominance", "आक्रामक लंगूर ने अपना प्रभुत्व दिखाने के लिए नुकीले दाँत दिखाए"),
    ("The curious monkey inspected the brass coin before tossing it away", "जिज्ञासु बंदर ने पीतल के सिक्के को देखकर दूर फेंक दिया"),
    ("The massive grizzly bear caught bees while raiding the sweet hive", "विशाल भालू ने मीठे छत्ते पर छापा मारकर मधुमक्खियाँ झटकीं"),
    ("The graceful antelope vaulted over the thorny perimeter with effortless ease", "सुंदर बारहसिंगे ने काँटेदार बाड़ को बड़ी सहजता से लांघ लिया"),
    ("The acrobat trained the performing monkey to salute the audience politely", "मदारी ने करतब दिखाने वाले बंदर को दर्शकों को सलाम करना सिखाया"),
    ("The gentle deer drank sweet morning dew from the broad forest leaves", "शांत हिरण ने जंगल के चौड़े पत्तों से सुबह की मीठी ओस पी"),

    # 161-205: साँप, बिच्छू, मेंढक, मगरमच्छ, मछली (Snakes, scorpions, frogs, reptiles, aquatic)
    ("The false friend turned out to be a venomous snake in sleeve", "जिसे मित्र समझा वह आस्तीन का ज़हरीला साँप साबित हुआ"),
    ("Feeding sweet milk to a poisonous cobra never removes its deadly venom", "ज़हरीले साँप को दूध पिलाने से उसका ज़हर कभी कम नहीं होता"),
    ("The clever diplomat resolved the issue without breaking the staff or snake", "कुशल मध्यस्थ ने लाठी तोड़े बिना और साँप मारे बिना मामला सुलझाया"),
    ("The green eyed neighbor suffered as if a black serpent crawled on liver", "ईर्ष्यालु पड़ोसी के कलेजे पर काला साँप लोटने लगा"),
    ("The weeping hypocrite shed false crocodile tears to deceive the public", "ढोंगी व्यक्ति ने जनता को धोखा देने के लिए मगरमच्छ के आँसू बहाए"),
    ("It is folly to make enmity with crocodile while living in water", "जल में रहकर मगर से बैर करना सबसे बड़ी मूर्खता है"),
    ("The parochial thinker remained a frog in well knowing nothing of world", "संकीर्ण सोच वाला व्यक्ति कुएँ का मेंढक बना रहा"),
    ("The separated lover languished restless like a fish out of water", "वियोगी प्रेमी जल बिन मछली की तरह तड़पता रहा"),
    ("Teaching an expert scholar was like teaching a fish how to swim", "विद्वान को सिखाना मछली के बच्चे को तैरना सिखाने जैसा था"),
    ("The deadly black cobra raised its flared hood in warning hiss", "खतरनाक काले नाग ने फुंकार मारकर अपना फन फैलाया"),
    ("The venomous scorpion hid under the cool stone ready to sting", "ज़हरीला बिच्छू डंक मारने के लिए ठंडे पत्थर के नीचे छिपा रहा"),
    ("The little frog leaped merrily from lily pad to lily pad", "छोटा मेंढक कमल के एक पत्ते से दूसरे पत्ते पर उछला"),
    ("The massive crocodile basked motionless upon the muddy river bank", "विशाल मगरमच्छ नदी के कीचड़ भरे किनारे पर स्थिर लेटा रहा"),
    ("The shimmering silver fish darted swiftly through the crystal clear brook", "चमकती चाँदी जैसी मछली स्वच्छ नाले में तेज़ी से तैरी"),
    ("The charmer played his gourd pipe making the hooded snake sway", "सपेरे ने बीन बजाकर फन फैलाए साँप को झूमने पर मजबूर किया"),
    ("The poisonous scorpion curled its segmented tail over its armored back", "ज़हरीले बिच्छू ने अपनी घुमावदार पूँछ को पीठ के ऊपर उठाया"),
    ("The noisy bullfrogs croaked in unison after the first monsoon shower", "पहली मानसूनी बारिश के बाद मेंढकों ने एक सुर में टर्र टर्र की"),
    ("The stealthy alligator glided beneath the green weed covered marsh waters", "मगरमच्छ जलकुंभी से ढके दलदल के पानी में चुपके से तैरा"),
    ("The golden carp swam circles around the sunken stone fountain", "सुनहरी मछली पत्थर के डूबे हुए फव्वारे के चारों ओर घूमी"),
    ("The snake shed its dry scaly skin among the thorny bushes", "साँप ने काँटेदार झाड़ियों के बीच अपनी पुरानी केंचुली छोड़ दी"),
    ("The sting of the desert scorpion caused burning agony to the barefoot traveler", "रेगिस्तानी बिच्छू के डंक ने नंगे पैर पथिक को तीव्र पीड़ा दी"),
    ("The croaking frogs announced the arrival of the blessed rainy season", "टर्राते मेंढकों ने सुखद वर्षा ऋतु के आगमन की सूचना दी"),
    ("The predatory crocodile snapped its powerful jaws with a loud splash", "शिकारी मगरमच्छ ने ज़ोरदार छपछपाहट के साथ अपने भारी जबड़े भींचे"),
    ("The tiny guppy fish fed upon mosquito larvae in the stagnant puddle", "छोटी मछली ने रुके हुए पानी में मच्छरों के लार्वा को खाया"),
    ("The harmless green grass snake slithered away into the dense shrubbery", "हानिरहित हरी घास का साँप घनी झाड़ियों में रेंगकर गायब हो गया"),
    ("The venomous sting of the red scorpion swelled the worker finger", "लाल बिच्छू के ज़हरीले डंक से मजदूर की उँगली सूज गई"),
    ("The spotted tree frog blended perfectly with the moist green bark", "चित्तीदार मेंढक पेड़ की नम हरी छाल के साथ पूरी तरह घुलमिल गया"),
    ("The armored river crocodile guarded its clutch of eggs buried in sand", "मगरमच्छ ने रेत में दबे अपने अंडों की चौकसी की"),
    ("The colorful school of coral fish glided gracefully through the reef", "रंग बिरंगी मछलियों के दल ने मूंगे की चट्टानों के बीच गोता लगाया"),
    ("The coiled viper struck with blinding lightning speed at the passing rat", "कुंडली मारे साँप ने तेज़ी से गुज़रते चूहे पर बिजली सा वार किया"),
    ("The venomous black scorpion scuttled across the dry kitchen floor at night", "काला बिच्छू रात में रसोई के सूखे फर्श पर तेज़ी से दौड़ा"),
    ("The frog hopped into the deep well to escape the scorching heat", "मेंढक तपती धूप से बचने के लिए गहरे कुएँ में कूद पड़ा"),
    ("The ferocious marsh mugger dragged the heavy timber into deep current", "खूँखार मगरमच्छ ने भारी लट्ठे को गहरे पानी में खींच लिया"),
    ("The speckled trout leaped out of water to catch a flying mayfly", "मछली ने हवा में उड़ते पतंगे को पकड़ने के लिए पानी से छलांग लगाई"),
    ("The serpent swallowed the chicken egg whole without cracking the shell", "साँप ने बिना तोड़े मुर्गी के पूरे अंडे को निगल लिया"),
    ("The mother scorpion carried dozens of tiny translucent babies on back", "बिच्छू माता ने दर्जनों नन्हें पारदर्शी बच्चों को अपनी पीठ पर लादा"),
    ("The chorus of swamp frogs resounded throughout the moonlit tropical jungle", "चाँदनी रात में दलदली मेंढकों की आवाज़ पूरे घने जंगल में गूँज उठी"),
    ("The gigantic salt water crocodile ruled the murky delta without rival", "विशाल खारे पानी का मगरमच्छ बिना किसी प्रतिद्वंद्वी के डेल्टा पर राज करता था"),
    ("The flying fish skimmed across the crests of the ocean waves", "उड़न मछली समुद्र की लहरों के ऊपर दूर तक तैरती रही"),
    ("The venomous kraits hid inside the cracks of the crumbling mud hut", "ज़हरीला करैत कच्ची मिट्टी की झोपड़ी की दरारों में छिपा रहा"),
    ("The sting of the yellow scorpion was treated with wild medicinal herbs", "पीले बिच्छू के डंक का इलाज जंगली औषधीय जड़ी बूटियों से किया गया"),
    ("The tree frog puffed its throat balloon to amplify its mating call", "मेंढक ने अपनी आवाज़ बढ़ाने के लिए गले की थैली फुलाई"),
    ("The cunning river crocodile lay submerged resembling a harmless floating log", "चालाक मगरमच्छ पानी में बहते हुए लट्ठे की तरह डूबा रहा"),
    ("The rainbow trout darted upstream against the torrential mountain current", "मछली तेज़ पहाड़ी धारा के विपरीत ऊपर की ओर तैरी"),
    ("The ancient python constricted the wild boar within its muscular coils", "विशाल अजगर ने जंगली सूअर को अपनी मज़बूत कुंडली में जकड़ लिया"),

    # 206-250: पक्षी व कीट (चींटी, चिड़िया, कौआ, उल्लू, हंस, तोता, मक्खी, मधुमक्खी)
    ("What use is sorrow after the stray birds have eaten the field", "अब पछताए होत क्या जब चिड़िया चुग गई खेत"),
    ("The selfish clerk was solely interested in straightening his own owl", "स्वार्थी बाबू केवल अपना उल्लू सीधा करने में लगा रहा"),
    ("The dishonest merchant made a complete owl of the credulous villagers", "बेईमान व्यापारी ने सीधे ग्रामीणों को पूरी तरह उल्लू बना दिया"),
    ("The little ant heading for self destruction suddenly grew ambitious wings", "चींटी के पर निकल आए और वह विनाश की ओर बढ़ने लगी"),
    ("The clumsy cart moved forward at the agonizing pace of an ant", "पुरानी गाड़ी चींटी की चाल से आगे खिसकती रही"),
    ("The pious hypocrite looked like a pious crane harboring wicked thoughts", "धोंगी साधु बगुला भगत बनकर सीधे लोगों को ठगता रहा"),
    ("The student repeated the difficult text mechanically like a caged parrot", "छात्र ने बिना समझे तोते की तरह पूरा पाठ रट लिया"),
    ("The crow tried to imitate the graceful gait of royal swan", "कौआ हंस की चाल चलने की कोशिश में अपनी चाल भी भूल गया"),
    ("The idle sluggard spent the whole sunny day swatting imaginary flies", "आलसी युवक पूरा दिन बैठकर केवल मक्खियाँ मारता रहा"),
    ("The tiny ant carried a sweet sugar grain ten times its weight", "छोटी चींटी ने अपने वजन से दस गुना बड़ा चीनी का दाना उठाया"),
    ("The wise nocturnal owl hooted from the hollow of the ancient banyan", "बुद्धिमान उल्लू ने प्राचीन बरगद के खोखल से गंभीर आवाज़ लगाई"),
    ("The flock of migratory cranes flew in a neat wedge across sky", "प्रवासी सारसों का झुंड आसमान में सुंदर कतार बनाकर उड़ा"),
    ("The green parakeet cracked the hard walnut shell with its curved beak", "हरे तोते ने अपनी मुड़ी हुई चोंच से अखरोट का कड़ा छिलका तोड़ा"),
    ("The clever black crow dropped pebbles into pitcher to raise water level", "चतुर कौए ने मटके में कंकड़ डालकर पानी का स्तर ऊपर उठाया"),
    ("The busy honeybee collected sweet floral nectar from a thousand blossoms", "मेहनती मधुमक्खी ने हज़ारों फूलों से मीठा रस इकट्ठा किया"),
    ("The white swan glided with serene elegance across the sacred lotus lake", "सफेद हंस पवित्र कमल सरोवर में शांत गरिमा के साथ तैरा"),
    ("The noisy flock of common sparrows nested beneath the tiled eaves", "चिड़ियों के चहकते झुंड ने खपरैल की छत के नीचे घोंसला बनाया"),
    ("The disciplined army of red ants marched in an unbroken straight line", "लाल चींटियों का अनुशासित दल एक सीधी अटूट रेखा में आगे बढ़ा"),
    ("The great horned owl blinked its large yellow eyes in daylight", "बड़ा उल्लू दिन के उजाले में अपनी पीली आँखें झपकाता रहा"),
    ("The singing nightingale filled the enchanted forest glade with melody", "गाने वाली बुलबुल ने जादुई वन को मधुर संगीत से भर दिया"),
    ("The caged parrot greeted the returning master with cheerful human words", "पिंजरे के तोते ने लौटते हुए स्वामी का मीठी बोली में स्वागत किया"),
    ("The scavenging ravens gathered around the feast leftovers on the terrace", "कौओं का झुंड छत पर बचे हुए भोजन के चारों ओर जमा हुआ"),
    ("The industrious bees constructed a hexagonal wax honeycomb on cliff", "मेहनती मधुमक्खियों ने चट्टान पर मोम का षट्कोणीय छत्ता बनाया"),
    ("The majestic swan separated milk from water with supreme discernment", "हंस ने अपने विवेक से दूध और पानी को अलग कर दिया"),
    ("The weaver bird wove an intricate hanging nest using dried grass blades", "बया पक्षी ने सूखी घास के तिनकों से लटकता हुआ सुंदर घोंसला बुना"),
    ("The industrious ant stored abundant food grains for the harsh winter", "मेहनती चींटी ने कठिन सर्दियों के लिए पर्याप्त अनाज जमा किया"),
    ("The screech owl hunted woodland mice silently under cover of night", "उल्लू ने रात के सन्नाटे में जंगल के चूहों का खामोशी से शिकार किया"),
    ("The flock of wild geese honked loudly across the misty morning sky", "जंगली कलहंसों का झुंड कोहरे भरे सुबह के आसमान में गूँजता हुआ उड़ा"),
    ("The trained falcon soared high and returned to the glove of master", "सिखाए हुए बाज़ ने ऊँची उड़ान भरी और स्वामी के हाथ पर लौट आया"),
    ("The talkative parrot repeated every secret spoken in the royal bedchamber", "बातूनी तोते ने शयनकक्ष में बोली गई हर गुप्त बात दोहरा दी"),
    ("The clever crow warned the entire forest of the approaching jungle cat", "चतुर कौए ने जंगली बिल्ली को आते देखकर पूरे जंगल को सावधान किया"),
    ("The queen bee remained in the royal cell surrounded by devoted workers", "रानी मधुमक्खी समर्पित सेवकों से घिरी अपने शाही कक्ष में रही"),
    ("The solitary black raven perched ominously upon the ruined stone fortress", "अकेला कौआ खंडहर बने पत्थर के किले पर अशुभ भाव से बैठा रहा"),
    ("The graceful pair of swans swam together along the silver river bank", "हंसों के सुंदर जोड़े ने चाँदी जैसी नदी के किनारे साथ साथ तैराकी की"),
    ("The tiny hummingbird hovered effortlessly before the crimson trumpet flower", "नन्हीं चिड़िया लाल फूल के आगे हवा में बिना हिले मँडराती रही"),
    ("The diligent carpenter bee bored a neat circular tunnel in dry wood", "मधुमक्खी ने सूखी लकड़ी में एक गोल सुंदर छेद बना दिया"),
    ("The tiny brown sparrow pecked at breadcrumbs strewn on stone courtyard", "छोटी भूरी गौरैया ने पत्थर के आँगन में बिखरे रोटी के टुकड़े चुगे"),
    ("The wise snowy owl watched the frozen tundra with unblinking golden gaze", "सफेद उल्लू ने जमी हुई बर्फीली ज़मीन को बिना पलक झपकाए देखा"),
    ("The kingfisher plunged headlong into the blue pool to spear small fish", "रामचिरैया ने छोटी मछली पकड़ने के लिए नीले पानी में डुबकी लगाई"),
    ("The pet parrot imitated the ringing of the telephone with perfect pitch", "पालतू तोते ने घंटी की आवाज़ की हूबहू नकल उतारकर सबको चौंकाया"),
    ("The black crow cawed incessantly from the rooftop signaling arriving guests", "मुंडेर पर बैठकर काँव काँव करते कौए ने मेहमानों के आगमन का संकेत दिया"),
    ("The honeybees defended their fragrant wax comb against the hungry marauders", "मधुमक्खियों ने भूखे लुटेरों से अपने सुगंधित छत्ते की रक्षा की"),
    ("The elegant wild swans rested upon the calm mirror of mountain lake", "जंगली हंसों ने पहाड़ी झील के शांत पानी पर आराम किया"),
    ("The swift swallow darted across the evening sky catching flying gnats", "फुर्तीली अबाबील ने शाम के आकाश में उड़ते हुए कीड़ों को पकड़ा"),
    ("The persistent ant climbed up the slippery glass wall after ten falls", "लगातार प्रयास करने वाली चींटी दस बार गिरकर भी कांच की दीवार पर चढ़ गई"),
]

# Set up semantic aligner
import importlib.util
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

# Extend vocabulary dictionary with fauna & nature terms
FAUNA_DICT = {
    'घोड़ा': ['horse'], 'घोड़े': ['horses', 'horse'], 'घोड़ी': ['mare'], 'बछेड़े': ['colt'], 'बछेड़ा': ['colt'],
    'गधा': ['donkey'], 'गधे': ['donkey', 'donkeys'], 'खच्चर': ['mule'],
    'ऊँट': ['camel'], 'ऊँटों': ['camels'], 'हाथी': ['elephant'], 'हाथियों': ['elephants'],
    'गाय': ['cow'], 'गऊ': ['cow'], 'गौ': ['cow'], 'बैल': ['bullock', 'bull', 'ox'], 'बैलों': ['bullocks'],
    'भैंस': ['buffalo'], 'भैंसों': ['buffaloes'], 'भैंसे': ['buffalo'], 'सांड': ['bull'],
    'बछड़ा': ['calf'], 'बछड़े': ['calf', 'fawn'],
    'बिल्ली': ['cat'], 'बिल्लियों': ['cats'], 'कुत्ता': ['dog'], 'कुत्ते': ['dog', 'dogs'], 'कुत्तों': ['dogs'],
    'पिल्ला': ['puppy'], 'पिल्ले': ['puppy'], 'लोमड़ी': ['fox'], 'भेड़िया': ['wolf'],
    'भेड़िए': ['wolf', 'wolves'], 'भेड़ियों': ['wolves'],
    'बंदर': ['monkey', 'ape'], 'बंदरों': ['monkeys'], 'वानर': ['ape', 'monkey'], 'लंगूर': ['langur', 'baboon'],
    'भालू': ['bear'], 'रीछ': ['bear'], 'मृग': ['deer', 'gazelle'], 'हिरण': ['deer', 'stag'], 'हिरणी': ['doe'],
    'बारहसिंगे': ['antelope'], 'कस्तूरी': ['musk'],
    'साँप': ['snake', 'serpent'], 'नाग': ['cobra', 'snake'], 'करैत': ['kraits'], 'अजगर': ['python'],
    'बिच्छू': ['scorpion'], 'मेंढक': ['frog', 'bullfrog', 'frogs'], 'मेंढकों': ['frogs'],
    'मगरमच्छ': ['crocodile', 'alligator'], 'मगर': ['crocodile'],
    'मछली': ['fish', 'carp', 'trout'], 'मछलियों': ['fish'],
    'चींटी': ['ant'], 'चींटियों': ['ants'], 'चिड़िया': ['bird', 'sparrow', 'birds'],
    'चिड़ियों': ['birds', 'sparrows'], 'कौआ': ['crow', 'raven'], 'कौए': ['crow', 'crows'], 'कौओं': ['crows', 'ravens'],
    'उल्लू': ['owl'], 'हंस': ['swan', 'swans'], 'सारसों': ['cranes'], 'कलहंसों': ['geese'],
    'बगुला': ['crane', 'heron'], 'तोता': ['parrot', 'parakeet'], 'तोते': ['parrot', 'parakeet'],
    'मक्खी': ['fly'], 'मक्खियाँ': ['flies'], 'मधुमक्खी': ['bee', 'honeybee'], 'मधुमक्खियों': ['bees', 'honeybees'],
    'चूहा': ['mouse', 'rat'], 'चूहे': ['mouse', 'mice', 'rat'], 'चूहों': ['mice', 'rats'],
    'मुर्गा': ['rooster'], 'मुर्गी': ['hen'], 'बकरी': ['goat'], 'भेड़': ['sheep'], 'भेड़ें': ['sheep'],
    'बाज़': ['falcon'], 'बुलबुल': ['nightingale'], 'गौरैया': ['sparrow'], 'रामचिरैया': ['kingfisher'],
    'अबाबील': ['swallow'], 'बया': ['weaver', 'bird'],
    'जंगल': ['jungle', 'forest'], 'घाटी': ['valley'], 'मैदान': ['field', 'meadow', 'plains'],
    'गुफा': ['cave'], 'मांद': ['den'], 'बिल': ['den', 'hole'], 'छत्ता': ['hive', 'comb', 'honeycomb'],
    'नदी': ['river', 'stream'], 'तालाब': ['pond', 'lake'], 'सरोवर': ['lake'], 'झील': ['lake'],
    'समुद्र': ['ocean', 'sea'], 'रेगिस्तान': ['desert'], 'काफिला': ['caravan', 'train'],
    'सवारी': ['rider'], 'सवार': ['mounted', 'rode', 'rider'], 'लगाम': ['rein', 'reins'],
    'खुर': ['hoof', 'hooves'], 'खुरों': ['hooves'], 'सींग': ['horns'], 'सींगों': ['horns'],
    'पूँछ': ['tail'], 'पंख': ['wings', 'feathers'], 'चोंच': ['beak'], 'पंजा': ['paw', 'claws'],
    'पंजों': ['paws', 'claws'], 'दाँत': ['teeth', 'fangs'], 'जबड़े': ['jaws'], 'डंक': ['sting'],
    'फन': ['hood'], 'केंचुली': ['skin', 'slough'], 'सूंड': ['trunk'], 'अंकुश': ['goad'],
    'महावत': ['mahout'], 'सपेरे': ['charmer'], 'बीन': ['pipe'], 'चारागाह': ['pasture'],
    'अस्तबल': ['stable'], 'रथ': ['carriage'], 'सराय': ['inn'], 'खलिहान': ['threshing', 'floor'],
    'शिकारी': ['hunter', 'hunters', 'hound'],
}
ga.DICT.update(FAUNA_DICT)

def validate_and_align(corpus_pairs):
    DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
    ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')

    # Load existing hi sentences
    existing_hi = {}
    for p in sorted((ROOT / "data").glob("phrases*.json")):
        if p.name == "phrases27.json":
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
        sid = f"p27s{idx:03d}"
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

        # Derive alignment with semantic word mappings
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
    print(f"Validating and aligning {len(PAIRS)} sentence pairs for Batch ID-03...")
    out, errors = validate_and_align(PAIRS)
    if errors:
        print(f"FOUND {len(errors)} ERRORS:")
        for e in errors[:25]:
            print("  ", e)
        sys.exit(1)

    out_file = ROOT / "data" / "phrases27.json"
    out_file.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"Successfully generated {out_file} with {len(out)} sentences.")

    # Update manifest.json
    manifest_file = ROOT / "data" / "manifest.json"
    manifest = json.load(open(manifest_file))
    manifest["files"] = [f for f in manifest["files"] if f["file"] != "data/phrases27.json"]
    manifest["files"].append({
        "file": "data/phrases27.json",
        "count": len(out)
    })
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated {manifest_file} with data/phrases27.json (count: {len(out)}).")

if __name__ == "__main__":
    main()
