---
name: audit-harness
description: Audite le harnais de développement IA (Context Engineering, Behavior, Loops) d'un dépôt.
---

# Skill : Audit Harness

Vérifie la présence et la qualité des composants de harnais AIDD sur le dépôt courant ou cible :
1. Fichiers de contexte racine (CLAUDE.md, AGENTS.md, .cursorrules).
2. Connaissances et documentation versionnées (docs/knowledge/, docs/context/).
3. Règles et compétences (.claude/rules/, .claude/skills/).
4. Boucles de rétroaction automatique (scripts/loop_fix.py, GitHub Actions CI).