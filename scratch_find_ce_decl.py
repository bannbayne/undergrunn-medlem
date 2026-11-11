with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = [m.start() for m in re.finditer(r'(const|let|var)\s+Ce\s*=', c)]
print('Ce declaration count:', len(matches))
for idx in matches:
    print(c[idx:idx+300])
