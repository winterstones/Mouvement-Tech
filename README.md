# 🚀 Mouvement-Tech — Moteur d'évaluation AI-Driven Development (AIDD)

> Solution d'évaluation empirique et de recommandation de trajectoire de montée en compétences pour développeurs et équipes adoptant l'intelligence artificielle.

---

## 🎯 Problématique

> **CTO :** *"Il me faut le niveau AI-Driven Development de toute ton équipe ainsi qu'un plan de progression pour chacun d'eux. Pour vendredi."*

Mouvement-Tech résout ce défi en ingérant les sources hétérogènes d'un développeur (activité Git, PRs, fichiers de contexte, harnais, sessions, déclaratif) et en le positionnant rigoureusement sur les **7 niveaux de la grille AIDD** via ses **4 axes fondamentaux**.

---

## 📊 Les 4 Axes & La Règle du Minimum (MIN)

```
Niveau Global = MIN(Axe Taille, Axe Harness, Axe Intervention, Axe Parallèle)
```

| Axe | Ce qu'il mesure | Signal empirique principal |
|---|---|---|
| **1. Taille** | Taille habituelle des features livrées avec l'IA | Distribution des PRs (`xs`, `s`, `m`, `l`, `xl`), médiane des lignes |
| **2. Harness** | Ce qui est mis en place autour de l'IA (mémoire, règles, agents) | `AGENTS.md`, `CLAUDE.md`, `.claude/skills`, `.claude/agents`, hooks |
| **3. Intervention** | Fréquence des reprises et corrections humaines après coup | Médiane des commits correctifs par PR, ratio de PR sans edit |
| **4. En Parallèle** | Capacité à mener plusieurs chantiers simultanément | Médiane des branches concurrentes (médiane >= 3 requis pour Copper+) |

---

## 🏆 Validation sur les 4 Profils de Référence

Notre moteur valide **100%** des profils fournis dans le sujet du hackathon :

| Profil | Niveau Attribué | Rang | Axe Limitant | Particularité validée |
|---|---|---|---|---|
| **Perceval** | 🔺 **Red** | 1 | Harness / Intervention | Se prétend "avancé", mais 4 commits correctifs/PR et aucun harness |
| **Bohort** | 🔹 **Blue** | 2 | Parallèle / Harness | Context engineering présent et maintenu, 2 commits correctifs/PR |
| **Leodagan** | 🟢 **Green** | 3 | Parallèle (médiane 1) | Cadrage préalable, 0 commit correctif, rules & agents versionnés |
| **Arthur** | 🥉 **Copper** | 4 | Harness (pas de boucles) | 4 chantiers parallèles en médiane (pic à 7), skills & agents avancés |

---

## 🛠️ Démarrage Rapide

### 1. Prérequis & Installation

```powershell
# Cloner ou se placer dans le dossier
cd D:\Users\worke\Documents\portfolio\liavel-up\Mouvement-Tech

# Activer l'environnement virtuel
.\.venv\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

### 2. Lancer l'API FastAPI

```powershell
.\.venv\Scripts\uvicorn api.main:app --reload --port 8000
```
- API & Documentation Swagger interactive disponible sur : **`http://127.0.0.1:8000/docs`**

### 3. Ouvrir l'Interface Web Dashboard

- Ouvrez simplement `web/index.html` dans votre navigateur ou servez-le localement.

### 4. Lancer les Tests Automatisés

```powershell
.\.venv\Scripts\pytest -v
```

---

## 🔌 Endpoints REST

- **`GET /levels`** : Référentiel complet des 7 niveaux AIDD et critères des 4 axes.
- **`GET /evaluate/{profile_id}`** : Évaluation instantanée d'un profil de référence (`perceval`, `bohort`, `leodagan`, `arthur`).
- **`POST /evaluate`** : Évaluation d'un profil arbitraire via chemin local ou URL de dépôt GitHub/GitLab.

---

## 🌟 Points Forts & Différenciateurs

1. **Rigueur Empirique** : Ne se laisse pas tromper par les auto-évaluations dithyrambiques (Perceval est ramené à Red avec avertissement explicite).
2. **Plan d'Action Actionnable** : Génère les étapes concrètes adaptées au niveau cible $N+1$ et à l'axe limitant précis.
3. **Enrichissement Multi-Plateformes** : Collecteurs intégrés pour GitHub API et GitLab API.
4. **Hybridation LLM / Algo** : Analyse quantitative déterministe combinée à l'analyse sémantique des sessions et déclaratifs (Gemini Flash).
