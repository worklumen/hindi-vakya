import json

data = json.load(open('data/phrases13.json'))
for s in data:
    if s['id'] == 'b218s037':
        print("Before:", s)
        # en: "may(0) I(1) select(2) yellow(3) ripe(4) bananas(5)"
        # hi: "क्या(0) मैं(1) पीले(3) पके(4) केले(5) चुन(2) सकता(0) हूँ(0)"
        s['hi'] = "क्या मैं पीले पके केले चुन सकता हूँ"
        s['align'] = "0 1 3 4 5 2 0 0"
        print("After:", s)
        break

json.dump(data, open('data/phrases13.json', 'w'), ensure_ascii=False, indent=2)
print("Updated data/phrases13.json")
