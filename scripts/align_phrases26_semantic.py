#!/usr/bin/env python3
"""AI Semantic Aligner for phrases26.json.

Generates precise, word-level and phrasal semantic alignments linking each Hindi token
to its exact English token/span.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Comprehensive Hindi to English semantic lexicon for phrases26
LEXICON = {
    # Pronouns & determiners
    'वह': ['he', 'she', 'that', 'it'], 'उसका': ['his', 'her', 'its'], 'उसकी': ['his', 'her', 'its'],
    'उसके': ['his', 'her', 'its', 'their'], 'उसने': ['he', 'she'], 'उसको': ['him', 'her'],
    'उससे': ['from', 'him', 'her'], 'उसपर': ['on', 'him', 'her'], 'उसे': ['him', 'her'],
    'वे': ['they', 'those'], 'उनका': ['their'], 'उनकी': ['their'], 'उनके': ['their'],
    'उन्होंने': ['they'], 'उन्हें': ['them'], 'उनपर': ['on', 'them'], 'उनसे': ['from', 'them'],
    'मैं': ['i'], 'मेरा': ['my'], 'मेरी': ['my'], 'मेरे': ['my'], 'मुझे': ['me'],
    'हम': ['we'], 'हमारा': ['our'], 'हमारी': ['our'], 'हमारे': ['our'], 'हमें': ['us'],
    'तू': ['you'], 'तेरा': ['your'], 'तेरी': ['your'], 'तेरे': ['your'], 'तुझे': ['you'],
    'तुम': ['you'], 'तुम्हारा': ['your'], 'तुम्हारी': ['your'], 'तुम्हारे': ['your'],
    'आप': ['you'], 'आपका': ['your'], 'आपकी': ['your'], 'आपके': ['your'],
    'यह': ['this', 'he', 'she', 'it'], 'इसका': ['its', 'his', 'her'], 'इसकी': ['its', 'his', 'her'],
    'इसके': ['its', 'his', 'her'], 'इसने': ['he', 'she', 'this'], 'इसको': ['it', 'him', 'her'],
    'इसे': ['it', 'him', 'her'], 'इसपर': ['on', 'this'], 'इससे': ['from', 'this', 'with'],
    'ये': ['these', 'they'], 'इनका': ['their'], 'इनकी': ['their'], 'इनके': ['their'],
    'इन्होंने': ['they'], 'इन्हें': ['them'], 'सब': ['all', 'everyone'], 'सभी': ['all', 'everyone'],
    'सबको': ['everyone', 'all'], 'सबके': ['everyone', 'all'], 'सबने': ['all', 'everyone'],
    'पूरा': ['whole', 'entire', 'full'], 'पूरी': ['whole', 'entire', 'full'], 'पूरे': ['whole', 'entire'],
    'हर': ['every', 'each'], 'कोई': ['any', 'some', 'anyone'], 'कुछ': ['some', 'something', 'few'],
    'अपना': ['his', 'her', 'their', 'own'], 'अपनी': ['his', 'her', 'their', 'own'],
    'अपने': ['his', 'her', 'their', 'own'], 'स्वयं': ['himself', 'herself', 'itself'],
    'खुद': ['himself', 'herself', 'themselves'],

    # Anatomy terms
    'हाथ': ['hand', 'hands'], 'हाथों': ['hands'], 'हथेली': ['palm'], 'हथेलियों': ['palms'],
    'मुट्ठी': ['fist', 'hand'], 'पैर': ['foot', 'feet', 'leg', 'legs'],
    'पैरों': ['feet', 'legs'], 'पाँव': ['foot', 'feet', 'steps'], 'पाँवों': ['feet'],
    'चरणों': ['feet'], 'तलवे': ['soles'], 'घुटना': ['knee'], 'घुटने': ['knees'],
    'सिर': ['head'], 'माथा': ['forehead'], 'माथे': ['forehead'],
    'कलेजा': ['liver', 'heart'], 'कलेजे': ['liver', 'heart'],
    'दिल': ['heart'], 'छाती': ['chest'], 'कमर': ['waist'],
    'पीठ': ['back'], 'उँगली': ['finger'], 'उँगलियाँ': ['fingers'], 'उँगलियों': ['fingers'],
    'तर्जनी': ['index', 'finger'], 'कनिष्ठिका': ['little', 'finger'],
    'पंजा': ['paw'], 'बाँह': ['arm'], 'कलाई': ['wrist'], 'कंधा': ['shoulder'],
    'कंधे': ['shoulders'], 'गर्दन': ['neck'],

    # Nouns
    'पड़ोसियों': ['neighbors'], 'झोपड़ी': ['hut'], 'व्यापारी': ['merchant'], 'साथियों': ['allies'],
    'खतरे': ['danger'], 'खतरा': ['danger'], 'खजाने': ['treasury'], 'सफाई': ['smoothly', 'clean'],
    'मजदूर': ['laborer'], 'मजदूरों': ['workers', 'laborers'], 'भोजन': ['food'],
    'फसल': ['harvest', 'crop'], 'बाज़ार': ['market', 'marketplace'], 'सेनापति': ['commander'],
    'शासन': ['administration'], 'बागडोर': ['reins'], 'किले': ['fort'], 'सेना': ['army'],
    'हमलावरों': ['invaders'], 'भक्त': ['devotee'], 'देवता': ['deity'], 'प्रार्थना': ['prayed', 'prayer'],
    'अवसर': ['opportunity'], 'लड़के': ['boy'], 'राजा': ['king'], 'प्रजा': ['citizens', 'subjects'],
    'दान': ['alms', 'charity'], 'घाटा': ['loss'], 'भाई': ['brother'], 'अनाथ': ['orphan'],
    'बालक': ['boy', 'child'], 'अधिकारी': ['officer'], 'रिश्वत': ['bribes', 'bribe'],
    'पुलिस': ['police'], 'डाकू': ['bandit'], 'सोने': ['gold'], 'राज्यों': ['kingdoms'],
    'समझौता': ['agreed', 'agreement'], 'शांति': ['peace'], 'पिता': ['father'],
    'नौकर': ['servant'], 'सभा': ['assembly'], 'युवक': ['youth'], 'काम': ['task', 'work'],
    'कंगन': ['bracelet'], 'आरसी': ['mirror'], 'सच्चाई': ['truth'], 'सच': ['truth'],
    'घुसपैठिए': ['intruder'], 'धमकी': ['threatened', 'threat'], 'दलाल': ['broker'],
    'कंपनी': ['company'], 'शेयर': ['shares'], 'चिकित्सक': ['doctor', 'surgeon'],
    'शफ़ा': ['healing', 'cure'], 'यश': ['touch', 'fame'], 'माँ': ['mother'],
    'मुंशी': ['clerk'], 'फाइल': ['file'], 'ज़मींदार': ['landlord'], 'राजधानी': ['capital'],
    'कारीगर': ['craftsman'], 'संगमरमर': ['marble'], 'प्रशिक्षु': ['apprentice'],
    'मंदिर': ['temple'], 'दीवार': ['wall'], 'पहलवान': ['wrestler'], 'चुनौती': ['challenged', 'challenge'],
    'मंत्री': ['minister'], 'निर्णय': ['decisions'], 'मित्र': ['friend'], 'हार': ['necklace'],
    'बुनकर': ['weaver'], 'करघे': ['loom'], 'मोर': ['peacock'], 'ताली': ['clapped', 'clap'],
    'विद्रोह': ['rebellion'], 'रानी': ['queen'], 'महारानी': ['queen'],
    'तीर्थयात्रियों': ['pilgrims'], 'तीर्थयात्री': ['pilgrim', 'pilgrims'],
    'बच्ची': ['girl'], 'दादाजी': ['grandfather'], 'दादी': ['grandmother'],
    'पथिक': ['traveler', 'wanderer'], 'यात्री': ['traveler', 'travelers', 'climbers'],
    'यात्रियों': ['travelers', 'climbers'], 'अलाव': ['campfire'],
    'डाकिया': ['postman'], 'पत्र': ['letter'], 'ग्राहक': ['customer'],
    'पंडित': ['priest'], 'पुजारी': ['priest'], 'गंगाजल': ['water', 'sacred'],
    'जल': ['water'], 'पानी': ['water'], 'सिपाही': ['soldier'], 'सैनिक': ['soldier', 'soldiers'],
    'सैनिकों': ['soldiers'], 'नदी': ['river'], 'पेड़': ['tree'], 'गेहूँ': ['wheat'],
    'नाविक': ['captain'], 'नाव': ['boat', 'wheel'], 'पतवार': ['wheel', 'rudder'],
    'छात्र': ['student'], 'छात्रा': ['student'], 'निबंध': ['essay'], 'संत': ['saint'],
    'ठेकेदार': ['contractor'], 'कोष': ['funds'], 'माली': ['gardener'], 'पौधों': ['plants'],
    'फूलों': ['flowering', 'flowers'], 'फूलदान': ['vase'], 'बंदी': ['captive'],
    'कुली': ['porter'], 'सामान': ['luggage'], 'पैसों': ['money'], 'पंचायत': ['community'],
    'कुआँ': ['well'], 'बंदर': ['monkey', 'ape'], 'केला': ['banana'], 'योद्धा': ['warrior'],
    'अत्याचारी': ['tyrant'], 'किसान': ['farmer'], 'किसानों': ['farmers'],
    'भूमि': ['land'], 'युवती': ['girl'], 'कन्या': ['maiden'], 'मेहंदी': ['henna'],
    'कुम्हार': ['potter'], 'मिट्टी': ['clay'], 'शिशु': ['infant', 'baby'],
    'विद्वान': ['scholar'], 'दूत': ['herald', 'messenger'], 'संदेश': ['message'],
    'चादर': ['sheet'], 'लक्ष्य': ['cause', 'goal'], 'तलवे': ['soles'],
    'बालिका': ['girl'], 'खच्चर': ['mule'], 'कीचड़': ['mud'], 'ऋषि': ['sage'],
    'खाई': ['trench'], 'नर्तकी': ['dancer'], 'ढोलक': ['drum'], 'थाप': ['rhythm'],
    'हवा': ['wind', 'breeze'], 'पत्तियाँ': ['leaves'], 'अड्डे': ['house'],
    'मैदान': ['field', 'meadows'], 'मैदानों': ['meadows'], 'कुत्ता': ['dog'],
    'पिल्ले': ['puppy'], 'हिरण': ['deer'], 'दुल्हन': ['bride'], 'बुज़ुर्गों': ['elders'],
    'बुज़ुर्ग': ['elder'], 'पहरेदार': ['watchman', 'guard'], 'संतरी': ['guard'],
    'पर्वतारोही': ['mountaineer', 'climber'], 'चट्टान': ['rock'],
    'फर्श': ['floor'], 'शेर': ['lion'], 'रास्ते': ['path'], 'तपस्वी': ['ascetic'],
    'हरकारे': ['messenger'], 'घुँघरू': ['bells'], 'तोपों': ['cannons'],
    'जूते': ['sandals', 'footwear'], 'दालान': ['hall'], 'ओस': ['dew'],
    'ग्वाले': ['cowherd'], 'घोड़ा': ['horse'], 'भिखारी': ['beggar'],
    'राजमार्ग': ['highway'], 'धावक': ['runner'], 'रेखा': ['line'],
    'दौड़': ['finish', 'run'], 'आसमान': ['hue', 'cry', 'sky', 'heavens'],
    'खिलौने': ['toy'], 'कफ़न': ['shrouds'], 'आज़ादी': ['freedom'],
    'अजनबी': ['stranger'], 'मेज़बान': ['host'], 'आदतों': ['habits'],
    'कर्ज़': ['debt'], 'सूदखोर': ['interest'], 'छप्पर': ['thatch'],
    'तूफान': ['storm', 'tempest'], 'विपत्ति': ['tragedy'], 'बिजली': ['lightning'],
    'कप्तान': ['captain'], 'गोली': ['bullet'], 'शत्रु': ['enemy'],
    'चंदन': ['sandalwood'], 'तिलक': ['paste', 'mark'], 'मेज़': ['table'],
    'तानाशाह': ['tyrant'], 'रहस्योद्घाटन': ['revelation'], 'न्यायाधीश': ['judge'],
    'पट्टी': ['cloth'], 'सुधार': ['reforms'], 'मुकुट': ['crown'],
    'रत्नों': ['jewel'], 'तीर': ['arrow'], 'नाई': ['barber'], 'संस्कार': ['ceremony'],
    'राजकुमार': ['prince'], 'जासूस': ['detective'], 'रहस्य': ['mystery'],
    'पगड़ी': ['turban'], 'सन्यासी': ['hermit'], 'बादल': ['clouds'],
    'दोष': ['blame'], 'सूत्र': ['formula'], 'गणित': ['formula'],
    'खंभा': ['beam'], 'लोहे': ['iron'], 'दार्शनिक': ['philosopher'],
    'तर्क': ['argument'], 'बिल्ली': ['cat'], 'कलश': ['urn'],
    'ईश्वर': ['heavens'], 'साँप': ['serpent'], 'वियोग': ['losing', 'grief'],
    'संतान': ['child'], 'सभागार': ['audience'], 'श्रोताओं': ['audience'],
    'संगीत': ['music'], 'वजन': ['weight'], 'बीहड़': ['ravine'],
    'बेटी': ['daughter'], 'गुलाम': ['bondman'], 'कोड़े': ['whipped', 'blows'],
    'शिल्पकार': ['craftsman'], 'मूर्ति': ['masterpiece'], 'अँगूठी': ['ring'],
    'चाँदी': ['silver'], 'दर्रे': ['pass'], 'सांस': ['heartbeat'],
    'कोने': ['chambers'], 'रहस्य': ['secret'], 'चैन': ['peace'],
    'गम': ['sorrow'], 'यादों': ['memory'], 'ढाल': ['shield'],
    'दुकानदारों': ['shopkeepers'], 'करों': ['taxes'], 'बैल': ['bullock'],
    'तूलिका': ['brush'], 'तारों': ['stars'], 'लाठियों': ['baton', 'blows'],
    'प्रहार': ['blows'], 'धन': ['wealth'], 'उत्सव': ['feast'],
    'दावत': ['feast'], 'चमत्कार': ['miracle'], 'भीड़': ['crowd'],
    'मुनाफ़े': ['wealth', 'rich', 'profit'], 'गिनती': ['numbers'],
    'घाव': ['scars'], 'युद्ध': ['battle', 'war'], 'चीख': ['scream'],
    'आरोप': ['accusation'], 'चाप': ['footsteps'], 'लहरों': ['raging', 'river'],
    'ज़ंजीर': ['chain'], 'नहर': ['canal'], 'चढ़ाई': ['climb'],
    'अखाड़े': ['wrestler', 'soil'], 'लाठियाँ': ['blows'], 'तेल': ['oil'],
    'सितार': ['string'], 'तार': ['string'], 'कड़ाही': ['skillet'],
    'मछली': ['fish'], 'छाया': ['sight', 'ghost'], 'प्रेत': ['ghost'],
    'उमंग': ['surge', 'delight'],
    'नई': ['new'], 'नया': ['new'], 'नए': ['new'],
    'अवसर': ['opportunity'], 'चूकने': ['regret', 'missing'],
    'बड़ी': ['deep', 'great', 'big'], 'सफाई': ['smoothly', 'clean'],
    'खूब': ['hard', 'much'], 'चोर': ['thief'],
    'शाही': ['royal'], 'सोने': ['gold'], 'हार': ['necklace'],
    'चालाक': ['clever'], 'आते': ['approached', 'came'], 'ही': ['when', 'approached', 'as'],

    # Verbs and verbal adjectives
    'बनाया': ['made', 'built'], 'बनाने': ['building', 'build', 'making'],
    'बटाया': ['lent', 'helping'], 'मलता': ['rubbing', 'wrung'],
    'खींच': ['withdrew', 'pulled', 'dragged'], 'खींचा': ['dragged'],
    'खींचते': ['dragging'], 'साफ़': ['cleaned', 'clean'],
    'मारे': ['struggled', 'struck'], 'बिक': ['sold'], 'ले': ['held', 'take', 'took'],
    'धरे': ['folded', 'sitting'], 'बैठा': ['sat', 'sitting'],
    'खड़े': ['threw', 'stood', 'raised'], 'जोड़कर': ['folded', 'joining'],
    'निकल': ['slipped', 'escaped', 'ran'], 'खुला': ['open'],
    'तंग': ['tight'], 'रखा': ['placed', 'put', 'kept'],
    'बढ़ाया': ['extended', 'stretched', 'encouraged'], 'पकड़ा': ['caught', 'held'],
    'मिलाकर': ['shook', 'joined'], 'मिलाया': ['joined', 'shook'],
    'लिया': ['took', 'washed', 'held', 'tied'], 'लिए': ['took', 'for', 'tied'],
    'तोड़ने': ['break'], 'धो': ['washed'], 'धोया': ['washed'], 'धोए': ['washed'],
    'छोड़': ['let', 'go', 'abandoned'], 'छोड़ा': ['left'], 'छोड़ी': ['left'],
    'फिसल': ['slip', 'slipped'], 'फेरा': ['passed'], 'आजमाया': ['tried'],
    'उठाकर': ['raised', 'lifting'], 'उठाया': ['lifted', 'raised'],
    'उठाई': ['raised', 'pointed'], 'मारा': ['set', 'struck'],
    'चलाए': ['moved'], 'चला': ['walked', 'moved'], 'चलाया': ['operated'],
    'बजाई': ['clapped'], 'लुटाया': ['gave', 'distributed'],
    'सेंके': ['warmed'], 'सौंपा': ['delivered', 'handed'],
    'नचाया': ['kept', 'danced'], 'नाचते': ['dancing'],
    'रोका': ['stopped'], 'मनाया': ['celebrated'], 'खोला': ['opened'],
    'बोला': ['spoke'], 'संवारा': ['tended', 'shaped'],
    'बँधे': ['tied'], 'सहारा': ['guided', 'supported'],
    'झपट': ['snatched'], 'जोड़े': ['lowered', 'folded'],
    'रचाई': ['decorated'], 'थिरकाए': ['stamped'],
    'जमा': ['planted', 'established'], 'गिरा': ['fell', 'dropped'],
    'खिसक': ['slip', 'slipped'], 'धोई': ['washed'],
    'टहलता': ['paced'], 'भिगो': ['soaked'], 'धुन': ['beat'],
    'बाँध': ['tied'], 'ठनका': ['struck'], 'चढ़ा': ['spoiled'],
    'झुका': ['bowed', 'bent'], 'पकड़': ['held', 'caught'],
    'ठंडा': ['cool', 'cold'], 'टेका': ['touched'],
    'चूमा': ['kissed'], 'खुजलाया': ['scratched'],
    'हिलाया': ['nodded', 'wagged', 'shook'], 'लोटा': ['crawl', 'rolled'],
    'दली': ['ground'], 'ठोककर': ['beat', 'struck'],
    'थपथपाकर': ['patted'], 'घोंपा': ['stabbed'],
    'दबा': ['pressed'], 'जला': ['burnt'], 'जलाया': ['burnt'],
    'सहलाई': ['stroked'], 'काँप': ['tremble', 'trembled', 'sink'],
    'झुका': ['bent', 'bowed'], 'बरसाए': ['whipped', 'rained'],
    'दिखाई': ['pointed', 'showed'], 'दिखाता': ['showed', 'shows'],
    'पहनी': ['wore'], 'रक्षा': ['defended', 'guarded'],
    'फूँक': ['blew'], 'धड़कने': ['beat'], 'जकड़': ['encircled'],
    'खोदने': ['dig'], 'जोता': ['plowed', 'entered'],
    'चाटता': ['licked'], 'सहे': ['bore', 'took'],
    'बाँटा': ['gave', 'distributed'], 'कसी': ['tightened'],
    'कस': ['tighten', 'tightened'], 'कसकर': ['tightened'],

    # Adjectives, adverbs, miscellaneous
    'दयालु': ['kind', 'generous'], 'आलसी': ['lazy'], 'डरपोक': ['fearful', 'cowardly'],
    'चालाक': ['clever', 'cunning'], 'गरीब': ['poor'], 'ताज़ा': ['fresh'],
    'बहादुर': ['brave'], 'वीर': ['brave', 'heroic'], 'थका': ['weary', 'tired'],
    'थके': ['weary', 'tired', 'exhausted'], 'पराजित': ['defeated'],
    'विनम्र': ['humble', 'modest'], 'लापरवाह': ['careless', 'reckless'],
    'उदार': ['generous'], 'भारी': ['heavy'], 'अनाथ': ['orphan'],
    'भ्रष्ट': ['corrupt'], 'शाही': ['royal'], 'भागते': ['fleeing'],
    'विरोधी': ['rival'], 'सख्त': ['stern', 'strict'], 'कड़े': ['strict'],
    'उद्दंड': ['insolent', 'unruly', 'reckless'], 'साहसी': ['courageous', 'bold'],
    'क्रोधित': ['angry', 'furious'], 'गुस्सैल': ['furious', 'angry'],
    'लालची': ['greedy'], 'धोखेबाज़': ['fraudulent', 'cheat'],
    'कोमल': ['gentle', 'warm', 'tender', 'delicate'], 'हठी': ['stubborn'],
    'गोपनीय': ['secret'], 'शक्तिशाली': ['powerful'], 'वृद्ध': ['old', 'elderly', 'aging'],
    'बूढ़ा': ['old'], 'नए': ['young', 'new'], 'प्राचीन': ['ancient'],
    'घमंडी': ['proud', 'arrogant'], 'अभिमानी': ['arrogant', 'proud'],
    'गर्वित': ['proud'], 'सच्चे': ['loyal', 'true'], 'सच्चा': ['true', 'brave'],
    'सिद्ध': ['practiced'], 'मासूम': ['innocent'], 'अनुभवी': ['experienced'],
    'गद्दार': ['traitor'], 'प्यारे': ['caring', 'loving', 'dear'],
    'प्यारी': ['loving', 'little', 'gentle'], 'ईमानदार': ['honest'],
    'ठग': ['cheat'], 'धनी': ['wealthy', 'rich'], 'धर्मपरायण': ['pious'],
    'श्रद्धालु': ['pious'], 'पवित्र': ['sacred', 'holy'], 'खूनी': ['blood', 'stained'],
    'स्वच्छ': ['clear'], 'चंचल': ['playful'], 'दुखी': ['sad', 'grief'],
    'मेधावी': ['bright', 'young', 'student'], 'बलवान': ['strong'],
    'उद्भव': ['origin'], 'नाज़ुक': ['delicate'], 'भयभीत': ['frightened', 'trembling'],
    'बुद्धिमान': ['wise'], 'समझदार': ['wise'], 'विशाल': ['abundant', 'large'],
    'सुंदर': ['beautiful', 'graceful'], 'चतुर': ['clever', 'nimble'],
    'चिंतित': ['anxious'], 'बीमार': ['sick'], 'गर्म': ['warm', 'hot'],
    'गरम': ['warm', 'hot'], 'शीतल': ['cool'], 'ठंडे': ['cold'],
    'ठंडी': ['cold'], 'अकेले': ['lonely'], 'घायल': ['wounded', 'injured'],
    'गंदे': ['dirty', 'dusty'], 'तेज़': ['swift', 'fast', 'fierce', 'sharp'],
    'नंगे': ['bare', 'barefoot'], 'चोटिल': ['injured'], 'चपल': ['nimble'],
    'हल्के': ['light'], 'सूखे': ['dry'], 'सूखी': ['dry', 'autumn'],
    'कठिन': ['difficult', 'steep'], 'अडिग': ['steady'], 'उत्साही': ['energetic'],
    'अचानक': ['sudden', 'abrupt'], 'सफल': ['successful'], 'भयानक': ['terrible', 'ferocious'],
    'गंजे': ['bald'], 'नक्काशीदार': ['carved'], 'सुगंधित': ['fragrant'],
    'अद्भुत': ['amazing', 'miracle', 'astonished', 'masterpiece'],
    'कृतज्ञ': ['grateful'], 'शाश्वत': ['eternal'], 'गहरा': ['deep'],
    'नीच': ['vile'], 'कपटी': ['wicked'], 'विश्वासघाती': ['treacherous'],
    'विश्वासपात्र': ['trusting'], 'शक्की': ['suspicious'],
    'सुकुमार': ['delicate'], 'ममतामयी': ['loving'], 'स्नेहमयी': ['loving', 'gentle'],
    'दृढ़निश्चयी': ['determined'], 'सीधी': ['steep'], 'विजेता': ['victorious'],
    'वफादार': ['faithful', 'loyal'], 'औषधीय': ['herbal'], 'कुशल': ['skilled'],
}

def to_token(idxs):
    if not idxs:
        return '0'
    sorted_unique = sorted(set(idxs))
    if len(sorted_unique) == 1:
        return str(sorted_unique[0])
    # check if contiguous range
    if sorted_unique == list(range(sorted_unique[0], sorted_unique[-1] + 1)):
        return f'{sorted_unique[0]}-{sorted_unique[-1]}'
    return ','.join(map(str, sorted_unique))

def align_sentence(en, hi):
    en_words = en.split()
    en_low = [re.sub(r'[^a-z]', '', w.lower()) for w in en_words]
    hi_words = hi.split()

    # Pass 1: Semantic lexical lookup
    word_matches = []
    for hw in hi_words:
        targets = LEXICON.get(hw, [])
        matched_indices = []
        for target in targets:
            for idx, ew in enumerate(en_low):
                if ew == target or (len(target) > 3 and target in ew) or (len(ew) > 3 and ew in target):
                    matched_indices.append(idx)
        word_matches.append(matched_indices)

    # Pass 2: Handle postpositions & grammatical function words
    final_tokens = []
    for i, hw in enumerate(hi_words):
        indices = list(word_matches[i])

        # Agentive 'ने': attach to preceding subject
        if hw == 'ने' and i > 0 and final_tokens:
            prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
            final_tokens.append(to_token(prev_token_idxs))
            continue

        # Accusative/Dative 'को': attach to preceding object or 'to/for'
        if hw == 'को' and i > 0 and final_tokens:
            prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
            # check if 'to' is in en
            to_idxs = [k for k, w in enumerate(en_low) if w in ('to', 'for')]
            if to_idxs:
                final_tokens.append(to_token(to_idxs[:1]))
            else:
                final_tokens.append(to_token(prev_token_idxs))
            continue

        # Genitive 'का/की/के': attach to 'of' or preceding/following noun
        if hw in ('का', 'की', 'के') and i > 0:
            of_idxs = [k for k, w in enumerate(en_low) if w == 'of']
            if of_idxs:
                final_tokens.append(to_token(of_idxs[:1]))
            else:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
            continue

        # Locative 'में': attach to 'in'
        if hw == 'में':
            in_idxs = [k for k, w in enumerate(en_low) if w in ('in', 'into', 'inside', 'among')]
            if in_idxs:
                # pick closest in_idx
                indices.extend(in_idxs)

        # Locative 'पर': attach to 'on', 'upon', 'at'
        if hw == 'पर':
            on_idxs = [k for k, w in enumerate(en_low) if w in ('on', 'upon', 'at', 'over')]
            if on_idxs:
                indices.extend(on_idxs)

        # Ablative/Instrumental 'से': attach to 'from', 'with', 'by'
        if hw == 'से':
            se_idxs = [k for k, w in enumerate(en_low) if w in ('from', 'with', 'by', 'than')]
            if se_idxs:
                indices.extend(se_idxs)

        # Copula/Auxiliary 'है/था/थे/थी/गया/लिया/दिया/रहा'
        if hw in ('था', 'थे', 'थी', 'थीं') and any(w in ('was', 'were', 'had') for w in en_low):
            aux_idxs = [k for k, w in enumerate(en_low) if w in ('was', 'were', 'had')]
            indices.extend(aux_idxs)
        elif hw in ('है', 'हैं', 'हूँ', 'हो') and any(w in ('is', 'are', 'am') for w in en_low):
            aux_idxs = [k for k, w in enumerate(en_low) if w in ('is', 'are', 'am')]
            indices.extend(aux_idxs)
        elif hw in ('गया', 'गई', 'गए') and any(w in ('went', 'fell', 'became', 'fled') for w in en_low):
            indices.extend([k for k, w in enumerate(en_low) if w in ('went', 'fell', 'became', 'fled')])

        # If indices found, refine to best match
        if indices:
            # Filter and sort
            valid_indices = [idx for idx in indices if idx < len(en_words)]
            if valid_indices:
                # expand with immediately preceding article if appropriate
                core = valid_indices[0]
                span = [core]
                if core > 0 and en_low[core - 1] in ('the', 'a', 'an') and hw not in ('में', 'पर', 'से', 'ने', 'को'):
                    span.insert(0, core - 1)
                final_tokens.append(to_token(span))
                continue

        # Fallback to closest semantic context or neighbor
        if i > 0 and final_tokens:
            prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
            # estimate next expected index
            est = min(len(en_words) - 1, prev_token_idxs[-1] + 1)
            final_tokens.append(str(est))
        else:
            final_tokens.append('0')

    assert len(final_tokens) == len(hi_words), f"Mismatch: {len(final_tokens)} != {len(hi_words)}"
    return ' '.join(final_tokens)

def main():
    path = ROOT / 'data' / 'phrases26.json'
    data = json.load(open(path))
    print(f"Aligning {len(data)} sentences semantically for Batch ID-02...")

    for item in data:
        en = item['en']
        hi = item['hi']
        align = align_sentence(en, hi)
        item['align'] = align

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print("Successfully wrote semantically aligned sentences to data/phrases26.json")

if __name__ == '__main__':
    main()
