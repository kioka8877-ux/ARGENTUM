# ARGENTUM — Cold Start
**LIS CE FICHIER EN PREMIER à chaque nouvelle session**

---

## Contexte en 3 lignes

Pipeline d'animation vectorielle "Ghost-Animator".  
Une vidéo source entre, un MP4 style dessin à la main sort.  
Le Champion valide à deux portes, le reste est automatique.

---

## Doctrine

VERBUM. Frégates étanches. Ledger nomade. Portes obligatoires.  
Si une frégate lâche : les artefacts des frégates précédentes survivent.  
On reprend depuis la dernière porte franchie.

---

## Nomenclature Silver Templars

- **ARGENTUM** = le projet (latin : argent, honore les Silver Templars)
- **VIGILIS** = F01 Ingest (planète Vigilus, surveillance)
- **ANSGAR** = F02 Stylize (Ancient Ansgar, porteur des couleurs)
- **AQUILA** = F03 Composite (Aquila Mortis, l'assemblage)
- **KRANSE** = F04 Encode (Chapter Master Kranse, livre le résultat)

---

## Flux Champion

```
Champion donne vidéo source
        ↓
VIGILIS  → frames PNG brutes
ANSGAR   → frames stylisées
    ↓
◆ PORTE I → Champion valide le rendu visuel
    ↓
AQUILA   → frames composites
    ↓
◆ PORTE II → Champion valide l'assemblage
    ↓
KRANSE   → MP4 final
Champion reçoit le fichier
```

---

## Fichiers clés

| Fichier | Rôle |
|---------|------|
| `ARGENTUM_LEDGER.json` | Source de vérité unique — ne jamais supprimer |
| `ARGENTUM_TRACKING.md` | État global du projet |
| `F01_VIGILIS/ARGENTUM_F01_TRACKING.md` | Spec frégate VIGILIS |
| `F02_ANSGAR/ARGENTUM_F02_TRACKING.md` | Spec frégate ANSGAR |
| `F03_AQUILA/ARGENTUM_F03_TRACKING.md` | Spec frégate AQUILA |
| `F04_KRANSE/ARGENTUM_F04_TRACKING.md` | Spec frégate KRANSE |

---

## Reprendre un travail interrompu

1. Lire `ARGENTUM_LEDGER.json` — trouver `derniere_porte_franchie`
2. Lire le tracking de la frégate concernée
3. Reprendre depuis l'artefact de la dernière porte
