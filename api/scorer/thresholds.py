from typing import Dict, Any
from api.models import AIDDLevel


LEVELS: Dict[str, AIDDLevel] = {
    "white": AIDDLevel(id="white", label="❖ White", rank=0),
    "red": AIDDLevel(id="red", label="🔺 Red", rank=1),
    "blue": AIDDLevel(id="blue", label="🔹 Blue", rank=2),
    "green": AIDDLevel(id="green", label="🟢 Green", rank=3),
    "copper": AIDDLevel(id="copper", label="🥉 Copper", rank=4),
    "silver": AIDDLevel(id="silver", label="🥈 Silver", rank=5),
    "gold": AIDDLevel(id="gold", label="🥇 Gold", rank=6),
}

RANK_TO_LEVEL: Dict[int, AIDDLevel] = {lvl.rank: lvl for lvl in LEVELS.values()}


# Definitions of axes criteria & thresholds
AXES_CRITERIA = {
    "taille": {
        "description": "La taille habituelle des features livrées avec l'IA.",
        "levels": {
            0: "Aucune",
            1: "S (petite ou triviale)",
            2: "M (complexité moyenne)",
            3: "L (multi-étapes)",
            4: "L-XL (multi-modules)",
            5: "L-XL",
            6: "L-XL",
        },
    },
    "harness": {
        "description": "Ce qui a été mis en place autour du modèle (contexte, règles, agents, boucles).",
        "levels": {
            0: "Rien",
            1: "Prompts simples sans fichiers de contexte",
            2: "Context engineering (AGENTS.md / CLAUDE.md présent)",
            3: "Context engineering + Behavior (règles et agents versionnés)",
            4: "Context engineering + Behavior avancé (skills, workflows, worktrees)",
            5: "Context engineering + Behavior + Boucles automatiques de validation",
            6: "Agents totalement autonomes avec boucles complètes",
        },
    },
    "intervention": {
        "description": "Niveau d'intervention humaine après génération.",
        "levels": {
            0: "Non applicable",
            1: "Après coup, sur la majorité (beaucoup de commits correctifs)",
            2: "Après coup, sur une partie (quelques commits correctifs)",
            3: "Aux étapes clés (presque aucun commit correctif, validation préalable)",
            4: "Aux étapes clés",
            5: "Jamais une fois la tâche cadrée (aucun commit humain après ouverture)",
            6: "Jamais, cadrage compris (autonomie totale)",
        },
    },
    "parallele": {
        "description": "Nombre de chantiers / branches menés de front de façon habituelle.",
        "levels": {
            0: "0 fil",
            1: "1 fil de front (médiane 1)",
            2: "1 fil de front (médiane 1)",
            3: "1 fil de front (médiane 1)",
            4: "3+ fils menés de front (médiane >= 3)",
            5: "3+ fils menés de front (médiane >= 3)",
            6: "3+ fils menés de front (médiane >= 3)",
        },
    },
}
