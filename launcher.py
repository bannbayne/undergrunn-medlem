import os
import sys
import subprocess
import time
import webbrowser

DIR = os.path.dirname(os.path.abspath(__file__))
UE_EDITOR = r"C:\Program Files\Epic Games\UE_5.8\Engine\Binaries\Win64\UnrealEditor.exe"
PROJECT_FILE = os.path.join(DIR, "BlodigOktober", "BlodigOktober.uproject")

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    clear()
    print("""
========================================================================
   ____  _     ____  ____ ___ ____     ___  _  _______ ____  ____  _____ ____  
  | __ )| |   / __ \\|  _ \\_ _/ ___|   / _ \\| |/ /_   _/ __ \\| __ )| ____|  _ \\ 
  |  _ \\| |  | |  | | | | | | |  _   | | | | ' /  | || |  | |  _ \\|  _| | |_) |
  | |_) | |__| |__| | |_| | | |_| |  | |_| | . \\  | || |__| | |_) | |___|  _ < 
  |____/|_____\\____/|____/___\\____|   \\___/|_|\\_\\ |_| \\____/|____/|_____|_| \\_\\

               NORSK AUTOTUNE HOTEL - STANDALONE LAUNCHER
========================================================================
""")

def play_game():
    print("\n[+] Starter Blodig oktober spillserver og vindu...")
    server_script = os.path.join(DIR, "server.py")
    subprocess.Popen([sys.executable, server_script])
    print("[+] Spillet er startet! Kos deg i kælderen og på konserten.")
    input("\nTrykk Enter for å gå tilbake til menyen...")

def launch_ue():
    if not os.path.exists(UE_EDITOR):
        print(f"\n[!] Fant ikke Unreal Engine 5.8 på: {UE_EDITOR}")
        input("Trykk Enter...")
        return

    if not os.path.exists(PROJECT_FILE):
        print(f"\n[!] Fant ikke prosjektfilen: {PROJECT_FILE}")
        input("Trykk Enter...")
        return

    print(f"\n[+] Starter Unreal Engine 5.8 med BlodigOktober...")
    subprocess.Popen([UE_EDITOR, PROJECT_FILE])
    print("[+] Unreal Engine 5.8 laster i bakgrunnen.")
    input("\nTrykk Enter for å gå tilbake til menyen...")

def play_music():
    print_banner()
    tracks = [
        ("kravle - blodig oktober", os.path.join(DIR, "music", "cd-blodigoktober.mp3")),
        ("leolegit - blodoktober (prod. Lykk)", os.path.join(DIR, "music", "cd-leolegit-blodoktober.mp3")),
        ("yungxware - russisk roulette", os.path.join(DIR, "music", "cd-yungxware-russisk-roulette.mp3")),
        ("lemonade - Dip Dip", os.path.join(DIR, "music", "cd-lemonade-dip-dip.mp3")),
        ("Hele albummet (Blodig oktober)", os.path.join(DIR, "music", "album-blodig-oktober.mp3")),
        ("Åhmingud", os.path.join(DIR, "music", "album-ahmingud.mp3")),
        ("Blod ud af næsen", os.path.join(DIR, "music", "album-blod-ud-af-naesen.mp3")),
    ]

    print("--- AUTOTUNE JUKEBOX ---")
    for idx, (title, path) in enumerate(tracks, 1):
        status = "TILGJENGELIG" if os.path.exists(path) else "MANGLER"
        print(f" [{idx}] {title} ({status})")

    choice = input("\nVelg sangnummer for å spille av (eller 0 for tilbake): ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(tracks):
        track_path = tracks[int(choice) - 1][1]
        if os.path.exists(track_path):
            os.startfile(track_path)
            print(f"[+] Spiller: {tracks[int(choice)-1][0]}")
        else:
            print("[!] Filen finnes ikke.")
        time.sleep(1.5)

def open_folder():
    os.startfile(DIR)

def main():
    while True:
        print_banner()
        print(" Hovedmeny:")
        print("   [1] Spill Blodig oktober NÅ (Åpner i eget spillvindu)")
        print("   [2] Åpne i Unreal Engine 5.8 (BlodigOktober prosjekt)")
        print("   [3] Autotune Jukebox (Hør musikken)")
        print("   [4] Åpne spillmappen i Explorer")
        print("   [5] Avslutt")
        print("------------------------------------------------------------------------")
        choice = input(" Tast inn et valg (1-5): ").strip()

        if choice == "1":
            play_game()
        elif choice == "2":
            launch_ue()
        elif choice == "3":
            play_music()
        elif choice == "4":
            open_folder()
        elif choice == "5":
            print("\nHa det bra!")
            break
        else:
            print("\nUgyldig valg.")
            time.sleep(1)

if __name__ == "__main__":
    main()
