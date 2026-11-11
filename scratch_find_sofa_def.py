with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('sofa:{')
if pos == -1:
    pos = c.find('"sofa":{')
print(c[pos-50:pos+350])
