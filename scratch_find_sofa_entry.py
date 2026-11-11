with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('id:"sofa"')
print("pos:", pos)
if pos != -1:
    print(c[pos-100:pos+300])
