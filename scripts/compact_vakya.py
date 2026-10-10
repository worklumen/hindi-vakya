"""Phase A: compact VAKYA.md without losing any vocab.

Transforms:
1. §4 vocab table (rank|word|freq) -> 4 tier subsections of wrapped word lists
   (global rank order preserved; rank implicit in position).
2. §1 `batches` JSON block -> moved verbatim to scripts/batches.json, replaced
   in VAKYA.md by a short summary + pointer.
3. §1 `vocab_log` JSON block -> one line per entry.

Run once. Verify with scripts/check_compaction.py (word-sequence identity)
and identical coverage_vakya.py output before/after.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
md_path = ROOT / "VAKYA.md"
lines = md_path.read_text().splitlines()

# ---------------- 1. extract vocab words in order ----------------
i4 = next(k for k, l in enumerate(lines) if l.startswith("## 4."))
vocab = []
for l in lines[i4:]:
    m = re.match(r"\|\s*\d+\s*\|\s*([^|]+?)\s*\|", l)
    if m:
        vocab.append(m.group(1).strip())
assert len(vocab) == 9418, f"expected 9418 vocab words, got {len(vocab)}"
assert len(set(vocab)) == len(vocab), "duplicate vocab words found"

BANDS = [(1, 500), (501, 2000), (2001, 5000), (5001, 9418)]
PER_LINE = 12

sec4 = [
    "## 4. Complete Vocabulary Corpus (All 9,418 Words)",
    "",
    "Total Cataloged Vocabulary: **9418** words across 4 frequency tiers.",
    "Words are listed in global frequency-rank order (rank = position from the "
    "start of the list); the four tier sections below follow the same order "
    "continuously. Plain word lists, 12 words per line.",
    "",
]
for lo, hi in BANDS:
    band = vocab[lo - 1:hi]
    sec4.append(f"### Vocabulary Rank {lo}-{hi}")
    sec4.append("")
    for k in range(0, len(band), PER_LINE):
        sec4.append(" ".join(band[k:k + PER_LINE]))
    sec4.append("")

# ---------------- 2. move `batches` JSON out ----------------
ib = next(k for k, l in enumerate(lines) if l.strip() == "### batches")
ib_open = next(k for k in range(ib, len(lines)) if lines[k].strip() == "```json")
ib_close = next(k for k in range(ib_open + 1, len(lines)) if lines[k].strip() == "```")
batches = json.loads("\n".join(lines[ib_open + 1:ib_close]))
(ROOT / "scripts" / "batches.json").write_text(
    json.dumps(batches, ensure_ascii=False, indent=2) + "\n")
done = sum(1 for b in batches if str(b.get("status", "")).lower() == "done")
batches_summary = [
    "### batches",
    "",
    f"{len(batches)} authoring batches logged ({done} done). Full batch metadata "
    "(ids, topics, files, counts, alignment status) now lives in "
    "`scripts/batches.json` — it is authoring history, not linguistic reference.",
    "",
]

# ---------------- 3. compress `vocab_log` ----------------
iv = next(k for k, l in enumerate(lines) if l.strip() == "### vocab_log")
iv_open = next(k for k in range(iv, len(lines)) if lines[k].strip() == "```json")
iv_close = next(k for k in range(iv_open + 1, len(lines)) if lines[k].strip() == "```")
vlog = json.loads("\n".join(lines[iv_open + 1:iv_close]))
vlog_lines = ["### vocab_log", ""]
for e in vlog:
    date = e.get("date", e.get("id", "?"))
    added = e.get("added", e.get("words", 0))
    vlog_lines.append(f"- {date}: +{added} — {e['note']}")
vlog_lines.append("")

# ---------------- reassemble ----------------
out = (lines[:iv] + vlog_lines           # compressed vocab_log
       + lines[iv_close + 1:ib]          # everything between vocab_log and batches
       + batches_summary                 # batches pointer
       + lines[ib_close + 1:i4]          # coverage / grammar_files / idioms_files + §2 §3
       + sec4)                           # compact §4
md_path.write_text("\n".join(out) + "\n")
print(f"vocab words carried over: {len(vocab)}")
print(f"batches moved to scripts/batches.json: {len(batches)} entries")
print(f"lines: {len(lines)} -> {len(out)}")
