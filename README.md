# 🩸 Blodig oktober - Norsk Autotune Hotel

Spillet er nå fullstendig fikset, gjort offline/standalone og **spillbart direkte på din datamaskin** med ferdige launchere!

---

## 🎮 Slik starter du og spiller

Du har nå tre enkle måter å starte på direkte fra mappen:

### 1. 🚀 Spill med ett klikk:
👉 **Dobbeltklikk på `Play_Game.bat`**
- Starter den lokale spillserveren automatisk.
- Åpner spillet umiddelbart i et rent, dedikert vindu (Edge App / nettleser).
- Du spawner direkte i **Kælder (Basement)** med fullt utstyr:
  - 1 000 000 Blodmynter
  - Våpen: Machete, Kniv, Pistol
  - Drugs & Dyrking: Weedfrø, Vannkanne, Weed, Jointpapir, Blunt wraps, Joints, Blunts, THC-A Joints, Lighter
  - Musikk: Walkman og alle 4 autotune CD-singler (Kravle, Leo Legit, Yung Xware, Lemonade) + Hele albummet
  - Diverse: Burgere, Forbindinger, Mystery Boxes, Nøkler, Hakke
- Full interaksjon: Knivstikking for blod (`stab.wav`), røyking av joints med 2x fart og buff-effekter, dør-navigasjon til The Stage (konsert), Butikken, Gaderne (PvP) og Minerne.

### 2. 🎛️ Full Launcher-meny:
👉 **Dobbeltklikk på `Start_Launcher.bat`**
- Gir deg en interaktiv meny med valg for å starte spillet, åpne prosjektet i Unreal Engine 5.8, høre på låtene i Jukeboxen eller åpne filene.

### 3. 🛠️ Åpne i Unreal Engine 5.8:
👉 **Dobbeltklikk på `Launch_Unreal_5.8.bat`**
- Åpner `BlodigOktober.uproject` direkte i Unreal Editor 5.8 med Top-Down isometrisk styring, navigasjons-mesh og importerte lydspor og teksturer.

---

## 📂 Nøkkelfiler i prosjektet

- `Play_Game.bat`: 1-klikks oppstart av spillet
- `Start_Launcher.bat`: Meny-launcher (`launcher.py`)
- `Launch_Unreal_5.8.bat`: Starter Unreal Engine 5.8
- `server.py`: Lokal spillserver med støtte for Edge App-vindu
- `play.html` / `index.html`: Spillklienten
- `assets/index-offline.js`: Den patched og fullt spillbare offline spillmotoren
- `BlodigOktober/`: Det komplette Unreal Engine 5.8-prosjektet
- `music/`: Autentiske autotune rap-låter i MP3
- `sfx/`: OSRS lydeffekter (stab, coins, doors, picks, light)
