with open('index-offline.js', 'r', encoding='utf-8') as f:
    c = f.read()

pos_i6 = c.find('function I6(')
if pos_i6 != -1:
    print("I6:", c[pos_i6:pos_i6+800])
pos_a6 = c.find('function A6(')
if pos_a6 != -1:
    print("A6:", c[pos_a6:pos_a6+800])
