import sys
from pathlib import Path
p = Path(__file__).resolve().parent.parent / "assets" / "suite.js"
s = p.read_text()
sep = "    // -----------------------------------------------------------------------\n"
title_target = '      title: "%s"' % sys.argv[1]
i = s.index(title_target)
a = s.rindex(sep, 0, s.rindex(sep, 0, i))
if sep in s[i:]:
    b = s.index(sep, i)
else:
    # Last game in array
    b = s.index("\n  ];", i)
p.write_text(s[:a] + s[b:])
print(f"Removed '{sys.argv[1]}'")
