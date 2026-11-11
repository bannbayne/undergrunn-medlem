import re, time

with open('index-offline.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Alias Ce.sofa to Ce.f_sofa
target_ce = 'for(const _k in Ce){if(Ce[_k])Ce[_k].placeable=!0;}'
repl_ce = 'for(const _k in Ce){if(Ce[_k])Ce[_k].placeable=!0;}Ce.sofa=Ce.f_sofa;'
if target_ce in code:
    code = code.replace(target_ce, repl_ce, 1)
    print("1. Added Ce.sofa = Ce.f_sofa alias")
else:
    print("WARNING: target_ce not found")

# 2. Update IM to use f_sofa
code = re.sub(r'storage:\{sofa:1\},', 'storage:{f_sofa:1},', code)
code = re.sub(r'storage:\{\},(\r?\n\s*stash:\{\},)', r'storage:{f_sofa:1},\1', code)
print("2. Updated IM storage to { f_sofa: 1 }")

# 3. Update AM to use f_sofa and migrate sofa -> f_sofa
target_am = 'if(Object.keys(p.storage).length===0)p.storage.sofa=1;'
repl_am = '''if(p.storage.sofa){p.storage.f_sofa=(p.storage.f_sofa||0)+p.storage.sofa;delete p.storage.sofa;}if(!p.storage.f_sofa&&Object.keys(p.storage).length===0)p.storage.f_sofa=1;'''
if target_am in code:
    code = code.replace(target_am, repl_am, 1)
    print("3. Updated AM storage to f_sofa")
else:
    print("WARNING: target_am not found")

# 4. Update Se take action to handle both sofa and f_sofa
old_take_key = 'const key = n.key;'
new_take_key = '''let key = n.key;
    if (key === "sofa" && !t.storage["sofa"] && t.storage["f_sofa"]) key = "f_sofa";
    if (key === "f_sofa" && !t.storage["f_sofa"] && t.storage["sofa"]) key = "sofa";'''
if old_take_key in code:
    code = code.replace(old_take_key, new_take_key, 1)
    print("4. Updated Se take action key mapping")
else:
    print("WARNING: old_take_key not found")

# 5. Update takeFromStorage in Au() to find slot with f or f_sofa
old_au_slot = 'const slot=s.inventory.findIndex(it=>it&&it.item===f);'
new_au_slot = 'const slot=s.inventory.findIndex(it=>it&&(it.item===f||it.item==="f_"+f||f==="f_"+it.item));if(slot>=0){const itKind=s.inventory[slot].item;'
if old_au_slot in code:
    code = code.replace(old_au_slot, new_au_slot, 1)
    code = code.replace('Dn={kind:f,source:"inv",slot:slot,owner:void 0};Wo=ir(f);', 'Dn={kind:itKind,source:"inv",slot:slot,owner:void 0};Wo=ir(itKind);', 1)
    print("5. Updated takeFromStorage slot matching in Au()")
else:
    print("WARNING: old_au_slot not found")

# 6. Ensure sofa nitro mapping
old_fn_map = 'FURNI_NITRO_MAP={}'
new_fn_map = 'FURNI_NITRO_MAP={sofa:"f_sofa.nitro",f_sofa:"f_sofa.nitro"}'
if old_fn_map in code:
    code = code.replace(old_fn_map, new_fn_map, 1)
    print("6. Updated FURNI_NITRO_MAP with f_sofa.nitro")
else:
    print("WARNING: old_fn_map not found")

with open('index-offline.js', 'w', encoding='utf-8') as f:
    f.write(code)

with open('assets/index-offline.js', 'w', encoding='utf-8') as f:
    f.write(code)

# Update cache buster
v = int(time.time() * 1000)
for fn in ['play.html', 'index.html']:
    with open(fn, 'r', encoding='utf-8') as f:
        html = f.read()
    html = re.sub(r'index-offline\.js\?v=\d+', f'index-offline.js?v={v}', html)
    with open(fn, 'w', encoding='utf-8') as f:
        f.write(html)
print(f"Updated cache busters in html files to v={v}")
