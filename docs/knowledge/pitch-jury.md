# 🎙️ Pitch Deck & Guide de Soutenance — Mouvement-Tech (Laivel Up)

> **Format recommandé pour le Jury :** 3 à 5 minutes de présentation + Démonstration live interactive + Q&A.

---

## ⏱️ Structure Chronométrée (Pitch 3 minutes)

`
00:00 - 00:45 ➔ Le Problème : L'illusion du Vibe Coding et le manque de métriques objectives
00:45 - 01:30 ➔ La Solution : Mouvement-Tech, l'évaluation 100% empirique et déterministe
01:30 - 02:45 ➔ Démonstration Live : Du scan de dépôt au Kanban d'adoption et plan CTO
02:45 - 03:00 ➔ La Vision & Conclusion : Transformer l'IA en ingénierie certifiée
`

---

## 📑 Les 7 Slides Clés du Pitch

### Slide 1 : Le Constat de Défaillance — L'Illusion du "Vibe Coding"
- **Titre :** *90% des développeurs utilisent l'IA, mais combien font de la vraie ingénierie ?*
- **Le Problème :** 
  - Aujourd'hui, les entreprises et les CTO sont aveugles face à l'adoption réelle de l'IA.
  - Deux écueils majeurs :
    1. **Le déclaratif subjectif :** Les formulaires et auto-évaluations où chacun prétend être expert.
    2. **La dette Vibe Coding :** Des lignes de code générées à la volée sans mémoire, sans tests, avec un taux de reprise humaine massif après coup.
- **La Punchline :** *"Générer du code ne fait pas de vous un ingénieur augmenté. Piloter l'IA avec rigueur, oui."*

---

### Slide 2 : La Thèse — L'Évaluation Empirique par les Traces Git
- **Titre :** *Mouvement-Tech : Mesurer ce qui est fait, pas ce qui est dit.*
- **Le Principe :**
  - Aucune question déclarative : l'audit repose exclusivement sur les **preuves vérifiables dans Git**.
  - **4 Axes AIDD déterministes** :
    1. **Taille (Amplitude fonctionnelle) :** Détection des briques S, M, L, XL via analyse multi-fichiers et commits sémantiques.
    2. **Harness (Mémoire & Outillage) :** Présence de AGENTS.md, règles .cursorrules, skills, hooks et boucles CI.
    3. **Intervention (Délégation réelle) :** Mesure des reprises après coup et du taux de réussite au 1er passage.
    4. **Parallèle (Multi-track) :** Gestion simultanée de chantiers via branches et worktrees.
- **Règle d'Or :** La **règle stricte du MIN** : votre niveau est celui de votre axe le plus faible.

---

### Slide 3 : L'Innovation Technique — Double Moteur AST & Dette Vibe Coding
- **Titre :** *Au-delà des lignes de code : La Santé Réelle du Code.*
- **L'Innovation :**
  - **Analyse AST (Abstract Syntax Tree) :** Évaluation de la maintenabilité, complexité cyclomatique, God Functions et densité de tests.
  - **Classification en 4 Archétypes :**
    - 🛡️ *Artisanat Sain* (Non-IA, code propre)
    - ⚠️ *Dette Legacy Manuelle* (Non-IA, spaghetti historique)
    - 🚨 *Dette Vibe Coding* (IA massive mais non cadrée, 80% de reprise)
    - 🏆 *AIDD Certifié* (IA maîtrisée, harnais complet, zéro dette)

---

### Slide 4 : Démonstration Live (3 Scénarios d'Entreprise)
- **Déroulé de la démo :**
  1. **Audit Live d'un dépôt réel (cline/cline ou winterstones/Mouvement-Tech) :**
     - Analyse instantanée des commits, PRs et du harnais.
     - Affichage du diagnostic avec explication transparente du goulot d'étranglement.
  2. **Tableau Kanban Jira de l'Équipe :**
     - Répartition visuelle des profils sur les 7 colonnes (White à Gold).
     - Filtre instantané sur les développeurs à risque Vibe Coding.
  3. **Plan Stratégique CTO & Backlog Actionnable :**
     - Matrice d'actions concrètes pour le vendredi.
     - Export en un clic des tickets Jira N+1 personnalisés par développeur.

---

### Slide 5 : Cas d'Usage & Modèle Économique (Business)
- **Titre :** *Qui utilise Mouvement-Tech et pourquoi ?*
- **3 Cibles Principales :**
  - **1. Le CTO / VP Engineering (B2B SaaS) :** Gouvernance d'équipe, allocation des budgets d'outils IA, élimination de la dette technique.
  - **2. Le Recruteur Tech & ESN (Pre-hire Audit) :** Certification objective des compétences IA d'un candidat à partir de son GitHub sans biais déclaratif.
  - **3. Le Développeur (Mentorat Auto-piloté) :** Feuille de route précise pour progresser vers le niveau supérieur.

---

### Slide 6 : Robustesse & Qualité d'Ingénierie
- **Nos Chiffres :**
  - **27/27 Tests Automatisés au Vert (100%)** couvrant toute l'API et les algorithmes.
  - **Architecture Déterministe :** FastAPI + Pydantic V2 + Tailwind SPA moderne.
  - **Projet Mouvement-Tech auto-évalué au Niveau 🥉 Copper (Rang 4) / Silver (5) sur le Harness.**
  - **100% de Conventional Commits** et traçabilité de co-authorship IA.

---

### Slide 7 : Conclusion & Punchline
- **Titre :** *Le futur du développement logiciel n'est pas de coder plus vite, mais de piloter mieux.*
- **Punchline Finale :**
  > **« Avec Mouvement-Tech, transformez l'engouement passager du Vibe Coding en une discipline d'ingénierie augmentée, mesurable et pérenne. »**

---

## 🛡️ Questions Pièges Anticipées du Jury & Réponses

| Question du Jury | Réponse Stratégique & Preuve |
|---|---|
| *« Comment évitez-vous qu'un développeur triche en faisant des gros commits artificiels ? »* | Notre moteur d'Axe 1 ne regarde pas les lignes brutes, mais le **périmètre multi-fichiers, la structure sémantique et la cohérence AST**. De plus, les axes 2 (harnais) et 3 (reprise/CI) pénalisent immédiatement le code non testé ou rejeté. |
| *« L'évaluation dépend-elle de l'IA (LLM) qui peut halluciner ? »* | **Non.** Le moteur de notation est **100% algorithmique et déterministe** (QuantitativeScorer). Le LLM n'est qu'un copilote de synthèse pour formuler des conseils textuels personnalisés. |
| *« Est-ce compatible avec les règles de confidentialité / RGPD ? »* | **Oui.** L'audit peut fonctionner soit en local (analyse de code sur machine), soit sur forges privées sans stocker le code source, uniquement les métadonnées Git. |
