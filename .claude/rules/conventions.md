# Code Conventions — Mouvement-Tech

1. **Python 3.11+ Standards :**
   - Formattage conforme PEP 8.
   - Utilisation de f-strings pour toute interpolation de chaînes.
   - Gestion des contextes avec 'with open(...)'.

2. **Gestion des Erreurs :**
   - HTTPException(status_code=422) pour les données de profil incomplètes ou invalides.
   - HTTPException(status_code=404) pour les profils ou dépôts introuvables.
   - Journalisation propre des avertissements dans le champ 'warnings' de EvaluationResult.

3. **Tests Automatisés :**
   - Tout nouveau composant doit avoir un fichier de test dédié dans tests/.
   - Les 4 profils de référence (Perceval, Bohort, Leodagan, Arthur) doivent être validés en continu.