with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = [m.start() for m in re.finditer(r'[^a-zA-Z0-9_$]mn\s*=', c)]
for idx in matches:
    print(c[idx:idx+250])
