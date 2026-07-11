# F03_AQUILA — Tracking Frégate
**Nom canon :** Aquila Mortis (étendard de mort des Silver Templars)  
**Rôle :** Composite — assemble terrain + frames stylisées + annotations  
**Statut :** A FORGER

---

## Mission

Prendre chaque frame stylisée de `frames/styled/`.  
Appliquer le flip horizontal (effet miroir anti-droits).  
Assembler avec le fond terrain et les éventuelles annotations tactiques.  
Sortir les frames finales dans `frames/final/`.

---

## Input

```
frames/styled/frame_*.png
assets/terrain.svg (fond statique)
ARGENTUM_LEDGER.json → config.flip_horizontal
```

## Output

```
frames/final/frame_0001.png
...
ARGENTUM_LEDGER.json → artefacts.F03_AQUILA.statut = "DONE"
```

---

## Opérations (ordre obligatoire)

### 1. Flip horizontal
Si `config.flip_horizontal = true` : miroir gauche/droite sur chaque frame.  
Objectif : rompre la reconnaissance algorithmique des séquences de match.

### 2. Composite terrain
Placer le fond terrain (SVG rendu en PNG) sous la frame stylisée.  
Le terrain est statique — rendu une seule fois en PNG au démarrage.

### 3. Annotations optionnelles
Si `config.annotations = true` :  
- Vecteurs de déplacement (flèches)
- Zone de pitch highlights
Ces éléments ajoutent la "valeur éducative" qui blinde la monétisation.

---

## Stack

- Python 3
- Pillow (PIL)
- CairoSVG (pour rendre terrain.svg en PNG)

---

## Règles

1. Terrain rendu une seule fois → mis en cache dans `assets/terrain_cache.png`
2. Le flip ne s'applique pas au terrain (il serait identique flippé)
3. Un sample de 3 frames composites est produit pour la PORTE II

---

## PORTE II — déclenchée après cette frégate

Le Champion reçoit les 3 frames composites.  
Il valide l'assemblage final ou donne des instructions.  
Tant que non validée : F04_KRANSE ne démarre pas.

---

## Fichier principal

`aquila.py` — A FORGER
