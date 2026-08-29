#!/usr/bin/env python3
"""
Worktree Helper for Parallel Development (Axe 4 - En Parallèle).
Facilitates managing multiple concurrent git worktrees with shared environment files.
"""

import sys
import subprocess
import shutil
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root_dir = Path(__file__).resolve().parent.parent


def list_worktrees():
    print("[*] Worktrees Git actifs :")
    res = subprocess.run(["git", "worktree", "list"], cwd=str(root_dir), capture_output=True, text=True)
    print(res.stdout if res.stdout else "Aucun worktree secondaire.")


def create_worktree(branch_name, path_name):
    target_path = root_dir.parent / path_name
    print(f"[*] Création du worktree sur la branche '{branch_name}' dans '{target_path}'...")
    res = subprocess.run(["git", "worktree", "add", "-b", branch_name, str(target_path)], cwd=str(root_dir), capture_output=True, text=True)
    if res.returncode == 0:
        print("✅ Worktree créé avec succès.")
        include_file = root_dir / ".worktreeinclude"
        if include_file.is_file():
            with open(include_file, "r") as f:
                for line in f:
                    item = line.strip()
                    if item and not item.startswith("#"):
                        src = root_dir / item
                        dst = target_path / item
                        if src.is_file():
                            shutil.copy2(src, dst)
                            print(f"  -> Synchronisé : {item}")
    else:
        print(f"❌ Erreur lors de la création : {res.stderr}")


if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] == "list":
        list_worktrees()
    elif sys.argv[1] == "add" and len(sys.argv) >= 4:
        create_worktree(sys.argv[2], sys.argv[3])
    else:
        print("Usage:")
        print("  python scripts/worktree_setup.py list")
        print("  python scripts/worktree_setup.py add <branch_name> <folder_name>")