#!/usr/bin/env python3
"""
F02_ANSGAR — Frégate de stylisation
Ancient Ansgar : porteur des couleurs et du standard

Input  : frames/raw/frame_*.png + config ARGENTUM_LEDGER.json
Output : frames/styled/frame_*.png + preview/ (5 frames) pour PORTE I
"""

import json
import sys
import numpy as np
from pathlib import Path
from datetime import datetime

try:
    import cv2
except ImportError:
    print("[ANSGAR] ERREUR : pip install opencv-python")
    sys.exit(1)

ROOT = Path(__file__).parent.parent
LEDGER_PATH = ROOT / "ARGENTUM_LEDGER.json"
FRAMES_RAW = ROOT / "frames" / "raw"
FRAMES_STYLED = ROOT / "frames" / "styled"
FRAMES_PREVIEW = FRAMES_STYLED / "preview"

PREVIEW_COUNT = 5


def load_ledger():
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(ledger):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)


def update_ledger_status(status, frames_count=None, error=None):
    ledger = load_ledger()
    ledger["artefacts"]["F02_ANSGAR"]["statut"] = status
    if frames_count is not None:
        ledger["artefacts"]["F02_ANSGAR"]["frames_count"] = frames_count
    if error:
        ledger["artefacts"]["F02_ANSGAR"]["error"] = error
    ledger["session_courante"]["phase"] = "F02_ANSGAR"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    save_ledger(ledger)


# ─── Transformations ────────────────────────────────────────────────────────


def posterize(img_bgr, steps=6):
    """
    Quantifie la palette de couleurs en N paliers.
    Transforme les dégradés en aplats — look dessin vectoriel.
    """
    factor = 255.0 / steps
    quantized = (np.floor(img_bgr.astype(np.float32) / factor) * factor)
    return np.clip(quantized, 0, 255).astype(np.uint8)


def detect_edges(img_bgr, threshold=40):
    """
    Détecte les contours par Laplacien sur image floutée.
    Retourne un masque binaire : 255 = contour, 0 = fond.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Léger flou avant Laplacien pour réduire le bruit de compression vidéo
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)
    lap = cv2.Laplacian(blurred, cv2.CV_64F, ksize=3)
    lap_abs = np.uint8(np.clip(np.abs(lap), 0, 255))
    _, edges = cv2.threshold(lap_abs, threshold, 255, cv2.THRESH_BINARY)
    return edges


def apply_boiling(edges, frame_num, intensity=0.3):
    """
    Simule le tremblement naturel du trait dessiné à la main.
    Déplace les pixels de contour de ±amp pixels selon un RNG seedé sur frame_num.
    Seed fixe par frame → résultat reproductible mais différent à chaque frame.
    """
    if intensity <= 0:
        return edges

    rng = np.random.default_rng(seed=int(frame_num))
    h, w = edges.shape
    amp = max(1, int(round(intensity * 2.5)))

    shift_y = rng.integers(-amp, amp + 1, size=(h, w)).astype(np.float32)
    shift_x = rng.integers(-amp, amp + 1, size=(h, w)).astype(np.float32)

    grid_y, grid_x = np.mgrid[0:h, 0:w]
    map_y = np.clip(grid_y + shift_y, 0, h - 1).astype(np.float32)
    map_x = np.clip(grid_x + shift_x, 0, w - 1).astype(np.float32)

    return cv2.remap(edges, map_x, map_y, cv2.INTER_NEAREST)


def stylize_frame(frame_path, frame_num, config):
    """
    Pipeline complet sur une frame :
    1. Postérisation → aplats de couleur
    2. Détection de contours → masque Laplacien
    3. Boiling effect → tremblement artisanal sur les contours
    4. Fusion → contours noirs sur image postérisée
    """
    img = cv2.imread(str(frame_path))
    if img is None:
        return None

    steps = config.get("posterize_steps", 6)
    threshold = config.get("contour_threshold", 40)
    boiling = config.get("boiling_intensity", 0.3)

    posterized = posterize(img, steps=steps)
    edges = detect_edges(img, threshold=threshold)
    edges_boiled = apply_boiling(edges, frame_num, intensity=boiling)

    result = posterized.copy()
    result[edges_boiled > 0] = [0, 0, 0]

    return result


# ─── Main ────────────────────────────────────────────────────────────────────


def main():
    print("[ANSGAR] ═══ Frégate F02 — Démarrage ═══")

    if not LEDGER_PATH.exists():
        print(f"[ANSGAR] ERREUR : LEDGER introuvable → {LEDGER_PATH}")
        sys.exit(1)

    ledger = load_ledger()

    # Vérification prérequis F01
    f01_status = ledger["artefacts"]["F01_VIGILIS"]["statut"]
    if f01_status != "DONE":
        print(f"[ANSGAR] ERREUR : F01_VIGILIS statut = '{f01_status}' — lancer vigilis.py d'abord.")
        sys.exit(1)

    update_ledger_status("EN_COURS")

    frames = sorted(FRAMES_RAW.glob("frame_*.png"))
    if not frames:
        print(f"[ANSGAR] ERREUR : aucune frame dans {FRAMES_RAW}")
        update_ledger_status("ERREUR", error="frames_raw_vides")
        sys.exit(1)

    print(f"[ANSGAR] {len(frames)} frames à styliser")

    config = ledger.get("config", {})
    config.setdefault("posterize_steps", 6)
    config.setdefault("contour_threshold", 40)
    config.setdefault("boiling_intensity", 0.3)

    print(f"[ANSGAR] Config → steps={config['posterize_steps']} | "
          f"threshold={config['contour_threshold']} | "
          f"boiling={config['boiling_intensity']}")

    FRAMES_STYLED.mkdir(parents=True, exist_ok=True)
    FRAMES_PREVIEW.mkdir(parents=True, exist_ok=True)

    done = 0
    errors = 0

    for i, frame_path in enumerate(frames):
        frame_num = i + 1
        result = stylize_frame(frame_path, frame_num, config)

        if result is None:
            errors += 1
            continue

        cv2.imwrite(str(FRAMES_STYLED / frame_path.name), result)
        done += 1

        if frame_num <= PREVIEW_COUNT:
            cv2.imwrite(str(FRAMES_PREVIEW / frame_path.name), result)

        if done % 50 == 0:
            print(f"[ANSGAR] {done}/{len(frames)}...")

    if done == 0:
        update_ledger_status("ERREUR", error="zero_frames_produites")
        sys.exit(1)

    # LEDGER final + déclenchement PORTE I
    ledger = load_ledger()
    ledger["artefacts"]["F02_ANSGAR"]["statut"] = "DONE"
    ledger["artefacts"]["F02_ANSGAR"]["frames_count"] = done
    ledger["session_courante"]["phase"] = "PORTE_I"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    ledger["portes"]["PORTE_I"]["statut"] = "EN_ATTENTE_VALIDATION"
    save_ledger(ledger)

    print(f"[ANSGAR] ✓ {done} frames → frames/styled/")
    if errors:
        print(f"[ANSGAR] ⚠ {errors} frames en erreur (ignorées)")
    print(f"[ANSGAR] ✓ {min(done, PREVIEW_COUNT)} frames preview → frames/styled/preview/")
    print(f"[ANSGAR] ═══ F02 terminée — PORTE I en attente Champion ═══")


if __name__ == "__main__":
    main()
