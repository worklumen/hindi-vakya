#!/usr/bin/env python3
"""Validate the phrase corpus: charset, align correctness, unique ids.

Usage: python3 scripts/validate_corpus.py [data/phrasesNN.json ...]
With no args, validates every phrases*.json in data/.
Exit code 1 if any error is found.
"""
import glob
import json
import re
import sys

DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')
ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')


def check_align(s, errs):
    a = s.get('align')
    if a is None:
        errs.append(f"{s['id']}: missing align")
        return
    toks = a.split()
    en = s['en'].split()
    hi = s['hi'].split()
    if len(toks) != len(hi):
        errs.append(f"{s['id']}: align has {len(toks)} tokens, hi has {len(hi)} words")
        return
    for t in toks:
        for part in re.split(r'[-,]', t):
            if not (part.isdigit() and int(part) < len(en)):
                errs.append(f"{s['id']}: bad align token {t!r} (en len {len(en)})")
                return


def main():
    files = sys.argv[1:] or sorted(glob.glob('data/phrases*.json'))
    if not files:
        print('no phrase files found')
        return 1
    errs = []
    seen_ids = {}
    seen_hi = {}
    total = 0
    for f in files:
        data = json.load(open(f))
        for s in data:
            total += 1
            sid = s.get('id', '<no id>')
            if sid in seen_ids:
                errs.append(f"{sid}: duplicate id (also in {seen_ids[sid]})")
            seen_ids[sid] = f
            if not ASC.match(s['en']):
                errs.append(f"{sid}: en not letters+spaces: {s['en']!r}")
            if not DEV.match(s['hi']):
                errs.append(f"{sid}: hi not Devanagari+spaces: {s['hi']!r}")
            check_align(s, errs)
            if s['hi'] in seen_hi:
                errs.append(f"{sid}: duplicate hi (also {seen_hi[s['hi']]})")
            seen_hi[s['hi']] = sid
    dup_hi = len([1 for _ in seen_hi])
    print(f"checked {total} sentences in {len(files)} files "
          f"({dup_hi} unique hi)")
    if errs:
        for e in errs[:50]:
            print('ERROR', e)
        if len(errs) > 50:
            print(f'... and {len(errs) - 50} more errors')
        print(f'{len(errs)} errors')
        return 1
    print('all OK')
    return 0


if __name__ == '__main__':
    sys.exit(main())
