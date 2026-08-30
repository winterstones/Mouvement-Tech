from typing import Dict, Any, Optional
from api.models import AxisScore, AxesScores
from api.scorer.thresholds import RANK_TO_LEVEL


class QuantitativeScorer:
    """Computes deterministic quantitative scores for the 4 AIDD axes based on empirical metrics."""

    @classmethod
    def score_all(cls, profile_data: Dict[str, Any]) -> AxesScores:
        git_activity = profile_data.get("git_activity", {})
        repo_context = profile_data.get("repo_context_files", {})
        session = profile_data.get("session")

        taille_score = cls.score_taille(git_activity)
        harness_score = cls.score_harness(git_activity, repo_context)
        intervention_score = cls.score_intervention(git_activity, session)
        parallele_score = cls.score_parallele(git_activity)

        return AxesScores(
            taille=taille_score,
            harness=harness_score,
            intervention=intervention_score,
            parallele=parallele_score,
        )

    @staticmethod
    def score_taille(git_activity: Dict[str, Any]) -> AxisScore:
        prs = git_activity.get("pull_requests", {})
        total = prs.get("total", 0)
        dist = prs.get("size_distribution", {})
        median_lines = prs.get("median_lines_changed", 0)

        if total == 0:
            return AxisScore(
                level=RANK_TO_LEVEL[0].id,
                rank=0,
                confident=True,
                evidence="Aucune pull request ou activité livrée répertoriée.",
                details={"total_prs": 0, "median_lines": 0},
            )

        xs = dist.get("xs", 0)
        s = dist.get("s", 0)
        m = dist.get("m", 0)
        l = dist.get("l", 0)
        xl = dist.get("xl", 0)

        small_share = (xs + s) / total
        medium_share = m / total
        large_share = (l + xl) / total
        xl_share = xl / total

        # Check L-XL dominance
        if (large_share >= 0.40 and large_share >= medium_share) or large_share >= 0.45 or median_lines >= 350:
            if xl_share >= 0.14 or median_lines >= 500 or (large_share >= 0.60):
                rank = 4  # L-XL (Copper+)
                level_id = RANK_TO_LEVEL[4].id
                evidence = (
                    f"Features L et XL dominantes ({l} L, {xl} XL sur {total} livrables, {large_share:.0%}), "
                    f"médiane de {median_lines} lignes modifiées par livrable."
                )
            else:
                rank = 3  # L (Green)
                level_id = RANK_TO_LEVEL[3].id
                evidence = (
                    f"Features L de complexité élevée dominantes ({l} L, {xl} XL sur {total} livrables, {large_share:.0%}), "
                    f"médiane de {median_lines} lignes modifiées par livrable."
                )
        # Check M dominance
        elif medium_share >= 0.35 or (medium_share >= small_share and median_lines >= 120):
            rank = 2  # M (Blue)
            level_id = RANK_TO_LEVEL[2].id
            evidence = (
                f"Features M de complexité moyenne dominantes ({m} M sur {total} livrables, {medium_share:.0%}), "
                f"médiane de {median_lines} lignes."
            )
        # S dominance
        else:
            rank = 1  # S (Red)
            level_id = RANK_TO_LEVEL[1].id
            evidence = (
                f"Features S ou XS dominantes ({xs + s}/{total} livrables S/XS, {small_share:.0%}), "
                f"médiane de {median_lines} lignes."
            )

        return AxisScore(
            level=level_id,
            rank=rank,
            confident=True,
            evidence=evidence,
            details={
                "total_prs": total,
                "median_lines": median_lines,
                "distribution": dist,
            },
        )

    @staticmethod
    def score_harness(
        git_activity: Dict[str, Any], repo_context_files: Dict[str, str] = None
    ) -> AxisScore:
        ctx = git_activity.get("context_files", {})
        repo_files = repo_context_files or {}

        agents_md = ctx.get("agents_md", False) or any(
            k.upper() in ["AGENTS.MD", "CLAUDE.MD", ".CURSORRULES", "PROMPT.MD", "CONVENTIONS.MD", ".AIDER.CONF.YML", ".WORKTREEINCLUDE"] or k.startswith(".aider")
            for k in repo_files.keys()
        )
        rules_count = ctx.get("rules_count", 0)
        skills_count = ctx.get("skills_count", 0)
        hooks_count = ctx.get("hooks_count", 0)
        agents_count = ctx.get("agents_count", 0)
        has_auto_loops = ctx.get("has_auto_loops", False)
        last_updated = ctx.get("last_updated")

        total_behavior_items = rules_count + skills_count + hooks_count + agents_count

        if not agents_md and total_behavior_items == 0:
            assistant_usage = git_activity.get("assistant_usage", {})
            if assistant_usage.get("sessions_per_week", 0) > 0 or assistant_usage.get("declared_tools"):
                rank = 1  # Red harness (prompts directs sans context engineering)
                level_id = RANK_TO_LEVEL[1].id
                evidence = "Prompts directs uniquement. Aucun fichier de contexte projet versionné."
            else:
                rank = 0
                level_id = RANK_TO_LEVEL[0].id
                evidence = "Aucun fichier de contexte (AGENTS.md, rules) ni harnais IA identifié."
        elif agents_md and total_behavior_items == 0:
            rank = 2
            level_id = RANK_TO_LEVEL[2].id
            evidence = (
                f"Context engineering en place (AGENTS.md / CLAUDE.md / configuration IA présente et mise à jour le {last_updated or 'récemment'}), "
                "mais sans règles, agents ni compétences spécialisées versionnées."
            )
        elif (agents_md or total_behavior_items >= 2) and has_auto_loops:
            if agents_md and (skills_count >= 2 or agents_count >= 2):
                rank = 5  # Silver harness
                level_id = RANK_TO_LEVEL[5].id
                evidence = (
                    "Context engineering + Behavior (agents, rules) + Boucles automatiques de convergence en place."
                )
            else:
                rank = 4  # Copper harness (auto-loops / validation suite / hooks)
                level_id = RANK_TO_LEVEL[4].id
                evidence = (
                    f"Harnais avancé avec boucles automatiques : Convergence CI/tests, {skills_count} compétences "
                    f"et {rules_count + hooks_count} règles/hooks en place."
                )
        elif agents_md and total_behavior_items > 0:
            if skills_count >= 3 or agents_count >= 2:
                rank = 4  # Copper harness (multi-skills, multi-agents, worktrees)
                level_id = RANK_TO_LEVEL[4].id
                evidence = (
                    f"Harnais multi-compétences versionné : {skills_count} skills, {agents_count} agents, "
                    f"{rules_count} règles et {hooks_count} hooks documentés."
                )
            else:
                rank = 3  # Green harness
                level_id = RANK_TO_LEVEL[3].id
                evidence = (
                    f"Context engineering + Behavior : {rules_count} règles, {skills_count} compétences, "
                    f"{hooks_count} hooks et {agents_count} agents versionnés (mis à jour le {last_updated or 'récent'})."
                )
        elif not agents_md and total_behavior_items > 0:
            if skills_count >= 2 or agents_count >= 1 or total_behavior_items >= 3 or has_auto_loops:
                rank = 3  # Green harness
                level_id = RANK_TO_LEVEL[3].id
                evidence = (
                    f"Outillage comportemental structuré : {total_behavior_items} éléments versionnés "
                    f"(règles/skills/hooks CI) assurant le cadrage et l'automatisation."
                )
            else:
                rank = 2  # Blue harness
                level_id = RANK_TO_LEVEL[2].id
                evidence = f"Harnais partiel : {total_behavior_items} règles/hooks versionnés sans mémoire globale formalisée."
        else:
            rank = 1
            level_id = RANK_TO_LEVEL[1].id
            evidence = "Éléments de contexte partiels sans architecture formalisée."

        return AxisScore(
            level=level_id,
            rank=rank,
            confident=True,
            evidence=evidence,
            details={
                "agents_md": agents_md,
                "rules_count": rules_count,
                "skills_count": skills_count,
                "hooks_count": hooks_count,
                "agents_count": agents_count,
                "last_updated": last_updated,
                "has_auto_loops": has_auto_loops,
            },
        )

    @staticmethod
    def score_intervention(
        git_activity: Dict[str, Any], session_text: Optional[str] = None
    ) -> AxisScore:
        prs = git_activity.get("pull_requests", {})
        total_prs = prs.get("total", 1)
        median_corrections = prs.get("median_correction_commits_after_open", 0)
        merged_no_edit = prs.get("merged_without_human_edit_after_open", 0)
        reverted = prs.get("reverted", 0)
        ci_failure_rate = git_activity.get("ci", {}).get("failure_rate", 0.0)
        ai_ratio = git_activity.get("commits", {}).get("ai_coauthored_ratio", 0.0)

        merged_no_edit_ratio = merged_no_edit / total_prs if total_prs else 0

        # Rank 1 (Red): Frequent post-hoc corrections (median >= 3 commits)
        if median_corrections >= 3:
            rank = 1
            level_id = RANK_TO_LEVEL[1].id
            evidence = (
                f"Intervention humaine fréquente après coup : médiane de {median_corrections} commits "
                f"correctifs par PR après ouverture ({reverted} PRs annulées, {ci_failure_rate:.0%} d'échec CI)."
            )
        # Rank 2 (Blue): Moderate post-hoc corrections (median == 2 commits)
        elif median_corrections == 2:
            rank = 2
            level_id = RANK_TO_LEVEL[2].id
            evidence = (
                f"Intervention modérée après coup : médiane de {median_corrections} commits correctifs par PR, "
                f"{merged_no_edit_ratio:.0%} de PRs mergées sans reprise humaine."
            )
        # Rank 3/4/5 (Green / Copper / Silver): Few or no corrections (median <= 1)
        elif median_corrections <= 1:
            # Silver requires 0 human edits after opening and near zero CI failure
            if median_corrections == 0 and merged_no_edit_ratio >= 0.85 and ci_failure_rate <= 0.02:
                rank = 5  # Silver
                level_id = RANK_TO_LEVEL[5].id
                evidence = (
                    f"Aucune intervention humaine après cadrage ({merged_no_edit_ratio:.0%} des PRs sans edit, "
                    f"0 commit correctif, {ci_failure_rate:.0%} d'échec CI)."
                )
            elif (ai_ratio >= 0.80 or merged_no_edit_ratio >= 0.70 or prs.get("median_lines_changed", 0) >= 350) and ci_failure_rate <= 0.08:
                rank = 4  # Copper
                level_id = RANK_TO_LEVEL[4].id
                evidence = (
                    f"Délégation de haute autonomie : {int(ai_ratio*100)}% de co-authorship IA, "
                    f"médiane de {median_corrections} commit correctif par livrable ({ci_failure_rate:.0%} d'échec CI)."
                )
            else:
                # Rank 3 for Green
                rank = 3
                level_id = RANK_TO_LEVEL[rank].id
                evidence = (
                    f"Intervention ciblée aux étapes clés : presque aucun commit correctif (médiane de {median_corrections} par PR), "
                    f"{merged_no_edit} PRs intégrées directement sans retouche ({ci_failure_rate:.0%} d'échec CI)."
                )
        else:
            rank = 1
            level_id = RANK_TO_LEVEL[1].id
            evidence = f"Médiane de {median_corrections} commits de correction par PR."

        return AxisScore(
            level=level_id,
            rank=rank,
            confident=True,
            evidence=evidence,
            details={
                "median_correction_commits": median_corrections,
                "merged_without_human_edit_ratio": round(merged_no_edit_ratio, 2),
                "reverted": reverted,
                "ci_failure_rate": ci_failure_rate,
            },
        )

    @staticmethod
    def score_parallele(git_activity: Dict[str, Any]) -> AxisScore:
        parallelism = git_activity.get("parallelism", {})
        median_branches = parallelism.get("median_concurrent_branches", 1)
        max_branches = parallelism.get("max_concurrent_branches", 1)

        if median_branches >= 3:
            rank = 4  # Satisfies Copper, Silver, Gold requirement (>= 3)
            level_id = RANK_TO_LEVEL[4].id
            evidence = (
                f"Multiples chantiers menés de front de manière habituelle : "
                f"médiane de {median_branches} branches simultanées (pic à {max_branches})."
            )
        elif median_branches >= 1:
            # 1 to 2 concurrent branches satisfies up to Green (rank 3)
            rank = 3
            level_id = RANK_TO_LEVEL[3].id
            evidence = (
                f"Un seul chantier principal mené de front de façon habituelle : "
                f"médiane de {median_branches} branche simultanée (pic à {max_branches})."
            )
        else:
            rank = 0
            level_id = RANK_TO_LEVEL[0].id
            evidence = "Aucune activité de branche parallèle répertoriée."

        return AxisScore(
            level=level_id,
            rank=rank,
            confident=True,
            evidence=evidence,
            details={
                "median_concurrent_branches": median_branches,
                "max_concurrent_branches": max_branches,
            },
        )
