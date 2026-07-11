# F04_KRANSE — Tracking Frégate
**Nom canon :** Chapter Master Emmrich Kranse (Silver Templars)  
**Rôle :** Encode — assemble et livre le MP4 final  
**Statut :** A FORGER

---

## Mission

Prendre toutes les frames finales de `frames/final/`.  
Encoder en MP4 à 12 FPS (look animation artisanale).  
Livrer le fichier dans `output/`.  
Mettre à jour le LEDGER avec le chemin du fichier final.

---

## Input

```
frames/final/frame_*.png
ARGENTUM_LEDGER.json → config.fps_output (12)
ARGENTUM_LEDGER.json → input.video_source (pour l'audio si besoin)
```

## Output

```
output/ARGENTUM_[timestamp].mp4
ARGENTUM_LEDGER.json → mp4_final = chemin absolu
ARGENTUM_LEDGER.json → artefacts.F04_KRANSE.statut = "DONE"
```

---

## Opérations FFmpeg

### 1. Assemblage des frames en vidéo muette
```bash
ffmpeg -framerate 12 -i frames/final/frame_%04d.png \
       -c:v libx264 -pix_fmt yuv420p \
       output/ARGENTUM_[timestamp].mp4
```

### 2. Ajout audio (optionnel)
Si un fichier audio est fourni dans `assets/audio.mp3` :
```bash
ffmpeg -i output/ARGENTUM_[timestamp].mp4 \
       -i assets/audio.mp3 \
       -c:v copy -c:a aac -shortest \
       output/ARGENTUM_[timestamp]_audio.mp4
```

---

## Stack

- FFmpeg (subprocess Python)

---

## Règles

1. Ne jamais écraser un MP4 existant — ajouter un timestamp unique
2. Vérifier que le nombre de frames en input correspond à `artefacts.F01_VIGILIS.frames_count`
3. Logger la durée finale et la taille du fichier dans le LEDGER

---

## Livraison

Après encodage réussi :  
- Le Champion reçoit le chemin du fichier dans le sandbox
- Le LEDGER est marqué `mp4_final` avec le chemin absolu

---

## Fichier principal

`kranse.py` — A FORGER
