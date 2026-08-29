# 📊 Référentiel & Critères AIDD — Mouvement-Tech

Ce document formalise les critères d'évaluation des 4 axes de la grille AI-Driven Development (AIDD) et leurs règles d'inférence.

---

## 1. Vue d'ensemble des 7 Niveaux

| Rang | Niveau | Emoji | Résumé |
|---|---|---|---|
| 0 | White | ❖ | Aucune adoption IA dans le workflow. |
| 1 | Red | 🔺 | Prompts simples, features S, nombreuses reprises manuelles. |
| 2 | Blue | 🔹 | Context engineering (AGENTS.md), features M, corrections modérées. |
| 3 | Green | 🟢 | Context + Behavior (rules/agents), features L, 0 commit correctif, cadrage en amont. |
| 4 | Copper | 🥉 | Context + Behavior avancé (skills, worktrees), features L/XL, 3+ chantiers parallèles. |
| 5 | Silver | 🥈 | Boucles automatiques de convergence, features L/XL livrées sans intervention humaine post-cadrage. |
| 6 | Gold | 🥇 | Autonomie totale des agents dès la phase de spécification. |

---

## 2. Les 4 Axes d'Évaluation

### 📏 Axe 1 : Taille (Scope des livrables IA)
Mesure la taille **habituelle** des features générées et livrées avec l'IA.
- **Formule d'inférence :**
  - Si $\text{Ratio}(L + XL) \ge 45\%$ ou $\text{MedianLines} \ge 500$ :
    - Si $\text{Ratio}(XL) \ge 20\%$ ou $\text{MedianLines} \ge 800$ $\rightarrow$ **Rank 4 (L-XL)**
    - Sinon $\rightarrow$ **Rank 3 (L)**
  - Sinon si $\text{Ratio}(M) \ge 35\%$ ou $\text{MedianLines} \ge 150$ $\rightarrow$ **Rank 2 (M)**
  - Sinon $\rightarrow$ **Rank 1 (S)**

### 🛡️ Axe 2 : Harness (Outillage & Context Engineering)
Mesure la maturité du contexte et des règles fournies à l'IA.
- **Niveau 0 (White) :** Aucun fichier de contexte ni harnais.
- **Niveau 1 (Red) :** Prompts manuels sans fichiers versionnés.
- **Niveau 2 (Blue) :** `AGENTS.md` ou `CLAUDE.md` présent et maintenu.
- **Niveau 3 (Green) :** Fichier de contexte + `rules`, `skills`, `hooks` et `agents` versionnés.
- **Niveau 4 (Copper) :** Harnais multi-dépôts, isolation par `worktrees`, compétences procédurales avancées.
- **Niveau 5 (Silver) :** Présence de scripts de boucle automatique relançant l'IA jusqu'au succès des tests.

### ✋ Axe 3 : Intervention (Reprises humaines post-génération)
Mesure le degré de reprise humaine nécessaire après le travail de l'IA.
- **Formule d'inférence :**
  - $\text{MedianCorrections} \ge 3$ $\rightarrow$ **Rank 1 (Red)** (reprises fréquentes après coup).
  - $\text{MedianCorrections} = 2$ $\rightarrow$ **Rank 2 (Blue)** (reprises partielles).
  - $\text{MedianCorrections} \le 1$ $\rightarrow$ **Rank 3 / 4 (Green/Copper)** (intervention ciblée aux étapes clés de cadrage).
  - $\text{MedianCorrections} = 0$ et $100\%$ PRs sans edit avec boucles $\rightarrow$ **Rank 5 (Silver)**.

### 🔀 Axe 4 : En Parallèle (Concurrence des chantiers)
Mesure le nombre habituel de branches et chantiers menés de front avec l'IA.
- **Formule d'inférence :**
  - $\text{MedianBranches} \ge 3$ $\rightarrow$ **Rank 4 (Copper/Silver/Gold)** (chantiers parallèles menés jusqu'au bout).
  - $\text{MedianBranches} \ge 1$ $\rightarrow$ **Rank 3 (Green/Blue/Red)** (1 fil habituel).
  - $\text{MedianBranches} = 0$ $\rightarrow$ **Rank 0 (White)**.

---

## 3. Règle Fondamentale du MIN

$$\text{Niveau Global} = \min(\text{Rang}_{\text{Taille}}, \text{Rang}_{\text{Harness}}, \text{Rang}_{\text{Intervention}}, \text{Rang}_{\text{Parallèle}})$$

Un développeur ne peut monter de niveau que si **l'intégralité des 4 axes** atteint le palier requis. L'axe le plus faible constitue le **goulot d'étranglement** (Axe Limitant) ciblé en priorité dans le plan de progression.
