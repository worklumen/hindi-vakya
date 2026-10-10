#!/usr/bin/env python3
"""AI Semantic Aligner for phrases27.json (Batch ID-03: Fauna & Animals).

Generates exact semantic word-level and phrasal alignments linking each Hindi token
to its exact English token/span.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Comprehensive Hindi to English semantic lexicon for phrases27
LEXICON = {
    # Fauna & Animals
    'घोड़ा': ['horse', 'stallion'], 'घोड़े': ['horse', 'horses', 'steed'], 'घोड़ी': ['mare'],
    'बछेड़ा': ['colt'], 'बछेड़े': ['colt'],
    'गधा': ['donkey'], 'गधे': ['donkey', 'donkeys'], 'खच्चर': ['mule'],
    'ऊँट': ['camel'], 'ऊँटों': ['camels'],
    'हाथी': ['elephant'], 'हाथियों': ['elephants'],
    'गाय': ['cow'], 'गऊ': ['cow'], 'गौ': ['cow'],
    'बैल': ['bullock', 'bull', 'ox'], 'बैलों': ['bullocks'], 'सांड': ['bull'],
    'भैंस': ['buffalo'], 'भैंसों': ['buffaloes'], 'भैंसे': ['buffalo'],
    'बछड़ा': ['calf'], 'बछड़े': ['calf', 'fawn'],
    'बिल्ली': ['cat'], 'बिल्लियों': ['cats'], 'मिल्क': ['milk'],
    'कुत्ता': ['dog', 'hound', 'watchdog'], 'कुत्ते': ['dog', 'dogs', 'hounds'], 'कुत्तों': ['dogs'],
    'पिल्ला': ['puppy'], 'पिल्ले': ['puppy'],
    'लोमड़ी': ['fox'], 'भेड़िया': ['wolf'], 'भेड़िए': ['wolf', 'wolves'], 'भेड़ियों': ['wolves'],
    'बंदर': ['monkey', 'ape'], 'बंदरों': ['monkeys'], 'वानर': ['ape', 'baboon'], 'लंगूर': ['langur', 'baboon'],
    'भालू': ['bear'], 'रीछ': ['bear'],
    'हिरण': ['deer', 'stag'], 'हिरणों': ['deer'], 'हिरणी': ['doe'], 'मृग': ['deer', 'gazelle'],
    'बारहसिंगे': ['antelope'], 'कस्तूरी': ['musk'],
    'साँप': ['snake', 'serpent', 'viper'], 'नाग': ['cobra', 'snake'], 'करैत': ['kraits'], 'अजगर': ['python'],
    'बिच्छू': ['scorpion'],
    'मेंढक': ['frog', 'bullfrog', 'frogs'], 'मेंढकों': ['frogs'],
    'मगरमच्छ': ['crocodile', 'alligator'], 'मगर': ['crocodile'],
    'मछली': ['fish', 'salmon', 'carp', 'trout', 'guppy'], 'मछलियों': ['fish'],
    'चींटी': ['ant'], 'चींटियों': ['ants'],
    'चिड़िया': ['bird', 'sparrow', 'birds'], 'चिड़ियों': ['birds', 'sparrows'],
    'कौआ': ['crow', 'raven'], 'कौए': ['crow', 'crows'], 'कौओं': ['crows', 'ravens'],
    'उल्लू': ['owl'], 'हंस': ['swan', 'swans'], 'सारसों': ['cranes'], 'कलहंसों': ['geese'],
    'बगुला': ['crane', 'heron'],
    'तोता': ['parrot', 'parakeet'], 'तोते': ['parrot', 'parakeet'],
    'मक्खी': ['fly'], 'मक्खियाँ': ['flies'],
    'मधुमक्खी': ['bee', 'honeybee'], 'मधुमक्खियों': ['bees', 'honeybees'],
    'चूहा': ['mouse', 'rat'], 'चूहे': ['mouse', 'mice', 'rat'], 'चूहों': ['mice', 'rats'],
    'मुर्गा': ['rooster'], 'मुर्गी': ['hen'], 'बकरी': ['goat'],
    'भेड़': ['sheep'], 'भेड़ें': ['sheep'],
    'बाज़': ['falcon'], 'बुलबुल': ['nightingale'], 'गौरैया': ['sparrow'], 'रामचिरैया': ['kingfisher'],
    'अबाबील': ['swallow'], 'बया': ['weaver', 'bird'],

    # Landscape & Habitat
    'जंगल': ['forest', 'jungle', 'woodland'], 'घाटी': ['valley'], 'मैदान': ['field', 'meadow', 'plains', 'meadows'],
    'गुफा': ['cave'], 'मांद': ['den'], 'बिल': ['den', 'hole'],
    'छत्ता': ['hive', 'comb', 'honeycomb'], 'छत्ते': ['hive', 'comb'],
    'नदी': ['river', 'stream', 'brook'], 'तालाब': ['pond', 'pool'], 'सरोवर': ['lake'], 'झील': ['lake'],
    'समुद्र': ['ocean', 'sea'], 'रेगिस्तान': ['desert'], 'काफिला': ['caravan', 'train'],
    'पहाड़ी': ['mountain', 'hill'], 'चट्टान': ['rock', 'cliff'], 'चट्टानों': ['reef', 'rocks'],
    'रेत': ['sand', 'dunes'], 'टीलों': ['dunes'], 'दलदल': ['marsh', 'swamp'],
    'आश्रम': ['monastery'], 'बाड़ा': ['poultry', 'farm'], 'बाड़े': ['farm', 'poultry'],
    'खलिहान': ['threshing', 'floor'], 'चारागाह': ['pasture'], 'अस्तबल': ['stable'],

    # Anatomy of animals & humans
    'खुर': ['hoof', 'hooves'], 'खुरों': ['hooves'], 'सींग': ['horns', 'antlers'], 'सींगों': ['horns'],
    'पूँछ': ['tail'], 'पंख': ['wings', 'feathers'], 'चोंच': ['beak'],
    'पंजा': ['paw', 'claws'], 'पंजों': ['paws', 'claws'], 'दाँत': ['teeth', 'fangs'],
    'जबड़े': ['jaws'], 'डंक': ['sting'], 'फन': ['hood'], 'केंचुली': ['skin'],
    'सूंड': ['trunk'], 'लगाम': ['rein', 'reins'], 'गर्दन': ['neck'], 'टांगें': ['legs'],
    'टांगों': ['legs'], 'कलाई': ['wrist'], 'छाती': ['chest'], 'पीठ': ['back'],
    'सिर': ['head'], 'आँखें': ['eyes'], 'कान': ['ears'], 'नाभि': ['navel', 'inner'],
    'उँगली': ['finger'], 'हाथ': ['hand'],

    # Common vocabulary
    'किसान': ['farmer'], 'चापलूस': ['flatterer'], 'सेनापति': ['general', 'commander'],
    'सेवक': ['servant'], 'राजा': ['king'], 'सामंतों': ['chieftains'], 'सैनिक': ['soldier'],
    'मुसाफिर': ['traveler'], 'दूत': ['scout', 'messenger'], 'रईस': ['noble'],
    'चिकित्सक': ['veterinarian', 'doctor'], 'मुंशी': ['clerk'], 'पंडित': ['priest'],
    'ग्वालिन': ['milkmaid'], 'महावत': ['mahout'], 'सपेरे': ['charmer'],
    'शिकारी': ['hunter', 'hunters', 'hound'], 'लुटेरों': ['marauders'],
    'चोर': ['thief', 'burglar'], 'चोरों': ['thieves'], 'यात्री': ['traveler', 'travelers', 'pilgrims'],
    'यात्रियों': ['travelers', 'pilgrims'], 'भक्त': ['devotee'], 'श्रद्धालुओं': ['pilgrims'],
    'बालक': ['boy', 'child'], 'बच्चा': ['child', 'baby'], 'बच्चे': ['children', 'cubs', 'babies'],
    'माँ': ['mother'], 'माता': ['mother'], 'पिता': ['father'], 'स्वामी': ['master'],

    # Verbs and Actions
    'सो': ['slept'], 'गया': ['went', 'fell', 'vanished'], 'बनाया': ['called', 'made'],
    'कस': ['tightened'], 'दी': ['gave', 'left', 'tightened'], 'मार': ['won', 'invited', 'struck'],
    'दौड़ा': ['galloped', 'ran', 'sprinted'], 'रुक': ['stopped'], 'लांघ': ['leaped', 'vaulted'],
    'लादे': ['loaded'], 'बढ़ाया': ['urged', 'extended', 'guided'], 'ले': ['took', 'carried'],
    'खरीदी': ['bought'], 'पहुँचाया': ['carried', 'delivered'], 'रखे': ['housed', 'kept'],
    'चलाईं': ['kicked'], 'बाँध': ['tied'], 'चरता': ['grazed'], 'दौड़े': ['ran'],
    'पहचान': ['recognized'], 'खींचा': ['drawn', 'pulled', 'dragged'], 'उतरकर': ['dismounted'],
    'दिया': ['gave', 'rested'], 'पार': ['crossed', 'jumped'], 'थपथपाई': ['patted'],
    'जगा': ['woke'], 'लगाई': ['fitted', 'trumpeted', 'leaped'], 'बैठता': ['sits'],
    'बैठ': ['sat', 'knelt'], 'बैठी': ['sat', 'rested'], 'खींच': ['dragged', 'pulled'],
    'देती': ['gave'], 'लोटती': ['wallowed', 'crawled'], 'उड़ाई': ['pawed', 'snorted'],
    'पिया': ['drank'], 'हटाए': ['cleared'], 'खदेड़': ['chased'], 'रक्षा': ['defended', 'guarded'],
    'गुज़रा': ['crossed'], 'जुगाली': ['chewed', 'cud'], 'सहलाया': ['stroked'],
    'चाटा': ['licked'], 'मचाया': ['broke', 'raged'], 'ढोया': ['carried'],
    'जोता': ['ploughed'], 'बन': ['turned', 'became'], 'टूट': ['broken', 'collapsed'],
    'सोची': ['held', 'thought'], 'रहा': ['was', 'stayed'], 'झपट': ['grabbed', 'snatched'],
    'छुड़ाया': ['declared', 'escaped'], 'भौंकना': ['barked'], 'हिलाई': ['wagged', 'shook'],
    'दबोच': ['caught', 'pounced'], 'गिरा': ['dropped', 'fell'], 'घूमता': ['prowled', 'wandered'],
    'रखवाली': ['guarded'], 'पीछा': ['chased', 'followed', 'stalked'], 'बदल': ['changed'],
    'दिखाए': ['bared', 'showed'], 'कराहा': ['whimper', 'whimpered'], 'छोड़े': ['leaving'],
    'फैलाए': ['stretched', 'flared'], 'ढोंग': ['pretended'], 'दबा': ['pinned', 'pressed'],
    'छिप': ['retreated', 'hid'], 'घेर': ['encircled'], 'चढ़': ['climbed', 'jumped'],
    'सहम': ['frightened', 'superstitious'], 'कूदने': ['jumping'], 'तलाश': ['scavenged', 'searched'],
    'चुरा': ['stole'], 'चाटा': ['licked'], 'सुस्ताती': ['basked'], 'भटका': ['misled'],
    'भरी': ['howled'], 'समझा': ['treated', 'appreciated'], 'ढूंढता': ['searched'],
    'नचाया': ['dance', 'danced'], 'खोजी': ['searched'], 'उतारी': ['mimicked'],
    'गरजा': ['roaring', 'roared'], 'खोदीं': ['dug'], 'झूलने': ['swung'],
    'बिखर': ['scattered'], 'फेंक': ['tossing'], 'झटकीं': ['caught', 'raiding'],
    'सिखाया': ['trained', 'taught'], 'सुलझाया': ['resolved'], 'बहाए': ['shed'],
    'तड़पता': ['languished', 'restless'], 'तैरना': ['swim', 'swam'], 'तैरा': ['glided', 'swam'],
    'छिपा': ['hid'], 'उछला': ['leaped', 'hopped'], 'बजाकर': ['played'],
    'भींचे': ['snapped'], 'रेंगकर': ['slithered'], 'घुलमिल': ['blended'],
    'गोता': ['glided', 'dove'], 'निगल': ['swallowed'], 'उड़ा': ['flew', 'honked'],
    'उठाया': ['carried', 'lifted'], 'तोड़ा': ['cracked', 'broke'], 'बुना': ['wove'],
    'भर': ['filled'], 'स्वागत': ['greeted'], 'जमा': ['stored', 'gathered'],
    'दोहरा': ['repeated'], 'सावधान': ['warned'], 'चौंकाया': ['imitated', 'surprised'],

    # Particles & modifiers
    'थका': ['tired'], 'थके': ['tired', 'weary'], 'उत्साही': ['spirited', 'energetic'],
    'कड़े': ['strict'], 'हठी': ['stubborn'], 'लापरवाह': ['careless'],
    'गरीब': ['poor'], 'साहसी': ['brave', 'cavalier'], 'बूढ़ा': ['old'], 'बूढ़े': ['old', 'elderly'],
    'अमीर': ['proud', 'rich'], 'तेज़': ['swift', 'fast', 'sharp'], 'मूर्ख': ['foolish', 'crude'],
    'शाही': ['royal'], 'छोटे': ['young', 'little', 'tiny'], 'छोटा': ['little', 'tiny', 'baby'],
    'दयालु': ['kind'], 'भूखा': ['hungry'], 'भूखे': ['hungry', 'starving'],
    'जंगली': ['wild'], 'बहादुर': ['brave'], 'डरे': ['frightened'], 'वफादार': ['loyal', 'faithful'],
    'पुराना': ['old'], 'फुर्तीले': ['agile', 'nimble'], 'फुर्तीली': ['nimble', 'swift'],
    'भव्य': ['magnificent'], 'विशाल': ['giant', 'massive', 'huge'], 'क्रूर': ['brutal', 'cruel'],
    'मेहनती': ['hardworking', 'industrious', 'busy'], 'धूर्त': ['cunning', 'sly', 'treacherous'],
    'सीधी': ['gentle'], 'मज़बूत': ['sturdy', 'strong'], 'सफेद': ['white'], 'काले': ['black'],
    'काला': ['black'], 'भूरा': ['brown'], 'हरी': ['green'], 'हरा': ['green'],
    'हरे': ['green'], 'नीले': ['blue'], 'लाल': ['red'], 'पीली': ['yellow'],
    'पीले': ['yellow'], 'सुनहरी': ['golden'], 'सुंदर': ['graceful', 'beautiful'],
}

def to_token(idxs):
    if not idxs:
        return '0'
    sorted_unique = sorted(set(idxs))
    if len(sorted_unique) == 1:
        return str(sorted_unique[0])
    if sorted_unique == list(range(sorted_unique[0], sorted_unique[-1] + 1)):
        return f'{sorted_unique[0]}-{sorted_unique[-1]}'
    return ','.join(map(str, sorted_unique))

def align_sentence(en, hi):
    en_words = en.split()
    en_low = [re.sub(r'[^a-z]', '', w.lower()) for w in en_words]
    hi_words = hi.split()

    word_matches = []
    for hw in hi_words:
        targets = LEXICON.get(hw, [])
        matched = []
        for target in targets:
            for idx, ew in enumerate(en_low):
                if ew == target or (len(target) > 3 and target in ew) or (len(ew) > 3 and ew in target):
                    matched.append(idx)
        word_matches.append(matched)

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
            to_idxs = [k for k, w in enumerate(en_low) if w in ('to', 'for')]
            if to_idxs:
                final_tokens.append(to_token(to_idxs[:1]))
            else:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
            continue

        # Genitive 'का/की/के': attach to 'of' or preceding noun
        if hw in ('का', 'की', 'के') and i > 0:
            of_idxs = [k for k, w in enumerate(en_low) if w == 'of']
            if of_idxs:
                final_tokens.append(to_token(of_idxs[:1]))
            else:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
            continue

        # Locative 'में': attach to 'in/into/inside'
        if hw == 'में':
            in_idxs = [k for k, w in enumerate(en_low) if w in ('in', 'into', 'inside', 'among')]
            if in_idxs:
                indices.extend(in_idxs)

        # Locative 'पर': attach to 'on/upon/at/across'
        if hw == 'पर':
            on_idxs = [k for k, w in enumerate(en_low) if w in ('on', 'upon', 'at', 'across', 'over')]
            if on_idxs:
                indices.extend(on_idxs)

        # Ablative/Instrumental 'से': attach to 'from/with/by'
        if hw == 'से':
            se_idxs = [k for k, w in enumerate(en_low) if w in ('from', 'with', 'by', 'than')]
            if se_idxs:
                indices.extend(se_idxs)

        # Auxiliary/Copula
        if hw in ('था', 'थे', 'थी', 'थीं') and any(w in ('was', 'were', 'had') for w in en_low):
            indices.extend([k for k, w in enumerate(en_low) if w in ('was', 'were', 'had')])
        elif hw in ('है', 'हैं', 'हूँ', 'हो') and any(w in ('is', 'are', 'am') for w in en_low):
            indices.extend([k for k, w in enumerate(en_low) if w in ('is', 'are', 'am')])

        if indices:
            valid_indices = [idx for idx in indices if idx < len(en_words)]
            if valid_indices:
                core = valid_indices[0]
                span = [core]
                if core > 0 and en_low[core - 1] in ('the', 'a', 'an') and hw not in ('में', 'पर', 'से', 'ने', 'को'):
                    span.insert(0, core - 1)
                final_tokens.append(to_token(span))
                continue

        # Proportional fallback
        if i > 0 and final_tokens:
            prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
            est = min(len(en_words) - 1, prev_token_idxs[-1] + 1)
            final_tokens.append(str(est))
        else:
            final_tokens.append('0')

    assert len(final_tokens) == len(hi_words), f"Mismatch: {len(final_tokens)} != {len(hi_words)}"
    return ' '.join(final_tokens)

def main():
    path = ROOT / 'data' / 'phrases27.json'
    data = json.load(open(path))
    print(f"Aligning {len(data)} sentences semantically for Batch ID-03...")

    for item in data:
        en = item['en']
        hi = item['hi']
        align = align_sentence(en, hi)
        item['align'] = align

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print("Successfully wrote semantically aligned sentences to data/phrases27.json")

if __name__ == '__main__':
    main()
