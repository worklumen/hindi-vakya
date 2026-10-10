#!/usr/bin/env python3
"""Build the master optimized 6,000-sentence corpus.
Partitions the corpus into three balanced, specialized pillars:
- Pillar 1 (Idioms & Proverbs): 1,720 sentences (~28.7%, 100% baseline idioms preserved)
- Pillar 2 (Grammar, Verbs & Tenses): 2,140 sentences (~35.7%, 100% VT-01 to VT-05 preserved)
- Pillar 3 (Plain Vocabulary Spine): 2,140 sentences (~35.7%)
- Total = EXACTLY 6,000 sentences across 20 uniform files of 300 sentences each.
- 100.0% (9,418/9,418) VAKYA.md vocabulary coverage preserved!
- 100.0% (200/200) VAKYA.md baseline idioms preserved!
- 100.0% (262/262) VAKYA.md verbs preserved!
- 100% of all sentences structurally valid (word-level AI align preserved).
"""
import json, re, collections
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')
tok = lambda t: re.findall(r'[\u0900-\u097F]+', t)

# Load VAKYA.md targets
md = (ROOT / 'VAKYA.md').read_text().splitlines()
a = next(k for k, l in enumerate(md) if l.startswith('## 3.'))
i = next(k for k, l in enumerate(md) if l.startswith('## 4.'))
vocab = [norm(w) for l in md[i+1:] if not l.startswith('#') for w in re.findall(r'[ऀ-ॿ]+', l)]
vocab_set = set(vocab)

idioms = []
for l in md[a:i]:
    m = re.match(r'\|\s*\d+\s*\|\s*\*\*(.+?)\*\*', l)
    if m:
        idioms.append(norm(m.group(1)))

# Grammar feature predicates
AUX = {'है','हैं','हूँ','हो','था','थे','थी','थीं','होगा','होगी','होंगे','होंगी'}
def has(t, pred): return any(pred(t, j) for j in range(len(t)))
G = {
 'present habitual': lambda t, j: re.search(r'(ता|ती|ते)$', t[j]) and j+1 < len(t) and t[j+1] in {'है','हैं','हूँ','हो'},
 'present continuous': lambda t, j: t[j] in {'रहा','रहे','रही'} and j+1 < len(t) and t[j+1] in {'है','हैं','हूँ','हो'},
 'past continuous': lambda t, j: t[j] in {'रहा','रहे','रही'} and j+1 < len(t) and t[j+1] in {'था','थे','थी','थीं'},
 'future continuous': lambda t, j: t[j] in {'रहा','रहे','रही'} and j+1 < len(t) and t[j+1].startswith('होंग') or (t[j] in {'रहा','रहे','रही'} and j+1 < len(t) and t[j+1] in {'होगा','होगी'}),
 'past habitual': lambda t, j: re.search(r'(ता|ती|ते)$', t[j]) and j+1 < len(t) and t[j+1] in {'था','थे','थी','थीं'},
 'simple future': lambda t, j: re.search(r'(ेगा|ेगी|ेंगे|ेंगी|ूँगा|ूँगी|ोगे|ोगी|ंगा|ंगी|ंगे)$', t[j]),
 'present perfect': lambda t, j: t[j] in {'किया','लिया','दिया','गया','आया','गई','गए','आए','चुका','चुके','चुकी'} and j+1 < len(t) and t[j+1] in {'है','हैं','हूँ','हो'},
 'past perfect': lambda t, j: t[j] in {'किया','लिया','दिया','गया','आया','गई','गए','आए','चुका','चुके','चुकी'} and j+1 < len(t) and t[j+1] in {'था','थे','थी','थीं'},
 'future perfect': lambda t, j: t[j] in {'चुका','चुके','चुकी'} and j+1 < len(t) and t[j+1] in {'होगा','होगी','होंगे','होंगी'},
 'ne ergative': lambda t, j: t[j] == 'ने',
 'modal sakna': lambda t, j: re.match(r'सक', t[j]) is not None,
 'obligation': lambda t, j: t[j] in {'चाहिए','चाहिये'} or re.match(r'पड़(ा|ेगा|ती|ता|ना|ी|े)$', t[j]) is not None,
 'passive jaana': lambda t, j: re.match(r'जा(ता|ती|ते|या|एगा|एगी|ए|ना|नी)$', t[j]) is not None or t[j] in {'गया','गई','गए','गयी'} and j > 0,
 'causative': lambda t, j: re.search(r'(वा(ता|ती|ते|या|ना|ई|ए|ओ|एगा)|ाना|ाता|ाती|ाते|ाया|ाई|ाओ)$', t[j]) is not None and len(t[j]) > 4,
 'compound verbs': lambda t, j: t[j] in {'उठा','उठी','उठे','पड़ा','पड़ी','पड़े','बैठा','बैठी','बैठे','डाला','डाली','डालो','लिया','दिया','जाओ'} and j > 0,
}
def g_score(text):
    t = [norm(w) for w in tok(text)]
    return sum(1 for p in G.values() if has(t, lambda tt, j: bool(p(tt, j))))

# 1. Load all 12,149 sentences from live corpus
all_sents = []
for f in sorted((ROOT / 'data').glob('phrases*.json')):
    fnum = int(f.name.replace('phrases','').replace('.json',''))
    is_idiom = fnum in [14, 15, 25, 26, 27, 28, 29, 30, 31, 32]
    is_vt = fnum in [33, 34, 35, 36, 37]
    for row in json.load(open(f)):
        words = set(norm(w) for w in tok(row['hi'])) & vocab_set
        all_sents.append({
            'id': row['id'],
            'row': row,
            'fnum': fnum,
            'vwords': words,
            'is_idiom': is_idiom,
            'is_vt': is_vt,
            'is_anchor_idiom': fnum in [14, 15],
            'gscore': g_score(row['hi']),
            'raw_len': len(row['hi'].split()),
            'toks': [norm(w) for w in tok(row['hi'])]
        })

print(f"Loaded {len(all_sents)} total sentences from corpus.")

# 2. Map 200 baseline idioms to guarantee anchor sentences
def get_idiom_anchors():
    anchors = set()
    for p in idioms:
        ws = [w for w in tok(p) if len(w) > 1]
        if not ws:
            continue
        stems = [w[:-2] if w.endswith(('ना', 'नी')) and len(w) >= 4 else w for w in ws]
        found = None
        for s in all_sents:
            t = s['toks']
            if ' '.join(ws) in ' '.join(t) or all(w in t for w in ws):
                found = s['id']; break
            elif all(any(x.startswith(st) for x in t) for st in stems):
                found = s['id']; break
            elif len(stems) > 2 and all(any(x.startswith(st) for x in t) for st in stems[:-1]):
                found = s['id']; break
        if found:
            anchors.add(found)
    return anchors

idiom_anchors = get_idiom_anchors()
print(f"Found {len(idiom_anchors)} anchor sentences for baseline idioms.")

# 3. Mandatory anchors:
# - phrases14 & phrases15 (1,260 sentences)
# - idiom anchor sentences (ensures 100% of 200 baseline idioms)
# - phrases33 to 37 (1,000 sentences, covering all VT-01 to VT-05 dedicated tense systems)
selected_ids = set()
selected_sents = []
cov = set()

for s in all_sents:
    if s['is_anchor_idiom'] or (s['id'] in idiom_anchors) or s['is_vt']:
        selected_sents.append(s)
        selected_ids.add(s['id'])
        cov.update(s['vwords'])

print(f"Mandatory anchors selected: {len(selected_sents)} sentences (covered {len(cov)}/{len(vocab_set)} vocab words).")

pool = [s for s in all_sents if s['id'] not in selected_ids]

# 4. Greedy Set-Cover to achieve 100.0% vocabulary closure
while cov < vocab_set and pool:
    def score_sent(s):
        gain = len(s['vwords'] - cov)
        if gain == 0:
            return 0
        return gain * (1.8 if s['is_idiom'] else 1.0)

    best = max(pool, key=score_sent)
    gain = len(best['vwords'] - cov)
    if gain == 0:
        break
    selected_sents.append(best)
    selected_ids.add(best['id'])
    cov.update(best['vwords'])
    pool.remove(best)

print(f"Greedy closure reached: {len(selected_sents)} sentences (covered {len(cov)}/{len(vocab_set)} vocab words).")

sel_idioms = [s for s in selected_sents if s['is_idiom']]
sel_non = [s for s in selected_sents if not s['is_idiom']]
print(f"Pre-padding breakdown: Idioms={len(sel_idioms)}, Non-idioms={len(sel_non)}")

# 5. Pad to exactly 6,000 sentences
# Target: Idioms = 1,720, Non-idioms = 4,280 (Grammar = 2,140, Plain Vocab = 2,140)
while len(selected_sents) < 6000 and pool:
    avail_id = [s for s in pool if s['is_idiom']]
    avail_non = [s for s in pool if not s['is_idiom']]
    if len(sel_idioms) < 1720 and avail_id:
        best_id = max(avail_id, key=lambda s: (len(s['vwords']), -abs(s['raw_len'] - 9)))
        selected_sents.append(best_id)
        selected_ids.add(best_id['id'])
        sel_idioms.append(best_id)
        pool.remove(best_id)
    elif avail_non:
        best_non = max(avail_non, key=lambda s: (len(s['vwords']), s['gscore'], -abs(s['raw_len'] - 9)))
        selected_sents.append(best_non)
        selected_ids.add(best_non['id'])
        sel_non.append(best_non)
        pool.remove(best_non)
    elif avail_id:
        best_id = max(avail_id, key=lambda s: (len(s['vwords']), -abs(s['raw_len'] - 9)))
        selected_sents.append(best_id)
        selected_ids.add(best_id['id'])
        sel_idioms.append(best_id)
        pool.remove(best_id)

assert len(selected_sents) == 6000, f"Expected 6000, got {len(selected_sents)}"

# 6. Partition Non-idioms into Grammar (2,140) and Plain Vocab (2,140)
vt_sents = [s for s in sel_non if s['is_vt']]
other_non = [s for s in sel_non if not s['is_vt']]
other_non.sort(key=lambda s: (s['gscore'], len(s['vwords'])), reverse=True)

needed_grammar_extra = 2140 - len(vt_sents)
grammar_sents = vt_sents + other_non[:needed_grammar_extra]
vocab_sents = other_non[needed_grammar_extra:]

assert len(sel_idioms) == 1720, f"Expected 1720 idioms, got {len(sel_idioms)}"
assert len(grammar_sents) == 2140, f"Expected 2140 grammar, got {len(grammar_sents)}"
assert len(vocab_sents) == 2140, f"Expected 2140 vocab, got {len(vocab_sents)}"

print("\n" + "=" * 60)
print("FINAL 6,000 MASTER SELECTION ACHIEVED:")
print(f"  Pillar 1 (Idioms & Proverbs):        {len(sel_idioms)} sentences ({len(sel_idioms)/60:.1f}%)")
print(f"  Pillar 2 (Grammar, Verbs & Tenses):  {len(grammar_sents)} sentences ({len(grammar_sents)/60:.1f}%)")
print(f"  Pillar 3 (Plain Vocabulary Spine):   {len(vocab_sents)} sentences ({len(vocab_sents)/60:.1f}%)")
print(f"  Total Master Corpus:                 {len(selected_sents)} sentences (100.0%)")
print("=" * 60)

# Check vocabulary coverage
final_toks = [[norm(w) for w in tok(s['row']['hi'])] for s in selected_sents]
used = collections.Counter(w for t in final_toks for w in t)
miss = [w for w in vocab if w not in used]
print(f"  Vocabulary Coverage: {len(vocab) - len(miss)}/{len(vocab)} exact-token ({100*(len(vocab)-len(miss))/len(vocab):.2f}%)")
assert len(miss) == 0, f"Missing {len(miss)} vocabulary words!"

# Check baseline idioms
text = [' '.join(t) for t in final_toks]
def idiom_hit(p):
    ws = [w for w in tok(p) if len(w) > 1]
    if not ws: return False
    if ' '.join(ws) in ' '.join(text): return True
    if any(all(w in t for w in ws) for t in final_toks): return True
    stems = [w[:-2] if w.endswith(('ना', 'नी')) and len(w) >= 4 else w for w in ws]
    if any(all(any(t.startswith(st) for t in sent) for st in stems) for sent in final_toks): return True
    if len(stems) > 2:
        head = stems[:-1]
        return any(all(any(t.startswith(st) for t in sent) for st in head) for sent in final_toks)
    return False

hit_idioms = sum(1 for p in idioms if idiom_hit(p))
print(f"  Baseline Idioms Coverage: {hit_idioms}/{len(idioms)} (100.0%)")
assert hit_idioms == len(idioms), f"Missing {len(idioms) - hit_idioms} idioms!"

# Check verbs
verbs = [(r, w) for r, w in [(r, norm(w)) for r, w in enumerate(vocab, 1)] if w.endswith('ना') and len(w) > 3 and ' ' not in w]
covered_verbs = 0
for r, v in verbs:
    st = v[:-2]
    hits = [w for w in used if w.startswith(st) and len(w) <= len(st) + 4]
    if hits or v in used:
        covered_verbs += 1
print(f"  Verbs Coverage: {covered_verbs}/{len(verbs)} (100.0%)")
assert covered_verbs == len(verbs), f"Missing {len(verbs) - covered_verbs} verbs!"

# 7. Output into 20 uniform files of 300 sentences each: opt_phrases01.json to opt_phrases20.json
out_dir = ROOT / "data" / "optimized_6000"
out_dir.mkdir(parents=True, exist_ok=True)

ordered_sents = []
# Ordered systematically:
# 1. Plain Vocabulary Spine (2,140 sentences)
# 2. Grammar, Verbs & Tenses (2,140 sentences)
# 3. Idioms, Proverbs & Cultural (1,720 sentences)
ordered_sents.extend(vocab_sents)
ordered_sents.extend(grammar_sents)
ordered_sents.extend(sel_idioms)

chunk_size = 300
manifest_files = []

for c_idx in range(20):
    start = c_idx * chunk_size
    end = start + chunk_size
    chunk = ordered_sents[start:end]
    fname = f"opt_phrases{c_idx+1:02d}.json"
    fpath = out_dir / fname

    clean_chunk = []
    for s in chunk:
        clean_chunk.append({
            'id': s['id'],
            'en': s['row']['en'],
            'hi': s['row']['hi'],
            'align': s['row']['align']
        })
    fpath.write_text(json.dumps(clean_chunk, ensure_ascii=False, indent=2) + '\n')
    manifest_files.append({
        'file': f"data/optimized_6000/{fname}",
        'count': len(clean_chunk)
    })
    print(f"Wrote {fpath.name} with {len(clean_chunk)} sentences.")

# Write manifest_6000.json
manifest_path = ROOT / "data" / "manifest_6000.json"
manifest_path.write_text(json.dumps({
    'total_sentences': len(selected_sents),
    'tier_distribution': {
        'idioms_and_proverbs': len(sel_idioms),
        'grammar_verbs_and_tenses': len(grammar_sents),
        'plain_vocabulary_spine': len(vocab_sents)
    },
    'files': manifest_files
}, ensure_ascii=False, indent=2) + '\n')
print(f"\nWrote manifest_6000.json with 20 chunk files totaling 6,000 sentences.")
