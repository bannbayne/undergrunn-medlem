with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('for(const')
# find where Ce items are assigned nitro
import re
matches = [m.start() for m in re.finditer(r'Ce\[[^\]]+\]\.nitro', c)]
print('Ce[...].nitro count:', len(matches))
for idx in matches:
    print(c[idx-50:idx+150])
    print('='*30)
