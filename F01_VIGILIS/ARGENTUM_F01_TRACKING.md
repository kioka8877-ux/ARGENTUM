# F01_VIGILIS — Tracking Frégate
**Nom canon :** Vigilis (planète de surveillance, Psychic Awakening)  
**Rôle :** Ingestion — extrait les frames PNG depuis la vidéo source  
**Statut :** A FORGER

---

## Mission

Recevoir une vidéo source (MP4, URL ou chemin local).  
Extraire chaque frame en PNG dans `frames/raw/`.  
Écrire les métadonnées dans le LEDGER.

---

## Input

```
ARGENTUM_LEDGER.json → input.video_source
```

## Output

```
frames/raw/frame_0001.png
frames/raw/frame_0002.png
...
ARGENTUM_LEDGER.json → artefacts.F01_VIGILIS.statut = "DONE"
ARGENTUM_LEDGER.json → artefacts.F01_VIGILIS.frames_count = N
```

---

## Stack

- Python 3
- FFmpeg (subprocess)
- Commande : `ffmpeg -i input.mp4 frames/raw/frame_%04d.png`

---

## Règles

1. Ne jamais modifier la vidéo source
2. Si le dossier `frames/raw/` contient déjà des frames → demander confirmation avant d'écraser
3. Écrire dans le LEDGER avant de terminer, même en cas d'erreur partielle

---

## Fichier principal

`vigilis.py` — A FORGER
