#!/usr/bin/env python3
"""Generate align strings for data/phrases14.json.

- g001-g400: exact template math (sentences came from gen_phrases.py templates)
- month entries: fixed hand formulas
- g425-g444: hand-authored aligns (HAND dict below)
- g445-g544: dictionary + proportional-position derivation (port of app.js deriveAlign)

Existing valid aligns are never overwritten. Run scripts/validate_corpus.py after.
"""
import json
import re

PATH = 'data/phrases14.json'

# subject en prefix -> (hi word, en word count)
SUBJ = [
    ('the children', 'बच्चे'), ('the women', 'औरतें'),
    ('the boy', 'लड़का'), ('the girl', 'लड़की'),
    ('I', 'मैं'), ('you', 'तुम'), ('you', 'आप'), ('he', 'वह'), ('she', 'वह'),
    ('we', 'हम'), ('they', 'वे'),
]

# hand-authored aligns for the 20 mixed grammar sentences
HAND = {
    'g425': '1 4 3 7 5 2',
    'g426': '0 2-3 1,4',
    'g427': '0 3-4 1-2,5',
    'g428': '0 3 5 6 5 1-2,4',
    'g429': '3-4 3 5 0-1',
    'g430': '0 7 5 2-3 1,4',
    'g431': '0 2 3 4 1,5',
    'g432': '0-1 4-5 4 6-7 3 2-3 2',
    'g433': '0 2-3 1',
    'g434': '0-1 0 3-4 2 2',
    'g435': '1-2 4 0 1,3',
    'g436': '5-6 4 0-1 2-3',
    'g437': '0 2 3 4-5 4 1 1',
    'g438': '0 2-3 2 1',
    'g439': '0 4-5 3 2 1 1',
    'g440': '0 5-6 4 2-3 1',
    'g441': '0 1 2 2 0 4 3 5-6 5-6 5',
    'g442': '0 2 3 1 1',
    'g443': '0 1 5 3-4 3 0,2',
    'g444': '0 3 5-6 4 2 2 1',
}

MONTH = {
    'jan': None,  # filled programmatically below
}

# small Devanagari->English-words dictionary for idiom derivation
DICT = {
    'आँख': ['eye', 'asleep', 'eyes'], 'आँखें': ['eyes'], 'हाथ': ['hand', 'hands', 'wringing'],
    'हाथों': ['hands', 'together'], 'सिर': ['head'], 'पीठ': ['back'], 'मुँह': ['mouth'],
    'कान': ['ears', 'ear'], 'दाँत': ['teeth'], 'दिल': ['heart'], 'पैर': ['legs'],
    'पेट': ['stomach'], 'घर': ['house', 'home'], 'बच्चे': ['children', 'child'],
    'बच्चों': ['children'], 'माँ': ['mother'], 'माँगने': ['asking'], 'माफ़ी': ['forgiveness'],
    'शिक्षक': ['teacher'], 'बुज़ुर्गों': ['elders'], 'झगड़े': ['quarrel'], 'काम': ['work', 'task'],
    'खेल': ['game'], 'मौका': ['chance', 'opportunity'], 'परीक्षा': ['exam'],
    'मेले': ['fair'], 'जी': ['heart'], 'खबर': ['news'], 'होश': ['senses'],
    'कमरे': ['room'], 'दम': ['breath'], 'पुरस्कार': ['prize'], 'सुबह': ['morning'],
    'बाज़ार': ['market'], 'धोखा': ['cheated'], 'पैसा': ['money'], 'बड़ों': ['elders'],
    'बुज़ुर्गों': ['elders'], 'मुसीबत': ['misery', 'hardship'], 'मेहनत': ['hard', 'work'],
    'सुस्ती': ['laziness'], 'झूठ': ['lie', 'lying'], 'चोरी': ['stealing'],
    'तारीफ़': ['prraise', 'praise'], 'कंधे': ['shoulder'], 'इंतज़ार': ['waiting', 'wait'],
    'चोर': ['thief'], 'मेहमान': ['guest'], 'कला': ['skill'], 'पहाड़': ['mountain'],
    'खेती': ['farming'], 'आग': ['fire'], 'घी': ['ghee'], 'नज़रें': ['eye'],
    'हवा': ['wind'], 'बाढ़': ['flood'], 'फसल': ['crop'], 'मिट्टी': ['soil'],
    'खेत': ['field'], 'खून': ['blood'], 'पसीना': ['sweat'], 'युद्ध': ['war'],
    'शत्रु': ['enemy'], 'दाम': ['price'], 'भाई': ['brother', 'brothers'],
    'ब्याज': ['interest'], 'बात': ['talk', 'matter'], 'बातों': ['talk'],
    'रसगुल्ले': ['cheese', 'balls'], 'मुश्किल': ['difficulty'], 'आसमान': ['storm'],
    'सूखे': ['drought'], 'किसान': ['farmers'], 'दाने': ['grain'], 'तीर': ['arrow'],
    'शिकार': ['prey'], 'डूबते': ['drowning'], 'तिनके': ['straw'], 'तैयारी': ['preparation'],
    'लोगों': ['people', 'lettered'], 'अंधों': ['eyed'], 'काना': ['eyed'], 'राजा': ['king'],
    'देन': ['pay'], 'ऊँट': ['camels'], 'मुँह': ['mouth'], 'जीरा': ['cumin'],
    'डर': ['fear', 'afraid'], 'जाँच': ['inquiry'], 'दूध': ['milk'], 'पानी': ['water'],
    'नाच': ['dance'], 'आँगन': ['courtyard'], 'टेढ़ा': ['crooked'], 'ताली': ['clap'],
    'धनख': ['bow'], 'भेदी': ['insider'], 'लंका': ['lanka'], 'देस': ['land'],
    'भेस': ['dress'], 'अनार': ['pomegranate'], 'बीमार': ['patients'], 'मियाँ': ['parrot'],
    'मिट्ठू': ['parrot'], 'टोकने': ['checked'], 'गुस्सा': ['anger'], 'बेकार': ['useless'],
    'लातों': ['kicks'], 'भूत': ['ghosts'], 'बातों': ['words'], 'सच': ['truth'],
    'चुप्पी': ['silence'], 'दाल': ['lentils', 'lentils'], 'अंगूर': ['grapes'],
    'नेकी': ['good'], 'दरिया': ['river'], 'आँधी': ['storm'], 'दिनों': ['days'],
    'मगरमच्छ': ['crocodile'], 'आँसू': ['tears'], 'चिराग': ['lamp', 'distant'],
    'अँधेरा': ['darkness'], 'चाह': ['will'], 'राह': ['way'], 'लाठी': ['staff'],
    'भैंस': ['buffalo'], 'सुनार': ['goldsmiths'], 'लोहार': ['blacksmith'],
    'धमाके': ['blow'], 'ढोल': ['drums'], 'दलीलों': ['arguments'], 'उल्लू': ['interest'],
    'म्यान': ['sheath'], 'तलवारें': ['swords'], 'बंदर': ['monkey'], 'अदरक': ['ginger'],
    'जान': ['life'], 'जहान': ['world'], 'दफ़्तर': ['office'], 'दुकान': ['shop'],
    'पकवान': ['dish'], 'पछताए': ['regret'], 'चिड़िया': ['bird'], 'बूढ़ा': ['good'],
    'गरजते': ['thunder'], 'बरसते': ['rain'], 'धीरज': ['patience'], 'फल': ['fruit'],
    'थैली': ['alike'], 'गुरु': ['teacher'], 'ज्ञान': ['knowledge'], 'आचार्य': ['teacher'],
    'आदर': ['honor'], 'घमंड': ['arrogance'], 'वक्त': ['time'], 'रेत': ['sand'],
    'हथेली': ['palm'], 'दीपक': ['lamp'], 'संतान': ['children'], 'गरीबी': ['poverty'],
    'फूल': ['flowers'], 'काँटों': ['thorns'], 'अमृत': ['nectar'], 'ज़हर': ['poison'],
    'जीवन': ['life'], 'साँप': ['snakes'], 'सीढ़ी': ['ladders'], 'खेल': ['game'],
    'उतार': ['falls'], 'चढ़ाव': ['rises'], 'सत्य': ['truth'], 'कलम': ['pen'],
    'तलवार': ['sword'], 'शांत': ['quiet'], 'घुटने': ['suffocate'],
}

PARTICLES = {'to', 'the', 'a', 'an', 'of', 'in', 'on', 'at', 'for', 'by', 'from'}


def to_token(idxs):
    if not idxs:
        return '0'
    if len(idxs) == 1:
        return str(idxs[0])
    if idxs == list(range(idxs[0], idxs[-1] + 1)):
        return f'{idxs[0]}-{idxs[-1]}'
    return ','.join(map(str, idxs))


def derive(en, hi):
    enw = en.lower().split()
    hiw = hi.split()
    hi_to_en = []
    for i, hw in enumerate(hiw):
        targets = DICT.get(hw)
        j = None
        if targets:
            for k, ew in enumerate(enw):
                if any(ew == t or (len(t) > 3 and t in ew) for t in targets):
                    j = k
                    break
        if j is None:
            j = min(len(enw) - 1,
                    max(0, round(i * (len(enw) - 1) / max(1, len(hiw) - 1))))
        hi_to_en.append(j)
    out = []
    for i, core in enumerate(hi_to_en):
        extra = []
        j = core - 1
        while j >= 0 and enw[j] in PARTICLES:
            extra.append(j)
            j -= 1
        out.append(to_token(sorted(set(extra + [core]))))
    return ' '.join(out)


def template_align(en, hi):
    """Exact align for gen_phrases.py templated tense sentences."""
    el = en.lower().split()
    hiw = hi.split()
    if el[0] == 'perhaps':
        # शायद subj form ; en: perhaps S verb( phrasal)
        se = el[1:]
        ns = 0
        for cse, _ in SUBJ:
            c = cse.lower().split()
            if se[:len(c)] == c:
                ns = len(c)
                break
        if ns:
            verb_start = 1 + ns
            verb_span = to_token(list(range(verb_start, len(el))))
            subj_tok = to_token(list(range(1, 1 + ns))) if ns > 1 else '1'
            return ' '.join(['0'] + [subj_tok] + [verb_span] * (len(hiw) - 2))
    subj = None
    for se, sh in SUBJ:
        if el[:len(se.split())] == se.lower().split():
            subj = (se, sh, len(se.split()))
            if sh in hiw:
                break
    if subj is None:
        return None
    se, sh, ns = subj
    if sh not in hiw:
        # try the other Hindi subject word with the same en prefix (you -> तुम/आप)
        alts = [h for e, h in SUBJ if e.lower() == se.lower() and h in hiw]
        if not alts:
            return None
        sh = alts[0]
    core = hiw.index(sh)
    if core is None:
        return None
    nadv = core  # words before subject are the adverbial
    tail = hiw[core + 1:]
    # detect tense from en
    if el[0] == 'perhaps' and len(tail) == 1:
        # शायद subj form
        # structure: शायद(nadv=1) subj form ; en: perhaps S verb
        verb_i = 1 + ns
        toks = []
        for i, w in enumerate(hiw):
            if i < nadv:
                toks.append('0')
            elif i == core:
                toks.append(to_token(list(range(1, 1 + ns))) if ns > 1 else '1')
            else:
                toks.append(str(verb_i))
        return ' '.join(toks)
    aux_i = ns  # index of was/were/will/had/has/have
    # locate participle/ing and adverb start per tense; handle phrasal "get up"
    def find_verb(start):
        span = 2 if el[start + 1] == 'up' else 1
        return start, start + span
    if el[aux_i:aux_i + 2] == ['will', 'be']:      # future continuous
        verb_i, adv_start = find_verb(ns + 2)
    elif el[aux_i:aux_i + 2] == ['will', 'have']:  # future perfect
        verb_i, adv_start = find_verb(ns + 2)
    elif el[aux_i] in ('was', 'were', 'had') or el[aux_i] in ('has', 'have'):
        verb_i, adv_start = find_verb(ns + 1)
    else:
        return None
    adv_range = to_token(list(range(adv_start, len(el)))) if adv_start < len(el) else str(len(el) - 1)
    subj_tok = to_token(list(range(ns))) if ns > 1 else '0'
    aux_tok = (to_token([aux_i, aux_i + 1])
               if el[aux_i] == 'will' else str(aux_i))
    verb_span = to_token(list(range(verb_i, adv_start)))
    toks = []
    for i, w in enumerate(hiw):
        if i < nadv:
            toks.append(adv_range)
        elif i == core:
            toks.append(subj_tok)
        elif i == len(hiw) - 1:
            toks.append(aux_tok)
        else:
            toks.append(verb_span)
    return ' '.join(toks)


def main():
    d = json.load(open(PATH))
    n_tmpl = n_hand = n_derive = 0
    for s in d:
        a = s.get('align')
        ok = False
        if a:
            toks = a.split()
            ok = (len(toks) == len(s['hi'].split())
                  and all(p.isdigit() and int(p) < len(s['en'].split())
                          for t in toks for p in re.split(r'[-,]', t)))
        if ok:
            continue
        if s['id'] in HAND:
            s['align'] = HAND[s['id']]
            n_hand += 1
        elif s['en'].split()[0] == 'School' and 'starts' in s['en']:
            # स्कूल month में शुरू होता है / School starts in Month
            s['align'] = '0 3 2 1 1 1'
        elif s['en'].split()[0] == 'My' and 'birthday' in s['en']:
            # मेरा जन्मदिन month में है / My birthday is in Month
            s['align'] = '0 1 4 3 2'
        else:
            t = template_align(s['en'], s['hi'])
            if t and len(t.split()) == len(s['hi'].split()):
                s['align'] = t
                n_tmpl += 1
            else:
                s['align'] = derive(s['en'], s['hi'])
                n_derive += 1
    json.dump(d, open(PATH, 'w'), ensure_ascii=False, indent=2)
    print(f'template {n_tmpl}, hand {n_hand}, derived {n_derive}')


if __name__ == '__main__':
    main()
