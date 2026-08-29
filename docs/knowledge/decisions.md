# 📜 Décisions d'Architecture (ADR) — Mouvement-Tech

Ce document consigne les choix clés et arbitrages d'ingénierie pris sur le projet.

---

### ADR 01 — Règle du Minimum Strict (MIN) pour le Niveau Global
- **Contexte :** La grille AIDD stipule : *"Un niveau n'est atteint que si tous ses axes le sont."*
- **Décision :** Le niveau attribué est calculé par `min(taille, harness, intervention, parallele)`. Aucune moyenne pondérée n'est autorisée.
- **Bénéfice :** Évite de sur-classer un développeur dont un des pans techniques (ex: parallélisme ou harnais) est défaillant.

---

### ADR 02 — Hybridation Algorithmique & LLM avec Fallback Heuristique
- **Contexte :** Les métriques quantitatives (`git-activity.json`) nécessitent un calcul déterministe et reproductible, tandis que les sessions de travail (`session.md`) et déclaratifs (`declaratif.md`) nécessitent une compréhension sémantique.
- **Décision :** 
  - Algorithme déterministe en Python pur (`api/scorer/algo.py`) pour les 4 axes.
  - LLM Gemini Flash (`api/scorer/llm.py`) pour l'analyse qualitative des textes.
  - Fallback heuristique automatique sans crash si aucune clé `GEMINI_API_KEY` n'est configurée.
- **Bénéfice :** 100% opérationnel immédiatement sans configuration externe requise, tout en exploitant le LLM dès qu'une clé est présente.

---

### ADR 03 — Détection des Biais Déclaratifs
- **Contexte :** Les développeurs ont tendance à se sur-évaluer ou se sous-évaluer dans les questionnaires internes (cf. Perceval vs Leodagan).
- **Décision :** Les métriques empiriques (PRs, commits correctifs, CI, harnais) ont toujours priorité absolue sur le déclaratif. Les divergences sont signalées comme `warnings` dans le résultat.
- **Bénéfice :** Évite le piège numéro 1 du sujet (*"Croire le déclaratif"*).

---

### ADR 04 — Traçabilité IA Native dans le Workflow Git
- **Contexte :** La collaboration avec les assistants IA doit être auditable et mesurable.
- **Décision :** Tous les commits produits avec l'aide de l'IA intègrent la signature standard `Co-authored-by: <Assistant> <email>`.
- **Bénéfice :** Garantit la transparence et alimente fidèlement le ratio `ai_coauthored_ratio` du projet.
