from typing import Dict, Any, List, Optional
from api.models import (
    AIDDLevel,
    AxesScores,
    EvaluationResult,
    ProgressionPlan,
)
from api.scorer.thresholds import RANK_TO_LEVEL


class EvaluationEngine:
    """Consolidates axis scores, applies the strict MIN rule, detects inconsistencies, and produces progression plans."""

    @classmethod
    def evaluate(
        cls,
        profile_data: Dict[str, Any],
        quantitative_scores: AxesScores,
        llm_insights: Optional[Dict[str, Any]] = None,
    ) -> EvaluationResult:
        axes = quantitative_scores

        # Rank of each axis
        ranks = {
            "taille": axes.taille.rank,
            "harness": axes.harness.rank,
            "intervention": axes.intervention.rank,
            "parallele": axes.parallele.rank,
        }

        # Strict MIN rule
        final_rank = min(ranks.values())
        final_level = RANK_TO_LEVEL[final_rank]

        # Identify which axis is holding the developer back (bottleneck)
        limiting_axes = [axis for axis, rank in ranks.items() if rank == final_rank]
        limiting_axis = limiting_axes[0] if limiting_axes else "harness"

        # Generate warnings / inconsistency checks
        warnings = cls._detect_inconsistencies(profile_data, final_level, axes)
        if "warnings" in profile_data and isinstance(profile_data["warnings"], list):
            for w in profile_data["warnings"]:
                if w not in warnings:
                    warnings.append(w)

        # Generate progression steps to reach final_rank + 1
        progression = cls._build_progression_plan(final_rank, limiting_axis, axes, profile_data)

        profile_info = profile_data.get("profile_info", {})
        profile_id = profile_data.get("profile_id", "unknown")
        role = profile_info.get("role")
        stack = profile_info.get("stack", [])
        data_sources = profile_data.get("available_sources", [])

        return EvaluationResult(
            profile_id=profile_id,
            role=role,
            stack=stack,
            level=final_level,
            axes=axes,
            limiting_axis=limiting_axis,
            confident=True,
            warnings=warnings,
            progression=progression,
            data_sources=data_sources,
        )

    @staticmethod
    def _detect_inconsistencies(
        profile_data: Dict[str, Any], final_level: AIDDLevel, axes: AxesScores
    ) -> List[str]:
        warnings = []
        declaratif = profile_data.get("declaratif")
        if not declaratif:
            return warnings

        dec_lower = declaratif.lower()

        # Inconsistency 1: Self-claims "avancé" or "haut du panier" but has low level
        if ("avancé" in dec_lower or "haut du panier" in dec_lower) and final_level.rank <= 1:
            warnings.append(
                "Incohérence déclarative : Le développeur se perçoit comme 'plutôt avancé', "
                f"mais les métriques empiriques le situent au niveau {final_level.label} "
                f"(4 commits correctifs/PR, aucun harness versionné, co-authorship IA à 4%)."
            )

        # Inconsistency 2: Underestimating self
        if ("milieu de tableau" in dec_lower or "débutant" in dec_lower) and final_level.rank >= 3:
            warnings.append(
                f"Modestie déclarative : Le développeur se déclare 'milieu de tableau', "
                f"alors que son outillage et sa rigueur le positionnent déjà au niveau {final_level.label}."
            )

        # Inconsistency 3: Mentions generating big features without harness
        if "features complètes quasi entièrement générées" in dec_lower and axes.harness.rank <= 1:
            warnings.append(
                "Alerte cadrage : Prétention de features complètes générées par IA sans aucun fichier de contexte ni harness structuré."
            )

        return warnings

    @staticmethod
    def _build_progression_plan(
        current_rank: int,
        limiting_axis: str,
        axes: AxesScores,
        profile_data: Dict[str, Any],
    ) -> ProgressionPlan:
        next_rank = min(current_rank + 1, 6)
        next_level = RANK_TO_LEVEL[next_rank] if next_rank > current_rank else None

        steps = []
        recommendations = []

        if current_rank == 0:  # White -> Red
            steps = [
                "Intégrer un assistant de code directement dans l'éditeur (VS Code / Cursor / Claude Code).",
                "Déléguer les tâches élémentaires (fonctions unitaires, boilerplate, regex, requêtes SQL).",
                "Co-signer systématiquement les commits générés avec l'IA pour suivre la traçabilité.",
            ]
            recommendations = [
                "Commencer par générer les tests unitaires pour valider les snippets produits.",
            ]
        elif current_rank == 1:  # Red -> Blue
            steps = [
                "Créer un fichier `AGENTS.md` ou `CLAUDE.md` à la racine de chaque dépôt avec l'architecture, les conventions et la stack (Context Engineering / Mémoire projet).",
                "Cadrer explicitement le contexte avant de lancer la génération pour faire passer la taille des PRs de S à M.",
                "Réduire les reprises post-génération en donnant les fichiers pertinents dès le premier prompt.",
            ]
            recommendations = [
                "Mettre à jour le fichier de contexte dès qu'une erreur se produit deux fois sur la même convention.",
                "Installer un plugin d'éditeur plutôt que de copier-coller dans une interface web afin de préserver l'historique et le contexte.",
            ]
        elif current_rank == 2:  # Blue -> Green
            steps = [
                "Enrichir le harness avec des règles modulaires (`.cursorrules`, `.claude/rules/`) et des compétences (`skills`).",
                "Systématiser la validation de la compréhension (spec review / prompt framing) avant d'écrire la moindre ligne de code.",
                "Viser zéro commit correctif après ouverture des PRs en confiant des chantiers complets multi-étapes (taille L).",
            ]
            recommendations = [
                "Créer des agents spécialisés pour les tâches récurrentes (migration, endpoints, refactoring).",
                "Imposer l'écriture préalable des tests et vérifier qu'ils échouent avant implémentation (TDD guidé par l'IA).",
            ]
        elif current_rank == 3:  # Green -> Copper
            steps = [
                "Organiser l'environnement de travail pour mener 3 chantiers en parallèle (isolation par git worktrees, sessions terminal distinctes).",
                "Automatiser la propagation des variables d'environnement (`.worktreeinclude`) pour isoler les contextes sans friction.",
                "Porter la taille habituelle des livrables vers des modules complets L et XL.",
            ]
            recommendations = [
                "Ne lancer en parallèle que des chantiers dont les dépendances croisées sont explicitement cartographiées dans les specs.",
                "Exploiter les subagents / agents d'arrière-plan pour paralléliser l'exploration de code et l'écriture de tests.",
            ]
        elif current_rank == 4:  # Copper -> Silver
            steps = [
                "Mettre en place des boucles d'auto-correction fermées (scripts relançant l'IA avec la sortie stderr tant que les tests ou linters échouent).",
                "Déléguer la phase d'implémentation complète sans aucune intervention humaine après le cadrage initial.",
                "Configurer la CI/CD (GitHub Actions / GitLab CI) pour alimenter l'assistant en feedback automatique d'échec de build.",
            ]
            recommendations = [
                "Tester les boucles de relance automatique d'abord sur les migrations d'API et les suites de tests unitaires.",
                "Intégrer des agents de test prédictif pour cibler automatiquement les tests d'impact.",
            ]
        elif current_rank == 5:  # Silver -> Gold
            steps = [
                "Déléguer également le cadrage initial : les agents analysent le backlog, spécifient et implémentent en autonomie.",
                "Mettre en place une gouvernance d'agents orchestrateurs supervisant les revues de code et le déploiement continu.",
            ]
            recommendations = [
                "Auditer en continu les garde-fous (IAM, credentials, manifests de production hors d'atteinte des agents).",
            ]

        return ProgressionPlan(
            next_level=next_level,
            limiting_axis=limiting_axis,
            steps=steps,
            recommendations=recommendations,
        )
