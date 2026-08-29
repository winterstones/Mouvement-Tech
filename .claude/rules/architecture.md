# Architecture Rules — Mouvement-Tech

1. **Séparation Stricte des Responsabilités :**
   - Les collecteurs (api/collectors/) n'effectuent AUCUN calcul de score. Ils se contentent d'extraire, de valider et de normaliser les données brutes.
   - Les scorers (api/scorer/) ne font aucun appel réseau direct. Ils consomment uniquement les dictionnaires de données normalisées.
   - Le moteur de fusion (api/scorer/fusion.py) est l'unique lieu où la règle du MIN et la détection d'incohérences sont appliquées.

2. **Typage Strict :**
   - Toutes les entrées/sorties exposées par l'API doivent utiliser les modèles Pydantic de api/models.py.
   - Utiliser des annotations de type explicites sur toutes les fonctions publiques.

3. **Résilience et Fallback :**
   - Aucune dépendance à une API externe ne doit bloquer l'évaluation locale de base.