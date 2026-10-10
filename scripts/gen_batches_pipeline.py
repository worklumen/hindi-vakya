#!/usr/bin/env python3
"""Batch Generation Pipeline Helper for Hindi Vakya corpus.
Validates constraints:
- ASC for English
- DEV for Hindi
- No duplicate Hindi
- Semantic alignment with build_master_aligner
- Manifest update
"""
import json
import re
import sys
from pathlib import Path
import build_master_aligner as bma

ROOT = Path(__file__).resolve().parent.parent

ASC = re.compile(r'^[A-Za-z]+(?: [A-Za-z]+)*$')
DEV = re.compile(r'^[ऀ-ॿ]+(?: [ऀ-ॿ]+)*$')

def process_batch(batch_num: int, id_prefix: str, pairs: list):
    manifest_file = ROOT / "data" / "manifest.json"
    manifest = json.load(open(manifest_file))

    # Collect existing Hindi
    existing_hi = {}
    for entry in manifest["files"]:
        fpath = ROOT / entry["file"]
        if fpath.exists() and entry["file"] != f"data/phrases{batch_num}.json":
            for row in json.load(open(fpath)):
                existing_hi[row["hi"]] = (entry["file"], row["id"])

    errors = []
    seen_hi = set()
    out = []

    for idx, (en, hi) in enumerate(pairs, start=1):
        sid = f"{id_prefix}{idx:03d}"
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

        align = bma.align_sentence(en, hi)
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
        print(f"FOUND {len(errors)} ERRORS IN BATCH {batch_num}:")
        for e in errors[:25]:
            print("  ", e)
        sys.exit(1)

    out_file = ROOT / "data" / f"phrases{batch_num}.json"
    out_file.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n")
    print(f"Successfully generated {out_file} with {len(out)} sentences.")

    manifest["files"] = [f for f in manifest["files"] if f["file"] != f"data/phrases{batch_num}.json"]
    manifest["files"].append({
        "file": f"data/phrases{batch_num}.json",
        "count": len(out)
    })
    manifest["files"].sort(key=lambda x: x["file"])
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    print(f"Updated {manifest_file} with data/phrases{batch_num}.json (count: {len(out)}).")

if __name__ == '__main__':
    print("Pipeline helper ready.")
