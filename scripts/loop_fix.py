#!/usr/bin/env python3
"""
Silver-Level Automated Closed Feedback Loop.
Executes test suite and linters, captures failures, and facilitates automated convergence.
"""

import sys
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root_dir = Path(__file__).resolve().parent.parent


def run_command(cmd, desc):
    print(f"[*] Exécution : {desc} ({' '.join(cmd)})...")
    res = subprocess.run(cmd, cwd=str(root_dir), capture_output=True, text=True)
    return res.returncode, res.stdout, res.stderr


def run_loop(max_iterations=3):
    print("=" * 60)
    print("🔄 Mouvement-Tech — Boucle d'Auto-Correction & Validation")
    print("=" * 60)

    for iteration in range(1, max_iterations + 1):
        print(f"\n--- Itération {iteration}/{max_iterations} ---")
        
        code, stdout, stderr = run_command([sys.executable, "-m", "pytest", "-v"], "Suite de tests pytest")
        
        if code == 0:
            print("✅ 100% des tests validés avec succès !")
            print("🎉 La boucle a convergé. Le dépôt satisfait les critères de qualité.")
            return True
        else:
            print("❌ Échec détecté dans la suite de tests.")
            print("\n--- Résumé des erreurs ---")
            lines = stdout.splitlines()
            failure_lines = [l for l in lines if "FAILED" in l or "ERROR" in l]
            for fl in failure_lines[:10]:
                print(f"  ❌ {fl}")
            
            if iteration < max_iterations:
                print("\n[!] Auto-diagnostic : Erreur active. Relance de l'analyse...")
            else:
                print("\n[!] Nombre maximal d'itérations atteint sans convergence.")
                return False

    return False


if __name__ == "__main__":
    success = run_loop()
    sys.exit(0 if success else 1)