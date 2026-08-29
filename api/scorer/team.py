from typing import List, Dict, Any, Optional
from collections import Counter
from api.models import (
    EvaluationResult,
    TeamEvaluationResult,
    ContributorMetrics,
    AIDDLevel,
)
from api.scorer.thresholds import RANK_TO_LEVEL, LEVELS


class TeamEngine:
    """Consolidates individual developer evaluations into a CTO-level Team Maturity Report."""

    @classmethod
    def evaluate_team(
        cls,
        members: List[EvaluationResult],
        team_name: str = "Équipe Ingénierie",
        contributors_breakdown: Optional[List[ContributorMetrics]] = None,
    ) -> TeamEvaluationResult:
        if not members:
            raise ValueError("Au moins un membre d'équipe est requis pour l'évaluation.")

        team_size = len(members)
        total_ranks = sum(m.level.rank for m in members)
        avg_rank = round(total_ranks / team_size, 2)
        closest_rank = min(6, max(0, round(avg_rank)))
        avg_level = RANK_TO_LEVEL[closest_rank]

        # Level distribution
        distribution: Dict[str, int] = {lvl_id: 0 for lvl_id in LEVELS.keys()}
        for m in members:
            distribution[m.level.id] = distribution.get(m.level.id, 0) + 1

        # Calculate most frequent bottleneck
        bottlenecks = [m.limiting_axis for m in members]
        bottleneck_counter = Counter(bottlenecks)
        team_bottleneck = bottleneck_counter.most_common(1)[0][0] if bottleneck_counter else "harness"

        # Strategic CTO recommendations
        team_recommendations = cls._generate_cto_recommendations(members, team_bottleneck, avg_rank)

        return TeamEvaluationResult(
            team_name=team_name,
            team_size=team_size,
            average_rank=avg_rank,
            average_level_label=avg_level.label,
            level_distribution=distribution,
            members=members,
            team_bottleneck_axis=team_bottleneck,
            team_recommendations=team_recommendations,
            contributors_breakdown=contributors_breakdown,
        )

    @staticmethod
    def _generate_cto_recommendations(
        members: List[EvaluationResult], team_bottleneck: str, avg_rank: float
    ) -> List[str]:
        recs = []

        red_members = [m for m in members if m.level.rank == 1]
        advanced_members = [m for m in members if m.level.rank >= 3]

        # Recommendation 1: Mentorship / Knowledge Transfer
        if red_members and advanced_members:
            adv_names = ", ".join(m.profile_id.capitalize() for m in advanced_members)
            red_names = ", ".join(m.profile_id.capitalize() for m in red_members)
            recs.append(
                f"Tutorat interne : Organiser des sessions de pair-programming entre les profils avancés ({adv_names}) "
                f"et les profils en transition ({red_names}) pour diffuser les pratiques de harnais et de cadrage."
            )

        # Recommendation 2: Address Team Bottleneck
        if team_bottleneck == "harness":
            recs.append(
                "Standardisation du Harnais : Déployer un modèle standard de `AGENTS.md` et de règles partagées "
                "dans tous les dépôts de l'entreprise pour éviter la dispersion des contextes."
            )
        elif team_bottleneck == "taille":
            recs.append(
                "Montée en taille de scope : Former l'équipe à spécifier des fonctionnalités complètes multi-étapes (taille L) "
                "plutôt que de générer du simple boilerplate fragmenté (taille S)."
            )
        elif team_bottleneck == "parallele":
            recs.append(
                "Outillage pour la parallélisation : Former l'équipe à l'isolation par Git worktrees "
                "(`claude --worktree`) pour mener plusieurs chantiers indépendants sans risque de collision."
            )
        elif team_bottleneck == "intervention":
            recs.append(
                "Validation préalable de cadrage : Imposer la validation écrite des spécifications et critères d'acceptation "
                "avant génération de code pour faire chuter les commits correctifs post-ouverture."
            )

        # Recommendation 3: Governance & AI Traceability
        recs.append(
            "Gouvernance & Traçabilité Git : Rendre obligatoire la signature `Co-authored-by: <IA>` dans la CI "
            "pour mesurer objectivement le taux d'adoption du code assisté dans chaque sous-projet."
        )

        # Recommendation 4: Continuous automated testing & loops
        recs.append(
            "Automatisation de la validation : Configurer des boucles de feedback en CI relançant l'IA tant que les tests "
            "échouent afin de préparer la transition vers le palier Silver."
        )

        return recs
