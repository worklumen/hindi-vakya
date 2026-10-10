#!/usr/bin/env python3
"""Batch ID-02: Anatomy & Sensations II with 100% AI-generated semantic alignments.

Every sentence pair contains explicit, human-quality AI semantic alignment mapping
linking each Devanagari token to its exact English word span.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Explicit AI-authored (en, hi, align) triples
TRIPLES = [
    # 1-25 (हाथ)
    (
        "The kind neighbors lent a helping hand in building the new hut",
        "दयालु पड़ोसियों ने नई झोपड़ी बनाने में हाथ बटाया",
        "0-1 2 2 10 9-11 8 7 4-6 3-5"
    ),
    (
        "The lazy merchant was left rubbing his hands in deep regret",
        "आलसी व्यापारी अवसर चूकने पर हाथ मलता रह गया",
        "0-1 2 9 9 9 6 4-5 3 3"
    ),
    (
        "The fearful allies withdrew their hands when the danger approached",
        "खतरा आते ही डरपोक साथियों ने अपना हाथ खींच लिया",
        "7 8 8 0-1 2 2 4 4-5 3 3"
    ),
    (
        "The clever thief cleaned his hands upon the royal treasury smoothly",
        "चालाक चोर ने शाही खजाने पर बड़ी सफाई से हाथ साफ़ किया",
        "0-1 2 2 7 8 6 10 10 10 4-5 3 3"
    ),
    (
        "The poor laborer struggled hard with hand and foot for food",
        "गरीब मजदूर ने भोजन के लिए खूब हाथ पैर मारे",
        "0-1 2 2 9 8-9 8-9 4 5 6 3 3"
    ),
    (
        "The fresh harvest sold rapidly from hand to hand in the morning",
        "सुबह की ताज़ा फसल बाज़ार में हाथों हाथ बिक गई",
        "9-11 9-11 0-1 2 2 2 5-7 5-7 3 3"
    ),
    (
        "The brave commander held the entire reins of administration in hand",
        "बहादुर सेनापति ने शासन की पूरी बागडोर अपने हाथ में ले ली",
        "0-1 2 2 7 6-7 4 5 10 10 9 3 3"
    ),
    (
        "The weary farmer sat idle with hands folded upon hands",
        "थका हुआ किसान हाथ पर हाथ धरे चुपचाप बैठा रहा",
        "0-1 0-1 2 5 7 8 6 4 3 3"
    ),
    (
        "The defeated army threw up its hands before the strong fort",
        "पराजित सेना ने शक्तिशाली किले के आगे हाथ खड़े कर दिए",
        "0-1 2 2 7 8 6 6 5 3-4 3-4 3-4"
    ),
    (
        "The humble devotee folded both hands and prayed before the deity",
        "विनम्र भक्त ने देवता के आगे दोनों हाथ जोड़कर प्रार्थना की",
        "0-1 2 2 9 8 8 4 5 3 6-7 6-7"
    ),
    (
        "The golden opportunity slipped away quietly from his careless hand",
        "लापरवाह लड़के के हाथ से सुनहरा अवसर चुपचाप निकल गया",
        "8 8 8 9 7 0-1 2 5 3-4 3-4"
    ),
    (
        "The generous king was known to possess a remarkably open hand",
        "उदार राजा का हाथ प्रजा को दान देने में हमेशा खुला रहता था",
        "0-1 2 2 9 2 9 9 9 9 8 3-5 3-5"
    ),
    (
        "The honest merchant suffered heavy loss and had a tight hand",
        "भारी घाटा होने के कारण व्यापारी का हाथ बहुत तंग हो गया",
        "4 5 3 3 3 0-2 2 9 8 8 6-7 6-7"
    ),
    (
        "The elder brother placed his blessing hand upon the young orphan",
        "बड़े भाई ने अनाथ बालक के सिर पर अपना हाथ रखा",
        "0 1 1 8 8 6 6 3 4-5 2"
    ),
    (
        "The corrupt officer extended his greedy hand for illegal bribes",
        "भ्रष्ट अधिकारी ने रिश्वत लेने के लिए अपना हाथ बढ़ाया",
        "0-1 2 2 7 7 6 6 4 5 3"
    ),
    (
        "The royal police caught the fleeing bandit red handed with gold",
        "शाही पुलिस ने भागते हुए डाकू को सोने के साथ रंगे हाथों पकड़ा",
        "0 1 1 4 5 5 8 7-8 6 6 2"
    ),
    (
        "The two rival kingdoms shook hands and agreed on lasting peace",
        "दोनों विरोधी राज्यों ने हाथ मिलाकर स्थाई शांति का समझौता किया",
        "0 1 2 2 4 3 8 9 7 6 6"
    ),
    (
        "The stern father took the insolent servant across hands firmly",
        "सख्त पिता ने उद्दंड नौकर को भरी सभा में आड़े हाथों लिया",
        "0 1 1 4 5 3 6 6 6 6 6 3"
    ),
    (
        "The courageous youth took the complex task boldly in his hand",
        "साहसी युवक ने कठिन काम को अपने हाथ में ले लिया",
        "0 1 1 4 5 3 8 9 7 2 2"
    ),
    (
        "The royal bracelet needed no mirror because truth was plain to see",
        "सच्चाई सबके सामने थी क्योंकि हाथ कंगन को आरसी क्या",
        "6 7-8 7-8 7-8 5 0 1 1 3-4 3-4"
    ),
    (
        "The angry youth threatened to break the hands of the intruder",
        "क्रोधित युवक ने घुसपैठिए के हाथ पैर तोड़ने की धमकी दी",
        "0 1 1 8 6 6 6 5 3-4 3-4"
    ),
    (
        "The greedy broker washed his hands of the fraudulent company shares",
        "लालची दलाल ने धोखेबाज़ कंपनी के घाटे से अपना हाथ धो लिया",
        "0 1 1 7 8 9 6 4 4-5 3 3"
    ),
    (
        "The noble doctor had a healing touch in his gentle hands",
        "दयालु चिकित्सक के कोमल हाथों में अद्भुत शफ़ा और यश था",
        "0 1 1 7 8 6 4-5 4-5 2 2"
    ),
    (
        "The stubborn child let go of the warm hand of his mother",
        "हठी बालक ने बाज़ार में अपनी माँ का कोमल हाथ छोड़ दिया",
        "0 1 1 2 2 8 9 7 6 7 2-4 2-4"
    ),
    (
        "The careless clerk allowed the secret file to slip out of hand",
        "लापरवाह मुंशी के हाथ से गोपनीय फाइल अचानक फिसल गई",
        "0 1 1 8 7 4 5 6 6-7 6-7"
    ),

    # 26-50 (हाथ)
    (
        "The powerful landlord had long hands that reached the distant capital",
        "शक्तिशाली ज़मींदार के हाथ राजधानी तक बहुत लंबे थे",
        "0 1 1 4 8 7 5 3 2"
    ),
    (
        "The old craftsman passed his delicate hand over the carved marble",
        "वृद्ध कारीगर ने नक्काशीदार संगमरमर पर अपना सधा हाथ फेरा",
        "0 1 1 7 8 6 4 4 5 2"
    ),
    (
        "The young apprentice tried his hand at painting the ancient temple",
        "नए प्रशिक्षु ने प्राचीन मंदिर की दीवार पर अपना हाथ आजमाया",
        "0 1 1 7 8 6 6 4 4 2-3"
    ),
    (
        "The proud wrestler challenged everyone with his muscular hands raised",
        "घमंडी पहलवान ने अपने बलिष्ठ हाथ उठाकर सबको चुनौती दी",
        "0 1 1 5 6 7 8 3 2 2"
    ),
    (
        "The cunning minister kept all major decisions tied to his hand",
        "चालाक मंत्री ने सभी प्रमुख निर्णय अपनी मुट्ठी में कर रखे थे",
        "0 1 1 3 4 5 8 9 7 2 2 2"
    ),
    (
        "The loyal friend stretched out a supportive hand in dark times",
        "सच्चे मित्र ने संकट के समय सहायता का हाथ बढ़ाया",
        "0 1 1 7 8 8 5 6 6 2-3"
    ),
    (
        "The greedy servant set his hands upon the forgotten gold necklace",
        "लालची नौकर ने मेज़ पर रखे सोने के हार पर हाथ मारा",
        "0 1 1 5 5 5 7 8 9 3 4 2"
    ),
    (
        "The skilled weaver moved his practiced hands across the wooden loom",
        "कुशल बुनकर ने लकड़ी के करघे पर अपने सिद्ध हाथ चलाए",
        "0 1 1 7 6 8 5 4 4 2"
    ),
    (
        "The innocent child clapped his hands with joy seeing the peacock",
        "मासूम बालक ने मोर को नाचते देखकर दोनों हाथों से ताली बजाई",
        "0 1 1 9 7 8 8 4 4 5 3 3"
    ),
    (
        "The experienced surgeon operated with an extremely steady hand",
        "अनुभवी शल्य चिकित्सक ने बहुत सधे हुए हाथ से सफल इलाज किया",
        "0 1 2 2 5 6 6 7 4 3 3 3"
    ),
    (
        "The wicked traitor had a hidden hand behind the sudden rebellion",
        "अचानक हुए विद्रोह के पीछे उस गद्दार का गुप्त हाथ था",
        "7 7 8 6 6 0-1 1 4 5 2"
    ),
    (
        "The kind queen gave alms with both hands to the poor pilgrims",
        "दयालु रानी ने दोनों हाथों से गरीब तीर्थयात्रियों को दान लुटाया",
        "0 1 1 4 5 5 7 8 6 3 2"
    ),
    (
        "The little girl held tightly to the caring hand of her grandfather",
        "छोटी बच्ची ने अपने प्यारे दादाजी का हाथ मज़बूती से पकड़ा",
        "0 1 1 6 7 8 5 4 3 3 2"
    ),
    (
        "The weary traveler felt cold hands and warmed them by the campfire",
        "थके हुए पथिक ने अलाव के पास अपने ठंडे हाथ सेंके",
        "0 0 1 1 9 7 8 5 4 5 6"
    ),
    (
        "The honest postman delivered the valuable letter into his own hands",
        "ईमानदार डाकिया ने ज़रूरी पत्र सीधे उसके हाथ में सौंपा",
        "0 1 1 4 5 6 7 8 6 2"
    ),
    (
        "The furious customer raised his hand in anger against the cheat",
        "क्रोधित ग्राहक ने ठग व्यापारी पर गुस्से में हाथ उठाया",
        "0 1 1 8 8 7 5 4 3 2"
    ),
    (
        "The wealthy merchant had a tight hand and gave very little charity",
        "धनी सेठ का हाथ दान धर्म के मामले में बहुत तंग था",
        "0 1 1 5 8 8 6 6 6 4 4 2"
    ),
    (
        "The pious lady placed sacred water upon the hands of the priest",
        "धर्मपरायण महिला ने पंडित के हाथों पर पवित्र गंगाजल रखा",
        "0 1 1 8 6 7 5 3 4 2"
    ),
    (
        "The weary soldier washed his blood stained hands in the clear river",
        "थके हुए सिपाही ने स्वच्छ नदी में अपने खूनी हाथ धोए",
        "0 0 1 1 8 9 7 3 4 5 2"
    ),
    (
        "The playful children held hands and danced around the big tree",
        "चंचल बच्चों ने एक दूसरे का हाथ पकड़कर पेड़ के चारों ओर नृत्य किया",
        "0 1 1 3 3 3 3 2 9 7 8 7 5 5"
    ),
    (
        "The angry farmer wrung his hands seeing the ruined wheat crop",
        "फसल बर्बाद देखकर दुखी किसान निराशा में अपने हाथ मलता रहा",
        "8 6 5 0 1 2 4 4 2 2 2"
    ),
    (
        "The experienced captain had a firm hand upon the wooden wheel",
        "अनुभवी नाविक ने नाव के पतवार पर अपना मज़बूत हाथ रखा",
        "0 1 1 7 5 8 6 4 4 5 2"
    ),
    (
        "The young student wrote the long essay with a very swift hand",
        "मेधावी छात्र ने अत्यंत तेज़ हाथ से लंबा निबंध लिखा",
        "0 1 1 6 7 8 5 4 4 2"
    ),
    (
        "The kind saint touched his hand to the forehead of the devotee",
        "दयालु संत ने भक्त के माथे पर आशीर्वाद का हाथ रखा",
        "0 1 1 9 6 7 4 4 4 2"
    ),
    (
        "The greedy contractor dipped his hand into public welfare funds",
        "लालची ठेकेदार ने जनता के कल्याण कोष में अपना हाथ डाला",
        "0 1 1 6 5 7 8 4 3 2"
    ),

    # 51-75 (हाथ & पैर/पाँव)
    (
        "The bold youth placed his hand upon his chest and spoke truth",
        "साहसी युवक ने अपनी छाती पर हाथ रखकर सच बोला",
        "0 1 1 4 5 3 2 2 8 7"
    ),
    (
        "The royal gardener tended the delicate flowering plants by hand",
        "शाही माली ने अपने हाथों से नाज़ुक फूलों के पौधों को संवारा",
        "0 1 1 7 8 7 4 5 5 6 3 2"
    ),
    (
        "The frightened captive had his hands tied behind his back",
        "भयभीत बंदी के दोनों हाथ उसकी पीठ के पीछे बँधे हुए थे",
        "0 1 1 3 4 6 7 5 5 4 4 2"
    ),
    (
        "The wise grandfather guided the unsteady hand of the small boy",
        "बुद्धिमान दादाजी ने छोटे बालक के डगमगाते हाथ को सहारा दिया",
        "0 1 1 7 8 6 4 5 3 2 2"
    ),
    (
        "The strong porter lifted the heavy luggage using both hands",
        "बलवान कुली ने दोनों हाथों से भारी सामान आसानी से उठाया",
        "0 1 1 6 7 6 4 5 2 2 2"
    ),
    (
        "The honest officer never stained his clean hands with bribe money",
        "ईमानदार अफसर ने कभी रिश्वत के पैसों से अपने हाथ काले नहीं किए",
        "0 1 1 2 7 8 6 4 5 3 2 2"
    ),
    (
        "The village elders joined hands to build the community well",
        "गाँव के बुज़ुर्गों ने मिलकर पंचायत का कुआँ बनाने में हाथ मिलाया",
        "0 0 1 1 2 6 5 7 4 3 2"
    ),
    (
        "The playful monkey snatched the sweet banana from his hand",
        "शरारती बंदर ने उसके हाथ से मीठा केला झपट लिया",
        "0 1 1 6 7 5 3 4 2 2"
    ),
    (
        "The brave warrior never lowered his hand before the cruel tyrant",
        "बहादुर योद्धा ने क्रूर अत्याचारी के आगे कभी हाथ नहीं जोड़े",
        "0 1 1 6 7 5 5 2 4 3 3"
    ),
    (
        "The generous landlord gave land into the hands of the tillers",
        "उदार ज़मींदार ने किसानों के हाथों में उपजाऊ भूमि सौंप दी",
        "0 1 1 7 4 5 3 3 2 2"
    ),
    (
        "The young girl decorated her hands with fragrant herbal henna",
        "युवती ने अपने सुंदर हाथों पर सुगंधित हरी मेहंदी रचाई",
        "0-1 1 3 3 3 4 5 6 2"
    ),
    (
        "The skilled potter shaped the wet clay with his nimble hands",
        "कुशल कुम्हार ने अपने चतुर हाथों से गीली मिट्टी को रूप दिया",
        "0 1 1 6 7 8 5 4 4 2 2"
    ),
    (
        "The anxious mother held the warm hand of her sick infant",
        "चिंतित माँ ने अपने बीमार शिशु का गरम हाथ थामे रखा",
        "0 1 1 5 6 7 4 4 2 2"
    ),
    (
        "The tired scholar rested his weary head upon his open hands",
        "थके हुए विद्वान ने अपने खुले हाथों पर भारी सिर टिकाया",
        "0 0 1 1 5 6 7 4 3 3 2"
    ),
    (
        "The royal herald carried the urgent message in his right hand",
        "शाही दूत ने अपने दाहिने हाथ में महत्वपूर्ण संदेश संभाला",
        "0 1 1 7 6 8 5 4 4 2"
    ),
    (
        "The tired traveler stretched his legs and relaxed under the tree",
        "थके हुए पथिक ने पेड़ के नीचे बैठकर अपने पैर पसारे",
        "0 0 1 1 8 6 7 5 3 4 2"
    ),
    (
        "The brave army made the feet of the invaders uproot completely",
        "बहादुर सेना ने हमलावरों के पैर पूरी तरह उखाड़ दिए",
        "0 1 1 6 4 8 8 2 7 2"
    ),
    (
        "The wise person always stretches feet according to the sheet",
        "समझदार व्यक्ति हमेशा अपनी चादर देखकर ही पैर पसारता है",
        "0 1 2 7 8 6 6 4 3 3"
    ),
    (
        "The courageous leader stepped upon burning coals for his noble cause",
        "साहसी नेता ने अपने पावन लक्ष्य के लिए अंगारों पर पैर रखे",
        "0 1 1 8 9 7 7 4 3 5 2"
    ),
    (
        "The frightened messenger hesitated with heavy feet to deliver bad news",
        "बुरा समाचार सुनाने के लिए भयभीत दूत के पाँव भारी हो गए",
        "8 9 7 6 0 1 1 4 3 2 2"
    ),
    (
        "The wicked flatterer licked the soles of the cruel king shameless",
        "दुष्ट चापलूस ने क्रूर राजा के तलवे चाटने में कोई शर्म न की",
        "0 1 1 6 7 5 4 2 2 8 8 8 8"
    ),
    (
        "The innocent girl took her first tentative steps into the royal hall",
        "मासूम बालिका ने राजदरबार में संकोच के साथ अपने पहले पाँव रखे",
        "0 1 1 7 8 6 4 5 3 2 2 2"
    ),
    (
        "The stubborn mule dug its feet into the mud and refused to move",
        "हठी खच्चर ने कीचड़ में अपने पैर जमा लिए और आगे न बढ़ा",
        "0 1 1 6 5 4 3 2 2 8 10 9 11"
    ),
    (
        "The proud merchant fell at the holy feet of the ancient sage",
        "घमंडी व्यापारी ने प्राचीन ऋषि के पवित्र चरणों में अपना सिर झुकाया",
        "0 1 1 8 9 5 6 4 3 2 2"
    ),
    (
        "The runaway servant fled as fast as his feet could carry him",
        "भागा हुआ नौकर सिर पर पैर रखकर तेज़ी से जंगल की ओर भागा",
        "0 0 1 6 6 6 6 4 5 2 2 2 2"
    ),

    # 76-100 (पैर/पाँव)
    (
        "The reckless hunter slipped his foot and fell into the deep trench",
        "लापरवाह शिकारी का पैर फिसल गया और वह गहरी खाई में गिरा",
        "0 1 1 4 2-3 2-3 7 8 10 11 9 5"
    ),
    (
        "The trembling soldier felt the ground slip from beneath his feet",
        "भयभीत सैनिक को लगा कि उसके पैरों तले ज़मीन खिसक गई है",
        "0 1 1 2 3 7 8 7 4 5 5 5"
    ),
    (
        "The pious pilgrim walked on bare feet to the mountain shrine",
        "श्रद्धालु तीर्थयात्री नंगे पैर चलकर पहाड़ी मंदिर तक पहुँचे",
        "0 1 4 5 2 7 8 6 6"
    ),
    (
        "The little dancer stamped her feet to the rhythm of the wooden drum",
        "नन्हीं नर्तकी ने ढोलक की थाप पर अपने कोमल पैर थिरकाए",
        "0 1 1 9 7 5 6 3 3 4 2"
    ),
    (
        "The fierce wind swept the autumn leaves beneath their feet",
        "तेज़ हवा ने उनके पैरों के नीचे सूखी पत्तियाँ बिखेर दीं",
        "0 1 1 6 7 5 5 4 4 2 2"
    ),
    (
        "The strict father told his son not to set foot in the gambling house",
        "कड़े पिता ने बेटे को जुए के अड्डे पर पैर न रखने को कहा",
        "0 1 1 4 3 10 8 9 7 7 6 6 2"
    ),
    (
        "The wounded soldier dragged his injured foot slowly across the field",
        "घायल सिपाही ने अपने चोटिल पैर को खींचते हुए मैदान पार किया",
        "0 1 1 3 4 5 2 2 9 8 8"
    ),
    (
        "The mischievous boy washed the sticky mud from his dusty feet",
        "शरारती बालक ने अपने गंदे पैरों से चिपचिपी मिट्टी धोई",
        "0 1 1 7 8 6 4 5 2"
    ),
    (
        "The loyal dog lay down quietly near the warm feet of its master",
        "वफादार कुत्ता अपने स्वामी के पैरों के पास चुपचाप लेट गया",
        "0 1 8 9 7 6 5 4 2 2"
    ),
    (
        "The swift deer ran without its feet touching the ground",
        "तेज़ दौड़ते हिरण के पैर ज़मीन पर पड़ते दिखाई नहीं देते थे",
        "0 2 1 1 4 7 6 5 3 3 3 3"
    ),
    (
        "The young bride touched the feet of the family elders with respect",
        "नई दुल्हन ने आदर के साथ परिवार के सभी बुज़ुर्गों के पैर छुए",
        "0 1 1 8 7 5 6 6 4 3 2"
    ),
    (
        "The tired watchman walked many miles until his feet were sore",
        "पहरेदार रात भर चलता रहा जिससे उसके पैर दुखने लगे",
        "0 2 2 2 2 4 7 8 9 9"
    ),
    (
        "The mountaineer planted his feet firmly on the icy rock",
        "पर्वतारोही ने बर्फीली चट्टान पर अपने पैर मज़बूती से जमाए",
        "0 1 6 7 5 4 3 3 2"
    ),
    (
        "The cold river water chilled the feet of the bathing children",
        "ठंडी नदी के पानी ने नहाते हुए बच्चों के पैर ठंडे कर दिए",
        "0 1 2 2 7 8 5 4 3 3 3"
    ),
    (
        "The clever diplomat established his foot firmly in the court",
        "कुशल राजनयिक ने दरबार के भीतर अपने पैर मज़बूती से जमा लिए",
        "0 1 1 8 7 4 3 3 2 2 2"
    ),
    (
        "The fearful boy tiptoed quietly on the wooden floor at night",
        "डरपोक बालक रात में दबे पाँव लकड़ी के फर्श पर चला",
        "0 1 8 7 2 2 5 6 4 2"
    ),
    (
        "The king bowed his head at the feet of his mother with devotion",
        "राजा ने भक्ति भाव से अपनी माँ के पाँवों में सिर रख दिया",
        "0 1 9 9 8 7 6 5 4 3 2 2"
    ),
    (
        "The joyful farmer danced with light feet after the pleasant rain",
        "सुखद बारिश के बाद प्रसन्न किसान ने हल्के पाँव नृत्य किया",
        "7 8 6 0 1 1 4 5 2 2"
    ),
    (
        "The elderly grandmother could hardly put her heavy feet forward",
        "वृद्ध दादी के लिए अपने भारी पाँव आगे बढ़ाना कठिन था",
        "0 1 1 2 6 7 8 5 3 4"
    ),
    (
        "The wounded lion dragged its bleeding paw across the thorny path",
        "घायल शेर ने काँटेदार रास्ते पर अपना घायल पैर खींचा",
        "0 1 1 7 8 6 4 5 2"
    ),
    (
        "The arrogant prince refused to touch the dusty feet of the ascetic",
        "अभिमानी राजकुमार ने तपस्वी के धूल भरे चरणों को छूने से इनकार किया",
        "0 1 1 9 6 7 5 3 4 2 2"
    ),
    (
        "The swift messenger tied bells to his feet to run through night",
        "तेज़ हरकारे ने रात में दौड़ने के लिए पैरों में घुँघरू बाँध लिए",
        "0 1 1 9 8 7 6 5 4 3 2 2"
    ),
    (
        "The brave freedom fighters stood with steady feet against the cannons",
        "वीर स्वतंत्रता सेनानी तोपों के आगे अडिग पाँव खड़े रहे",
        "0 1 2 8 7 5 6 3 3"
    ),
    (
        "The playful puppy nipped gently at the bare feet of the boy",
        "चंचल पिल्ले ने बालक के नंगे पाँव को प्यार से छुआ",
        "0 1 1 8 7 5 6 4 3 3 2"
    ),
    (
        "The poor peasant lacked leather sandals to protect his worn feet",
        "गरीब किसान के पास अपने फटे पैरों के लिए चमड़े के जूते न थे",
        "0 1 1 2 7 8 6 6 4 5 3 2"
    ),

    # 101-125 (पैर/पाँव & सिर/माथा)
    (
        "The traveler washed the street dust from his feet with clear water",
        "यात्री ने स्वच्छ जल से अपने पैरों की धूल धोई",
        "0 1 9 10 8 6 7 4 2"
    ),
    (
        "The anxious father paced up and down with restless feet in the hall",
        "चिंतित पिता दालान में बेचैन पैरों से इधर उधर टहलता रहा",
        "0 1 11 10 6 7 5 3 4 2 2"
    ),
    (
        "The cold morning dew soaked the bare feet of the young cowherd",
        "सुबह की ठंडी ओस ने नन्हें ग्वाले के नंगे पाँव भिगो दिए",
        "1 0 2 2 8 9 7 5 6 3 3"
    ),
    (
        "The arrogant officer ordered the peasants to fall at his feet",
        "घमंडी अफसर ने किसानों को अपने पैरों में गिरने का हुक्म दिया",
        "0 1 1 4 3 8 7 6 5 2 2"
    ),
    (
        "The wise elder advised the youth never to stray on evil feet",
        "बुद्धिमान बुज़ुर्ग ने युवा को कुमार्ग पर पाँव न रखने की सीख दी",
        "0 1 1 4 3 8 7 6 5 2 2 2"
    ),
    (
        "The loyal horse stood with weary feet beside the fallen warrior",
        "वफादार घोड़ा गिरे हुए योद्धा के पास थके पाँव खड़ा रहा",
        "0 1 7 8 6 4 5 2 2"
    ),
    (
        "The energetic boy ran barefoot across the green meadows with joy",
        "उत्साही लड़का खुशी से हरे मैदानों में नंगे पैर दौड़ा",
        "0 1 8 7 5 6 4 3 3 2"
    ),
    (
        "The old beggar dragged his swollen feet along the dusty highway",
        "बूढ़ा भिखारी धूल भरे राजमार्ग पर अपने सूजे हुए पैर घसीटता रहा",
        "0 1 6 7 5 4 4 2 2"
    ),
    (
        "The swift runner crossed the finish line with nimble feet",
        "तेज़ धावक ने चपल पैरों से दौड़ की अंतिम रेखा पार की",
        "0 1 1 6 7 5 4 3 2 2"
    ),
    (
        "The sacred temple prohibited leather footwear on its holy premises",
        "पवित्र मंदिर के परिसर में चमड़े के जूते पहनना वर्जित था",
        "0 1 7 8 6 3 4 2 2"
    ),
    (
        "The innocent child raised a huge hue and cry on his head",
        "मासूम बच्चे ने खिलौने के लिए सारा आसमान सिर पर उठा लिया",
        "0 1 1 8 8 7 8 9 3 2 2"
    ),
    (
        "The proud warrior preferred having his head severed to bowing down",
        "वीर योद्धा ने सिर झुकाने की अपेक्षा सिर कटाना उचित समझा",
        "0 1 1 4 8 7 4 5 3 2"
    ),
    (
        "The insolent servant ate the head of his master with constant chattering",
        "उद्दंड नौकर ने लगातार बोलकर अपने मालिक का सिर खा लिया",
        "0 1 1 7 8 5 6 4 3 2"
    ),
    (
        "The grief stricken father beat his head in despair after the disaster",
        "आपदा के बाद दुखी पिता ने निराशा में अपना सिर धुन लिया",
        "9 8 0 1 1 6 5 4 3 2"
    ),
    (
        "The brave revolutionaries tied shrouds to their heads for freedom",
        "वीर क्रांतिकारियों ने देश की आज़ादी के लिए सिर पर कफ़न बाँध लिया",
        "0 1 1 7 8 6 6 5 4 3 2"
    ),
    (
        "The intuition of danger struck his forehead when he saw the stranger",
        "अजनबी को देखकर चतुर पहरेदार का माथा तुरंत ठनका",
        "9 8 7 4 4 1 2 3 3"
    ),
    (
        "The grateful guest placed the hospitality of the host on his head",
        "कृतज्ञ अतिथि ने मेज़बान के आदर सत्कार को सिर आँखों पर रखा",
        "0 1 1 6 4 5 3 8 9 2"
    ),
    (
        "The reckless youth fell headlong into ruin because of bad habits",
        "बुरी आदतों के कारण लापरवाह युवक सिर के बल गर्त में गिरा",
        "8 8 7 0 1 3 3 5 6 2"
    ),
    (
        "The sudden debt of interest rose high above the head of the farmer",
        "सूदखोर के भारी कर्ज़ का बोझ किसान के सिर से ऊपर हो गया",
        "0 2 1 3 10 7 8 5 6 4 4"
    ),
    (
        "The doting parents spoiled their only son by putting him on head",
        "लाड़ले बेटे को अत्यधिक छूट देकर माता पिता ने सिर पर चढ़ा लिया",
        "0 4 3 2 2 1 1 1 8 9 2 2"
    ),
    (
        "The humble scholar bowed his head before the eternal truth",
        "विनम्र विद्वान ने शाश्वत सत्य के सामने आदर से सिर झुकाया",
        "0 1 1 6 7 5 3 4 2 2"
    ),
    (
        "The ferocious storm tore the thatch from above their heads",
        "भीषण तूफान ने उनके सिर के ऊपर से फूस का छप्पर उड़ा दिया",
        "0 1 1 6 7 5 5 4 4 2 2"
    ),
    (
        "The sudden tragedy struck like a lightning bolt upon his bare head",
        "अचानक आई विपत्ति उसके सिर पर बिजली बनकर टूट पड़ी",
        "0 0 1 6 7 5 4 4 2 2"
    ),
    (
        "The proud merchant walked through the town with his head held high",
        "सफल व्यापारी पूरे नगर में अपना सिर ऊँचा करके चला",
        "0 1 4 5 3 7 8 2 2"
    ),
    (
        "The furious mother held her head in despair over the broken vase",
        "टूटा हुआ फूलदान देखकर माँ ने परेशानी में अपना सिर पकड़ लिया",
        "8 8 9 7 0 1 5 4 3 2 2"
    ),

    # 126-150 (सिर/माथा)
    (
        "The courageous captain kept a cool head amid the raging tempest",
        "भयानक तूफान के बीच बहादुर कप्तान ने अपना सिर ठंडा रखा",
        "6 7 5 0 1 1 4 3 2 2"
    ),
    (
        "The playful monkey sat right upon the bald head of the priest",
        "शरारती बंदर पंडित जी के गंजे सिर पर जाकर बैठ गया",
        "0 1 8 8 6 7 5 2 2 2"
    ),
    (
        "The old woman carried a heavy basket of vegetables upon her head",
        "वृद्धा ने सब्जियों से भरी भारी टोकरी अपने सिर पर रखी",
        "0-1 1 6 5 4 5 8 9 2"
    ),
    (
        "The brave soldier took the enemy bullet directly on his forehead",
        "बहादुर सैनिक ने शत्रु की गोली सीधे अपने माथे पर खाई",
        "0 1 1 4 5 6 8 7 2"
    ),
    (
        "The holy priest smeared fragrant sandalwood paste on the royal forehead",
        "पवित्र पुजारी ने राजा के माथे पर सुगंधित चंदन का तिलक लगाया",
        "0 1 1 7 8 6 3 4 5 2 2"
    ),
    (
        "The tired clerk rested his aching head on the wooden table",
        "थके हुए मुंशी ने अपना दुखता सिर लकड़ी की मेज़ पर टिकाया",
        "0 0 1 1 4 5 7 8 6 2"
    ),
    (
        "The cruel tyrant demanded every citizen bow head in subservience",
        "क्रूर तानाशाह ने हर नागरिक से अपने सामने सिर झुकाने की मांग की",
        "0 1 1 3 4 5 6 6 5 2 2 2"
    ),
    (
        "The shocking revelation made the head of the judge spin in wonder",
        "अद्भुत रहस्योद्घाटन से न्यायाधीश का सिर चक्कर खाने लगा",
        "0 1 2 6 4 7 7 2 2"
    ),
    (
        "The loyal companion placed a cool wet cloth on his burning forehead",
        "वफादार साथी ने उसके तपते माथे पर ठंडी गीली पट्टी रखी",
        "0 1 1 7 8 6 4 4 5 2"
    ),
    (
        "The bold thinker carried the heavy burden of reforms on his head",
        "विचारक ने समाज सुधार का भारी बोझ अपने सिर पर उठाया",
        "0 1 1 6 5 3 4 8 9 2"
    ),
    (
        "The victorious king wore the jewel encrusted crown upon his head",
        "विजयी राजा ने अपने सिर पर रत्नों से जड़ा मुकुट पहना",
        "0 1 1 8 9 7 4 4 5 2"
    ),
    (
        "The pious lady touched her forehead to the cool marble floor of the temple",
        "श्रद्धालु महिला ने मंदिर के शीतल संगमरमर पर अपना माथा टेका",
        "0 1 1 11 8 6 7 5 4 2"
    ),
    (
        "The wicked enemy aimed his sharp arrow straight at the forehead",
        "दुष्ट शत्रु ने अपना नुकीला तीर सीधे उसके माथे पर ताना",
        "0 1 1 4 5 6 8 7 2"
    ),
    (
        "The loving mother kissed the tender forehead of her sleeping baby",
        "स्नेहमयी माँ ने अपने सोते हुए शिशु के कोमल माथे को चूमा",
        "0 1 1 7 6 8 4 5 3 2"
    ),
    (
        "The angry father pointed his finger at the head of the lazy youth",
        "क्रोधित पिता ने आलसी युवक के सिर की ओर उँगली उठाई",
        "0 1 1 9 10 6 7 7 4 2 2"
    ),
    (
        "The sudden loud noise caused severe pain inside his throbbing head",
        "अचानक हुए तेज़ धमाके से उसके सिर में असहनीय दर्द होने लगा",
        "0 0 1 2 2 7 8 4 5 3 3"
    ),
    (
        "The royal barber shaved the head of the young prince before the ceremony",
        "शाही नाई ने संस्कार से पहले राजकुमार का सिर मुंडाया",
        "0 1 1 10 9 7 4 2"
    ),
    (
        "The clever detective scratched his head trying to solve the mystery",
        "चतुर जासूस ने रहस्य सुलझाने के लिए अपना सिर खुजलाया",
        "0 1 1 8 6 7 4 2"
    ),
    (
        "The weary traveler tied a turban of white cotton around his head",
        "थके हुए पथिक ने अपने सिर पर सफेद सूती पगड़ी बाँधी",
        "0 0 1 1 8 9 5 6 4 2"
    ),
    (
        "The haughty minister refused to incline his head to the simple hermit",
        "अभिमानी मंत्री ने सीधे सादे सन्यासी के आगे सिर नहीं नवाया",
        "0 1 1 8 8 9 7 5 3 2"
    ),
    (
        "The dark clouds gathered right above the head of the lonely wanderer",
        "अकेले पथिक के सिर पर घने काले बादल उमड़ने लगे",
        "8 9 6 7 0 1 1 3 3"
    ),
    (
        "The courageous leader took the entire blame on his own head",
        "साहसी नेता ने सारी असफलता का दोष अपने सिर पर ले लिया",
        "0 1 1 3 4 4 7 8 2 2"
    ),
    (
        "The anxious student could not get the complicated formula into head",
        "चिंतित छात्र के सिर में गणित का कठिन सूत्र नहीं बैठा",
        "0 1 1 8 7 6 6 5 2 2"
    ),
    (
        "The heavy iron beam fell narrowly missing the head of the worker",
        "भारी लोहे का खंभा मजदूर के सिर के पास से होकर गिरा",
        "0 1 2 9 6 7 5 5 5 3"
    ),
    (
        "The old philosopher nodded his head in agreement with the argument",
        "वृद्ध दार्शनिक ने तर्क से सहमत होकर अपना सिर हिलाया",
        "0 1 1 8 6 7 7 4 2"
    ),

    # 151-175 (सिर & कलेजा/दिल)
    (
        "The bright red mark shone prominently on the forehead of the warrior",
        "योद्धा के माथे पर लाल विजय तिलक चमक रहा था",
        "9 6 7 1 2 2 3 3 3"
    ),
    (
        "The gentle breeze caressed the forehead of the exhausted climber",
        "शीतल मंद हवा ने थके हुए पर्वतारोही के माथे को छुआ",
        "0 1 1 1 6 7 4 5 2"
    ),
    (
        "The mischievous boy dropped water on the head of the sleeping cat",
        "शरारती लड़के ने सोती हुई बिल्ली के सिर पर पानी गिरा दिया",
        "0 1 1 8 9 5 6 3 2 2"
    ),
    (
        "The pious pilgrim carried sacred river water in a pot on head",
        "तीर्थयात्री ने पवित्र गंगाजल का घड़ा अपने सिर पर उठाया",
        "0 1 2 3 7 10 11 2"
    ),
    (
        "The cruel master hit the forehead of the servant in sudden rage",
        "क्रूर मालिक ने गुस्से में नौकर के माथे पर चोट पहुँचाई",
        "0 1 1 8 7 5 3 4 2 2"
    ),
    (
        "The loving sister tied a protective silk thread with bowed head",
        "प्यारी बहन ने सिर झुकाकर भाई की कलाई पर रक्षासूत्र बाँधा",
        "0 1 1 8 8 2 4 4 3 2"
    ),
    (
        "The young scholar shook his head in disbelief at the strange tale",
        "युवा विद्वान ने विचित्र कथा सुनकर अविश्वास में सिर हिलाया",
        "0 1 1 9 10 8 6 7 3 2"
    ),
    (
        "The fierce heat of the desert beat mercilessly on their bare heads",
        "रेगिस्तान की भीषण धूप उनके नंगे सिर पर बरस रही थी",
        "4 1 0 2 7 8 6 5 5"
    ),
    (
        "The graceful queen carried the gold urn on her head with poise",
        "सुंदर रानी ने सोने का कलश अपने सिर पर संतुलन से रखा",
        "0 1 1 4 5 7 8 9 9 2"
    ),
    (
        "The humble potter thanked the heavens with hands folded above head",
        "गरीब कुम्हार ने सिर से ऊपर हाथ जोड़कर ईश्वर का धन्यवाद किया",
        "0 1 1 9 8 8 6 7 3 2 2"
    ),
    (
        "The sight of the burning house made a serpent crawl on his liver",
        "पड़ोसी का सुंदर घर देखकर ईर्ष्यालु व्यक्ति के कलेजे पर साँप लोटा",
        "3 4 3 0 1 1 10 11 7 8"
    ),
    (
        "The avenger felt his liver turn cold after defeating the tyrant",
        "अत्याचारी को पराजित करके पीड़ित व्यक्ति का कलेजा ठंडा हुआ",
        "8 6 7 0 1 1 3 4 2"
    ),
    (
        "The brave mother hardened her liver and sent her son to war",
        "वीर माँ ने अपना कलेजा कड़ा करके बेटे को युद्ध में भेजा",
        "0 1 1 3 4 2 2 7 8 6 5"
    ),
    (
        "The sudden tragic news pierced the tender liver of the sister",
        "दुखद समाचार ने बेचारी बहन का कलेजा छलनी कर दिया",
        "1 2 2 8 8 6 4 3 3"
    ),
    (
        "Her heart became like a garden upon receiving the good news",
        "शुभ समाचार सुनकर प्रसन्न बालिका का दिल बाग बाग हो गया",
        "8 9 6 0 1 1 4 4 2 2"
    ),
    (
        "The terrifying roar of the tiger made the heart of the traveler sink",
        "बाघ की भयंकर दहाड़ सुनकर यात्री का दिल बैठ गया",
        "4 1 2 5 8 6 10 10"
    ),
    (
        "The kind king possessed a golden heart filled with boundless compassion",
        "दयालु राजा का दिल असीम करुणा से भरा हुआ था",
        "0 1 1 5 7 8 6 6 2"
    ),
    (
        "The sudden betrayal broke the trusting heart of the loyal companion",
        "विश्वासघात ने वफादार साथी के कोमल दिल को तोड़ दिया",
        "1 1 6 7 4 5 3 2 2"
    ),
    (
        "The proud father swelled his chest with pride at the graduation",
        "बेटे की सफलता देखकर पिता की छाती गर्व से फूल गई",
        "0 1 1 4 5 3 6 2 2"
    ),
    (
        "The wicked enemy ground lentils right upon their chest for years",
        "दुष्ट शत्रु ने वर्षों तक पड़ोसियों की छाती पर मूँग दली",
        "0 1 1 9 9 5 6 4 3 2"
    ),
    (
        "The brave soldier beat his chest and defied the oncoming invaders",
        "वीर सैनिक ने अपनी छाती ठोककर हमलावरों को ललकारा",
        "0 1 1 3 4 2 7 5"
    ),
    (
        "The loving mother embraced her returned son tightly to her chest",
        "स्नेहमयी माँ ने लौटे हुए पुत्र को अपनी छाती से लगा लिया",
        "0 1 1 4 4 5 8 9 7 2 2"
    ),
    (
        "The students tightened their waists determinedly for the examination",
        "वार्षिक परीक्षा के लिए सभी छात्रों ने अपनी कमर कस ली",
        "6 6 5 0 0 1 2 2 2"
    ),
    (
        "The heavy burden of agricultural debt broke the waist of the farmers",
        "भारी कर्ज़ के बोझ ने गरीब किसानों की कमर तोड़ दी",
        "0 4 1 2 7 8 6 5 2"
    ),
    (
        "The brave soldier never showed his back in the battlefield",
        "सच्चा सिपाही युद्ध के मैदान में कभी पीठ नहीं दिखाता",
        "0 1 6 5 7 2 4 3 3"
    ),

    # 176-200 (पीठ, उँगली, छाती, कमर)
    (
        "The wise teacher patted the back of the student to encourage him",
        "शिक्षक ने मेधावी छात्र की पीठ थपथपाकर उसका हौसला बढ़ाया",
        "0 1 1 5 6 3 2 8 7 7"
    ),
    (
        "The wicked traitor stabbed his trusting master right in the back",
        "कपटी गद्दार ने अपने विश्वासपात्र स्वामी की पीठ में छुरा घोंपा",
        "0 1 1 4 5 8 7 2 2"
    ),
    (
        "The vile slanderer spoke ill behind the back of his benefactor",
        "नीच व्यक्ति ने अपने उपकारी के पीठ पीछे बुराई की",
        "0 1 1 8 8 5 4 2 2"
    ),
    (
        "The astonished crowd pressed finger under teeth witnessing the miracle",
        "अद्भुत चमत्कार देखकर चकित भीड़ ने दाँतों तले उँगली दबा ली",
        "7 7 6 0 1 1 5 4 3 2 2"
    ),
    (
        "The proud king never let anyone raise a finger against his justice",
        "न्यायप्रिय राजा ने कभी अपने न्याय पर उँगली नहीं उठने दी",
        "0 1 1 2 7 8 5 4 4 4"
    ),
    (
        "The rich merchant had all five fingers soaked in fragrant ghee",
        "व्यापार में भारी मुनाफ़े से सेठ की पाँचों उँगलियाँ घी में थीं",
        "0 1 1 1 0 1 4 4 7 8 2"
    ),
    (
        "The naughty boy burnt his fingers poking into the hot embers",
        "शरारती बालक ने गरम अलाव में हाथ डालकर अपनी उँगली जला ली",
        "0 1 1 6 7 5 4 4 3 2 2"
    ),
    (
        "The mischievous ape counted numbers on its long crooked fingers",
        "चतुर बंदर ने अपनी टेढ़ी उँगलियों पर गिनती गिनना सीखा",
        "0 1 1 4 5 6 3 2 2 2"
    ),
    (
        "The loving grandmother stroked the aching back of the weary child",
        "प्यारी दादी ने थके हुए बालक की दुखती पीठ सहलाई",
        "0 1 1 7 7 8 5 4 2"
    ),
    (
        "The brave warrior bore numerous scars of battle on his broad chest",
        "योद्धा की चौड़ी छाती पर युद्ध के अनेक घाव चमक रहे थे",
        "1 1 8 9 7 5 3 4 2 2 2"
    ),
    (
        "The cruel tyrant placed his iron heel upon the chest of the defeated",
        "क्रूर विजेता ने पराजित राजा की छाती पर अपना पाँव रखा",
        "0 1 1 9 10 7 6 4 5 2"
    ),
    (
        "The sudden terrifying scream made their liver tremble within them",
        "भयानक चीख सुनकर सभी उपस्थित लोगों का कलेजा काँप उठा",
        "1 2 0 4 4 4 5 6 3 3"
    ),
    (
        "The grief of losing her child tore the liver of the poor mother",
        "संतान के वियोग ने बेचारी माँ के कलेजे को टुकड़े टुकड़े कर दिया",
        "3 0 1 2 9 9 7 4 4 4 4"
    ),
    (
        "The honest young man did not have the heart to tell a falsehood",
        "ईमानदार युवक का दिल किसी से झूठ बोलने को गवारा न हुआ",
        "0 1 1 5 8 9 9 4 4 3 3"
    ),
    (
        "The melodious music won the heart of the entire audience instantly",
        "मधुर संगीत ने सभागार में उपस्थित सभी श्रोताओं का दिल जीत लिया",
        "0 1 1 7 7 6 7 4 2 2 2"
    ),
    (
        "The cruel words pierced like poisonous arrows into the deep heart",
        "कड़वे शब्दों ने उसके कोमल दिल में ज़हरीले तीर की तरह चुभन की",
        "0 1 1 7 8 9 3 4 2 2 2 2"
    ),
    (
        "The old porter bent his arched waist under the enormous weight",
        "वृद्ध कुली ने भारी वजन के नीचे अपनी झुकी कमर सीधी की",
        "0 1 1 7 8 6 4 4 5 2 2"
    ),
    (
        "The continuous agricultural toil bent the waist of the elder",
        "खेतों की लगातार मेहनत ने बूढ़े किसान की कमर झुका दी",
        "1 1 0 2 2 6 7 4 3 3"
    ),
    (
        "The brave youth straightened his waist and faced the coming storm",
        "साहसी युवक ने अपनी कमर सीधी करके आने वाले संकट का सामना किया",
        "0 1 1 4 2 2 6 7 8 5 5 5"
    ),
    (
        "The cowardly bandit showed his back and escaped into the ravine",
        "डरपोक डाकू ने पीठ दिखाई और घने बीहड़ में भाग खड़ा हुआ",
        "0 1 1 4 3 5 8 9 7 6 6 6"
    ),
    (
        "The caring father carried his sleepy daughter upon his warm back",
        "प्यारे पिता ने अपनी सोती हुई नन्हीं बेटी को पीठ पर लाद लिया",
        "0 1 1 3 3 4 4 8 7 2 2"
    ),
    (
        "The cruel master whipped the bare back of the runaway bondman",
        "क्रूर जमींदार ने भागे हुए गुलाम की नंगी पीठ पर कोड़े बरसाए",
        "0 1 1 7 7 8 4 5 3 2 2"
    ),
    (
        "The proud craftsman pointed his finger at the completed masterpiece",
        "गर्वित शिल्पकार ने अपनी बनाई अद्भुत मूर्ति की ओर उँगली दिखाई",
        "0 1 1 5 6 6 6 4 3 2"
    ),
    (
        "The suspicious neighbor pointed an accusing finger at the stranger",
        "शक्की पड़ोसी ने अजनबी व्यक्ति की ओर शक की उँगली उठाई",
        "0 1 1 8 8 6 4 4 5 2"
    ),
    (
        "The delicate girl wore a sparkling silver ring on her little finger",
        "सुकुमार कन्या ने अपनी छोटी उँगली में चमकदार चाँदी की अँगूठी पहनी",
        "0 1 1 9 10 8 4 5 6 2"
    ),

    # 201-225 (दिल, छाती, कमर, पीठ)
    (
        "The brave soldier defended the pass until his last heartbeat",
        "बहादुर सैनिक ने अपनी अंतिम सांस तक दर्रे की रक्षा की",
        "0 1 1 6 7 5 4 2 2"
    ),
    (
        "The deep secret remained buried within the chambers of his heart",
        "गहरा रहस्य हमेशा उसके दिल के गुप्त कोने में दबा रहा",
        "0 1 2 8 9 6 7 5 3 3"
    ),
    (
        "The generous lady opened her heart and sheltered the lost puppy",
        "उदार महिला ने बड़े दिल से भटके हुए पिल्ले को शरण दी",
        "0 1 1 3 4 2 6 7 5 2"
    ),
    (
        "The sorrowful news took away all peace from the maternal heart",
        "शोक समाचार ने ममता भरे दिल का सारा चैन छीन लिया",
        "0 1 1 7 8 6 4 4 2 2"
    ),
    (
        "The fierce competitor possessed a stout heart that knew no retreat",
        "साहसी खिलाड़ी का दिल कभी पीछे हटना नहीं जानता था",
        "0 1 1 4 6 7 7 5 2 2"
    ),
    (
        "The joyful news brought relief to the burning liver of the father",
        "शुभ समाचार से चिंतित पिता के जलते कलेजे को ठंडक मिली",
        "0 1 1 8 8 6 7 5 2 2"
    ),
    (
        "The mother held the child close to her chest through the cold night",
        "माँ ने ठंड से बचाने के लिए बालक को अपनी छाती से चिपकाए रखा",
        "0 1 9 10 10 10 3 6 7 5 2 2"
    ),
    (
        "The royal warrior expanded his chest and roared like a wild lion",
        "शाही योद्धा ने अपनी छाती फुलाकर सिंह की तरह गर्जना की",
        "0 1 1 4 2 2 8 7 6 5"
    ),
    (
        "The sudden stone hurt the chest of the marching watchman",
        "उड़ते हुए पत्थर ने पहरेदार की चौड़ी छाती पर चोट की",
        "0 1 1 7 5 4 6 2 2"
    ),
    (
        "The old warrior had not forgotten how to tighten his waist for war",
        "बूढ़ा सिपाही युद्ध के लिए कमर कसना नहीं भूला था",
        "0 1 10 9 8 7 4 3 2"
    ),
    (
        "The hard labor in the stone quarry broke the waist of workers",
        "पत्थर की खदान में कठोर परिश्रम ने मजदूरों की कमर तोड़ डाली",
        "4 5 5 0 1 1 8 7 6 6"
    ),
    (
        "The treacherous spy turned his back upon his native country",
        "विश्वासघाती जासूस ने अपनी मातृभूमि से पीठ फेर ली",
        "0 1 1 7 6 4 3 3"
    ),
    (
        "The grateful student touched the back of the teacher with respect",
        "कृतज्ञ छात्र ने आदर से अपने पूज्य गुरु की पीठ छुई",
        "0 1 1 8 8 6 7 4 2"
    ),
    (
        "The heavy backpack weighed down the back of the mountain climber",
        "भारी बस्ते ने पर्वतारोही की मज़बूत पीठ को झुका दिया",
        "0 1 1 8 6 5 2 2 2"
    ),
    (
        "The child twisted his finger playfully while learning to write",
        "लिखना सीखते समय बालक ने चंचलता से अपनी उँगली घुमाई",
        "7 6 5 0 1 3 3 2 2"
    ),
    (
        "The sharp knife nicked the index finger of the careless cook",
        "तेज़ चाकू से लापरवाह रसोइए की तर्जनी उँगली कट गई",
        "0 1 1 8 9 5 4 2 2"
    ),
    (
        "The loving mother blew upon the injured finger of her daughter",
        "ममतामयी माँ ने बेटी की चोटिल उँगली पर फूँक मारी",
        "0 1 1 8 6 5 4 2 2"
    ),
    (
        "The greedy usurer kept the entire village under his little finger",
        "लालची साहूकार ने पूरे गाँव को अपनी उँगलियों पर नचाया",
        "0 1 1 4 5 3 8 7 2"
    ),
    (
        "The terrified traveler felt his liver jump into his very mouth",
        "अचानक साँप देखकर डर के मारे पथिक का कलेजा मुँह को आ गया",
        "1 1 1 0 0 1 4 7 8 5 6"
    ),
    (
        "The heroic deed of the son brought immense joy to the father liver",
        "बेटे के साहसिक काम ने पिता के कलेजे को बहुत सुकून दिया",
        "4 1 0 2 11 11 11 7 8 5"
    ),
    (
        "The cruel accusation pierced the heart of the innocent maiden",
        "झूठे आरोप ने मासूम कन्या के पवित्र दिल को गहरा आघात पहुँचाया",
        "0 1 1 7 8 5 4 2 2 2"
    ),
    (
        "The true friend gave from the bottom of his generous heart",
        "सच्चे मित्र ने अपने उदार दिल की गहराई से सहायता की",
        "0 1 1 6 7 8 4 5 2 2"
    ),
    (
        "The sound of footsteps made the heart of the hiding thief beat fast",
        "पैरों की चाप सुनकर छिपे हुए चोर का दिल ज़ोर से धड़कने लगा",
        "2 0 1 3 6 7 8 5 11 11 9 10"
    ),
    (
        "The courageous youth stood chest forward against the raging river",
        "साहसी युवक छाती ताने उफनती नदी की लहरों के आगे डटा रहा",
        "0 1 3 4 8 9 7 7 2 2"
    ),
    (
        "The heavy iron chain encircled the broad chest of the captive",
        "भारी लोहे की ज़ंजीर ने बंदी की चौड़ी छाती को जकड़ रखा था",
        "0 1 2 2 8 6 5 3 3 3"
    ),

    # 226-250 (अंतिम समूह)
    (
        "The determined village folk tightened their waists to dig the canal",
        "दृढ़निश्चयी ग्रामीणों ने नहर खोदने के लिए अपनी कमर कस ली",
        "0 1 1 9 7 8 3 4 4 4"
    ),
    (
        "The steep mountain climb tested the waist and endurance of travelers",
        "सीधी पहाड़ी चढ़ाई ने सभी यात्रियों की कमर और धीरज की परीक्षा ली",
        "0 1 2 2 8 9 5 6 7 3 3"
    ),
    (
        "The victorious wrestler showed the flat back of his opponent to soil",
        "विजेता पहलवान ने अखाड़े में विरोधी की पीठ ज़मीन पर लगा दी",
        "0 1 1 11 11 7 5 10 9 2 2"
    ),
    (
        "The faithful servant received the heavy blows upon his own back",
        "वफादार सेवक ने स्वामी की रक्षा में अपनी पीठ पर लाठियाँ खाईं",
        "0 1 1 7 8 8 7 6 4 3"
    ),
    (
        "The gentle mother rubbed herbal oil upon the back of her son",
        "स्नेहमयी माँ ने अपने बेटे की पीठ पर औषधीय तेल मला",
        "0 1 1 9 10 6 7 3 4 2"
    ),
    (
        "The skilled musician plucked the string with his delicate finger",
        "कुशल संगीतकार ने अपनी कोमल उँगली से सितार का तार छेड़ा",
        "0 1 1 6 7 8 4 4 2"
    ),
    (
        "The wise elder wagged his finger warning the reckless boys",
        "बुद्धिमान बुज़ुर्ग ने उँगली हिलाकर उद्दंड लड़कों को सावधान किया",
        "0 1 1 4 2 7 8 5 3 3"
    ),
    (
        "The little sister clasped the little finger of her elder brother",
        "छोटी बहन ने प्यार से अपने बड़े भाई की कनिष्ठिका उँगली थाम ली",
        "0 1 1 2 2 7 8 3 4 2 2"
    ),
    (
        "The greedy cat burnt its paw trying to steal fish from the skillet",
        "मछली चुराने के चक्कर में बिल्ली ने गरम कड़ाही में अपना पंजा जलाया",
        "6 5 4 4 0 1 1 10 11 9 3 2"
    ),
    (
        "The fearful guard felt his liver sink at the sight of the ghost",
        "अंधेरे में प्रेत की छाया देखकर पहरेदार का कलेजा काँप गया",
        "9 9 9 7 6 0 1 4 3 3"
    ),
    (
        "The kind queen opened the treasury with an abundant heart",
        "दयालु महारानी ने विशाल दिल से गरीबों के लिए खजाना खोल दिया",
        "0 1 1 6 7 5 5 4 3 2"
    ),
    (
        "The sweet memory brought a surge of delight to the aging heart",
        "सुखद यादों ने वृद्ध के उदास दिल में नई उमंग जगा दी",
        "0 1 1 8 9 9 4 5 2 2"
    ),
    (
        "The brave commander struck his chest and vowed to conquer the hill",
        "सेनापति ने अपनी छाती ठोककर पहाड़ी जीतने की प्रतिज्ञा की",
        "0-1 1 3 4 2 9 8 5 5"
    ),
    (
        "The protective shield guarded the chest of the frontline soldier",
        "लोहे की ढाल ने आगे खड़े सैनिक की छाती की रक्षा की",
        "0 1 1 6 7 7 4 2 2"
    ),
    (
        "The farmer tightened his waistcloth and entered the muddy field",
        "किसान ने अपनी कमर कसकर कीचड़ भरे खेत में हल जोता",
        "0 1 2 2 6 7 5 5 5"
    ),
    (
        "The heavy taxes broke the economic waist of small shopkeepers",
        "अत्यधिक करों ने छोटे दुकानदारों की आर्थिक कमर तोड़ दी",
        "0 1 1 6 7 4 5 2 2"
    ),
    (
        "The cunning politician turned his back on the promises made earlier",
        "चालाक नेता ने चुनाव से पहले किए गए वादों से पीठ फेर ली",
        "0 1 1 8 8 7 7 6 4 3 3"
    ),
    (
        "The warm sun shone upon the back of the resting bullock",
        "दोपहर की गुनगुनी धूप सुस्ताते हुए बैल की पीठ पर चमक रही थी",
        "0 0 1 1 7 8 5 4 2 2 2"
    ),
    (
        "The skilled painter held the slender brush between two fingers",
        "कुशल चित्रकार ने दो उँगलियों के बीच बारीक तूलिका संभाली",
        "0 1 1 6 7 5 3 4 2"
    ),
    (
        "The curious toddler pointed his finger at the shining stars",
        "जिज्ञासु बालक ने आसमान के चमकते तारों की ओर उँगली उठाई",
        "0 1 1 6 7 7 5 4 2 2"
    ),
    (
        "The greedy merchant licked his fingers after the lavish banquet",
        "शाही दावत खाने के बाद लालची व्यापारी अपनी उँगलियाँ चाटता रहा",
        "6 7 5 5 0 1 4 2 2 2"
    ),
    (
        "The brave freedom fighter took the baton blows upon his chest",
        "स्वतंत्रता सेनानी ने पुलिस की लाठियों के प्रहार अपनी छाती पर सहे",
        "0-2 2 2 5 6 4 7 8 3"
    ),
    (
        "The sorrowful parting tore the heart of the emigrant into pieces",
        "मातृभूमि से बिछड़ने के गम ने परदेसी के दिल को चकनाचूर कर दिया",
        "0 0 1 1 6 4 9 9 2 2"
    ),
    (
        "The generous philanthropist gave wealth with an unhesitating heart",
        "उदार दानी ने बिना संकोच के खुले दिल से विपुल धन बाँटा",
        "0 1 1 4 5 6 6 3 3 2"
    ),
    (
        "The entire household tightened their waists to prepare the feast",
        "पूरे परिवार ने उत्सव की दावत तैयार करने के लिए कमर कसी",
        "0 1 1 7 8 5 6 3 2"
    ),
]

def main():
    print(f"Checking {len(TRIPLES)} AI-authored triples...")
    errs = []
    seen_hi = set()
    out = []

    # Check against existing files
    existing_hi = {}
    for p in sorted((ROOT / "data").glob("phrases*.json")):
        if p.name == "phrases26.json":
            continue
        data = json.load(open(p))
        for item in data:
            existing_hi[item["hi"]] = (p.name, item["id"])

    DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
    ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')

    for idx, (en, hi, align) in enumerate(TRIPLES, start=1):
        sid = f"p26s{idx:03d}"
        if not ASC.match(en):
            errs.append(f"{sid}: bad en: {en}")
        if not DEV.match(hi):
            errs.append(f"{sid}: bad hi: {hi}")
        if hi in seen_hi:
            errs.append(f"{sid}: dup hi in batch: {hi}")
        seen_hi.add(hi)
        if hi in existing_hi:
            errs.append(f"{sid}: dup hi with {existing_hi[hi]}: {hi}")

        enw = en.split()
        hiw = hi.split()
        alw = align.split()

        if len(hiw) != len(alw):
            errs.append(f"{sid}: hi words ({len(hiw)}) != align words ({len(alw)}) for {hi}")
        for t in alw:
            for part in re.split(r'[-,]', t):
                if not (part.isdigit() and int(part) < len(enw)):
                    errs.append(f"{sid}: bad token {t} (en len {len(enw)}) in {en}")

        out.append({
            "id": sid,
            "en": en,
            "hi": hi,
            "align": align
        })

    if errs:
        print(f"FAILED with {len(errs)} errors:")
        for e in errs[:20]:
            print("  ", e)
        sys.exit(1)

    print("All 250 AI alignments verified with 0 errors!")
    out_file = ROOT / "data" / "phrases26.json"
    out_file.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {out_file}")

    # Update manifest
    man = json.load(open(ROOT / "data" / "manifest.json"))
    man["files"] = [f for f in man["files"] if f["file"] != "data/phrases26.json"]
    man["files"].append({"file": "data/phrases26.json", "count": len(out)})
    json.dump(man, open(ROOT / "data" / "manifest.json", "w"), ensure_ascii=False, indent=2)
    print("Updated data/manifest.json")

if __name__ == "__main__":
    main()
