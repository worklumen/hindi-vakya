import json, re, glob
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parent.parent

# Setup alignment derivation
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

norm = lambda w: w.replace('\u095c','\u0921').replace('\u095d','\u0922').replace('\u093c', '')
tok = lambda t: re.findall(r'[\u0900-\u097F]+', t)

# Load VAKYA idioms
lines = (ROOT / "VAKYA.md").read_text().splitlines()
all_idioms = []
in_sec = False
for l in lines:
    if l.startswith("## 3."): in_sec = True
    elif l.startswith("## 4."): in_sec = False
    if in_sec:
        m = re.match(r"\|\s*\d+\s*\|\s*\*\*(.+?)\*\*\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|", l)
        if m:
            all_idioms.append((m.group(1).strip(), m.group(3).strip(), m.group(4).strip()))

print(f"Loaded {len(all_idioms)} idioms from VAKYA.md")

# New idioms are indices 100 to 199 (100 idioms total)
new_idioms = all_idioms[100:]
print(f"New idioms to add across batches: {len(new_idioms)}")
