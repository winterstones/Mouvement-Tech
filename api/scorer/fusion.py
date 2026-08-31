from typing import Dict, Any, List, Optional
from api.models import (
    AIDDLevel,
    AxesScores,
    EvaluationResult,
    ProgressionPlan,
    VibeRiskMetrics,
    ActionTicket,
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

        # Calculate Vibe-Coding Risk & AI Debt Index
        vibe_risk = cls._calculate_vibe_risk(axes, warnings, profile_data)

        # Analyze AST code health, technical debt & spaghetti architecture
        from api.analyzers.code_health import CodeHealthAnalyzer
        git_act = profile_data.get("git_activity", {})
        commits_data = git_act.get("commits", {})
        ai_ratio = commits_data.get("ai_coauthored_ratio", 0.0)
        has_harness = (axes.harness.rank >= 2)
        prs_data = git_act.get("pull_requests", {})
        correction_rate = float(prs_data.get("median_correction_commits_after_open", 0))
        code_files = profile_data.get("repo_context_files", {})
        
        code_health = CodeHealthAnalyzer.analyze_repository_or_files(
            files_dict=code_files,
            ai_ratio=ai_ratio,
            has_harness=has_harness,
            correction_commits_rate=correction_rate,
        )

        # Generate progression steps and Jira action tickets to reach final_rank + 1
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
            vibe_risk=vibe_risk,
            code_health=code_health,
            data_sources=data_sources,
        )

    @classmethod
    def _calculate_vibe_risk(
        cls, axes: AxesScores, warnings: List[str], profile_data: Dict[str, Any]
    ) -> VibeRiskMetrics:
        """Calculates the Vibe-Coding Risk Index and AI Debt Probability."""
        h_rank = axes.harness.rank
        i_rank = axes.intervention.rank
        
        # 1. Evaluate AI Exposure
        git_act = profile_data.get("git_activity") or {}
        commits_data = git_act.get("commits") or {}
        ai_ratio = commits_data.get("ai_coauthored_ratio", 0.0)
        assistant_usage = git_act.get("assistant_usage") or {}
        declared_tools = assistant_usage.get("declared_tools") or []
        sessions_pw = assistant_usage.get("sessions_per_week", 0)
        has_session = profile_data.get("session") is not None
        declaratif = (profile_data.get("declaratif") or "").lower()

        is_using_ai = (
            ai_ratio > 0.0
            or len(declared_tools) > 0
            or sessions_pw > 0
            or has_session
            or bool((git_act.get("context_files") or {}).get("agents_md"))
            or bool((git_act.get("context_files") or {}).get("rules_count", 0) > 0)
        )

        # If the developer does not use AI at all (traditional engineering Level 0 White), Vibe Coding Risk is strictly 0
        if not is_using_ai:
            return VibeRiskMetrics(
                risk_score=0,
                risk_level="Nul (Non exposé)",
                rework_ratio=0.0,
                context_coverage_detected=False,
                explanation="Aucun risque de vibe coding : développement logiciel traditionnel sans recours aux assistants IA (0% d'exposition IA).",
            )

        # 2. Base risk calculation for AI users
        risk_score = 50
        
        # Penalize lack of harness & high manual rework post-PR
        if h_rank <= 1:
            risk_score += 25
        elif h_rank >= 3:
            risk_score -= 25
            
        if i_rank <= 1:
            risk_score += 20
        elif i_rank >= 3:
            risk_score -= 25
            
        # Warning presence adds risk (declarative overconfidence)
        if any("Incohérence" in w or "Alerte" in w for w in warnings):
            risk_score += 15
            
        risk_score = max(5, min(95, risk_score))
        
        if risk_score >= 70:
            risk_level = "Élevé"
            rework_ratio = 0.75
            explanation = "Risque élevé de vibe coding : nombreuses reprises post-génération, absence de harness de contexte formalisé et dérive potentielle de la base de code."
        elif risk_score >= 35:
            risk_level = "Modéré"
            rework_ratio = 0.35
            explanation = "Risque modéré : contexte partiellement structuré mais des reprises manuelles subsistent."
        else:
            risk_level = "Faible"
            rework_ratio = 0.10
            explanation = "Risque très faible : ingénierie rigoureuse, harness structuré, zéro commit de panique et cadrage amont éprouvé."
            
        return VibeRiskMetrics(
            risk_score=risk_score,
            risk_level=risk_level,
            rework_ratio=rework_ratio,
            context_coverage_detected=(h_rank >= 2),
            explanation=explanation,
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
        from api.models import ActionTicket

        next_rank = min(current_rank + 1, 6)
        next_level = RANK_TO_LEVEL[next_rank] if next_rank > current_rank else None

        steps = []
        recommendations = []
        tickets: List[ActionTicket] = []

        if current_rank == 0:  # White -> Red
            steps = [
                "Intégrer un assistant de code directement dans l'éditeur (VS Code / Cursor / Claude Code).",
                "Déléguer les tâches élémentaires (fonctions unitaires, boilerplate, regex, requêtes SQL).",
                "Co-signer systématiquement les commits générés avec l'IA pour suivre la traçabilité.",
            ]
            recommendations = [
                "Commencer par générer les tests unitaires pour valider les snippets produits.",
            ]
            tickets = [
                ActionTicket(
                    ticket_id="AIDD-001",
                    title="Installer et configurer l'IDE assisté par IA (Cursor / Claude Code)",
                    axis="harness",
                    priority="High",
                    estimated_effort="2 heures",
                    target_level="Red",
                    definition_of_done="L'extension est active et génère au moins 3 snippets validés.",
                ),
                ActionTicket(
                    ticket_id="AIDD-002",
                    title="Mettre en place la signature Co-authored-by sur les commits assistés",
                    axis="intervention",
                    priority="Medium",
                    estimated_effort="1 heure",
                    target_level="Red",
                    definition_of_done="100% des commits assistés par IA portent la mention de co-auteur.",
                ),
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
            tickets = [
                ActionTicket(
                    ticket_id="AIDD-101",
                    title="Rédiger le fichier AGENTS.md (Mémoire d'architecture & Conventions)",
                    axis="harness",
                    priority="Critical",
                    estimated_effort="1 demi-journée",
                    target_level="Blue",
                    definition_of_done="Un fichier AGENTS.md versionné détaille la stack, les règles de nommage et les commandes de test.",
                ),
                ActionTicket(
                    ticket_id="AIDD-102",
                    title="Réduire les commits correctifs post-PR (Objectif <= 2 par PR)",
                    axis="intervention",
                    priority="High",
                    estimated_effort="2 jours",
                    target_level="Blue",
                    definition_of_done="La médiane des commits correctifs après ouverture de PR passe sous la barre de 2.",
                ),
                ActionTicket(
                    ticket_id="AIDD-103",
                    title="Déléguer des features complètes de taille M (50 à 300 lignes)",
                    axis="taille",
                    priority="Medium",
                    estimated_effort="1 semaine",
                    target_level="Blue",
                    definition_of_done="Au moins 3 PRs de taille M sont fusionnées avec l'aide de l'IA.",
                ),
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
            tickets = [
                ActionTicket(
                    ticket_id="AIDD-201",
                    title="Standardiser les règles comportementales (.cursorrules & agents)",
                    axis="harness",
                    priority="High",
                    estimated_effort="1 jour",
                    target_level="Green",
                    definition_of_done="Présence de règles modulaires et d'agents spécialisés dans le dépôt.",
                ),
                ActionTicket(
                    ticket_id="AIDD-202",
                    title="Adopter le TDD assisté (Écrire les tests avant l'implémentation)",
                    axis="intervention",
                    priority="Critical",
                    estimated_effort="3 jours",
                    target_level="Green",
                    definition_of_done="Zéro commit correctif nécessaire sur les PRs de taille L.",
                ),
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
            tickets = [
                ActionTicket(
                    ticket_id="AIDD-301",
                    title="Configurer l'isolation parallèle par Git Worktrees",
                    axis="parallele",
                    priority="Critical",
                    estimated_effort="1 jour",
                    target_level="Copper",
                    definition_of_done="Capacité à mener 3 branches concurrentes en parallèle avec contextes isolés.",
                ),
                ActionTicket(
                    ticket_id="AIDD-302",
                    title="Industrialiser la livraison de modules complets XL",
                    axis="taille",
                    priority="High",
                    estimated_effort="1 semaine",
                    target_level="Copper",
                    definition_of_done="Médiane de taille de PR atteignant le niveau L-XL avec validation complète.",
                ),
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
            tickets = [
                ActionTicket(
                    ticket_id="AIDD-401",
                    title="Implémenter la boucle de feedback fermée d'auto-correction CI/CD",
                    axis="harness",
                    priority="Critical",
                    estimated_effort="3 jours",
                    target_level="Silver",
                    definition_of_done="Script ou workflow CI relançant l'IA jusqu'à convergence 100% verte sans intervention humaine.",
                ),
                ActionTicket(
                    ticket_id="AIDD-402",
                    title="Délégation complète de l'implémentation (Zero human edit post-spec)",
                    axis="intervention",
                    priority="High",
                    estimated_effort="1 semaine",
                    target_level="Silver",
                    definition_of_done="PRs complexes mergées sans aucun commit d'ajustement humain une fois le cadrage posé.",
                ),
            ]
        elif current_rank == 5:  # Silver -> Gold
            steps = [
                "Déléguer également le cadrage initial : les agents analysent le backlog, spécifient et implémentent en autonomie.",
                "Mettre en place une gouvernance d'agents orchestrateurs supervisant les revues de code et le déploiement continu.",
            ]
            recommendations = [
                "Auditer en continu les garde-fous (IAM, credentials, manifests de production hors d'atteinte des agents).",
            ]
            tickets = [
                ActionTicket(
                    ticket_id="AIDD-501",
                    title="Orchestration autonome multi-agents du backlog",
                    axis="harness",
                    priority="Critical",
                    estimated_effort="2 semaines",
                    target_level="Gold",
                    definition_of_done="Les agents prennent en charge les tickets du backlog de bout en bout en autonomie cadrée.",
                ),
            ]

        return ProgressionPlan(
            next_level=next_level,
            limiting_axis=limiting_axis,
            steps=steps,
            recommendations=recommendations,
            action_tickets=tickets,
        )
