# AGENTS.md — Mouvement-Tech

Mouvement-Tech est un moteur d'évaluation et de recommandation AIDD (AI-Driven Development) pour situer le niveau d'un développeur et lui fournir un plan de progression.

Ce fichier constitue le point d'entrée principal pour tout agent ou assistant IA (Antigravity, Cursor, Claude Code, Copilot) intervenant sur ce dépôt.

---

## 📚 Base de Connaissances (`docs/knowledge/`)

Toute la documentation de référence et les décisions d'architecture sont versionnées dans `docs/knowledge/` :
- [`docs/knowledge/criteres-aidd.md`](./docs/knowledge/criteres-aidd.md) : Définition formelle des 7 niveaux, des 4 axes de mesure et des formules mathématiques d'inférence.
- [`docs/knowledge/architecture.md`](./docs/knowledge/architecture.md) : Diagramme des composants, flux de données et rôles de chaque module (`collectors`, `scorer`, `api`, `web`).
- [`docs/knowledge/decisions.md`](./docs/knowledge/decisions.md) : Registre des décisions d'architecture (ADRs) et arbitrages techniques.
- [`levels/aidd.md`](./levels/aidd.md) : Référentiel officiel du hackathon Laivel Up.

---

## 🏛️ Structure du Codebase

```text
Mouvement-Tech/
├── api/
│   ├── collectors/          # Ingestion multi-sources
│   │   ├── profile.py       # Validation & chargement des dossiers de profil locaux
│   │   ├── github.py        # Connecteur GitHub API (/pulls, /contents, /workflows)
│   │   └── gitlab.py        # Connecteur GitLab API (/tree, /merge_requests)
│   ├── scorer/              # Moteur de calcul AIDD
│   │   ├── thresholds.py    # Définition des niveaux, rangs et métadonnées d'axes
│   │   ├── algo.py          # Scoring quantitatif déterministe (4 axes)
│   │   ├── llm.py           # Juge qualitatif sémantique (Gemini Flash / Heuristique)
│   │   └── fusion.py        # Agrégation (règle du MIN), détection d'incohérences et plan
│   ├── models.py            # Schémas de données Pydantic typés
│   └── main.py              # Application FastAPI REST & documentation Swagger
├── docs/
│   └── knowledge/           # Documentation technique et savoir métier
├── tests/                   # Suite de tests automatisés (100% de réussite exigé)
│   ├── test_profiles.py     # Validation des 4 profils de référence (Perceval, Bohort, Leodagan, Arthur)
│   ├── test_algo.py         # Tests unitaires du scoring quantitatif
│   └── test_api.py          # Tests d'intégration des routes REST
├── web/                     # Dashboard web interactif (index.html)
└── requirements.txt         # Dépendances Python du projet
```

---

## 🔒 Principes d'Ingénierie & Règles d'Or

1. **Règle Fondamentale du MIN :** Le niveau global est strictement égal au minimum des 4 axes. Aucun axe ne peut compenser la faiblesse d'un autre.
2. **Primauté des Faits Empiriques :** Les métriques Git (PRs, commits correctifs, CI, harnais) prévalent toujours sur les affirmations des développeurs.
3. **Traçabilité & Preuve (`evidence`) :** Chaque axe calculé doit comporter une justification textuelle précise mentionnant les chiffres clés.
4. **Gestion Robuste des Données Manquantes :** Refus explicite (erreur 422) si les pièces indispensables (`profile.json`, `git-activity.json`) sont absentes.
5. **Mise à Jour de la Connaissance :** Si un changement d'architecture ou de règle intervient, mettre à jour le document correspondant dans `docs/knowledge/`.

---

## 🚀 Protocole Git, Commit & Push avec Traçabilité IA

Chaque intervention sur ce dépôt doit respecter le protocole de traçabilité suivant :

### 1. Format Conventional Commits
```text
<type>(<scope>): <description courte et impérative>

[Corps explicatif optionnel détaillant le contexte et les choix techniques]

Co-authored-by: Antigravity <antigravity@google.com>
```
Types : `feat`, `fix`, `test`, `refactor`, `docs`, `chore`, `perf`, `ci`.

### 2. Signature de Co-Auteur Obligatoire
Chaque commit assisté par l'IA **doit inclure** la mention de co-auteur en fin de message :
- Antigravity / Gemini : `Co-authored-by: Antigravity <antigravity@google.com>`
- Claude : `Co-authored-by: Claude <noreply@anthropic.com>`
- GitHub Copilot : `Co-authored-by: GitHub Copilot <copilot@github.com>`

### 3. Pipeline Pré-Commit / Pré-Push
Avant tout commit ou push :
```powershell
# 1. Vérifier que la suite de tests est à 100% verte
pytest -v

# 2. Vérifier l'état des fichiers modifiés
git status

# 3. Indexer et commiter avec la signature
git add <fichiers>
git commit -m "docs(knowledge): ajouter la base de connaissances et actualiser AGENTS.md`n`nCo-authored-by: Antigravity <antigravity@google.com>"

# 4. Pousser vers la branche distante
git push origin <branche>
```