# CLAUDE.md — Directives & Contexte Projet Mouvement-Tech

Mouvement-Tech est un moteur d'évaluation empirique du niveau AI-Driven Development (AIDD) des développeurs et équipes.

## 🛠️ Commandes Principales
- Lancer les tests : pytest -v
- Lancer l'API FastAPI : uvicorn api.main:app --reload --port 8000
- Évaluer un profil local : python scripts/evaluate.py perceval
- Lancer la boucle d'auto-correction : python scripts/loop_fix.py
- Gérer les worktrees parallèles : python scripts/worktree_setup.py list

## 🏗️ Architecture & Composants
- api/collectors/ : Ingestion des profils locaux et des dépôts distants (GitHub / GitLab).
- api/scorer/ :
  - algo.py : Calcul quantitatif déterministe des 4 axes (Taille, Harness, Intervention, Parallèle).
  - llm.py : Juge sémantique qualitatif (Gemini Flash avec fallback heuristique sans crash).
  - fusion.py : Application stricte de la règle du MIN, détection d'incohérences et plan N+1.
- api/models.py : Schémas Pydantic typés.
- web/index.html : Dashboard interactif.

## 📏 Règles d'Ingénierie & AIDD
1. **Règle du MIN absolue :** Niveau = MIN(Taille, Harness, Intervention, Parallèle).
2. **Priorité aux faits empiriques :** Les métriques Git prévalent toujours sur les déclarations.
3. **Zéro régression :** 100% des tests de tests/ doivent passer.
4. **Traçabilité des commits :** Tout commit assisté par l'IA doit inclure Co-authored-by: Assistant <email>.
5. **Context Engineering :** Toute modification structurelle doit être répercutée dans docs/knowledge/.