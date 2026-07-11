# ARGENTUM — Tracking Global du Projet
**Statut :** ALPHA — Architecture posée, frégates à forger  
**Champion :** Operator  
**Date de création :** 2026-07-11  
**Doctrine :** VERBUM  

---

## Objectif

Pipeline d'animation vectorielle automatisé.  
Input : vidéo source (action de match réel)  
Output : MP4 style dessin à la main, 12 FPS, prêt upload

---

## Les Silver Templars — Nomenclature canonique

| Nom canon | Rôle dans la Chapter | Rôle dans ARGENTUM |
|-----------|---------------------|-------------------|
| ARGENTUM | Le projet — latin "argent", honore les Silver Templars | Nom du projet |
| KRANSE | Chapter Master Emmrich Kranse — livre le résultat final | F04_ENCODE |
| ANSGAR | Ancient Ansgar — porteur du standard, des couleurs | F02_STYLIZE |
| VIGILIS | La planète Vigilus — surveillance, première observation | F01_INGEST |
| AQUILA | Aquila Mortis — l'étendard, l'assemblage final | F03_COMPOSITE |

---

## Architecture des Frégates

```
F01_VIGILIS     → Ingestion — extrait les frames PNG depuis la vidéo source
F02_ANSGAR      → Stylisation — applique le style vectoriel plat + boiling
F03_AQUILA      → Composite — assemble terrain + personnages + annotations
F04_KRANSE      → Encode — FFmpeg, 12fps, flip, MP4 final
```

---

## Portes (Gates)

| Porte | Après | Ce que le Champion valide |
|-------|-------|--------------------------|
| PORTE I | F02_ANSGAR | 5 frames stylisées — le rendu visuel est bon ? |
| PORTE II | F03_AQUILA | Preview composite — l'assemblage est correct ? |

---

## Ledger

Source de vérité : `ARGENTUM_LEDGER.json`  
Chaque frégate lit le ledger en entrée et y écrit son output avant de passer la porte.

---

## État des frégates

| Frégate | Fichier principal | Statut |
|---------|------------------|--------|
| F01_VIGILIS | vigilis.py | A FORGER |
| F02_ANSGAR | ansgar.py | A FORGER |
| F03_AQUILA | aquila.py | A FORGER |
| F04_KRANSE | kranse.py | A FORGER |
| ORCHESTRATEUR | orchestrateur.py | A FORGER |
| CUSTOS | custos.py | A FORGER |
