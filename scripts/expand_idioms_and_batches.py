import json, re, glob
from pathlib import Path

ROOT = Path('.')

# Let's verify existing idioms in VAKYA.md
lines = open('VAKYA.md').read().splitlines()
idx_sec3 = next(i for i, l in enumerate(lines) if l.startswith('## 3.'))
idx_sec4 = next(i for i, l in enumerate(lines) if l.startswith('## 4.'))

print(f"Sec 3 is lines {idx_sec3} to {idx_sec4}")
