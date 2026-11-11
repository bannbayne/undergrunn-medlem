with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('opens:"character"}}')
print("Ce end pos:", pos)
if pos != -1:
    print(c[pos:pos+200])
