#!/usr/bin/env python3
"""
F04_KRANSE — Frégate d'encodage
Chapter Master Emmrich Kranse : livre le résultat final

Input  : frames/final/frame_*.png + config LEDGER
Output : output/ARGENTUM_[timestamp].mp4 + mise à jour LEDGER
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
LEDGER_PATH = ROOT / "ARGENTUM_LEDGER.json"
FRAMES_FINAL = ROOT / "frames" / "final"
OUTPUT_DIR = ROOT / "output"
AUDIO_PATH = ROOT / "assets" / "audio.mp3"


def load_ledger():
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(ledger):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)


def update_ledger_status(status, error=None):
    ledger = load_ledger()
    ledger["artefacts"]["F04_KRANSE"]["statut"] = status
    if error:
        ledger["artefacts"]["F04_KRANSE"]["error"] = error
    ledger["session_courante"]["phase"] = "F04_KRANSE"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    save_ledger(ledger)


def get_video_duration(path):
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_format", str(path)
    ], capture_output=True, text=True)
    if result.returncode != 0:
        return None
    data = json.loads(result.stdout)
    return float(data.get("format", {}).get("duration", 0))


def encode_silent(frames_pattern, output_path, fps):
    """Assemble les frames en MP4 muet."""
    result = subprocess.run([
        "ffmpeg", "-y",
        "-framerate", str(fps),
        "-i", str(frames_pattern),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-crf", "18",
        "-preset", "slow",
        str(output_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[KRANSE] ERREUR ffmpeg encode :\n{result.stderr[-800:]}")
        return False
    return True


def mux_audio(video_path, audio_path, output_path):
    """Mixe audio sur la vidéo muette — coupe à la durée vidéo."""
    result = subprocess.run([
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[KRANSE] ERREUR ffmpeg audio mux :\n{result.stderr[-400:]}")
        return False
    return True


def main():
    print("[KRANSE] ═══ Frégate F04 — Démarrage ═══")

    if not LEDGER_PATH.exists():
        print(f"[KRANSE] ERREUR : LEDGER introuvable → {LEDGER_PATH}")
        sys.exit(1)

    ledger = load_ledger()

    # Vérification prérequis F03
    f03_status = ledger["artefacts"]["F03_AQUILA"]["statut"]
    if f03_status != "DONE":
        print(f"[KRANSE] ERREUR : F03_AQUILA statut = '{f03_status}' — lancer aquila.py d'abord.")
        sys.exit(1)

    # Vérification PORTE II validée
    porte2 = ledger["portes"]["PORTE_II"]["statut"]
    if porte2 != "VALIDEE":
        print(f"[KRANSE] ERREUR : PORTE II statut = '{porte2}' — Champion doit valider avant F04.")
        sys.exit(1)

    update_ledger_status("EN_COURS")

    # Frames finales
    frames = sorted(FRAMES_FINAL.glob("frame_*.png"))
    if not frames:
        print(f"[KRANSE] ERREUR : aucune frame dans {FRAMES_FINAL}")
        update_ledger_status("ERREUR", error="frames_final_vides")
        sys.exit(1)

    # Cohérence avec F01
    f01_count = ledger["artefacts"]["F01_VIGILIS"].get("frames_count")
    if f01_count and len(frames) != f01_count:
        print(f"[KRANSE] AVERTISSEMENT : {len(frames)} frames finales vs {f01_count} ingérées (F01)")

    print(f"[KRANSE] {len(frames)} frames à encoder")

    config = ledger.get("config", {})
    fps = config.get("fps_output", 12)
    print(f"[KRANSE] FPS output : {fps}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    frames_pattern = FRAMES_FINAL / "frame_%04d.png"
    silent_path = OUTPUT_DIR / f"ARGENTUM_{timestamp}_silent.mp4"
    final_path = OUTPUT_DIR / f"ARGENTUM_{timestamp}.mp4"

    # Encodage vidéo muette
    print("[KRANSE] Encodage vidéo...")
    if not encode_silent(frames_pattern, silent_path, fps):
        update_ledger_status("ERREUR", error="encode_echoue")
        sys.exit(1)

    # Audio optionnel
    if AUDIO_PATH.exists():
        print(f"[KRANSE] Audio détecté → {AUDIO_PATH.name}")
        if mux_audio(silent_path, AUDIO_PATH, final_path):
            silent_path.unlink()
            print("[KRANSE] Audio mixé")
        else:
            print("[KRANSE] Mux audio échoué — livraison vidéo muette")
            silent_path.rename(final_path)
    else:
        silent_path.rename(final_path)
        print("[KRANSE] Pas d'audio — livraison muette (déposer audio.mp3 dans assets/ pour la prochaine fois)")

    # Métadonnées finales
    duration = get_video_duration(final_path)
    size_mb = round(final_path.stat().st_size / (1024 * 1024), 2)

    print(f"[KRANSE] Durée : {duration:.1f}s — Taille : {size_mb} MB")

    # LEDGER final
    ledger = load_ledger()
    ledger["artefacts"]["F04_KRANSE"]["statut"] = "DONE"
    ledger["artefacts"]["F04_KRANSE"]["fichier_mp4"] = final_path.name
    ledger["artefacts"]["F04_KRANSE"]["chemin"] = str(final_path)
    ledger["mp4_final"] = str(final_path)
    ledger["session_courante"]["phase"] = "TERMINE"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    ledger["portes"]["PORTE_II"]["statut"] = "FRANCHIE"
    save_ledger(ledger)

    print(f"[KRANSE] ✓ MP4 livré → {final_path.name}")
    print(f"[KRANSE] ✓ LEDGER mis à jour — phase : TERMINE")
    print(f"[KRANSE] ═══ F04 terminée — ARGENTUM complet ═══")
    print(f"\n{'═'*50}")
    print(f"  LIVRAISON : output/{final_path.name}")
    print(f"{'═'*50}")


if __name__ == "__main__":
    main()
