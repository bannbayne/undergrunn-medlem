with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('function Pi(')
print(c[pos+300:pos+1500])
