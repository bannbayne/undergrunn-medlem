with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('{id:"sofa"')
print("Or entry for sofa:")
print(c[pos-50:pos+300])
pos_io = c.find('Io=')
if pos_io != -1:
    print("Io:", c[pos_io-10:pos_io+30])
