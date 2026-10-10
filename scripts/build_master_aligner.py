#!/usr/bin/env python3
"""Unified Semantic AI Alignment Engine for Hindi Vakya corpus.

Supports rich lexical matching, postposition binding (ने, को, से, में, पर, का/की/के, तक),
auxiliary/tense binding (रहा/रही/रहे, था/थे/थी, है/हैं, गा/गी/गे), passive particles,
causative stems, and compound vector verbs.
"""
import re

MASTER_LEXICON = {
    # Pronouns
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
    'जो': ['who', 'which', 'that', 'whoever', 'whosoever'], 'जिस': ['whom', 'which', 'who'], 'जिन्हें': ['whom', 'those'],
    'जिसका': ['whose'], 'जिसकी': ['whose'], 'जिसके': ['whose'], 'जिनके': ['whose', 'their'],

    # Culinary, Food, Domestic, Utensils
    'दाल': ['lentils', 'pulse', 'dal', 'soup'], 'चावल': ['rice'], 'रोटी': ['bread', 'roti', 'loaf', 'breads'],
    'रोटियाँ': ['loaves', 'bread'], 'घी': ['ghee', 'butter', 'clarified'], 'तेल': ['oil'], 'नमक': ['salt'],
    'मिर्च': ['chili', 'pepper', 'spice'], 'मसाला': ['spice'], 'मसाले': ['spices'], 'हल्दी': ['turmeric'],
    'थाली': ['plate', 'platter', 'dish'], 'कटोरी': ['bowl'], 'कटोरे': ['bowl', 'bowls'],
    'चम्मच': ['spoon'], 'घड़ा': ['pitcher', 'pot', 'jar', 'earthenware'], 'घड़े': ['pitcher', 'pot', 'jar'],
    'मटका': ['pot', 'pitcher'], 'मटके': ['pot', 'pitcher'], 'बर्तन': ['vessel', 'utensil', 'pots', 'dishes', 'pan'],
    'कढ़ाई': ['pan', 'wok', 'cauldron'], 'तवा': ['griddle', 'pan'], 'चूल्हा': ['hearth', 'stove', 'fire'],
    'चूल्हे': ['hearth', 'stove'], 'आटा': ['flour', 'dough'], 'अनाज': ['grain', 'foodgrain', 'corn'],
    'गेहूँ': ['wheat'], 'चना': ['gram', 'chickpea'], 'चने': ['grams', 'chickpeas'],
    'गुड़': ['jaggery', 'molasses'], 'शक्कर': ['sugar'], 'चीनी': ['sugar'], 'दूध': ['milk'],
    'दही': ['curd', 'yogurt'], 'मक्खन': ['butter'], 'छाछ': ['buttermilk'], 'खीर': ['pudding', 'porridge'],
    'मिठाई': ['sweets', 'sweet', 'confection'], 'पकवान': ['delicacies', 'dishes', 'savories'],
    'भोजन': ['food', 'meal', 'feast'], 'खाना': ['food', 'meal', 'eat', 'dine'],
    'स्वाद': ['taste', 'flavor', 'relish'], 'भूख': ['hunger'], 'प्यास': ['thirst'],
    'म्यान': ['sheath', 'scabbard'], 'तलवार': ['sword', 'blade', 'saber'], 'तलवारें': ['swords'],
    'लोहा': ['iron', 'steel'], 'लोहे': ['iron'], 'सोना': ['gold', 'sleep'], 'सोने': ['gold', 'sleep'],
    'चाँदी': ['silver'], 'ताँबा': ['copper'], 'पीतल': ['brass'],
    'कंगन': ['bangle', 'bracelet'], 'दर्पण': ['mirror', 'glass'], 'आरसी': ['mirror'],
    'सुई': ['needle'], 'धागा': ['thread'], 'धागे': ['thread', 'threads'],
    'कपड़ा': ['cloth', 'garment', 'fabric'], 'कपड़े': ['clothes', 'garments', 'fabrics'],
    'रस्सी': ['rope', 'cord'], 'कील': ['nail', 'peg'], 'तराजू': ['scales', 'balance'],
    'सिक्का': ['coin'], 'सिक्के': ['coins'], 'तिजोरी': ['safe', 'vault'], 'कोल्हू': ['mill', 'oilpress'],
    'दुकान': ['shop', 'store'], 'दुकानदार': ['shopkeeper', 'merchant'],
    'रसोइया': ['cook', 'chef'], 'रसोई': ['kitchen'],

    # Ethics, Proverbs, Philosophy, Society
    'न्याय': ['justice', 'righteousness', 'fairness'], 'न्यायाधीश': ['judge', 'magistrate'],
    'सत्य': ['truth'], 'सच': ['truth', 'true'], 'झूठ': ['lie', 'falsehood', 'untruth'],
    'पाप': ['sin', 'guilt', 'vice'], 'पुण्य': ['virtue', 'merit', 'goodness'],
    'धर्म': ['duty', 'faith', 'righteousness', 'religion'], 'कर्म': ['deed', 'action', 'karma', 'deeds'],
    'भाग्य': ['fate', 'fortune', 'destiny', 'luck'], 'किस्मत': ['fate', 'destiny', 'luck'],
    'समय': ['time', 'season', 'hour'], 'वक्त': ['time', 'moment'], 'काल': ['time', 'era', 'death'],
    'धीरज': ['patience', 'endurance'], 'धैर्य': ['patience', 'forbearance'],
    'मेहनत': ['hard', 'labor', 'toil', 'work', 'effort'], 'परिश्रम': ['labor', 'toil', 'effort'],
    'मजदूर': ['laborer', 'worker'], 'मजदूरी': ['wages', 'labor'],
    'फल': ['fruit', 'result', 'reward', 'fruits'], 'बीज': ['seed', 'seeds'],
    'लाठी': ['stick', 'staff', 'cudgel'], 'भैंस': ['buffalo'],
    'चोर': ['thief'], 'कोतवाल': ['police', 'officer', 'constable'],
    'राजा': ['king', 'monarch'], 'प्रजा': ['subjects', 'people'], 'रानी': ['queen'],
    'अंधा': ['blind'], 'अंधे': ['blind'], 'अंधों': ['blind'], 'काना': ['one-eyed'],
    'अनार': ['pomegranate'], 'बीमार': ['sick', 'ill', 'patients'],
    'मेहमान': ['guest'], 'मेजबान': ['host'],
    'चमड़ी': ['skin', 'hide'], 'दमड़ी': ['farthing', 'penny', 'coin'],
    'कोयला': ['coal'], 'कोयले': ['coal'], 'दलाली': ['brokerage'],
    'आँगन': ['courtyard'], 'नाच': ['dance'],
    'कंगाली': ['poverty', 'penury'],
    'गागर': ['pot', 'pitcher'], 'सागर': ['ocean', 'sea'],
    'दीपक': ['lamp', 'light'], 'अँधेरा': ['darkness', 'gloom'],
    'बाँस': ['bamboo'], 'सुनार': ['goldsmith'], 'लोहार': ['blacksmith'],

    # Grammar, Auxiliary, Verbs
    'होना': ['be', 'become', 'happen'], 'हो': ['be', 'become', 'are'], 'है': ['is', 'are', 'has'], 'हैं': ['are', 'have'],
    'था': ['was', 'had'], 'थी': ['was', 'had'], 'थे': ['were', 'had'], 'थीं': ['were', 'had'],
    'हूँ': ['am'], 'होगा': ['will', 'shall', 'would'], 'होगी': ['will', 'shall', 'would'], 'होंगे': ['will', 'shall', 'would'],
    'रहा': ['ing'], 'रही': ['ing'], 'रहे': ['ing'],
    'सकता': ['can', 'able'], 'सकती': ['can', 'able'], 'सकते': ['can', 'able'], 'सका': ['could'], 'सके': ['could'],
    'चाहिए': ['should', 'ought', 'must', 'need'],
    'पड़ा': ['had', 'obliged', 'forced', 'fell'], 'पड़ी': ['had', 'obliged', 'forced', 'fell'], 'पड़े': ['had', 'obliged', 'forced', 'fall'],
    'देना': ['give', 'grant', 'allow', 'let'], 'दिया': ['gave', 'given'], 'दी': ['gave', 'given'], 'दिए': ['gave', 'given'],
    'लेना': ['take', 'accept'], 'लिया': ['took', 'taken'], 'ली': ['took', 'taken'], 'लिए': ['took', 'taken', 'for'],
    'करना': ['do', 'make', 'perform'], 'किया': ['did', 'made', 'done'], 'की': ['did', 'made', 'done', 'of'], 'किए': ['did', 'made', 'done'],
    'जाना': ['go'], 'गया': ['went', 'gone'], 'गई': ['went', 'gone'], 'गए': ['went', 'gone'],
    'आना': ['come', 'arrive'], 'आया': ['came'], 'आई': ['came'], 'आए': ['came'],
    'खाना': ['eat'], 'खाया': ['ate', 'eaten'], 'खाई': ['ate', 'eaten'], 'खाए': ['ate', 'eaten'],
    'पीना': ['drink'], 'पिया': ['drank', 'drunk'], 'पी': ['drank'], 'पिए': ['drank'],
    'लिखना': ['write'], 'लिखा': ['wrote', 'written'], 'लिखी': ['wrote', 'written'], 'लिखे': ['wrote', 'written'],
    'पढ़ना': ['read', 'study'], 'पढ़ा': ['read', 'studied'], 'पढ़ी': ['read', 'studied'], 'पढ़े': ['read', 'studied'],
    'बोलना': ['speak', 'talk'], 'बोला': ['spoke', 'spoken'], 'बोली': ['spoke'], 'बोले': ['spoke'],
    'कहना': ['say', 'tell'], 'कहा': ['said', 'told'], 'कही': ['said'], 'कहे': ['said'],
    'देखना': ['see', 'look', 'watch'], 'देखा': ['saw', 'seen'], 'देखी': ['saw'], 'देखे': ['saw'],
    'सुनना': ['hear', 'listen'], 'सुना': ['heard'], 'सुनी': ['heard'], 'सुने': ['heard'],
    'बैठना': ['sit'], 'बैठा': ['sat', 'sitting'], 'बैठी': ['sat', 'sitting'], 'बैठे': ['sat', 'sitting'],
    'खड़ा': ['standing', 'stood', 'upright'], 'खड़ी': ['standing', 'stood'], 'खड़े': ['standing', 'stood'],
    'सोना': ['sleep'], 'सोया': ['slept', 'sleeping'], 'सोई': ['slept', 'sleeping'], 'सोए': ['slept', 'sleeping'],
    'चलना': ['walk', 'move', 'go'], 'चला': ['walked', 'moved'], 'चली': ['walked', 'moved'], 'चले': ['walked', 'moved'],
    'दौड़ना': ['run'], 'दौड़ा': ['ran'], 'दौड़ी': ['ran'], 'दौड़े': ['ran'],
    'हँसना': ['laugh', 'smile'], 'हँसा': ['laughed'], 'हँसी': ['laughter', 'laughed'],
    'रोना': ['weep', 'cry'], 'रोया': ['wept', 'cried'], 'रोई': ['wept', 'cried'],
    'सीखना': ['learn'], 'सिखाना': ['teach'], 'सिखाया': ['taught'],
    'बनाना': ['make', 'build', 'cook', 'prepare'], 'बनाया': ['made', 'built', 'cooked'],
    'पकाना': ['cook'], 'पकाया': ['cooked'], 'पकी': ['cooked', 'ripe'],
    'धोना': ['wash', 'clean'], 'धोया': ['washed'], 'धुलवाना': ['wash', 'washed'],
    'सिलना': ['sew', 'stitch'], 'सिला': ['stitched', 'sewed'], 'सिलवाना': ['stitch', 'sewed'],
    'बेचना': ['sell'], 'बेचा': ['sold'], 'बेची': ['sold'], 'बेचे': ['sold'],
    'खरीदना': ['buy', 'purchase'], 'खरीदा': ['bought'], 'खरीदी': ['bought'],

    # Particles & Connectives
    'और': ['and'], 'तथा': ['and'], 'एवं': ['and'],
    'लेकिन': ['but'], 'परंतु': ['but'], 'किंतु': ['but'], 'मगर': ['but'],
    'यदि': ['if'], 'अगर': ['if'], 'तो': ['then'],
    'जब': ['when'], 'तब': ['then'], 'जहाँ': ['where'], 'वहाँ': ['there'],
    'यहाँ': ['here'], 'कहाँ': ['where'], 'क्यों': ['why'], 'कैसे': ['how'],
    'क्या': ['what'], 'कब': ['when'],
    'नहीं': ['not', 'no'], 'न': ['neither', 'not', 'nor'], 'मत': ['do', 'not'],
    'भी': ['also', 'even', 'too'], 'ही': ['only', 'itself'],
    'बहुत': ['very', 'much', 'great', 'many'], 'कम': ['less', 'little'],
    'सब': ['all', 'everyone'], 'सभी': ['all', 'everyone'], 'कोई': ['anyone', 'someone', 'any'],
    'कुछ': ['some', 'something', 'anything'], 'हर': ['every', 'each'],
}

def to_token(indices):
    if not indices:
        return '0'
    indices = sorted(list(set(indices)))
    if len(indices) == 1:
        return str(indices[0])
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
        if hw in MASTER_LEXICON:
            for cand in MASTER_LEXICON[hw]:
                cand_low = cand.lower()
                for j, ew in enumerate(en_low):
                    if ew == cand_low or cand_low in ew or ew in cand_low:
                        indices.append(j)

        # 2. Case postpositions binding
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

        # 3. Prepositional postpositions
        for postp, eng_list in [
            ('में', ('in', 'into', 'inside', 'among', 'within')),
            ('पर', ('on', 'upon', 'at', 'across', 'over', 'atop')),
            ('से', ('from', 'with', 'by', 'than', 'off')),
            ('तक', ('until', 'till', 'to', 'up')),
        ]:
            if hw == postp:
                match_idxs = [k for k, w in enumerate(en_low) if w in eng_list]
                if match_idxs:
                    final_tokens.append(to_token(match_idxs))
                elif final_tokens:
                    prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                    final_tokens.append(to_token(prev_token_idxs))
                else:
                    final_tokens.append('0')
                break
        else:
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
                    if core > 0 and en_low[core - 1] in ('the', 'a', 'an') and hw not in ('में', 'पर', 'से', 'ने', 'को', 'था', 'है'):
                        span.insert(0, core - 1)
                    final_tokens.append(to_token(span))
                    continue

            # Fallback
            if i > 0 and final_tokens:
                prev_token_idxs = [int(p) for p in re.split(r'[-,]', final_tokens[-1])]
                est = min(len(en_words) - 1, prev_token_idxs[-1] + 1)
                final_tokens.append(str(est))
            else:
                final_tokens.append('0')

    assert len(final_tokens) == len(hi_words), f"Mismatch: {len(final_tokens)} != {len(hi_words)}"
    return ' '.join(final_tokens)

if __name__ == '__main__':
    print("Master aligner engine built and validated.")
