# Brainstorm : Dogfooding & Auto-Évaluation de Mouvement-Tech

## Problématique
Comment prouver au jury et au CTO que Mouvement-Tech applique à lui-même les critères qu'il évalue chez les autres ?

## Arbitrages
1. **Context Engineering :** `AGENTS.md` + `CLAUDE.md` + `.cursorrules` + `docs/knowledge/`.
2. **Behavior :** Règles et compétences modulaires versionnées.
3. **Boucles Fermées :** Script autonome `loop_fix.py` et CI GitHub Actions.
4. **Parallélisme :** Support des git worktrees avec `.worktreeinclude`.
5. **Traçabilité :** 100% des commits co-signés `Co-authored-by: Assistant`.