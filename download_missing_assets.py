import os
import urllib.request
import urllib.error
import time

FURNI_DIR = r"c:\Users\josou\Downloads\NORSK AUTOTUNE SPILLET\furni"
GORDON_DIR = r"c:\Users\josou\Downloads\NORSK AUTOTUNE SPILLET\gordon\PRODUCTION-202006192205-424220153"
os.makedirs(FURNI_DIR, exist_ok=True)
os.makedirs(GORDON_DIR, exist_ok=True)

# 1. Download furniture .nitro files
with open(r"c:\Users\josou\Downloads\NORSK AUTOTUNE SPILLET\furniture_list.txt", "r", encoding="utf-8") as f:
    furni_files = [line.strip() for line in f if line.strip()]

furni_base = "https://playlistmag.studio/hotel/"
f_ok = 0
f_err = 0

print(f"Downloading {len(furni_files)} furniture files...")
for rel in furni_files:
    fname = os.path.basename(rel)
    dst = os.path.join(FURNI_DIR, fname)
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        f_ok += 1
        continue
    url = furni_base + rel
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            with open(dst, "wb") as out:
                out.write(data)
        f_ok += 1
        print(f"[FURNI OK] {fname} ({len(data)} B)")
    except Exception as e:
        f_err += 1
        print(f"[FURNI FAIL] {fname}: {e}")

print(f"Furniture: {f_ok} ok, {f_err} failed.")

# 2. Download core avatar libraries (atlas.png and offset.json)
bobba_base = "https://images.bobba.io/gordon/PRODUCTION-202006192205-424220153/"
core_libs = [
    "hh_human_body",
    "hh_human_shirt",
    "hh_human_leg",
    "hh_human_hair",
    "hh_human_face",
    "hh_human_hats",
    "hh_human_item"
]

b_ok = 0
b_err = 0
print(f"\nDownloading {len(core_libs)} avatar libraries...")
for lib in core_libs:
    lib_dir = os.path.join(GORDON_DIR, lib)
    os.makedirs(lib_dir, exist_ok=True)
    for asset in ["atlas.png", "offset.json"]:
        dst = os.path.join(lib_dir, asset)
        if os.path.exists(dst) and os.path.getsize(dst) > 0:
            b_ok += 1
            continue
        url = bobba_base + f"{lib}/{asset}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = resp.read()
                with open(dst, "wb") as out:
                    out.write(data)
            b_ok += 1
            print(f"[AVATAR OK] {lib}/{asset} ({len(data)} B)")
        except Exception as e:
            b_err += 1
            print(f"[AVATAR FAIL] {lib}/{asset}: {e}")

print(f"Avatar libs: {b_ok} ok, {b_err} failed.")
