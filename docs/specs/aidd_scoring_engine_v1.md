# Spec : Moteur de Scoring AIDD v1.0

## Objectif
Permettre à un CTO d'évaluer objectivement le niveau d'adoption de l'AI-Driven Development (AIDD) d'un développeur ou d'une équipe, et d'obtenir un plan d'action personnalisé $N+1$.

## Entrées
- Dossier de profil local (profile.json, git-activity.json, repo-context, pull-requests.json, sonar-measures.json, session.md, declaratif.md).
- Ou URL publique de dépôt GitHub / GitLab.

## Sorties
- Niveau global AIDD (0 à 6).
- Score détaillé et justification empirique sur les 4 axes (Taille, Harness, Intervention, Parallèle).
- Axe limitant (goulot d'étranglement).
- Liste des incohérences déclaratives / alertes de cadrage.
- Plan de progression structuré en étapes et recommandations.