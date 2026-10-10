import re
from pathlib import Path
R = Path(__file__).resolve().parent.parent / "assets"

s = (R/"suite.js").read_text()
a = s.index("    // -----------------------------------------------------------------------\n    // Game 26: Chasing Shadows")
b = s.index("    // -----------------------------------------------------------------------\n    // Game 27")
s = s[:a] + s[b:]
s = s.replace("  const speakHindi = window.__speakHindi;\n", "")
(R/"suite.js").write_text(s)

e = (R/"engine.js").read_text()
e = re.sub(r"  function speakHindi\(text\) \{.*?\n  \}\n\n?", "", e, count=1, flags=re.S)
e = e.replace("  window.__speakHindi = speakHindi;\n", "")
(R/"engine.js").write_text(e)

p = (R/"app.js").read_text()
p = re.sub(r"    function speakHindi\(text\) \{.*?\n    \}\n\n", "", p, count=1, flags=re.S)
p = re.sub(r"    function listen\(\) \{.*?\n    \}\n\n", "", p, count=1, flags=re.S)
p = p.replace('      dom.btnListen.addEventListener("click", listen);\n', "")
p = p.replace('"btn-listen", ', "")
(R/"app.js").write_text(p)

h = Path(R.parent/"index.html")
t = h.read_text()
t = re.sub(r'\s*<button id="btn-listen".*?</button>', "", t, count=1, flags=re.S)
h.write_text(t)
