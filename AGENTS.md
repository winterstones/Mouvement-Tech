# AGENTS.md — Mouvement-Tech

Mouvement-Tech est un moteur d'évaluation et de recommandation AIDD (AI-Driven Development) pour situer le niveau d'un développeur et lui fournir un plan de progression.

## Architecture
- `api/` : FastAPI & architecture de scoring
  - `collectors/` :
    - `profile.py` : Analyseur de dossiers de profil locaux
    - `github.py` : Collecteur via GitHub API
    - `gitlab.py` : Collecteur via GitLab API
  - `scorer/` :
    - `thresholds.py` : Définition des niveaux, rangs et seuils minimaux par axe
    - `algo.py` : Moteur de scoring quantitatif / algorithmique
    - `llm.py` : Analyse qualitative des sessions et du déclaratif via LLM (Gemini Flash)
    - `fusion.py` : Consolidation, calcul du goulot d'étranglement (MIN) et génération du plan de progression
  - `models.py` : Schémas Pydantic typés
  - `main.py` : Routes FastAPI et point d'entrée API
- `web/` : Interface dashboard interactive (`index.html`)
- `tests/` :
  - `test_profiles.py` : Validation sur les 4 profils de référence (perceval=red, bohort=blue, leodagan=green, arthur=copper)
  - `test_algo.py` : Tests unitaires du scoring
  - `test_api.py` : Tests d'intégration des endpoints REST

---

## 🔒 Règles Fondamentales du Moteur
1. **Règle du MIN** : Le niveau global est strictement le minimum des 4 axes (Taille, Harness, Intervention, Parallèle).
2. **Priorité aux faits empiriques** : Les métriques Git, PR et commits correctifs priment sur le déclaratif.
3. **Justification systématique** : Chaque axe inclut une `evidence` factuelle basée sur les données chiffrées.
4. **Gestion des données minimales** : Refus explicite si `profile.json` ou `git-activity.json` est absent.

---

## 🚀 Protocole Git, Commit & Push avec Traçabilité IA

Tous les agents et assistants travaillant sur ce dépôt doivent respecter le protocole de traçabilité Git suivant :

### 1. Format des Messages de Commit (Conventional Commits)
Chaque commit doit respecter la structure standard :
```text
<type>(<scope>): <description courte et impérative>

[Corps optionnel expliquant le contexte et le pourquoi]

Co-authored-by: Antigravity <antigravity@google.com>
```

Types autorisés : `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `perf`, `ci`.

### 2. Traçabilité Obligatoire (Co-authored-by)
Chaque commit généré ou assisté par l'IA **doit inclure** la mention de co-auteur en fin de message pour garantir un ratio de co-authorship traçable :
- Pour Antigravity / Gemini : `Co-authored-by: Antigravity <antigravity@google.com>`
- Pour Claude : `Co-authored-by: Claude <noreply@anthropic.com>`
- Pour Copilot : `Co-authored-by: GitHub Copilot <copilot@github.com>`

### 3. Pipeline Pré-Commit / Pré-Push
Avant de commiter ou pousser des changements :
1. **Exécuter les tests** : `pytest -v` (doit être à 100% vert, 0 échec).
2. **Vérifier les secrets** : Ne jamais ajouter de fichier `.env` ou de clés API réelles.
3. **Statut Git propre** : Vérifier avec `git status` que seuls les fichiers ciblés sont indexés.

### 4. Automatisation des Commandes Git
Pour réaliser une livraison propre :
```powershell
# 1. Validation de la suite de tests
pytest -v

# 2. Indexation des fichiers modifiés
git add <fichiers>

# 3. Commit avec signature de co-auteur
git commit -m "feat(scorer): description du changement`n`nCo-authored-by: Antigravity <antigravity@google.com>"

# 4. Push vers GitHub sur la branche active
git push origin <nom-de-branche>
```