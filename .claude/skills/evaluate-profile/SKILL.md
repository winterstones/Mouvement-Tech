---
name: evaluate-profile
description: Évalue le niveau AIDD d'un profil de développeur local ou d'un dépôt distant.
---

# Skill : Evaluate Profile

Permet à un agent d'évaluer rapidement un profil ou un dépôt via la ligne de commande.

## Utilisation
`ash
# Évaluer un profil local de référence
python scripts/evaluate.py perceval
python scripts/evaluate.py arthur

# Évaluer un dossier arbitraire
python scripts/evaluate.py /chemin/vers/dossier

# Évaluer un dépôt GitHub
python scripts/evaluate.py https://github.com/owner/repo
`