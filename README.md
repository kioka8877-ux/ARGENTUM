# ARGENTUM
**Media Pipeline Architecture — Doctrine VERBUM**

Pipeline d'animation vectorielle automatisé.  
Input : vidéo source (action de match réel)  
Output : MP4 style dessin à la main, 12 FPS

---

## Nomenclature Silver Templars

| Nom | Origine | Rôle |
|-----|---------|------|
| ARGENTUM | Latin "argent" — honore le Chapitre | Projet |
| VIGILIS | Planète Vigilus | F01 — Ingestion |
| ANSGAR | Ancient Ansgar, porteur des couleurs | F02 — Stylisation |
| AQUILA | Aquila Mortis, l'étendard | F03 — Composite |
| KRANSE | Chapter Master Emmrich Kranse | F04 — Encode |

---

## Architecture

```
F01_VIGILIS   → extrait frames PNG depuis vidéo source
F02_ANSGAR    → applique style vectoriel plat + boiling effect
     ↓
◆ PORTE I — validation visuelle Champion
     ↓
F03_AQUILA    → composite terrain + frames + annotations
     ↓
◆ PORTE II — validation assemblage Champion
     ↓
F04_KRANSE    → encode MP4 final 12 FPS
```

---

## Statut

ALPHA — structure posée, frégates à forger.
