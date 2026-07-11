# F02_ANSGAR — Tracking Frégate
**Nom canon :** Ancient Ansgar (porteur de l'étendard Aquila Mortis, Silver Templars)  
**Rôle :** Stylisation — applique le style vectoriel plat + effets artisanaux  
**Statut :** A FORGER

---

## Mission

Prendre chaque frame PNG brute de `frames/raw/`.  
Appliquer la transformation visuelle qui donne l'illusion du dessin à la main.  
Sortir les frames stylisées dans `frames/styled/`.

---

## Input

```
frames/raw/frame_*.png
ARGENTUM_LEDGER.json → config (palette, boiling_intensity)
```

## Output

```
frames/styled/frame_0001.png
...
ARGENTUM_LEDGER.json → artefacts.F02_ANSGAR.statut = "DONE"
```

---

## Transformations appliquées (ordre obligatoire)

### 1. Postérisation (aplats de couleur)
Quantification des couleurs : réduire la palette à 4-8 couleurs max.  
Chaque pixel est forcé vers la couleur la plus proche dans la palette.

### 2. Détection de contours (trait noir)
Filtre Laplacien ou Sobel sur la frame brute.  
Les zones de contraste élevé → pixel noir.  
Seuil paramétrable dans le LEDGER (`config.contour_threshold`).

### 3. Boiling effect (tremblement artisanal)
Injecter un déplacement aléatoire faible (+/- 1-2 pixels) sur les contours.  
Seed différent à chaque frame → le trait "vit".  
Intensité : `config.boiling_intensity` (0.0 à 1.0).

---

## Stack

- Python 3
- Pillow (PIL)
- NumPy
- OpenCV (cv2) pour Sobel/Laplacien

---

## Règles

1. Chaque frame est indépendante — parallélisable
2. La seed du boiling doit être fonction du numéro de frame (reproductible)
3. Les 5 premières frames sont copiées dans `frames/styled/preview/` pour la PORTE I

---

## PORTE I — déclenchée après cette frégate

Le Champion reçoit les 5 frames preview.  
Il valide le rendu ou donne des instructions (ajuster palette, contours, boiling).  
Tant que non validée : F03_AQUILA ne démarre pas.

---

## Fichier principal

`ansgar.py` — A FORGER
