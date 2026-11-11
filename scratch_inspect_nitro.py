import zlib, json

with open('furni/f_sofa.nitro', 'rb') as f:
    data = f.read()

print("f_sofa.nitro size:", len(data))
# Nitro format: binary bundle of JSON + PNG
# Let's inspect the files inside
offset = 0
while offset < len(data):
    if offset + 4 > len(data):
        break
    # Check nitro header
    break
