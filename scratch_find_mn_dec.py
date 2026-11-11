with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos = c.find('mn(n)')
print("around mn(n):")
print(c[pos-200:pos+100])
# find declaration of mn before this
pos_dec = c.rfind('mn=', 0, pos)
if pos_dec != -1:
    print("mn declaration:", c[pos_dec-20:pos_dec+100])
else:
    pos_fn = c.rfind('function mn', 0, pos)
    print("mn function:", c[pos_fn:pos_fn+100])
