#!/usr/bin/env python3
"""
Audits the AIDD Harness completeness of Mouvement-Tech repository itself.
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root_dir = Path(__file__).resolve().parent.parent

checks = [
    ("Context Engineering - CLAUDE.md", root_dir / "CLAUDE.md"),
    ("Context Engineering - AGENTS.md", root_dir / "AGENTS.md"),
    ("Context Engineering - .cursorrules", root_dir / ".cursorrules"),
    ("Knowledge Base - architecture.md", root_dir / "docs" / "knowledge" / "architecture.md"),
    ("Knowledge Base - criteres-aidd.md", root_dir / "docs" / "knowledge" / "criteres-aidd.md"),
    ("Knowledge Base - decisions.md (ADRs)", root_dir / "docs" / "knowledge" / "decisions.md"),
    ("Knowledge Base - methode.md (Livrable)", root_dir / "docs" / "methode.md"),
    ("Behavior - Rules (.claude/rules)", root_dir / ".claude" / "rules" / "architecture.md"),
    ("Behavior - Skills (.claude/skills)", root_dir / ".claude" / "skills" / "evaluate-profile" / "SKILL.md"),
    ("Loops (Silver) - Feedback Runner", root_dir / "scripts" / "loop_fix.py"),
    ("Loops (Silver) - GitHub Actions CI", root_dir / ".github" / "workflows" / "ci.yml"),
    ("Concurrency - .worktreeinclude", root_dir / ".worktreeinclude"),
    ("Concurrency - Worktree Helper", root_dir / "scripts" / "worktree_setup.py"),
]

print("=" * 60)
print("🛡️  AUDIT DU HARNAIS AIDD — MOUVEMENT-TECH")
print("=" * 60)

passed = 0
for name, path in checks:
    exists = path.exists()
    status = "✅ PRÉSENT" if exists else "❌ MANQUANT"
    if exists:
        passed += 1
    print(f"  {status:<14} | {name}")

print("=" * 60)
score = (passed / len(checks)) * 100
print(f"Score de complétude du harnais : {score:.1f}% ({passed}/{len(checks)} briques)")
if passed == len(checks):
    print("🏆 Statut : Harnais de niveau SILVER / GOLD complet.")
else:
    print("⚠️  Statut : Harnais incomplet.")
print("=" * 60)