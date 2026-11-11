with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find(',Ce=')
if pos != -1:
    print(c[pos-50:pos+350])
