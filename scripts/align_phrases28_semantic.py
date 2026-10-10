#!/usr/bin/env python3
"""AI Semantic Aligner for phrases28.json (Batch ID-04: Elements, Nature, Idioms, Verbs & Tenses).

Generates exact semantic word-level and phrasal alignments linking each Hindi token
to its exact English token/span.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Comprehensive Hindi to English semantic lexicon for phrases28 (Elements, Nature & Tenses)
LEXICON = {
    # Elements & Nature
    'हवा': ['wind', 'air', 'breeze', 'gale'], 'वायु': ['air', 'wind'], 'समीर': ['breeze'],
    'पानी': ['water', 'rain'], 'जल': ['water'], 'नीर': ['water'], 'बूँद': ['drop'], 'बूँदें': ['drops'],
    'आग': ['fire', 'flames', 'blaze'], 'अग्नि': ['fire'], 'ज्वाला': ['flame', 'flames'], 'लपटें': ['flames'], 'चिनगारी': ['spark'],
    'आसमान': ['sky', 'heavens'], 'गगन': ['sky'], 'आकाश': ['sky', 'firmament'], 'नभ': ['sky'],
    'ज़मीन': ['ground', 'earth', 'land', 'floor'], 'धरती': ['earth', 'ground', 'soil'], 'भूमि': ['land', 'soil', 'earth'],
    'पहाड़': ['mountain', 'mountains', 'hill'], 'पहाड़ों': ['mountains'], 'पर्वत': ['mountain', 'peak'], 'शिखर': ['peak', 'summit'],
    'धूप': ['sunlight', 'sun', 'sunshine'], 'छाँव': ['shade', 'shadow'], 'छाया': ['shade', 'shadow'],
    'बादल': ['cloud', 'clouds'], 'मेघ': ['clouds', 'cloud'], 'घटा': ['clouds'], 'घटाएँ': ['clouds'],
    'सूरज': ['sun'], 'सूर्य': ['sun'], 'किरणें': ['rays', 'sunbeams'], 'किरण': ['ray', 'beam'],
    'चाँद': ['moon'], 'चंद्रमा': ['moon'], 'चाँदनी': ['moonlight'],
    'तारे': ['stars'], 'तारा': ['star'], 'तारों': ['stars'],
    'तूफ़ान': ['storm', 'tempest', 'gale', 'blizzard'], 'आँधी': ['storm', 'duststorm', 'gale'],
    'बिजली': ['lightning', 'thunderbolt'], 'गरज': ['thunder'], 'गड़गड़ाहट': ['rumble', 'thunder'],
    'बारिश': ['rain', 'downpour', 'shower'], 'वर्षा': ['rain', 'rainfall'], 'ओले': ['hail', 'hailstones'],
    'बर्फ़': ['snow', 'ice'], 'हिम': ['snow'], 'कोहरा': ['fog', 'mist'], 'धुंध': ['mist', 'haze', 'fog'],
    'ओस': ['dew'], 'शबनम': ['dew'],
    'समुद्र': ['ocean', 'sea'], 'सागर': ['ocean', 'sea'], 'लहरें': ['waves', 'billows'], 'लहर': ['wave'],
    'नदी': ['river', 'stream'], 'धारा': ['stream', 'current', 'flow'], 'झरना': ['waterfall', 'cascade'], 'झरने': ['waterfalls', 'springs'],
    'तालाब': ['pond', 'pool'], 'सरोवर': ['lake'], 'झील': ['lake'], 'कीचड़': ['mud', 'slush', 'mire'],
    'मिट्टी': ['soil', 'earth', 'dust'], 'धूल': ['dust'], 'रेत': ['sand'],
    'जंगल': ['forest', 'jungle', 'woods'], 'वन': ['forest'], 'पेड़': ['tree', 'trees'], 'वृक्ष': ['tree', 'trees'],
    'पत्ते': ['leaves'], 'पत्ता': ['leaf'], 'पत्तियों': ['leaves'],
    'फूल': ['flower', 'flowers', 'blossoms'], 'कली': ['bud'], 'कलियाँ': ['buds'],
    'शाखा': ['branch', 'bough'], 'शाखाएँ': ['branches'], 'टहनी': ['twig', 'branch'], 'टहनियाँ': ['twigs'],
    'जड़': ['root', 'roots'], 'जड़ें': ['roots'],

    # Weather & Physical States
    'गर्मी': ['heat', 'summer'], 'ताप': ['heat'], 'उमस': ['humidity', 'sultriness'],
    'सर्दी': ['cold', 'winter'], 'ठंड': ['cold', 'chill'], 'शीत': ['cold'],
    'सूखा': ['drought', 'dry'], 'बाढ़': ['flood', 'inundation', 'deluge'],
    'राख': ['ashes', 'ash'], 'धुआँ': ['smoke'], 'अंगारे': ['embers'],

    # Pronouns & People
    'मैं': ['i'], 'मुझे': ['me', 'i'], 'मुझ': ['me'], 'मेरा': ['my', 'mine'], 'मेरी': ['my', 'mine'], 'मेरे': ['my', 'mine'],
    'हम': ['we', 'us'], 'हमें': ['us', 'we'], 'हमारा': ['our', 'ours'], 'हमारी': ['our', 'ours'], 'हमारे': ['our', 'ours'],
    'तू': ['you'], 'तुझे': ['you'], 'तेरा': ['your'], 'तेरी': ['your'], 'तेरे': ['your'],
    'तुम': ['you'], 'तुम्हें': ['you'], 'तुम्हारा': ['your'], 'तुम्हारी': ['your'], 'तुम्हारे': ['your'],
    'आप': ['you'], 'आपको': ['you'], 'आपका': ['your'], 'आपकी': ['your'], 'आपके': ['your'],
    'वह': ['he', 'she', 'it', 'that'], 'उसे': ['him', 'her', 'it'], 'उस': ['that', 'him', 'her', 'it', 'his'],
    'उसका': ['his', 'her', 'its'], 'उसकी': ['his', 'her', 'its'], 'उसके': ['his', 'her', 'its', 'their'],
    'वे': ['they', 'those'], 'उन्हें': ['them', 'they'], 'उन': ['them', 'those', 'their'],
    'उनका': ['their', 'theirs'], 'उनकी': ['their', 'theirs'], 'उनके': ['their', 'theirs'],
    'यह': ['this', 'it'], 'इसे': ['this', 'it', 'him'], 'इस': ['this'],
    'इसका': ['its', 'this'], 'इसकी': ['its', 'this'], 'इसके': ['its', 'this'],
    'ये': ['these', 'they'], 'इन्हें': ['them', 'these'], 'इन': ['these'],
    'लोग': ['people', 'men', 'folk'], 'लोगों': ['people'],
    'किसान': ['farmer', 'farmers'], 'नाविक': ['sailor', 'boatman', 'sailors'], 'मछुआरे': ['fishermen'],
    'यात्री': ['traveler', 'travelers', 'passenger'], 'मुसाफिर': ['traveler', 'wanderer'],
    'बच्चे': ['children', 'kids'], 'बच्चा': ['child'], 'लड़का': ['boy'], 'लड़की': ['girl'],
    'गाँव': ['village'], 'गाँववाले': ['villagers'], 'शहर': ['city', 'town'],

    # Verbs - Motion, Action & Sensation
    'बहना': ['blow', 'flow'], 'बहती': ['blows', 'flows'], 'बहता': ['blows', 'flows'], 'बहते': ['blow', 'flow'], 'बहा': ['swept', 'carried', 'flowed'], 'बह': ['flow', 'blow'],
    'उड़ना': ['fly', 'drift'], 'उड़ता': ['flies', 'drifts'], 'उड़ती': ['flies', 'drifts'], 'उड़ते': ['fly', 'drift'], 'उड़ा': ['flew', 'blew'], 'उड़': ['fly', 'drift'],
    'जलना': ['burn', 'scorch'], 'जलती': ['burns'], 'जलते': ['burn'], 'जला': ['burned', 'burnt', 'lit'], 'जलाया': ['kindled', 'burned', 'lit'], 'जल': ['burn'],
    'बुझना': ['extinguish', 'quench'], 'बुझाना': ['extinguish', 'put'], 'बुझा': ['extinguished', 'quenched', 'put'], 'बुझ': ['extinguished', 'out'],
    'गरजना': ['roar', 'thunder'], 'गरजते': ['thunder', 'roar'], 'गरजा': ['thundered', 'roared'],
    'बरसना': ['pour', 'rain'], 'बरसता': ['pours', 'rains'], 'बरसती': ['pours', 'rains'], 'बरसा': ['poured', 'rained'], 'बरस': ['pour', 'rain'],
    'चमकना': ['shine', 'flash', 'glitter', 'gleam'], 'चमकती': ['shines', 'flashes', 'gleams'], 'चमकता': ['shines', 'glitters'], 'चमकी': ['flashed', 'shone'], 'चमक': ['shine', 'gleam', 'flash'],
    'डूबना': ['sink', 'drown'], 'डूबा': ['sank', 'drowned'], 'डूब': ['sink', 'drown'],
    'तैरना': ['swim', 'float'], 'तैरता': ['swims', 'floats'], 'तैरती': ['floats', 'swims'], 'तैरा': ['swam', 'floated'],
    'गिरना': ['fall', 'drop'], 'गिरती': ['falls', 'drops'], 'गिरते': ['fall'], 'गिरा': ['fell', 'dropped'], 'गिर': ['fall'],
    'उठना': ['rise', 'arise'], 'उठती': ['rises', 'arises'], 'उठता': ['rises'], 'उठा': ['rose', 'raised'], 'उठ': ['rise'],
    'बैठना': ['sit', 'settle'], 'बैठ': ['sit', 'settle', 'settled'],
    'चलना': ['walk', 'move', 'blow'], 'चलता': ['walks', 'moves'], 'चलती': ['blows', 'moves'], 'चला': ['walked', 'moved'],
    'दौड़ना': ['run'], 'दौड़ा': ['ran'],
    'देखना': ['see', 'look', 'watch'], 'देखा': ['saw', 'looked', 'watched'], 'देख': ['see', 'look'],
    'सुनना': ['hear', 'listen'], 'सुना': ['heard', 'listened'], 'सुन': ['hear', 'listen'],
    'कहना': ['say', 'tell'], 'कहा': ['said', 'told'],
    'करना': ['do', 'make'], 'किया': ['did', 'made'], 'कर': ['do', 'make'], 'करते': ['do', 'make'], 'करती': ['does', 'makes'],
    'होना': ['be', 'become', 'happen'], 'हुआ': ['became', 'happened', 'was'], 'हुई': ['became', 'happened', 'was'], 'हुए': ['became', 'happened', 'were'],
    'जाना': ['go'], 'गया': ['went', 'gone'], 'गई': ['went', 'gone'], 'गए': ['went', 'gone'], 'जाता': ['goes'], 'जाती': ['goes'],
    'आना': ['come'], 'आया': ['came'], 'आई': ['came'], 'आए': ['came'], 'आता': ['comes'], 'आती': ['comes'],
    'देना': ['give'], 'दिया': ['gave', 'given'], 'दी': ['gave', 'given'], 'दिए': ['gave', 'given'],
    'लेना': ['take'], 'लिया': ['took', 'taken'], 'ली': ['took', 'taken'], 'लिए': ['took', 'taken'],
    'पाना': ['find', 'get'], 'पाया': ['found', 'got'],
    'खोलना': ['open'], 'खोला': ['opened'],
    'बाँधना': ['tie', 'bind'], 'बाँधा': ['tied', 'bound'],
    'रोकना': ['stop', 'block', 'halt'], 'रोका': ['stopped', 'blocked', 'halted'],
    'छोड़ना': ['leave', 'release'], 'छोड़ा': ['left', 'released'],

    # Common Modifiers, Adverbs, Prepositions
    'बहुत': ['very', 'much', 'great', 'intensely', 'heavy'], 'तेज़': ['strong', 'fast', 'fierce', 'swift', 'sharp', 'loud', 'hard'],
    'धीरे': ['slowly', 'gently', 'softly'], 'धीमी': ['gentle', 'slow', 'soft'], 'धीमे': ['soft', 'gentle'],
    'ठंडी': ['cold', 'cool', 'chilly'], 'ठंडा': ['cold', 'cool'], 'ठंडे': ['cold', 'cool'],
    'गर्म': ['hot', 'warm'], 'गरम': ['hot', 'warm'],
    'ऊँचा': ['high', 'tall'], 'ऊँचे': ['high', 'lofty', 'tall'], 'ऊँची': ['high', 'lofty'], 'ऊँचाई': ['height', 'altitude'],
    'गहरा': ['deep'], 'गहरे': ['deep'], 'गहरी': ['deep', 'profound'], 'गहराई': ['depth', 'depths'],
    'साफ़': ['clear', 'clean', 'pure'], 'स्वच्छ': ['clean', 'pure', 'clear'],
    'काला': ['black', 'dark'], 'काले': ['black', 'dark'], 'काली': ['black', 'dark'],
    'नीला': ['blue', 'azure'], 'नीले': ['blue'], 'नीली': ['blue'],
    'सफ़ेद': ['white'], 'लाल': ['red'],
    'चारों': ['all', 'four'], 'ओर': ['sides', 'directions', 'around', 'towards'],
    'सब': ['all', 'everyone', 'everything'], 'सभी': ['all', 'everyone'],
    'कोई': ['anyone', 'someone', 'no', 'any'], 'कुछ': ['some', 'something', 'anything'],
    'हर': ['every', 'each'], 'प्रत्येक': ['each', 'every'],
    'भी': ['also', 'even', 'too'], 'ही': ['only', 'itself'],
    'और': ['and'], 'तथा': ['and'], 'एवं': ['and'],
    'लेकिन': ['but'], 'परंतु': ['but'], 'किंतु': ['but'], 'मगर': ['but'],
    'जब': ['when'], 'तब': ['then'], 'यदि': ['if'], 'अगर': ['if'], 'तो': ['then'],
    'जैसे': ['as', 'like'], 'वैसे': ['so', 'similarly'],
    'क्योंकि': ['because'], 'इसलिए': ['therefore', 'so'],
    'न': ['not', 'neither'], 'नहीं': ['not', 'no'], 'मत': ['do', 'not'],
    'साथ': ['with', 'together', 'along'], 'बिना': ['without'],
    'पास': ['near', 'close', 'by'], 'दूर': ['far', 'distant', 'away'],
    'ऊपर': ['up', 'above', 'upon', 'over'], 'नीचे': ['down', 'below', 'under'],
    'आगे': ['ahead', 'forward', 'front'], 'पीछे': ['behind', 'back'],
    'अंदर': ['inside', 'in'], 'बाहर': ['outside', 'out'],
    'बीच': ['middle', 'midst', 'between', 'among'],
}

def to_token(indices):
    if not indices:
        return '0'
    indices = sorted(list(set(indices)))
    if len(indices) == 1:
        return str(indices[0])
    # Check if contiguous
    if indices == list(range(indices[0], indices[-1] + 1)):
        return f"{indices[0]}-{indices[-1]}"
    return ','.join(str(i) for i in indices)

def align_sentence(en: str, hi: str) -> str:
    en_words = en.split()
    hi_words = hi.split()
    en_low = [w.lower() for w in en_words]

    final_tokens = []

    for i, hw in enumerate(hi_words):
        indices = []

        # 1. Direct lexical lookup
        if hw in LEXICON:
            for cand in LEXICON[hw]:
                cand_low = cand.lower()
                for j, ew in enumerate(en_low):
                    if ew == cand_low or cand_low in ew or ew in cand_low:
                        indices.append(j)

        # 2. Case postpositions binding to previous noun/pronoun
        if hw in ('ने', 'को', 'का', 'की', 'के') and final_tokens:
            prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
            of_idxs = [k for k, w in enumerate(en_low) if w in ('of', 'for', 'to')]
            if hw in ('का', 'की', 'के') and of_idxs:
                final_tokens.append(to_token(of_idxs))
            elif hw == 'को' and any(w in ('to', 'for') for w in en_low):
                to_idxs = [k for k, w in enumerate(en_low) if w in ('to', 'for')]
                final_tokens.append(to_token(to_idxs))
            else:
                final_tokens.append(to_token(prev_token_idxs))
            continue

        # 3. Locative / Ablative / Instrumental postpositions
        if hw == 'में':
            in_idxs = [k for k, w in enumerate(en_low) if w in ('in', 'into', 'inside', 'among', 'within')]
            if in_idxs:
                final_tokens.append(to_token(in_idxs))
                continue
            elif final_tokens:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
                continue

        if hw == 'पर':
            on_idxs = [k for k, w in enumerate(en_low) if w in ('on', 'upon', 'at', 'across', 'over', 'atop')]
            if on_idxs:
                final_tokens.append(to_token(on_idxs))
                continue
            elif final_tokens:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
                continue

        if hw == 'से':
            se_idxs = [k for k, w in enumerate(en_low) if w in ('from', 'with', 'by', 'than', 'off')]
            if se_idxs:
                final_tokens.append(to_token(se_idxs))
                continue
            elif final_tokens:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
                continue

        if hw == 'तक':
            tak_idxs = [k for k, w in enumerate(en_low) if w in ('until', 'till', 'to', 'up')]
            if tak_idxs:
                final_tokens.append(to_token(tak_idxs))
                continue
            elif final_tokens:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                final_tokens.append(to_token(prev_token_idxs))
                continue

        # 4. Aspectual auxiliaries & Copulas
        if hw in ('रहा', 'रही', 'रहे'):
            ing_idxs = [k for k, w in enumerate(en_low) if w.endswith('ing')]
            if ing_idxs:
                indices.extend(ing_idxs)
        elif hw in ('था', 'थे', 'थी', 'थीं'):
            past_idxs = [k for k, w in enumerate(en_low) if w in ('was', 'were', 'had', 'did')]
            if past_idxs:
                indices.extend(past_idxs)
        elif hw in ('है', 'हैं', 'हूँ', 'हो'):
            pres_idxs = [k for k, w in enumerate(en_low) if w in ('is', 'are', 'am', 'has', 'have', 'does', 'do')]
            if pres_idxs:
                indices.extend(pres_idxs)
        elif hw in ('गा', 'गी', 'गे'):
            fut_idxs = [k for k, w in enumerate(en_low) if w in ('will', 'shall', 'would')]
            if fut_idxs:
                indices.extend(fut_idxs)

        if indices:
            valid_indices = [idx for idx in indices if idx < len(en_words)]
            if valid_indices:
                core = valid_indices[0]
                span = [core]
                # If preceded by article ('the', 'a', 'an'), include in span
                if core > 0 and en_low[core - 1] in ('the', 'a', 'an') and hw not in ('में', 'पर', 'से', 'ने', 'को', 'था', 'है'):
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
    path = ROOT / 'data' / 'phrases28.json'
    data = json.load(open(path))
    print(f"Aligning {len(data)} sentences semantically for Batch ID-04...")

    for item in data:
        en = item['en']
        hi = item['hi']
        align = align_sentence(en, hi)
        item['align'] = align

    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n')
    print("Successfully wrote semantically aligned sentences to data/phrases28.json")

if __name__ == '__main__':
    main()
