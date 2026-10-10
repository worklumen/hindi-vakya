#!/usr/bin/env python3
"""Batch ID-04: Elements, Idioms, Verbs & Tenses.

Focuses on authentic idioms of Elements & Nature (हवा, पानी, आग, आसमान, ज़मीन, पहाड़, धूप/छाँव, बादल)
interwoven with rich verbal aspects (Habitual, Continuous, Ergative Perfectives with ने, Vector Verbs, Causatives, Subjunctive).

Generates data/phrases28.json (250 sentences) with semantic alignments.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

PAIRS = [
    # 1-45: हवा, तूफान, आंधी, बयार (Wind, Storm, Gale - Idioms & Tenses)
    ("The proud merchant was flying high in the air after making profit", "भारी मुनाफ़ा कमाकर घमंडी व्यापारी हवा में उड़ रहा था"),
    ("Wise politicians always observe the direction of wind before taking action", "समझदार राजनेता कोई कदम उठाने से पहले हवा का रुख देखते हैं"),
    ("The bad companion influenced the naive boy with harmful habits", "बुरे साथियों की हवा लगने से सीधा बालक बिगड़ गया"),
    ("The clever thief vanished into thin air before the police arrived", "पुलिस के आने से पहले ही चालाक चोर हवा हो गया"),
    ("The magnificent Arabian stallion was running as fast as the wind", "भव्य अरबी घोड़ा मैदान में हवा से बातें कर रहा था"),
    ("The sudden inheritance was like windfall mangoes after the seasonal storm", "अचानक मिला धन उसके लिए आंधी के आम की तरह साबित हुआ"),
    ("The fierce northern gale blew away the thatched roof of the cottage", "तेज़ उत्तरी आंधी ने झोपड़ी का फूस का छप्पर उड़ा दिया"),
    ("The gentle morning breeze will be blowing through the pine forest", "सुबह की शीतल बयार चीड़ के जंगल में बह रही होगी"),
    ("The dark storm had extinguished the lone earthen lamp of the temple", "काली आंधी ने मंदिर के अकेले मिट्टी के दीये को बुझा दिया था"),
    ("The courageous sailor will steer the boat against the violent gale", "साहसी नाविक तूफानी हवा के थपेड़ों के विपरीत नाव चलाएगा"),
    ("The arrogant prince talks big as if he has caught the wind", "अभिमानी राजकुमार ऐसी बातें करता है मानो उसने हवा बांध ली हो"),
    ("The terrified villagers were fleeing before the advancing desert dust storm", "रेगिस्तानी रेतीली आंधी को देखकर भयभीत ग्रामीण गाँव छोड़कर भाग रहे थे"),
    ("The violent gale will have uprooted dozens of ancient banyan trees", "भीषण तूफान ने दर्जनों प्राचीन बरगद के पेड़ उखाड़ दिए होंगे"),
    ("The old grandfather used to stroll in the cool evening breeze", "बूढ़े दादाजी शाम की ठंडी हवा में टहला करते थे"),
    ("The dry autumn leaves were swirling rapidly in the sudden gust", "हवा के अचानक झोंके से सूखे पत्ते तेज़ी से घूमने लगे"),
    ("If the fierce storm comes the weak mud walls might collapse", "अगर भीषण आंधी आई तो कच्ची दीवारें ढह सकती हैं"),
    ("The brave commander made his horse leap across the windy gorge", "बहादुर सेनापति ने तूफानी दर्रे के पार अपना घोड़ा कुदा दिया"),
    ("The continuous cold breeze had chilled the weary mountain travelers", "लगातार चलती सर्द हवा ने थके हुए पर्वतारोहियों को कंपा दिया था"),
    ("The cunning minister caused rumors to fly in the open market", "चालाक मंत्री ने खुले बाज़ार में तरह तरह की अफवाहें उड़ा दीं"),
    ("The little girl will be flying a colorful kite in the gentle wind", "छोटी बालिका हल्की हवा में रंग बिरंगी पतंग उड़ा रही होगी"),
    ("The sudden gust of wind had scattered all important state papers", "हवा के तेज़ झोंके ने सरकारी कार्यालय के सभी ज़रूरी कागज़ बिखेर दिए थे"),
    ("The wise farmer does not winnow the wheat grain without proper wind", "समझदार किसान अनुकूल हवा के बिना गेहूँ की ओसाई नहीं करता है"),
    ("The storm raged fiercely while the frightened children prayed inside", "बाहर आंधी गरजती रही जबकि अंदर डरे हुए बच्चे प्रार्थना करते रहे"),
    ("The cold wind makes the traveler tighten his woolen shawl tightly", "सर्द हवा मुसाफिर को अपनी ऊनी शॉल कसकर लपेटने पर मजबूर करती है"),
    ("The great hurricane has destroyed several coastal fishing hamlets completely", "विशाल समुद्री तूफान ने कई तटीय बस्तियों को पूरी तरह तहस नहस कर दिया है"),
    ("The rumor spread like wildfire through the entire busy marketplace", "वह झूठी खबर हवा की तेज़ी से पूरे व्यस्त बाज़ार में फैल गई"),
    ("The brave scouts had been watching the dusty horizon for hours", "बहादुर दूत घंटों से धूल भरी क्षितिज की निगरानी कर रहे थे"),
    ("Perhaps the pleasant evening breeze may bring relief from humid heat", "शायद शाम की सुखद बयार उमस भरी गर्मी से राहत दिला सके"),
    ("The storm broke the branches and blocked the royal highway totally", "आंधी ने पेड़ की डालियाँ तोड़कर शाही राजमार्ग को पूरी तरह रोक दिया"),
    ("The proud challenger lost all his bluster after the first round", "पहले ही मुकाबले के बाद घमंडी पहलवान की सारी हवा निकल गई"),
    ("The sailors had unfurled the white sails to catch the ocean wind", "नाविकों ने समुद्री हवा पकड़ने के लिए सफेद पाल खोल दिए थे"),
    ("The cold gale was whistling through the narrow cracks of the fortress", "ठंडी हवा किले की संकरी दरारों में से सीटी बजाती हुई निकल रही थी"),
    ("The swift rider will reach the capital before the storm breaks", "तूफान आने से पहले ही तेज़ घुड़सवार राजधानी पहुँच जाएगा"),
    ("The autumn wind strips the dry golden leaves from every tree", "शरद ऋतु की हवा हर पेड़ से सूखे सुनहरे पत्तों को गिरा देती है"),
    ("The violent dust storm blinded the marching soldiers for an hour", "धूल भरी भयंकर आंधी ने आगे बढ़ते सैनिकों की आँखों में धूल झोंक दी"),
    ("The gentle zephyr was whispering softly through the bamboo grove", "मंद बयार बाँस के कुंज में हौले हौले सरसरा रही थी"),
    ("The experienced captain had navigated through many treacherous sea storms", "अनुभवी कप्तान ने समुद्र के कई खतरनाक तूफानों का सामना किया था"),
    ("The sudden squall overturned two small wooden fishing boats near shore", "अचानक आए बवंडर ने किनारे के पास दो छोटी नावें पलट दीं"),
    ("The wild wind howled like a hungry wolf across the desolate moor", "उजाड़ मैदान में तूफानी हवा भूखे भेड़िए की तरह दहाड़ रही थी"),
    ("The gardener watered the plants before the dry wind parched them", "माली ने सूखी हवा से झुलसने से पहले पौधों को पानी दिया"),
    ("The furious storm has broken the electric wires in the city", "भीषण तूफान ने नगर के बिजली के खंभों को उखाड़ फेंका है"),
    ("The cold north wind brings snow to the high Himalayan peaks", "उत्तरी ठंडी हवा हिमालय की ऊँची चोटियों पर ताज़ा बर्फ़ लाती है"),
    ("The swift wind carried the fragrant aroma of jasmine to the terrace", "तेज़ हवा चमेली के फूलों की भीनी महक छत तक ले आई"),
    ("The young prince would practice archery under the breezy open pavilion", "युवा राजकुमार खुली हवादार बारादरी में तीरंदाजी का अभ्यास करता था"),
    ("The sudden thunderstorm washed the stale summer dust from the streets", "अचानक आई आंधी और बारिश ने गलियों की धूल धो डाली"),

    # 46-90: पानी, नदी, समंदर, घाट (Water, River, Ocean, Flood - Idioms & Tenses)
    ("The caught cheat was so ashamed that he wished to drown in a spoonful", "रंगे हाथ पकड़े जाने पर शर्मिंदा ठग चुल्लू भर पानी में डूब मरा"),
    ("The continuous betrayal turned the great hopes of the father into water", "लगातार विश्वासघात ने पिता की सारी उम्मीदों पर पानी फेर दिया"),
    ("The cunning merchant had drunk water from many ghats in his career", "उस चतुर व्यापारी ने अपने जीवन में घाट घाट का पानी पिया था"),
    ("The disgraced traitor turned completely into water with unbearable shame", "अदालत में भेद खुल जाने पर गद्दार शर्म से पानी पानी हो गया"),
    ("Human life is fragile and transient like a tiny bubble of water", "मनुष्य का नश्वर जीवन पानी के छोटे बुलबुले की तरह क्षणभंगुर है"),
    ("The greedy broker washed his hands in the flowing river of charity", "लालची दलाल ने बहती गंगा में हाथ धोकर खूब धन कमाया"),
    ("The desperate lover was writhing restless like a fish out of water", "वियोग में दुखी प्रेमी जल बिन मछली की तरह तड़प रहा था"),
    ("The torrential mountain rain had caused the river to overflow banks", "मूसलाधार पहाड़ी बारिश ने नदी के दोनों किनारों को जलमग्न कर दिया था"),
    ("The sacred river flows peacefully beside the ancient marble temples", "पवित्र नदी प्राचीन संगमरमर के मंदिरों के पास शांत भाव से बहती है"),
    ("The brave swimmer will cross the turbulent river before the sunset", "साहसी तैराक सूर्यास्त से पहले उफनती नदी को तैरकर पार करेगा"),
    ("The deep ocean hides precious pearls within its silent depths", "गहरा समंदर अपनी शांत गहराइयों में अनमोल मोती छिपाकर रखता है"),
    ("The great flood has submerged hundreds of fertile paddy fields", "विशाल बाढ़ ने सैकड़ों उपजाऊ धान के खेतों को डुबो दिया है"),
    ("The thirsty pilgrim was drinking cold crystal water from the spring", "प्यासा तीर्थयात्री पहाड़ी सोते से शीतल स्वच्छ जल पी रहा था"),
    ("If the dam breaks the rushing water would drown the entire valley", "अगर बाँध टूटा तो बहता पानी पूरी घाटी को जलमग्न कर देगा"),
    ("The mother had poured sacred river water upon the head of child", "माँ ने नन्हें बालक के सिर पर पवित्र गंगाजल छिड़क दिया था"),
    ("The angry river washed away the weak wooden bridge during night", "उफनती नदी ने रात के अंधेरे में कमज़ोर लकड़ी के पुल को बहा दिया"),
    ("The wise sage said that truth separates milk from water cleanly", "ज्ञानी ऋषि ने कहा कि सच्चा विवेक दूध का दूध पानी का पानी करता है"),
    ("The thirsty travelers will have found a freshwater oasis in desert", "प्यासे यात्रियों को तपते मरुस्थल में मीठे पानी का नखलिस्तान मिल चुका होगा"),
    ("The heavy monsoon rains are filling the dried ponds of the village", "सावन की भारी बारिश गाँव के सूखे तालाबों को पानी से भर रही है"),
    ("The experienced boatman knows every whirlpool in this wide river", "अनुभवी मल्लाह इस चौड़ी नदी के हर खतरनाक भँवर को पहचानता है"),
    ("The dirty water of the drain polluted the clean lake water completely", "गंदे नाले के पानी ने सुंदर झील के स्वच्छ जल को दूषित कर दिया"),
    ("The villagers used to draw sweet water from the deep stone well", "गाँव के लोग गहरे पत्थर के कुएँ से मीठा पानी खींचा करते थे"),
    ("The rapid stream cascaded down the rocky cliff with deafening roar", "तेज़ जलधारा गगनभेदी गर्जना के साथ पथरीली चट्टान से नीचे गिरी"),
    ("The diligent farmer had channeled the canal water to his dry orchard", "मेहनती किसान ने नहर का पानी अपने सूखे बाग की ओर मोड़ दिया था"),
    ("The kind lady offered a copper pot of cool water to the stranger", "दयालु महिला ने अजनबी मुसाफिर को तांबे के लोटे में ठंडा पानी दिया"),
    ("The muddy flood water had inundated the narrow village pathways", "कीचड़ भरे बाढ़ के पानी ने गाँव की संकरी पगडंडियों को डुबो दिया था"),
    ("The ancient stone bridge has withstood the furious currents for centuries", "प्राचीन पत्थर का पुल सदियों से नदी के प्रचंड प्रवाह को झेलता आया है"),
    ("The fisherman casts his broad nylon net into the deep calm water", "मछुआरा गहरे शांत पानी में अपना चौड़ा नायलॉन का जाल फेंकता है"),
    ("The holy lake reflected the snow clad peaks like a polished mirror", "पवित्र झील ने बर्फ़ीली चोटियों को दर्पण की तरह अपने जल में चमकाया"),
    ("The little boy was splashing joyfully in the clear mountain stream", "छोटा बालक स्वच्छ पहाड़ी नाले में खुशी से छपछप कर रहा था"),
    ("The water of the natural spring remains cool throughout the hot summer", "प्राकृतिक झरने का पानी भीषण गर्मी में भी हमेशा शीतल रहता है"),
    ("The torrential downpour caused waterlogging on all major roads of city", "मूसलाधार बारिश ने नगर के सभी मुख्य मार्गों पर भारी जलभराव कर दिया"),
    ("The brave lifeguard saved the drowning child from the deep current", "साहसी गोताखोर ने गहरे पानी में डूबते हुए बच्चे को बचा लिया"),
    ("The dry summer heat has evaporated the water of the shallow pond", "गर्मियों की तीव्र धूप ने उथले तालाब के पानी को सुखा दिया है"),
    ("The royal fountain was spraying fine droplets of scented rose water", "शाही फव्वारा गुलाब जल की नन्हीं सुगंधित बूँदें चारों ओर बिखेर रहा था"),
    ("The water carrier was transporting leather bags of water on bullock", "भिश्ती बैल की पीठ पर चमड़े की मशक लादकर पानी पहुँचा रहा था"),
    ("The ancient tank provided water to the fortress during the long siege", "प्राचीन जलकुंड ने लंबे घेरे के दौरान किले के निवासियों को पानी दिया"),
    ("The gentle rain drops were rippling the surface of the green pool", "धीमी बारिश की बूँदें हरे तालाब की सतह पर सुंदर तरंगें बना रही थीं"),
    ("The river formed a fertile delta before merging into the blue ocean", "नीले समंदर में मिलने से पहले नदी ने उपजाऊ डेल्टा का निर्माण किया"),
    ("The villagers will build a check dam to conserve the monsoon water", "ग्रामीण मानसूनी बारिश के पानी को सहेजने के लिए छोटा बाँध बनाएंगे"),
    ("The cool river water has revitalized the exhausted cavalry regiment", "शीतल नदी के जल ने थके हुए घुड़सवार दस्ते में नई ताजगी भर दी है"),
    ("The crystal clear brook was babbling through the emerald green meadow", "स्वच्छ कलकल बहती धारा मखमली हरे मैदान के बीच से गुज़र रही थी"),
    ("The continuous seepage of water weakened the foundations of the tower", "पानी के लगातार रिसाव ने पुराने बुर्ज की नींव को कमज़ोर कर दिया"),
    ("The holy hermits performed morning ablutions in the flowing current", "पवित्र संन्यासियों ने बहती धारा में सुबह का स्नान और ध्यान किया"),
    ("The thirsty stag drank water warily looking around for predators", "प्यासे बारहसिंगे ने शिकारियों से चौकन्ना रहकर नदी से पानी पिया"),

    # 91-135: आग, अंगार, शोला, धुआँ (Fire, Embers, Smoke - Idioms & Tenses)
    ("The short tempered master became a blazing fireball in terrible anger", "कर्मचारियों की भूल देखकर क्रोधी मालिक गुस्से में आग बबूला हो गया"),
    ("The malicious gossip poured pure clarified butter into the raging fire", "चुगलखोर पड़ोसी की बातों ने दोनों परिवारों के झगड़े में घी डाल दिया"),
    ("The envious rival was rolling upon hot coals seeing their success", "उनकी शानदार सफलता देखकर ईर्ष्यालु प्रतिद्वंद्वी अंगारों पर लोटने लगा"),
    ("The reckless youth was playing with fire by challenging the king", "राजा को खुली चुनौती देकर लापरवाह युवक सीधे आग से खेल रहा था"),
    ("The furious orator was spitting red hot embers in his speech", "मंच पर भाषण देते हुए क्रोधी वक्ता गुस्से में अंगारे उगल रहा था"),
    ("There is no smoke without fire in this mysterious palace scandal", "महल के इस विचित्र मामले में बिना आग के धुआँ नहीं उठता है"),
    ("The poor laborer works day and night to appease the belly fire", "गरीब मजदूर पेट की आग बुझाने के लिए दिन रात मेहनत करता है"),
    ("The brave firefighters extinguished the roaring flames of the warehouse", "बहादुर दमकलकर्मियों ने गोदाम की भीषण लपटों को पानी डालकर बुझा दिया"),
    ("The blacksmith blew the leather bellows making the coal fire glow", "लोहार ने चमड़े की धौंकनी चलाकर कोयले की आग को भड़का दिया"),
    ("The camp fire will be warming the weary mountain climbers tonight", "आज रात अलाव की गरम आग थके हुए पर्वतारोहियों को गर्माहट देगी"),
    ("The devastating blaze has gutted fifty wooden shops in the market", "भीषण अग्निकांड ने बाज़ार की पचास लकड़ी की दुकानों को जलाकर राख कर दिया है"),
    ("The sacrificial fire was consuming fragrant sandalwood and pure butter", "यज्ञ की पावन अग्नि में सुगंधित चंदन और शुद्ध घी की आहुति दी जा रही थी"),
    ("The sparks from the anvil were flying in all directions of smithy", "निहाई पर हथौड़े की चोट से आग की चिंगारियाँ चारों ओर बिखर रही थीं"),
    ("The dry summer leaves caught fire instantly from a single matchstick", "गर्मी में सूखे पत्तों ने एक ही माचिस की तीली से तुरंत आग पकड़ ली"),
    ("If the dry wind blows the forest fire might spread to village", "अगर सूखी हवा चली तो जंगल की दावानल गाँव तक फैल सकती है"),
    ("The cooking fire had filled the little hut with thick pungent smoke", "चूल्हे की आग ने छोटी झोपड़ी को घने कड़वे धुएँ से भर दिया था"),
    ("The soldiers warmed their frozen hands beside the trench fire", "सैनिकों ने खंदक के अलाव के पास अपने ठंडे हाथों को सेंक लिया"),
    ("The fierce volcano spewed molten lava and black ash into the sky", "भयंकर ज्वालामुखी ने आसमान में खौलता लावा और काला धुआँ उगल दिया"),
    ("The ancient beacon fire alerted the distant garrisons of the invasion", "पहाड़ी पर जलती आग ने दूर की छावनियों को शत्रु के हमले से सावधान किया"),
    ("The playful children were roasting sweet corn over the hot charcoal", "चंचल बच्चे गरम अंगारों पर भुट्टे सेंककर मजे से खा रहे थे"),
    ("The potter fired his earthenware pots in the brick kiln for days", "कुम्हार ने ईंटों के भट्ठे में मिट्टी के बर्तनों को कई दिन तक पकाया"),
    ("The wicked enemy set fire to the standing wheat crops at midnight", "दुष्ट शत्रु ने आधी रात को पकी हुई गेहूँ की फसल में आग लगा दी"),
    ("The smoke from the burning incense purifies the sacred temple hall", "सुगंधित धूप का पावन धुआँ मंदिर के गर्भगृह को पवित्र कर देता है"),
    ("The night watchman kept the bonfire burning until the dawn broke", "रात के पहरेदार ने सुबह होने तक अलाव की आग को जलता रखा"),
    ("The angry mob has set ablaze several transport buses on the street", "उपद्रवी भीड़ ने सड़क पर खड़ी कई यात्री बसों को आग के हवाले कर दिया है"),
    ("The red embers were glowing brightly beneath the grey surface ash", "सफेद राख के नीचे लाल अंगारे अभी भी तेज़ी से दहक रहे थे"),
    ("The golden ornaments were purified in the roaring flames of furnace", "सोने के आभूषणों को भट्टी की तेज़ आग में तपाकर शुद्ध किया गया"),
    ("The sudden fire had forced the wild beasts to flee the forest", "अचानक लगी आग ने जंगली जानवरों को जंगल छोड़कर भागने पर विवश किया"),
    ("The villagers will extinguish the chimney fire with sand and blankets", "ग्रामीण रेत और कंबलों की सहायता से चिमनी की आग को बुझाएंगे"),
    ("The dry thatch roof caught fire from an errant spark of lantern", "लालटेन की एक चिंगारी से फूस के सूखे छप्पर ने तुरंत आग पकड़ ली"),
    ("The burning torch illuminated the dark stone corridors of the tomb", "जलती हुई मशाल ने तहखाने के अंधेरे गलियारों को रोशनी से भर दिया"),
    ("The intense heat of the glass furnace melted the colored silica", "कांच की भट्टी की प्रचंड गर्मी ने रंगीन सिलिका को पूरी तरह पिघला दिया"),
    ("The hunter buried the camp embers carefully before departing the glade", "शिकारी ने जंगल छोड़ने से पहले अलाव के अंगारों को मिट्टी से ढक दिया"),
    ("The fire had consumed the ancient timber beams of the clock tower", "भीषण आग ने घंटाघर के प्राचीन लकड़ी के शहतीरों को भस्म कर दिया था"),
    ("The holy priest offered prayers to the sacred elemental fire at dusk", "पवित्र पुजारी ने संध्याकाल में पावन अग्नि देव की विधिवत वंदना की"),
    ("The roaring forge of the armorer produced hundreds of steel swords", "हथियार निर्माता की धधकती भट्टी ने सैकड़ों फौलादी तलवारें तैयार कीं"),
    ("The dense black smoke signaled the distress of the stranded sailors", "काले घने धुएँ ने फँसे हुए नाविकों के गंभीर संकट का संकेत दिया"),
    ("The little girl blew upon the dying ember to rekindle the flame", "छोटी बालिका ने बुझते हुए अंगारे पर फूँक मारकर लौ को फिर से जलाया"),
    ("The friction of dry bamboo stalks started a massive jungle wildfire", "सूखे बाँसों की रगड़ से घने जंगल में भीषण दावानल भड़क उठी"),
    ("The warm fireplace made the cozy sitting room comfortable in winter", "गरम अंगीठी ने सर्दियों में बैठक के कमरे को सुखद और आरामदायक बना दिया"),
    ("The royal pyrotechnics illuminated the dark night sky with red fire", "शाही आतिशबाजी ने लाल लपटों और चिंगारियों से अंधेरे आसमान को जगमगा दिया"),
    ("The smelter separates the molten metal from the slag in hot fire", "धातु कर्मी तेज़ आग में पिघली धातु को कचरे से अलग करता है"),
    ("The fire flared up fiercely when the dry cedar wood was added", "सूखी देवदार की लकड़ी डालते ही अलाव की आग अचानक भड़क उठी"),
    ("The villagers sat in a close circle around the crackling winter logs", "ग्रामीण चटकती लकड़ियों के अलाव के चारों ओर घेरा बनाकर बैठे रहे"),
    ("The brave boy saved his little sister from the blazing house", "साहसी बालक ने जलते हुए मकान से अपनी नन्हीं बहन को बचा लिया"),

    # 136-175: आसमान, आकाश, तारे, बिजली (Sky, Heavens, Stars, Lightning - Idioms & Tenses)
    ("The mischievous boy raised the sky on his head for a petty toy", "मासूम बालक ने छोटे से खिलौने के लिए सारा आसमान सिर पर उठा लिया"),
    ("The lofty marble towers of the royal palace were talking to sky", "शाही महल के ऊँचे संगमरमर के बुर्ज आसमान से बातें कर रहे थे"),
    ("Falling from the sky he got trapped into the tall palm tree", "नौकरी छूटने के बाद वह आसमान से गिरा और खजूर में अटका"),
    ("The heavy blow on his head made him see stars in daylight", "सिर पर भारी चोट लगते ही उस घमंडी युवक को दिन में तारे दिखाई दिए"),
    ("The hardworking students will unite earth and sky to pass the exam", "परीक्षा में सफल होने के लिए मेहनती छात्र ज़मीन आसमान एक कर देंगे"),
    ("The sudden catastrophic news fell like a lightning bolt upon family", "अचानक आई दुखद खबर परिवार के ऊपर आकाशीय बिजली बनकर टूट पड़ी"),
    ("The melodious performance of the singer added four moons to evening", "सुरीले गायक की शानदार प्रस्तुति ने सांस्कृतिक शाम में चार चाँद लगा दिए"),
    ("The golden eagles were soaring high in the vast azure sky", "सुनहरी चीलें नीले विशाल आसमान में बहुत ऊँचाई पर उड़ रही थीं"),
    ("The bright evening star was shining like a diamond in west", "शाम का चमकीला तारा पश्चिम के आकाश में हीरे की तरह चमक रहा था"),
    ("The sudden flash of lightning illuminated the dark stormy countryside", "बिजली की तेज़ कौंध ने तूफानी रात में पूरे ग्रामीण इलाके को चमका दिया"),
    ("The dark thunderclouds have covered the blue vault of the sky", "काले कजरारे बादलों ने नीले आसमान को पूरी तरह अपनी चादर में ढक लिया है"),
    ("The ancient astrologer was calculating the celestial movements of planets", "प्राचीन ज्योतिषी रात में ग्रहों और तारों की चाल का सूक्ष्म अध्ययन कर रहा था"),
    ("The silver moon has scattered serene white light upon the earth", "सफेद चाँद ने पृथ्वी पर अपनी शीतल और शांत चाँदनी बिखेर दी है"),
    ("If the dark clouds disperse we might observe the falling meteor", "अगर घने बादल छँट जाएँ तो हम टूटते हुए तारे को देख सकते हैं"),
    ("The sudden deafening thunderclap terrified the grazing cattle in meadow", "आसमान में अचानक हुए भीषण वज्रपात ने मैदान में चरते पशुओं को डरा दिया"),
    ("The royal dome rose majestically toward the clear blue sky", "महल का भव्य गुंबद स्वच्छ नीले आसमान की ओर शान से सिर उठाए खड़ा था"),
    ("The little child was gazing in wonder at the twinkling night stars", "छोटा बालक रात के टिमटिमाते तारों को विस्मय से निहार रहा था"),
    ("The lightning struck the tall pine tree and split the trunk apart", "आकाशीय बिजली ने ऊँचे चीड़ के पेड़ पर गिरकर उसके तने को चीर दिया"),
    ("The morning sun painted the eastern sky with glorious crimson hues", "सुबह के सूरज ने पूर्वी आसमान को सुनहरे और लाल रंगों से सजा दिया"),
    ("The flock of migratory cranes flew in a V shape across sky", "प्रवासी सारसों का दल आसमान में सुंदर कतार बनाकर उड़ रहा था"),
    ("The shooting star streaked across the dark velvet of midnight sky", "टूटता हुआ तारा आधी रात के मखमली आसमान में लकीर खींचता हुआ गुज़रा"),
    ("The stormy sky was rumbling continuously throughout the wet afternoon", "बरसाती दोपहरी में बादलों से भरा आसमान लगातार गड़गड़ाहट कर रहा था"),
    ("The rainbow arched gracefully across the eastern sky after rain", "बारिश थमने के बाद पूर्वी आसमान में सुंदर सतरंगी इंद्रधनुष खिल उठा"),
    ("The old astronomer spent forty years mapping the distant constellations", "वृद्ध खगोलशास्त्री ने दूर के नक्षत्रों का नक्शा बनाने में चालीस वर्ष बिताए"),
    ("The brilliant sun disperses the thick morning fog from the valley", "तेजस्वी सूर्य पहाड़ी घाटी से सुबह के घने कोहरे को छांट देता है"),
    ("The full moon will be illuminating the white marble of the temple", "पूर्णिमा का चाँद मंदिर के सफेद संगमरमर को दिव्य रोशनी से नहलाएगा"),
    ("The lightning flickered ominously along the jagged mountain ridge", "पहाड़ी कटक के ऊपर बिजली भयानक रूप से बार बार चमक रही थी"),
    ("The boundless sky reminds the philosopher of infinite cosmic space", "अनंत आसमान दार्शनिक को ब्रह्मांड के असीम विस्तार की याद दिलाता है"),
    ("The heavy gray clouds had cast a somber twilight over village", "गहरे सलेटी बादलों ने दोपहर में ही गाँव पर गोधूलि का अंधेरा फैला दिया था"),
    ("The red sunset glow was fading slowly along the western horizon", "पश्चिमी क्षितिज पर सूरज की लालिमा धीरे धीरे शांत हो रही थी"),
    ("The loud crack of thunder startled the flock of resting pigeons", "आसमान की भीषण गर्जना ने सुस्ताते कबूतरों के झुंड को चौंका दिया"),
    ("The northern lights danced in shimmering green ribbons across sky", "उत्तरी ध्रुव के आसमान में हरी आभा की सुंदर तरंगें नाच रही थीं"),
    ("The clear night sky displays millions of glittering celestial gems", "स्वच्छ रात का आसमान लाखों चमकते हुए तारों का खजाना दिखाता है"),
    ("The sudden cloudburst poured torrents of water upon the city", "आसमान फटने से नगर के ऊपर मूसलाधार पानी की बाढ़ सी आ गई"),
    ("The morning star heralds the arrival of the auspicious new dawn", "भोर का तारा पूर्व दिशा में एक नए पावन सवेरे का संदेश लाता है"),
    ("The golden crescent moon was cradled in the arms of dusk", "शाम के धुंधलके में दूज का चाँद हँसिए की तरह चमक रहा था"),
    ("The dense bank of storm clouds blocked the warmth of the sun", "तूफानी बादलों के घने घेरे ने सूरज की धूप को पूरी तरह रोक दिया"),
    ("The royal standard fluttered proudly against the backdrop of blue sky", "शाही ध्वज नीले आसमान की पृष्ठभूमि में शान से लहरा रहा था"),
    ("The vast sky embraces all living beings without any prejudice", "विशाल आसमान बिना किसी भेद के सभी प्राणियों को अपने में समेटता है"),
    ("The celestial lightning flash lasted merely for a fraction of second", "आसमानी बिजली की कौंध केवल एक पल के लिए चमकी और गायब हो गई"),

    # 176-215: ज़मीन, मिट्टी, धूल, पाताल (Earth, Soil, Dust - Idioms & Tenses)
    ("The proud victor walked so haughtily as if feet did not touch ground", "अहंकार के मारे विजयी राजा के पैर ज़मीन पर नहीं पड़ रहे थे"),
    ("The severe earthquake mixed the ancient proud palaces into dust", "भीषण भूकंप ने राजा के सुंदर महलों को मिट्टी में मिला दिया"),
    ("The defeated army had to lick the dust before the strong citadel", "शक्तिशाली किले के आगे पराजित हमलावरों को धूल चाटनी पड़ी"),
    ("The forgotten glory of the old empire faded away into dusty obscurity", "पुराने साम्राज्य का प्राचीन वैभव समय के साथ धूल में मिल गया"),
    ("The humble devotee kissed the sacred dust of the holy threshold", "विनम्र भक्त ने पवित्र मंदिर की चौखट की पावन धूल को चूमा"),
    ("The prices of essential grains had fallen to the nether depths", "अत्यधिक पैदावार के कारण अनाज के दाम पाताल में पहुँच गए"),
    ("The mother earth provides rich nourishment to all living creatures", "धरती माता सभी जीवित प्राणियों को भरपूर अन्न और पोषण देती है"),
    ("The fertile soil of the river valley yields three rich harvests yearly", "नदी घाटी की उपजाऊ मिट्टी साल में तीन भरपूर फसलें देती है"),
    ("The hardworking plowman had turned the rich black loam for sowing", "मेहनती हलवाहे ने बुआई के लिए उपजाऊ काली मिट्टी को उलट पलट दिया था"),
    ("The potter will shape delicate earthen cups upon his revolving wheel", "कुम्हार अपने घूमते चाक पर मिट्टी के सुंदर कुल्हड़ बनाएगा"),
    ("The fragrant smell of parched earth rose after the first rain shower", "पहली बारिश की बूँदें पड़ते ही तपी हुई मिट्टी से सौंधी खुशबू उठी"),
    ("The heavy iron anchor sank deep into the muddy sea bottom", "लोहे का भारी लंगर समंदर की कीचड़ भरी तलहटी में धँस गया"),
    ("The fierce wind blew thick clouds of dust across the dry highway", "तेज़ हवा ने सूखे राजमार्ग पर धूल के घने गुबार उड़ा दिए"),
    ("The loyal soldier promised to defend every inch of his native soil", "वफादार सिपाही ने अपनी मातृभूमि की एक एक इंच मिट्टी की रक्षा की"),
    ("If the drought continues the productive soil will turn to dust", "अगर सूखा जारी रहा तो उपजाऊ ज़मीन बंजर धूल में बदल जाएगी"),
    ("The innocent child was building miniature sandcastles on the beach", "मासूम बालक नदी के किनारे गीली रेत के छोटे महल बना रहा था"),
    ("The stubborn roots of the oak tree penetrated deep into rocky earth", "बलूत के पेड़ की मज़बूत जड़ें पथरीली ज़मीन के भीतर गहराई तक गईं"),
    ("The peasant kneaded the damp clay to plaster the village cottage walls", "किसान ने झोपड़ी की दीवारों की लिपाई के लिए गीली मिट्टी तैयार की"),
    ("The golden grains of wheat were scattered upon the threshing floor", "खलिहान की समतल ज़मीन पर सुनहरे गेहूँ के दाने बिखरे हुए थे"),
    ("The underground spring gushed forth from the depths of dry earth", "सूखी ज़मीन की गहराइयों से मीठे पानी का शीतल सोता फूट पड़ा"),
    ("The red dust of the cart track coated the leaves of roadside trees", "कच्चे रास्ते की लाल धूल ने सड़क किनारे के पेड़ों को ढक दिया था"),
    ("The wise elder advised the youth to stay rooted firmly to ground", "बुद्धिमान बुज़ुर्ग ने युवा को हमेशा ज़मीन से जुड़े रहने की सीख दी"),
    ("The ancient artifacts lay buried under five layers of river silt", "प्राचीन धरोहरें नदी की गाद की पाँच परतों के नीचे दबी पड़ी थीं"),
    ("The energetic boy ran barefoot upon the soft green grass of courtyard", "उत्साही बालक आँगन की कोमल हरी घास की ज़मीन पर नंगे पैर दौड़ा"),
    ("The volcanic ash enriched the agricultural soil around the crater", "ज्वालामुखी की राख ने आसपास की कृषि भूमि को अत्यंत उपजाऊ बना दिया"),
    ("The heavy bullock cart wheels made deep ruts in the wet mud", "बैलगाड़ी के भारी पहियों ने गीली मिट्टी में गहरे निशान बना दिए"),
    ("The humble ascetic slept upon the bare hard floor without mattress", "विनम्र तपस्वी बिना बिछौने के कठोर ज़मीन पर ही विश्राम करता था"),
    ("The diligent gardener loosened the compact earth around rose roots", "माली ने गुलाब के पौधों के चारों ओर की सख्त मिट्टी को खुरपी से ढीला किया"),
    ("The dust raised by the galloping cavalry darkened the noon sun", "दौड़ती सेना के घोड़ों के खुरों की धूल ने दोपहर के सूरज को ढक दिया"),
    ("The landslide dumped thousands of tons of earth upon mountain road", "भूस्खलन ने पहाड़ी सड़क पर हज़ारों टन मिट्टी और पत्थर गिरा दिए"),
    ("The sacred soil of the motherland inspires deep devotion in patriots", "मातृभूमि की पावन माटी देशप्रेमियों के दिलों में गहरा अनुराग जगाती है"),
    ("The small earthworm aerates the garden soil making it porous", "छोटा केंचुआ बगीचे की मिट्टी को भुरभुरा बनाकर उपजाऊ बनाता है"),
    ("The deep cracks appeared in the parched clay during summer drought", "गर्मी के सूखे में खेत की सूखी मिट्टी में गहरी दरारें पड़ गईं"),
    ("The miner descended hundreds of feet into the dark earth for coal", "कोयला निकालने के लिए मजदूर ज़मीन के सैकड़ों फीट नीचे उतरा"),
    ("The dust storm coated the marble monuments with yellow desert powder", "रेतीले तूफान ने संगमरमर के स्मारकों पर पीली धूल की परत चढ़ा दी"),
    ("The sweet smelling wet soil reminds the poet of village monsoons", "गीली मिट्टी की सोंधी महक कवि को गाँव के सावन की याद दिलाती है"),
    ("The sturdy brick foundations rest securely upon the bedrock of earth", "मकान की मज़बूत ईंटों की नींव चट्टानी ज़मीन पर टिकी हुई है"),
    ("The farmer smoothed the ploughed earth using a heavy wooden beam", "किसान ने भारी पाटे की मदद से जोते हुए खेत की मिट्टी को समतल किया"),
    ("The sacred ashes were consigned to the holy river with prayers", "पवित्र भस्म को आदर के साथ बहती नदी की जलधारा में विसर्जित किया गया"),
    ("The green shoots of barley sprouted from the warm damp earth", "गीली मिट्टी की कोख से जौ के नन्हें हरे अंकुर फूट पड़े"),

    # 216-250: पहाड़, धूप, छाँव, बादल, बरखा (Mountain, Sun/Shadow, Clouds, Rain - Idioms & Tenses)
    ("The foolish neighbor made a huge mountain out of a small mustard seed", "छोटी सी बात पर मूर्ख पड़ोसी ने राई का पहाड़ बना दिया"),
    ("The prolonged investigation dug up a mountain only to catch a mouse", "महीनों की लंबी जाँच में खोदा पहाड़ निकली चुहिया वाली बात हुई"),
    ("A mountain of unbearable sorrow crashed upon the lonely widow", "अकेली बेसहारा महिला के ऊपर दुखों का भारी पहाड़ टूट पड़ा"),
    ("Human life is a fleeting game of pleasant sunshine and shadow", "मानव जीवन सुख और दुख की धूप छाँव का अनोखा खेल है"),
    ("Those empty clouds that thunder loudly rarely bring beneficial rain", "जो बादल बहुत गरजते हैं वे कभी झमाझम बरसते नहीं हैं"),
    ("Dark clouds of impending war gathered along the vulnerable border", "कमज़ोर सीमा के ऊपर विनाशकारी युद्ध के काले बादल मंडराने लगे"),
    ("The patient traveler will have crossed the snow covered mountain pass", "धैर्यवान यात्री बर्फ़ से ढके ऊँचे पहाड़ी दर्रे को पार कर चुका होगा"),
    ("The towering granite peaks were touched by the golden morning light", "विशाल ग्रेनाइट की पहाड़ियाँ सुबह की सुनहरी धूप से चमक उठीं"),
    ("The heavy monsoon clouds poured continuous torrential rain for three days", "सावन के घने बादलों ने तीन दिन तक लगातार मूसलाधार बारिश बरसाई"),
    ("The weary pilgrim rested under the cool shade of the roadside banyan", "थके हुए तीर्थयात्री ने सड़क किनारे बरगद की ठंडी छाँव में विश्राम किया"),
    ("The bright sunshine melted the thick ice sheets upon the mountain slope", "चमकीली धूप ने पहाड़ी ढलान पर जमी बर्फ़ की मोटी चादर को पिघला दिया"),
    ("The dark storm clouds had blocked the direct rays of the sun", "काले तूफानी बादलों ने दोपहर के सूरज की सीधी किरणों को रोक दिया था"),
    ("If the rain stops the stranded villagers might repair the road", "अगर बारिश रुक जाए तो फँसे हुए ग्रामीण सड़क की मरम्मत कर सकते हैं"),
    ("The towering Himalayan mountain range protects the country from northern cold", "विशाल हिमालय पर्वतमाला देश को उत्तर की बर्फीली हवाओं से बचाती है"),
    ("The dancing peacock spreads its vibrant feathers when the clouds rumble", "बादलों की गड़गड़ाहट सुनकर मोर अपने रंग बिरंगे पंख फैलाकर नाचता है"),
    ("The playful children were running across the puddles after the shower", "बारिश थमने के बाद चंचल बच्चे पानी के गड्ढों में उछलकूद कर रहे थे"),
    ("The shepherd guided his flock to the sunny southern hillside for pasture", "चरवाहे ने अपनी भेड़ों को धूप वाली दक्षिणी पहाड़ी ढलान पर पहुँचाया"),
    ("The mountain stream was tumbling down the steep rocks with foam", "पहाड़ी झरना झाग उड़ाता हुआ सीधी चट्टानों से नीचे गिर रहा था"),
    ("The thick cloud of white mist covered the sleepy valley at sunrise", "सूर्योदय के समय घने सफेद कोहरे ने पूरी शांत घाटी को ढक लिया"),
    ("The sudden cloudburst had washed away several stone terrace farms", "अचानक हुए बादल फटने से पहाड़ के कई सीढ़ीदार खेत बह गए थे"),
    ("The gentle rain nourishes the thirsty saplings in the nursery", "रिमझिम बारिश पौधशाला के नन्हें प्यासे पौधों को नया जीवन देती है"),
    ("The ancient pine tree offered welcome shade to the tired woodsman", "पुराने चीड़ के पेड़ ने थके हुए लकड़हारे को सुखद छाँव प्रदान की"),
    ("The snowy mountain summits sparkled brilliantly under the midday sun", "बर्फ़ीली पर्वत चोटियाँ दोपहर की तेज़ धूप में हीरे जैसी चमक रही थीं"),
    ("The sudden thunderstorm forced the picnickers to seek shelter in cave", "अचानक आई आंधी बारिश ने सैलानियों को गुफा में शरण लेने पर विवश किया"),
    ("The farmer looked anxiously at the empty sky hoping for rain clouds", "किसान बारिश के बादलों की उम्मीद में सूने आसमान की ओर देखता रहा"),
    ("The dense grey clouds rumbled with deep reverberating bass across hills", "घने सलेटी बादल पहाड़ियों के बीच गंभीर गर्जना के साथ गूँज रहे थे"),
    ("The bright rainbow arched over the waterfall creating a magical halo", "झरने के ऊपर सतरंगी इंद्रधनुष ने एक जादुई छटा बिखेर दी"),
    ("The mountain climbers pitched their sturdy canvas tents on the ridge", "पर्वतारोहियों ने पहाड़ी कटक पर अपने मज़बूत तंबू गाड़ दिए"),
    ("The gentle morning sunshine warmed the dew drenched flower petals", "सुबह की गुनगुनी धूप ने ओस से भीगी फूलों की पंखुड़ियों को सुखाया"),
    ("The torrential mountain torrent was roaring like a caged beast", "तेज़ पहाड़ी नाला पिंजरे में बंद दहाड़ते शेर की तरह उफन रहा था"),
    ("The shadow of the great peak lengthened across the green valley", "शाम ढलते ही विशाल पर्वत की लंबी परछाईं हरी घाटी पर फैल गई"),
    ("The rainy season brings abundant greenery to the barren countryside", "वर्षा ऋतु बंजर ग्रामीण इलाके में चारों ओर हरियाली बिखेर देती है"),
    ("The dark thunderclouds unleashed hail stones upon the ripe wheat fields", "काले बादलों ने पकी हुई गेहूँ की फसलों पर ओलों की बौछार कर दी"),
    ("The mountain guides navigate the narrow rocky ledges with practiced ease", "पहाड़ी मार्गदर्शक संकरी पथरीली पगडंडियों पर बिना हिचकिचाहट के चलते हैं"),
    ("The pleasant sunshine of spring brought out hundreds of yellow butterflies", "वसंत की सुखद धूप ने सरसों के खेतों में पीली तितलियों को आकर्षित किया"),
]

def main():
    # Setup ga module
    import importlib.util
    spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
    ga = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ga)

    DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
    ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')

    # Load existing hi sentences across all previous phrase files
    existing_hi = {}
    for p in sorted((ROOT / "data").glob("phrases*.json")):
        if p.name == "phrases28.json":
            continue
        data = json.load(open(p))
        for item in data:
            existing_hi[item["hi"]] = (p.name, item["id"])

    errors = []
    seen_hi = set()
    out = []

    if len(PAIRS) != 250:
        errors.append(f"Expected 250 pairs, got {len(PAIRS)}")

    for idx, (en, hi) in enumerate(PAIRS, start=1):
        sid = f"p28s{idx:03d}"
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

    if errors:
        print(f"FOUND {len(errors)} ERRORS:")
        for e in errors[:25]:
            print("  ", e)
        sys.exit(1)

    out_file = ROOT / "data" / "phrases28.json"
    out_file.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"Successfully generated {out_file} with {len(out)} sentences.")

    # Update manifest.json
    manifest_file = ROOT / "data" / "manifest.json"
    manifest = json.load(open(manifest_file))
    manifest["files"] = [f for f in manifest["files"] if f["file"] != "data/phrases28.json"]
    manifest["files"].append({
        "file": "data/phrases28.json",
        "count": len(out)
    })
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated {manifest_file} with data/phrases28.json (count: {len(out)}).")

if __name__ == "__main__":
    main()
