with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('function mn(t){')
print(c[pos+4000:pos+5000])
