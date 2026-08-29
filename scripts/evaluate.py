#!/usr/bin/env python3
"""CLI Tool for Mouvement-Tech AIDD Evaluation Engine."""

import sys
import os
import json
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from api.collectors.profile import ProfileCollector
from api.collectors.github import GitHubCollector
from api.scorer.algo import QuantitativeScorer
from api.scorer.llm import LLMQualitativeJudge
from api.scorer.fusion import EvaluationEngine


def evaluate_target(target: str, repo_url: str = None):
    print(f"[*] Évaluation AIDD de la cible : {target}...")
    
    profiles_base = root_dir.parent / "laivel-up-sujet" / "profiles"
    candidate_profile = profiles_base / target
    
    profile_data = None
    import asyncio
    if candidate_profile.is_dir():
        profile_data = ProfileCollector.load_profile(candidate_profile)
    elif Path(target).is_dir():
        profile_data = ProfileCollector.load_profile(Path(target))
    elif target.startswith("http://") or target.startswith("https://") or "github.com" in target:
        gh = GitHubCollector()
        profile_data = asyncio.run(gh.fetch_full_profile_from_repo(target))
    else:
        print(f"[!] Cible introuvable : {target}")
        sys.exit(1)

    quant_scores = QuantitativeScorer.score_all(profile_data)
    llm_judge = LLMQualitativeJudge()
    llm_insights = asyncio.run(llm_judge.analyze(profile_data))
    result = EvaluationEngine.evaluate(profile_data, quant_scores, llm_insights)

    print("\n" + "=" * 60)
    print(f"🎯 RÉSULTAT ÉVALUATION : {result.profile_id.upper()}")
    print(f"🏷️  Rôle : {result.role or 'N/A'} | Stack : {', '.join(result.stack or [])}")
    print(f"🏆 Niveau Global Attribué : {result.level.label} (Rang {result.level.rank})")
    print(f"⚠️  Axe Limitant (Goulot)   : {result.limiting_axis.upper()}")
    print("=" * 60)
    
    from api.scorer.thresholds import RANK_TO_LEVEL
    print("\n📊 SCORES PAR AXE :")
    for axis_name, axis_score in result.axes.model_dump().items():
        lvl_label = RANK_TO_LEVEL[axis_score['rank']].label
        print(f"  • {axis_name.capitalize():<14} : {lvl_label:<10} (Rang {axis_score['rank']})")
        print(f"    Justification : {axis_score['evidence']}")

    if result.warnings:
        print("\n🚨 AVERTISSEMENTS / INCOHÉRENCES DÉCLARATIVES :")
        for w in result.warnings:
            print(f"  ⚠️  {w}")

    if result.progression:
        next_lvl = result.progression.next_level.label if result.progression.next_level else 'MAX'
        print(f"\n🚀 PLAN DE PROGRESSION VERS {next_lvl} :")
        for i, step in enumerate(result.progression.steps, 1):
            print(f"  {i}. {step}")
        if result.progression.recommendations:
            print("  💡 Recommandations :")
            for rec in result.progression.recommendations:
                print(f"     - {rec}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/evaluate.py <profile_name_or_path_or_repo_url> [repo_url_override]")
        print("Examples:")
        print("  python scripts/evaluate.py perceval")
        print("  python scripts/evaluate.py arthur")
        print("  python scripts/evaluate.py https://github.com/ai-driven-dev/laivel-up")
        sys.exit(0)
    
    target_arg = sys.argv[1]
    repo_override = sys.argv[2] if len(sys.argv) > 2 else None
    evaluate_target(target_arg, repo_override)