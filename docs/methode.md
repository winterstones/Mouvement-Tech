# 📄 Notre Méthode en 1 Page — Mouvement-Tech
> **Ce que nous mesurons, comment nous l'évaluons et pourquoi.**

---

## 🎯 1. La Problématique & La Vision

Face à la demande d'un CTO (*« Il me faut le niveau AIDD de toute l'équipe et un plan de progression pour vendredi »*), le piège immédiat est de se fier aux déclarations d'intention ou au simple volume de lignes générées.

**Notre conviction :** L'efficacité d'un développeur avec l'IA ne se mesure pas au nombre de prompts envoyés, mais à la **robustesse de son harnais**, à son **autonomie de boucle (moindre reprise humaine)** et à sa **capacité de parallélisation**. 

Les études industrielles confirment cette approche :
- **Google DORA / State of DevOps :** Les équipes d'élite avec automatisation avancée déploient **208 fois plus souvent** et récupèrent des pannes **106 fois plus vite** grâce à des boucles de feedback serrées.
- **McKinsey AI Survey :** La refonte des workflows agentiques et l'intégration de processus fermés génèrent le plus fort impact opérationnel et financier.

---

## 📊 2. Ce que nous mesurons (Les 4 Axes Empiriques)

Nous ingérons les données brutes (activité Git, PRs, dépôts, sessions, déclaratif) pour positionner le profil sur les 4 axes fondamentaux du référentiel AIDD :

| Axe | Métrique empirique extraite | Justification technique |
|---|---|---|
| **1. Taille** | Distribution des tailles de PR (xs, s, m, l, xl), médiane de lignes modifiées. | Mesure la granularité habituelle déléguée à l'IA (d'un simple snippet S à un module complet XL). |
| **2. Harness** | Détection de fichiers structurés (CLAUDE.md, AGENTS.md, .cursorrules, skills, boucles CI). | **Le cœur de la maturité :** Passage de l'*IA sans mémoire* (One-shot) à la *Mémoire de contexte* (Blue/Green), puis aux *Boucles d'auto-correction* (Silver). |
| **3. Intervention** | Nombre médian de commits correctifs post-ouverture de PR, ratio de PR sans edit. | Évalue l'efficacité du cadrage en amont : moins il y a de reprises après coup, plus l'IA a été guidée avec précision. |
| **4. En Parallèle** | Médiane des branches concurrentes actives et menées jusqu'au merge. | Mesure la maîtrise des environnements isolés (git worktrees, contextes séparés) pour démultiplier la vélocité. |

---

## ⚖️ 3. La Règle du Minimum Strict (MIN) & Détection des Biais

`
Niveau Global = MIN(Axe Taille, Axe Harness, Axe Intervention, Axe Parallèle)
`

1. **Aucune moyenne pondérée :** Un développeur produisant des modules XL mais sans aucun harnais et avec 4 commits correctifs par PR reste bloqué à **Red** (cas *Perceval*). Le maillon le plus faible dicte le niveau réel.
2. **Priorité absolue aux faits sur le déclaratif :** Notre moteur compare ce que le développeur affirme et ce que Git prouve. Les divergences sont signalées sous forme d'alertes de cadrage (*warnings*).

---

## 🚀 4. Plan de Progression Actionnable (+1$)

L'outil ne se contente pas de noter : il identifie l'**Axe Limitant (goulot d'étranglement)** et génère la feuille de route concrète pour débloquer le palier supérieur :
* **Vers Blue :** Poser les bases du *Context Engineering* (mémoire d'architecture et conventions dans un AGENTS.md).
* **Vers Green :** Cadrer les tâches en amont (spécifications préalables, tests d'abord) et versionner des règles de comportement.
* **Vers Copper :** Structurer le travail en parallèle (isolation par git worktrees, multi-sessions).
* **Vers Silver/Gold :** Fermer la boucle avec l'auto-correction (*Feedback Loops* CI/CD relançant l'IA sur échec de test).

---

## 🛠️ 5. Robustesse & Indépendance

* **100% Autonome & Local :** Moteur déterministe en Python pur, ne nécessitant aucune clé d'API pour fonctionner.
* **Hybridation LLM :** Enrichissement sémantique optionnel via Gemini Flash pour qualifier les sessions et déclaratifs.
* **Multi-Sources :** Compatible dossiers de profils locaux et analyse en direct de dépôts distants (GitHub/GitLab).