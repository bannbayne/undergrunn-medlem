with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('async function mn(')
print(c[pos:pos+600])
