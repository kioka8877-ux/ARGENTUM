#!/usr/bin/env python3
"""
F01_VIGILIS — Frégate d'ingestion
Planète Vigilus : surveillance et extraction

Input  : vidéo source (arg CLI ou ARGENTUM_LEDGER.json)
Output : frames PNG dans frames/raw/ + mise à jour LEDGER
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.parent
LEDGER_PATH = ROOT / "ARGENTUM_LEDGER.json"
FRAMES_RAW = ROOT / "frames" / "raw"


def load_ledger():
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(ledger):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)


def update_ledger_status(status, frames_count=None, error=None):
    ledger = load_ledger()
    ledger["artefacts"]["F01_VIGILIS"]["statut"] = status
    if frames_count is not None:
        ledger["artefacts"]["F01_VIGILIS"]["frames_count"] = frames_count
    if error:
        ledger["artefacts"]["F01_VIGILIS"]["error"] = error
    ledger["session_courante"]["phase"] = "F01_VIGILIS"
    ledger["session_courante"]["date"] = datetime.now().isoformat()
    save_ledger(ledger)


def get_video_source(ledger):
    if len(sys.argv) > 1:
        source = sys.argv[1]
        ledger["input"]["video_source"] = source
        save_ledger(ledger)
        return source
    return ledger.get("input", {}).get("video_source")


def download_video(url, dest_path):
    print(f"[VIGILIS] Téléchargement : {url}")

    # Essai yt-dlp (YouTube, TikTok, etc.)
    result = subprocess.run(
        ["yt-dlp", "-o", str(dest_path), "--no-playlist",
         "--merge-output-format", "mp4", url],
        capture_output=True, text=True
    )
    if result.returncode == 0 and dest_path.exists():
        return True

    # Fallback wget pour URL directe
    result = subprocess.run(
        ["wget", "-q", "-O", str(dest_path), url],
        capture_output=True, text=True
    )
    return result.returncode == 0 and dest_path.exists()


def get_video_info(video_path):
    result = subprocess.run([
        "ffprobe", "-v", "quiet",
        "-print_format", "json",
        "-show_streams", "-show_format",
        str(video_path)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        return None, None, None, None

    data = json.loads(result.stdout)
    fps = None
    duration = None
    src_w = None
    src_h = None

    for stream in data.get("streams", []):
        if stream.get("codec_type") == "video":
            r = stream.get("r_frame_rate", "25/1")
            num, den = r.split("/")
            fps = round(int(num) / max(int(den), 1), 2)
            src_w = stream.get("width")
            src_h = stream.get("height")
            break

    duration = float(data.get("format", {}).get("duration", 0))
    return fps, duration, src_w, src_h


def build_vf_filter(src_w, src_h, out_w, out_h):
    """Calcule le filtre ffmpeg -vf pour convertir la source au format cible."""
    if src_w is None or src_h is None:
        return f"scale={out_w}:{out_h}"

    src_ratio = src_w / src_h
    out_ratio = out_w / out_h

    if abs(src_ratio - out_ratio) < 0.02:
        # Même ratio : scale direct
        return f"scale={out_w}:{out_h}"

    if src_ratio > 1 and out_ratio < 1:
        # Source horizontale → sortie verticale : crop centré 9:16
        crop_w = f"ih*{out_w}/{out_h}"
        crop_x = f"(iw-ih*{out_w}/{out_h})/2"
        return f"crop={crop_w}:ih:{crop_x}:0,scale={out_w}:{out_h}"

    if src_ratio < 1 and out_ratio > 1:
        # Source verticale → sortie horizontale : crop centré 16:9
        crop_h = f"iw*{out_h}/{out_w}"
        crop_y = f"(ih-iw*{out_h}/{out_w})/2"
        return f"crop=iw:{crop_h}:0:{crop_y},scale={out_w}:{out_h}"

    # Même orientation, ratios différents : crop centré puis scale
    if src_ratio > out_ratio:
        crop_w = f"ih*{out_w}/{out_h}"
        return f"crop={crop_w}:ih:(iw-{crop_w})/2:0,scale={out_w}:{out_h}"
    else:
        crop_h = f"iw*{out_h}/{out_w}"
        return f"crop=iw:{crop_h}:0:(ih-{crop_h})/2,scale={out_w}:{out_h}"


def extract_frames(video_path, output_dir, vf_filter):
    output_dir.mkdir(parents=True, exist_ok=True)
    output_pattern = output_dir / "frame_%04d.png"

    print(f"[VIGILIS] Extraction → {output_dir}/")
    print(f"[VIGILIS] Filtre format : {vf_filter}")

    result = subprocess.run([
        "ffmpeg", "-i", str(video_path),
        "-vf", vf_filter,
        "-q:v", "2",
        str(output_pattern)
    ], capture_output=True, text=True)

    if result.returncode != 0:
        print(f"[VIGILIS] ERREUR ffmpeg :\n{result.stderr[-800:]}")
        return 0

    return len(list(output_dir.glob("frame_*.png")))


def main():
    print("[VIGILIS] ═══ Frégate F01 — Démarrage ═══")

    if not LEDGER_PATH.exists():
        print(f"[VIGILIS] ERREUR : LEDGER introuvable → {LEDGER_PATH}")
        sys.exit(1)

    ledger = load_ledger()
    update_ledger_status("EN_COURS")

    source = get_video_source(ledger)
    if not source:
        print("[VIGILIS] ERREUR : pas de source. Passer en arg : python vigilis.py <url_ou_chemin>")
        update_ledger_status("ERREUR", error="source_manquante")
        sys.exit(1)

    # Frames existantes → nettoyage
    if FRAMES_RAW.exists():
        existing = list(FRAMES_RAW.glob("frame_*.png"))
        if existing:
            print(f"[VIGILIS] {len(existing)} frames déjà présentes — nettoyage")
            for f in existing:
                f.unlink()

    is_url = source.startswith("http://") or source.startswith("https://")
    video_path = ROOT / "tmp_source.mp4"

    if is_url:
        if not download_video(source, video_path):
            print("[VIGILIS] ERREUR : téléchargement échoué")
            update_ledger_status("ERREUR", error="download_failed")
            sys.exit(1)
    else:
        video_path = Path(source)
        if not video_path.exists():
            print(f"[VIGILIS] ERREUR : fichier introuvable → {source}")
            update_ledger_status("ERREUR", error="fichier_introuvable")
            sys.exit(1)

    fps, duration, src_w, src_h = get_video_info(video_path)
    print(f"[VIGILIS] Vidéo : {fps} FPS — {duration:.1f}s — {src_w}×{src_h}")

    ledger = load_ledger()
    ledger["input"]["fps_source"] = fps
    ledger["input"]["duree_secondes"] = round(duration, 2) if duration else None
    ledger["input"]["source_width"] = src_w
    ledger["input"]["source_height"] = src_h
    save_ledger(ledger)

    config = ledger.get("config", {})
    out_w = config.get("output_width", 1080)
    out_h = config.get("output_height", 1920)
    out_fmt = config.get("output_format", "vertical")
    print(f"[VIGILIS] Format cible : {out_fmt} ({out_w}×{out_h})")

    vf_filter = build_vf_filter(src_w, src_h, out_w, out_h)
    frames_count = extract_frames(video_path, FRAMES_RAW, vf_filter)

    if is_url and video_path.exists():
        video_path.unlink()

    if frames_count == 0:
        update_ledger_status("ERREUR", error="extraction_echouee")
        sys.exit(1)

    update_ledger_status("DONE", frames_count=frames_count)

    print(f"[VIGILIS] ✓ {frames_count} frames → frames/raw/")
    print(f"[VIGILIS] ✓ LEDGER mis à jour")
    print(f"[VIGILIS] ═══ F01 terminée — ANSGAR peut démarrer ═══")


if __name__ == "__main__":
    main()
