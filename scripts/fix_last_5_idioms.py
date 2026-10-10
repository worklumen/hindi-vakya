import json, re, glob
from pathlib import Path
import importlib.util

ROOT = Path('.')
spec = importlib.util.spec_from_file_location("ga", ROOT / "scripts" / "gen_align.py")
ga = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ga)

# Explicit target sentences matching exact idiom strings:
FIXES = [
    ("The magical spectacle left everyone completely dumbfounded", "जादू का खेल देखकर सब हक्का बक्का रह गए"),
    ("Incompetent people blame the courtyard dancing dancing courtyard becomes small", "असमर्थ व्यक्ति कहता है नाचते नाचते आँगन छोटा"),
    ("If you plant acacia you cannot expect sweet mangoes", "बोए पेड़ बबूल का तो आम कहाँ से होय पुरानी सीख है"),
    ("Bad company brings dishonor as hands turn black in coal brokerage", "गलत लोगों के साथ कोयले की दलाली में हाथ काले होते हैं"),
    ("In deep adversity human wisdom is lost", "कठिन विपत्ति में बुद्धि नष्ट होती है इसलिए शांत रहो"),
]

data = json.load(open('data/phrases24.json'))
prefix = "p24"

for e, h in FIXES:
    align = ga.derive(e, h)
    data.append({
        "id": f"{prefix}s{len(data)+1:03d}",
        "en": e,
        "hi": h,
        "align": align
    })

open('data/phrases24.json', 'w').write(json.dumps(data, ensure_ascii=False, indent=2) + "\n")
print(f"Updated data/phrases24.json to {len(data)} sentences")

man = json.load(open('data/manifest.json'))
for f in man['files']:
    if f['file'] == 'data/phrases24.json':
        f['count'] = len(data)
json.dump(man, open('data/manifest.json', 'w'), ensure_ascii=False, indent=2)
print("Updated manifest.json")
