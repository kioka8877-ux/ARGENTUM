#!/usr/bin/env python3
"""
F03_AQUILA — Frégate composite
Aquila Mortis : l'assemblage final avant le Champion

Input  : frames/styled/ + assets/terrain.svg + config LEDGER
Output : frames/final/ + preview/ (3 frames) pour PORTE II
"""

import json
import sys
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import cv2
except ImportError:
    print("[AQUILA] ERREUR : pip install opencv-python")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
LEDGER_PATH = ROOT / "ARGENTUM_LEDGER.json"
FRAMES_STYLED = ROOT / "frames" / "styled"
FRAMES_FINAL = ROOT / "frames" / "final"
FRAMES_PREVIEW = FRAMES_FINAL / "preview"
TERRAIN_SVG = ROOT / "assets" / "terrain.svg"
TERRAIN_CACHE = ROOT / "assets" / "terrain_cache.png"

PREVIEW_COUNT = 3


def load_ledger():
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(ledger):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)


def update_ledger_status(status, frames_count=None, error=None):
    ledger = load_ledger()
    ledger["artefacts"]["F03_AQUILA"]["statut"] = status
    if frames_count is not None:
        ledger["artefacts"]["F03_AQUILA"]["frames_count"] = frames_count
    if error:
        ledger["artefacts"]["F03_AQUILA"]["error"] = error
    ledger["session_courante"]["phase"] = "F03_AQUILA"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    save_ledger(ledger)


# ─── Terrain ─────────────────────────────────────────────────────────────────


def render_terrain_svg(width, height):
    """
    Rend le terrain.svg en PNG à la dimension exacte de la frame.
    Tente cairosvg, sinon dessine programmatiquement avec cv2.
    Cache dans assets/terrain_cache.png.
    """
    # Vérifier cache valide
    if TERRAIN_CACHE.exists():
        cached = cv2.imread(str(TERRAIN_CACHE))
        if cached is not None and cached.shape[1] == width and cached.shape[0] == height:
            return cached

    terrain = None

    # Essai cairosvg
    if TERRAIN_SVG.exists():
        try:
            import cairosvg
            png_bytes = cairosvg.svg2png(
                url=str(TERRAIN_SVG),
                output_width=width,
                output_height=height
            )
            arr = np.frombuffer(png_bytes, dtype=np.uint8)
            terrain = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"[AQUILA] cairosvg indisponible ({e}), rendu cv2 utilisé")

    # Fallback : terrain dessiné par cv2
    if terrain is None:
        terrain = draw_terrain_cv2(width, height)

    cv2.imwrite(str(TERRAIN_CACHE), terrain)
    print(f"[AQUILA] Terrain rendu et mis en cache ({width}×{height})")
    return terrain


def draw_terrain_cv2(width, height):
    """Terrain de football minimal dessiné avec cv2 — fallback sans cairosvg."""
    img = np.zeros((height, width, 3), dtype=np.uint8)

    # Pelouse verte
    img[:, :] = (68, 125, 58)  # BGR vert

    # Bandes alternées
    stripe_w = width // 10
    for i in range(10):
        if i % 2 == 1:
            x1 = i * stripe_w
            x2 = min(x1 + stripe_w, width)
            img[:, x1:x2] = (52, 115, 45)

    w, h = float(width), float(height)

    def sc(x, y):
        return (int(x / 120.0 * w), int(y / 80.0 * h))

    WHITE = (255, 255, 255)
    t = max(1, int(width / 800))

    # Contour
    cv2.rectangle(img, sc(0, 0), sc(120, 80), WHITE, t)
    # Ligne médiane
    cv2.line(img, sc(60, 0), sc(60, 80), WHITE, t)
    # Cercle central
    r_circle = int(9.15 / 120.0 * w)
    cv2.circle(img, sc(60, 40), r_circle, WHITE, t)
    cv2.circle(img, sc(60, 40), max(2, t), WHITE, -1)
    # Surface gauche
    cv2.rectangle(img, sc(0, 18), sc(16.5, 62), WHITE, t)
    cv2.rectangle(img, sc(0, 30.34), sc(5.5, 49.66), WHITE, t)
    cv2.circle(img, sc(11, 40), max(2, t), WHITE, -1)
    # Surface droite
    cv2.rectangle(img, sc(103.5, 18), sc(120, 62), WHITE, t)
    cv2.rectangle(img, sc(114.5, 30.34), sc(120, 49.66), WHITE, t)
    cv2.circle(img, sc(109, 40), max(2, t), WHITE, -1)
    # Buts
    cv2.rectangle(img, sc(-2, 34.16), sc(0, 45.84), (200, 200, 200), t)
    cv2.rectangle(img, sc(120, 34.16), sc(122, 45.84), (200, 200, 200), t)

    return img


# ─── Composite ───────────────────────────────────────────────────────────────


def blend_styled_over_terrain(terrain, styled):
    """
    Fusionne la frame stylisée sur le terrain.
    Les zones noires (contours) et colorées de styled remplacent le terrain.
    Le terrain transparaît légèrement pour garder la texture de pelouse.
    """
    if terrain.shape[:2] != styled.shape[:2]:
        styled = cv2.resize(styled, (terrain.shape[1], terrain.shape[0]))

    # Masque zones sombres (contours) dans la frame stylisée
    gray_styled = cv2.cvtColor(styled, cv2.COLOR_BGR2GRAY)
    _, dark_mask = cv2.threshold(gray_styled, 30, 255, cv2.THRESH_BINARY_INV)

    # Blend : 70% styled + 30% terrain pour les zones claires
    # 100% styled pour les contours noirs
    alpha = 0.70
    blended = cv2.addWeighted(styled, alpha, terrain, 1 - alpha, 0)

    # Restituer les contours noirs purs
    blended[dark_mask > 0] = styled[dark_mask > 0]

    return blended


def composite_frame(styled_path, terrain, config, frame_num):
    """
    Pipeline composite sur une frame :
    1. Flip horizontal (si configuré)
    2. Blend styled + terrain
    """
    img = cv2.imread(str(styled_path))
    if img is None:
        return None

    # 1. Flip horizontal
    if config.get("flip_horizontal", True):
        img = cv2.flip(img, 1)

    # 2. Composite avec terrain
    result = blend_styled_over_terrain(terrain, img)

    return result


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    print("[AQUILA] ═══ Frégate F03 — Démarrage ═══")

    if not LEDGER_PATH.exists():
        print(f"[AQUILA] ERREUR : LEDGER introuvable → {LEDGER_PATH}")
        sys.exit(1)

    ledger = load_ledger()

    # Vérification prérequis F02
    f02_status = ledger["artefacts"]["F02_ANSGAR"]["statut"]
    if f02_status != "DONE":
        print(f"[AQUILA] ERREUR : F02_ANSGAR statut = '{f02_status}' — lancer ansgar.py d'abord.")
        sys.exit(1)

    # Vérification PORTE I validée
    porte1 = ledger["portes"]["PORTE_I"]["statut"]
    if porte1 != "VALIDEE":
        print(f"[AQUILA] ERREUR : PORTE I statut = '{porte1}' — Champion doit valider avant F03.")
        sys.exit(1)

    update_ledger_status("EN_COURS")

    frames = sorted(FRAMES_STYLED.glob("frame_*.png"))
    if not frames:
        print(f"[AQUILA] ERREUR : aucune frame dans {FRAMES_STYLED}")
        update_ledger_status("ERREUR", error="frames_styled_vides")
        sys.exit(1)

    print(f"[AQUILA] {len(frames)} frames à composer")

    config = ledger.get("config", {})
    config.setdefault("flip_horizontal", True)

    flip_str = "OUI" if config["flip_horizontal"] else "NON"
    print(f"[AQUILA] Flip horizontal : {flip_str}")

    FRAMES_FINAL.mkdir(parents=True, exist_ok=True)
    FRAMES_PREVIEW.mkdir(parents=True, exist_ok=True)

    # Lire une frame pour connaître les dimensions
    sample = cv2.imread(str(frames[0]))
    if sample is None:
        print("[AQUILA] ERREUR : impossible de lire la première frame")
        update_ledger_status("ERREUR", error="frame_illisible")
        sys.exit(1)

    h, w = sample.shape[:2]
    terrain = render_terrain_svg(w, h)

    done = 0
    errors = 0

    for i, frame_path in enumerate(frames):
        frame_num = i + 1
        result = composite_frame(frame_path, terrain, config, frame_num)

        if result is None:
            errors += 1
            continue

        cv2.imwrite(str(FRAMES_FINAL / frame_path.name), result)
        done += 1

        if frame_num <= PREVIEW_COUNT:
            cv2.imwrite(str(FRAMES_PREVIEW / frame_path.name), result)

        if done % 50 == 0:
            print(f"[AQUILA] {done}/{len(frames)}...")

    if done == 0:
        update_ledger_status("ERREUR", error="zero_frames_produites")
        sys.exit(1)

    # LEDGER final + déclenchement PORTE II
    ledger = load_ledger()
    ledger["artefacts"]["F03_AQUILA"]["statut"] = "DONE"
    ledger["artefacts"]["F03_AQUILA"]["frames_count"] = done
    ledger["session_courante"]["phase"] = "PORTE_II"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    ledger["portes"]["PORTE_II"]["statut"] = "EN_ATTENTE_VALIDATION"
    save_ledger(ledger)

    print(f"[AQUILA] ✓ {done} frames → frames/final/")
    if errors:
        print(f"[AQUILA] ⚠ {errors} frames en erreur (ignorées)")
    print(f"[AQUILA] ✓ {min(done, PREVIEW_COUNT)} frames preview → frames/final/preview/")
    print(f"[AQUILA] ═══ F03 terminée — PORTE II en attente Champion ═══")


if __name__ == "__main__":
    main()
