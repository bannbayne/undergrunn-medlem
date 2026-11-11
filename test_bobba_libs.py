import urllib.request
import os

bobba_base = "https://images.bobba.io/gordon/PRODUCTION-202006192205-424220153/"

libs_to_test = [
    "hh_human_shoe",
    "hh_human_acc_face",
    "hh_human_acc_head",
    "hh_human_acc_chest",
    "hh_human_acc_waist",
    "hh_human_acc_eye"
]

found = []
for lib in libs_to_test:
    url = bobba_base + f"{lib}/atlas.png"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
        with urllib.request.urlopen(req, timeout=5) as resp:
            if resp.status == 200:
                print(f"[FOUND] {lib} (size: {resp.headers.get('Content-Length')})")
                found.append(lib)
    except Exception as e:
        print(f"[FAILED] {lib}: {e}")

print("Total found:", len(found))
