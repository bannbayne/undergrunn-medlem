with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

import re
for fn in ['I6', 'A6']:
    matches = [m.start() for m in re.finditer(r'[^a-zA-Z0-9_$]' + fn + r'\s*=', c)]
    for idx in matches:
        print(fn, c[idx:idx+200])
