import urllib.request
import os

mp3s = [
    'cd-blodigoktober.mp3',
    'cd-leolegit-blodoktober.mp3',
    'cd-yungxware-russisk-roulette.mp3',
    'cd-lemonade-dip-dip.mp3'
]

bases = [
    "https://playlistmag.studio/hotel/audio/",
    "https://playlistmag.studio/hotel/",
    "https://playlistmag.studio/audio/",
    "https://playlistmag.studio/hotel/music/"
]

for m in mp3s:
    found = False
    for b in bases:
        url = b + m
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'}, method='HEAD')
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    print(f"[FOUND] {url} (size: {resp.headers.get('Content-Length')})")
                    found = True
                    break
        except Exception:
            pass
    if not found:
        print(f"[NOT FOUND] {m}")
