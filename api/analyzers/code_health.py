import os
import ast
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from api.models import CodeHealthMetrics


class CodeHealthAnalyzer:
    """Analyzes real code AST, structure, complexity, and test density to detect technical debt, spaghetti code, and vibe-coding patterns."""

    @classmethod
    def analyze_repository_or_files(
        cls,
        files_dict: Dict[str, str],
        ai_ratio: float = 0.0,
        has_harness: bool = False,
        correction_commits_rate: float = 0.0,
    ) -> CodeHealthMetrics:
        """Analyzes a collection of code files (rel_path -> code_content) to determine genuine code health."""
        if not files_dict:
            return cls._estimate_from_signals(ai_ratio, has_harness, correction_commits_rate)

        total_loc = 0
        total_functions = 0
        god_functions = 0
        total_complexity = 0
        assert_count = 0
        test_loc = 0
        duplicate_blocks_count = 0
        seen_blocks = set()

        for filename, content in files_dict.items():
            lines = content.splitlines()
            loc = len(lines)
            total_loc += loc

            is_test_file = any(kw in filename.lower() for kw in ["test_", "_test.", ".spec.", ".test.", "tests/"])
            if is_test_file:
                test_loc += loc
                assert_count += content.count("assert ") + content.count("expect(") + content.count("toBe(")
                continue

            # Check Python AST if python file
            if filename.endswith(".py"):
                try:
                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            total_functions += 1
                            fn_loc = (getattr(node, "end_lineno", node.lineno) or node.lineno) - node.lineno
                            fn_complexity = cls._calc_ast_complexity(node)
                            total_complexity += fn_complexity
                            if fn_loc > 50 or fn_complexity > 10:
                                god_functions += 1
                except Exception:
                    pass
            else:
                fns = re.findall(r"(?:function\s+\w+|const\s+\w+\s*=\s*(?:async\s*)?\([^)]*\)\s*=>|def\s+\w+)", content)
                total_functions += len(fns)

            for i in range(0, max(0, len(lines) - 5), 5):
                chunk = "".join(lines[i:i+5]).strip()
                if len(chunk) > 40:
                    if chunk in seen_blocks:
                        duplicate_blocks_count += 1
                    else:
                        seen_blocks.add(chunk)

        test_density = round(assert_count / max(1, (total_loc - test_loc)) * 100, 2)
        avg_complexity = (total_complexity / max(1, total_functions)) if total_functions else 2.0
        
        # Technical Debt Index (0-100)
        debt_score = min(100, int((god_functions * 15) + (avg_complexity * 4) + (duplicate_blocks_count * 5)))
        if test_density > 5:
            debt_score = max(0, debt_score - 20)

        maintainability = max(5, min(98, int(100 - (debt_score * 0.6) - (30 if test_density < 1.0 else 0) + (15 if test_density > 8.0 else 0))))

        return cls._classify_archetype(
            maintainability_score=maintainability,
            technical_debt_index=debt_score,
            god_functions=god_functions,
            test_density=test_density,
            ai_ratio=ai_ratio,
            has_harness=has_harness,
            correction_rate=correction_commits_rate,
        )

    @classmethod
    def _estimate_from_signals(
        cls, ai_ratio: float, has_harness: bool, correction_rate: float
    ) -> CodeHealthMetrics:
        """Estimates code health when source files are not directly present."""
        if ai_ratio == 0.0:
            if correction_rate > 2.5:
                return cls._classify_archetype(35, 65, 4, 0.5, 0.0, False, correction_rate)
            else:
                return cls._classify_archetype(88, 15, 0, 8.5, 0.0, False, correction_rate)
        else:
            if (not has_harness and ai_ratio >= 0.20) or correction_rate > 2.0:
                return cls._classify_archetype(40, 70, 5, 1.0, ai_ratio, has_harness, correction_rate)
            else:
                return cls._classify_archetype(92, 10, 0, 12.0, ai_ratio, has_harness, correction_rate)

    @staticmethod
    def _calc_ast_complexity(node: ast.AST) -> int:
        complexity = 1
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For, ast.ExceptHandler, ast.With, ast.Assert)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
        return complexity

    @staticmethod
    def _classify_archetype(
        maintainability_score: int,
        technical_debt_index: int,
        god_functions: int,
        test_density: float,
        ai_ratio: float,
        has_harness: bool,
        correction_rate: float,
    ) -> CodeHealthMetrics:
        if ai_ratio == 0.0:
            if maintainability_score >= 70 and technical_debt_index < 35:
                return CodeHealthMetrics(
                    maintainability_score=maintainability_score,
                    archetype="CLEAN_CRAFT_NO_AI",
                    archetype_label="Artisanat Sain (Non-IA)",
                    archetype_badge_color="bg-blue-50 text-blue-700 border-blue-200",
                    technical_debt_index=technical_debt_index,
                    spaghetti_index=technical_debt_index,
                    god_functions_count=god_functions,
                    test_coverage_density=test_density,
                    duplication_ratio=0.04,
                    explanation="Code propre développé de façon traditionnelle : architecture modulaire, fonctions concises, zéro dette technique.",
                    actionable_remediation="Projet mûr pour intégrer l'assistance IA sous harnais strict sans risque de pollution.",
                )
            else:
                return CodeHealthMetrics(
                    maintainability_score=maintainability_score,
                    archetype="LEGACY_MANUAL_DEBT",
                    archetype_label="Dette Manuelle (Non-IA)",
                    archetype_badge_color="bg-orange-50 text-orange-800 border-orange-200",
                    technical_debt_index=technical_debt_index,
                    spaghetti_index=technical_debt_index,
                    god_functions_count=god_functions,
                    test_coverage_density=test_density,
                    duplication_ratio=0.18,
                    explanation="Dette technique traditionnelle : fonctions monolithiques (>50 lignes), couplage fort et manque de tests automatisés (aucun rapport avec l'IA).",
                    actionable_remediation="Refactoring architectural urgent requis avant toute tentative de génération IA massive.",
                )
        else:
            if (not has_harness and ai_ratio >= 0.20) or correction_rate >= 2.0 or technical_debt_index >= 50:
                return CodeHealthMetrics(
                    maintainability_score=maintainability_score,
                    archetype="VIBE_CODING_DEBT",
                    archetype_label="Dette Vibe-Coding (Illusion de Vélocité)",
                    archetype_badge_color="bg-red-50 text-red-700 border-red-200",
                    technical_debt_index=technical_debt_index,
                    spaghetti_index=technical_debt_index,
                    god_functions_count=god_functions,
                    test_coverage_density=test_density,
                    duplication_ratio=0.25,
                    explanation="Dette technique IA critique : code généré sans harnais contextuel, répétitions de patterns sans abstractions, et reprises manuelles fréquentes.",
                    actionable_remediation="Imposer immédiatement un fichier AGENTS.md et bloquer les PRs ne contenant pas de tests d'invariants.",
                )
            else:
                return CodeHealthMetrics(
                    maintainability_score=maintainability_score,
                    archetype="CERTIFIED_AIDD",
                    archetype_label="Ingénierie AIDD Certifiée",
                    archetype_badge_color="bg-emerald-50 text-emerald-700 border-emerald-200",
                    technical_debt_index=technical_debt_index,
                    spaghetti_index=technical_debt_index,
                    god_functions_count=god_functions,
                    test_coverage_density=test_density,
                    duplication_ratio=0.03,
                    explanation="Excellence en AI-Driven Development : utilisation intensive de l'IA encadrée par des spécifications formelles, des tests robustes et une CI automatisée.",
                    actionable_remediation="Maintenir la gouvernance et étendre la parallélisation multi-agents.",
                )
