#!/usr/bin/env python3
"""
ORCHESTRATEUR ARGENTUM
Nerf central — connaît l'état de chaque frégate, gère l'ordre et les reprises.

Usage :
  python orchestrateur.py <video_source>   # lancement complet
  python orchestrateur.py --status         # état du pipeline
  python orchestrateur.py --valider-porte1 # valider PORTE I
  python orchestrateur.py --valider-porte2 # valider PORTE II
  python orchestrateur.py --reprendre      # reprendre depuis dernière porte franchie
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
LEDGER_PATH = ROOT / "ARGENTUM_LEDGER.json"


def load_ledger():
    with open(LEDGER_PATH, "r") as f:
        return json.load(f)


def save_ledger(ledger):
    with open(LEDGER_PATH, "w") as f:
        json.dump(ledger, f, indent=2, ensure_ascii=False)


def run_fregate(script, label):
    print(f"\n{'─'*50}")
    print(f"  LANCEMENT {label}")
    print(f"{'─'*50}")
    result = subprocess.run(
        [sys.executable, str(ROOT / script)],
        cwd=str(ROOT)
    )
    return result.returncode == 0


def show_status():
    ledger = load_ledger()
    art = ledger["artefacts"]
    portes = ledger["portes"]
    phase = ledger["session_courante"].get("phase", "—")

    print("\n╔══════════════════════════════════════╗")
    print("║         ARGENTUM — État pipeline      ║")
    print("╠══════════════════════════════════════╣")
    print(f"║  Phase courante : {phase:<19}║")
    print("╠══════════════════════════════════════╣")

    for key, label in [
        ("F01_VIGILIS", "F01 VIGILIS  "),
        ("F02_ANSGAR",  "F02 ANSGAR   "),
        ("F03_AQUILA",  "F03 AQUILA   "),
        ("F04_KRANSE",  "F04 KRANSE   "),
    ]:
        statut = art[key]["statut"]
        count = art[key].get("frames_count", "—")
        print(f"║  {label} {statut:<12} frames:{str(count):<6}║")

    print("╠══════════════════════════════════════╣")
    p1 = portes["PORTE_I"]["statut"]
    p2 = portes["PORTE_II"]["statut"]
    print(f"║  PORTE I  : {p1:<26}║")
    print(f"║  PORTE II : {p2:<26}║")
    print("╠══════════════════════════════════════╣")
    mp4 = ledger.get("mp4_final")
    if mp4:
        print(f"║  MP4 : {Path(mp4).name:<31}║")
    else:
        print(f"║  MP4 : en attente{' '*19}║")
    print("╚══════════════════════════════════════╝\n")


def valider_porte(num):
    ledger = load_ledger()
    key = f"PORTE_{['I','II'][num-1]}"
    ledger["portes"][key]["statut"] = "VALIDEE"
    ledger["portes"][key]["validee_par"] = "Champion"
    ledger["portes"][key]["date"] = datetime.now().isoformat()
    save_ledger(ledger)
    print(f"[ORCHESTRATEUR] PORTE {['I','II'][num-1]} validée.")


def run_pipeline(source=None):
    ledger = load_ledger()

    if source:
        ledger["input"]["video_source"] = source
        save_ledger(ledger)

    # F01
    if ledger["artefacts"]["F01_VIGILIS"]["statut"] != "DONE":
        args = [sys.executable, str(ROOT / "F01_VIGILIS" / "vigilis.py")]
        if source:
            args.append(source)
        print("\n── F01 VIGILIS ─────────────────────────")
        result = subprocess.run(args, cwd=str(ROOT))
        if result.returncode != 0:
            print("[ORCHESTRATEUR] F01 échouée. Arrêt.")
            return False
    else:
        print("[ORCHESTRATEUR] F01 déjà DONE — passage direct F02")

    # F02
    if ledger["artefacts"]["F02_ANSGAR"]["statut"] != "DONE":
        if not run_fregate("F02_ANSGAR/ansgar.py", "F02 ANSGAR"):
            print("[ORCHESTRATEUR] F02 échouée. Arrêt.")
            return False
    else:
        print("[ORCHESTRATEUR] F02 déjà DONE — passage direct PORTE I")

    # PORTE I
    ledger = load_ledger()
    if ledger["portes"]["PORTE_I"]["statut"] != "VALIDEE":
        print("\n╔══════════════════════════════════════════════════╗")
        print("║  PORTE I — EN ATTENTE VALIDATION CHAMPION         ║")
        print("║  Vérifier : frames/styled/preview/                ║")
        print("║  Puis : python orchestrateur.py --valider-porte1  ║")
        print("╚══════════════════════════════════════════════════╝")
        return True

    # F03
    if ledger["artefacts"]["F03_AQUILA"]["statut"] != "DONE":
        if not run_fregate("F03_AQUILA/aquila.py", "F03 AQUILA"):
            print("[ORCHESTRATEUR] F03 échouée. Arrêt.")
            return False
    else:
        print("[ORCHESTRATEUR] F03 déjà DONE — passage direct PORTE II")

    # PORTE II
    ledger = load_ledger()
    if ledger["portes"]["PORTE_II"]["statut"] != "VALIDEE":
        print("\n╔══════════════════════════════════════════════════╗")
        print("║  PORTE II — EN ATTENTE VALIDATION CHAMPION        ║")
        print("║  Vérifier : frames/final/preview/                 ║")
        print("║  Puis : python orchestrateur.py --valider-porte2  ║")
        print("╚══════════════════════════════════════════════════╝")
        return True

    # F04
    if not run_fregate("F04_KRANSE/kranse.py", "F04 KRANSE"):
        print("[ORCHESTRATEUR] F04 échouée. Arrêt.")
        return False

    show_status()
    return True


def main():
    args = sys.argv[1:]

    if not args:
        print(__doc__)
        sys.exit(0)

    if "--status" in args:
        show_status()
    elif "--valider-porte1" in args:
        valider_porte(1)
    elif "--valider-porte2" in args:
        valider_porte(2)
    elif "--reprendre" in args:
        run_pipeline()
    else:
        source = args[0]
        run_pipeline(source)


if __name__ == "__main__":
    main()
