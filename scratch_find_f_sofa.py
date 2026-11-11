with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

import re
matches = [m.start() for m in re.finditer(r'f_sofa', c)]
print('f_sofa matches:', len(matches))
for idx in matches:
    print(c[idx-50:idx+150])
    print('='*30)
