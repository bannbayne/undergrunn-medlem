import os
import urllib.request
import urllib.error
import json
import concurrent.futures

GORDON_DIR = r"c:\Users\josou\Downloads\NORSK AUTOTUNE SPILLET\gordon\PRODUCTION-202006192205-424220153"
bobba_base = "https://images.bobba.io/gordon/PRODUCTION-202006192205-424220153/"

with open(os.path.join(GORDON_DIR, "map.json"), "r", encoding="utf-8") as f:
    map_data = json.load(f)

all_libs = set()
for part, dict_data in map_data.items():
    for id_val, lib_name in dict_data.items():
        all_libs.add(lib_name)

# Ensure core libs are included
core_libs = [
    "hh_human_shoe",
    "hh_human_acc_face",
    "hh_human_acc_head",
    "hh_human_acc_chest",
    "hh_human_acc_waist",
    "hh_human_acc_eye"
]
for c in core_libs:
    all_libs.add(c)

print(f"Total unique figure libraries to check: {len(all_libs)}")

def download_lib(lib):
    lib_dir = os.path.join(GORDON_DIR, lib)
    png_dst = os.path.join(lib_dir, "atlas.png")
    json_dst = os.path.join(lib_dir, "offset.json")
    
    if os.path.exists(png_dst) and os.path.getsize(png_dst) > 0 and os.path.exists(json_dst) and os.path.getsize(json_dst) > 0:
        return (lib, "already_exists")
    
    # Try fetching atlas.png
    url_png = bobba_base + f"{lib}/atlas.png"
    url_json = bobba_base + f"{lib}/offset.json"
    
    try:
        req = urllib.request.Request(url_png, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            png_data = resp.read()
    except Exception:
        return (lib, "404")
    
    try:
        req = urllib.request.Request(url_json, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            json_data = resp.read()
    except Exception:
        json_data = b"{}"
        
    os.makedirs(lib_dir, exist_ok=True)
    with open(png_dst, "wb") as f_out:
        f_out.write(png_data)
    with open(json_dst, "wb") as f_out:
        f_out.write(json_data)
        
    return (lib, f"ok ({len(png_data)} B)")

results = {}
with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
    future_to_lib = {executor.submit(download_lib, lib): lib for lib in all_libs}
    for future in concurrent.futures.as_completed(future_to_lib):
        lib = future_to_lib[future]
        try:
            status = future.result()
            results[lib] = status[1]
            if "ok" in status[1]:
                print(f"[DOWNLOADED] {lib}: {status[1]}")
        except Exception as e:
            results[lib] = str(e)

ok_count = sum(1 for v in results.values() if "ok" in v or v == "already_exists")
print(f"\nDone: {ok_count} libraries available locally.")
