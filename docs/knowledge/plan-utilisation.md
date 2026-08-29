# 📖 Plan d'Utilisation & Scénarios Métiers — Mouvement-Tech

Ce guide détaille les parcours utilisateurs opérationnels de Mouvement-Tech selon les contextes d'entreprise.

---

## 1. Scénario A : Le Diagnostic d'Équipe Flash (Audit Hebdomadaire CTO)

> **Objectif :** Obtenir la cartographie de l'équipe et le plan d'action managérial en moins de 2 minutes.

```text
[1. Connexion au Dashboard] ──> [2. Coller l'URL du Dépôt / Scanner] ──> [3. Analyse Automatique] ──> [4. Export Rapport CTO]
```

### Étapes pas-à-pas :
1. **Lancement de l'audit :** Le CTO ou Lead ouvre l'interface `web/index.html` et colle l'URL du dépôt GitHub partagé ou charge le dossier de l'équipe.
2. **Scan automatique multi-sources :**
   - Le moteur extrait les commits, les PRs et analyse les fichiers de contexte (`AGENTS.md`, `.cursorrules`, etc.).
   - L'algorithme calcule les 4 axes pour chaque développeur et applique la règle du MIN.
3. **Restitution visuelle :**
   - Le dashboard affiche la **Maturité Moyenne de l'Équipe** (ex: $2.5/6$).
   - L'axe goulot d'étranglement est mis en évidence (ex: *Intervention* ou *Harnais*).
   - Les **4 actions stratégiques prioritaires** pour vendredi sont générées automatiquement.
4. **Diffusion :** Le CTO copie les recommandations ou exporte les fiches pour le point d'ingénierie hebdomadaire.

---

## 2. Scénario B : L'Entretien Individuel & Revue de Performance (Tech Lead & Développeur)

> **Objectif :** Poser un diagnostic neutre et bienveillant, basé sur les faits, lors d'un 1-on-1.

### Étapes pas-à-pas :
1. **Sélection du profil :** Le Tech Lead clique sur la ligne du développeur dans la Matrice d'Équipe.
2. **Analyse des 4 axes :**
   - **Taille :** Analyse de la distribution des PRs ($S$, $M$, $L$, $XL$) et de la complexité déléguée.
   - **Harnais :** Vérification de la présence et de la maintenance des fichiers de mémoire projet.
   - **Intervention :** Examen du nombre de commits correctifs post-ouverture (mesure de la précision du cadrage).
   - **Parallèle :** Examen du nombre de chantiers menés de front.
3. **Discussion sur les alertes :** Si le développeur se surestime (ex: Perceval) ou se sous-estime (ex: Bohort), l'alerte factuelle permet d'objectiver l'échange sans jugement personnel.
4. **Adoption du Plan $N+1$ :** Le développeur repart avec **3 actions concrètes et mesurables** pour le sprint suivant (ex: *"Créer un AGENTS.md avec l'architecture"* ou *"Viser 0 commit correctif après ouverture"*).

---

## 3. Scénario C : Intégration dans le Pipeline CI/CD (Gouvernance Continue)

> **Objectif :** Maintenir la qualité du harnais et la traçabilité IA sur chaque Pull Request.

```yaml
# .github/workflows/aidd-audit.yml
name: AIDD Compliance Audit
on: [pull_request]
jobs:
  audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Verify Context Files
        run: |
          test -f AGENTS.md || (echo "Erreur: AGENTS.md obligatoire pour le niveau Blue+" && exit 1)
      - name: Check AI Traceability
        run: |
          git log -1 --pretty=%B | grep -i "Co-authored-by:" || echo "Warning: Commit non signé IA"
```

---

## 4. Matrice RACI de l'Utilisation de l'Outil

| Rôle | Lancer l'audit | Analyser les 4 axes | Valider le Plan $N+1$ | Déployer le Harnais |
|---|---|---|---|---|
| **CTO** | **A**ccountable | **I**nformed | **A**ccountable | **I**nformed |
| **Tech Lead** | **R**esponsible | **R**esponsible | **R**esponsible | **A**ccountable |
| **Développeur** | **C**onsulted | **C**onsulted | **R**esponsible | **R**esponsible |
| **Scrum / Coach** | **I**nformed | **I**nformed | **C**onsulted | **I**nformed |

*(R = Responsable, A = Approbateur / Décideur, C = Consulté, I = Informé)*
