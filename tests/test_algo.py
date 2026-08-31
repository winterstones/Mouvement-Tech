from api.scorer.algo import QuantitativeScorer


def test_score_taille_empty():
    score = QuantitativeScorer.score_taille({})
    assert score.level == "white"
    assert score.rank == 0


def test_score_taille_s():
    git_act = {
        "pull_requests": {
            "total": 10,
            "size_distribution": {"xs": 5, "s": 5, "m": 0, "l": 0, "xl": 0},
            "median_lines_changed": 30,
        }
    }
    score = QuantitativeScorer.score_taille(git_act)
    assert score.level == "red"
    assert score.rank == 1


def test_score_taille_m():
    git_act = {
        "pull_requests": {
            "total": 10,
            "size_distribution": {"xs": 1, "s": 1, "m": 6, "l": 2, "xl": 0},
            "median_lines_changed": 200,
        }
    }
    score = QuantitativeScorer.score_taille(git_act)
    assert score.level == "blue"
    assert score.rank == 2


def test_score_harness_white():
    score = QuantitativeScorer.score_harness({}, {})
    assert score.level == "white"
    assert score.rank == 0


def test_score_harness_blue():
    git_act = {"context_files": {"agents_md": True, "rules_count": 0}}
    score = QuantitativeScorer.score_harness(git_act, {"AGENTS.md": "contexte projet"})
    assert score.level == "blue"
    assert score.rank == 2


def test_score_parallele_multi():
    git_act = {"parallelism": {"median_concurrent_branches": 4, "max_concurrent_branches": 6}}
    score = QuantitativeScorer.score_parallele(git_act)
    assert score.level == "copper"
    assert score.rank == 4


def test_score_harness_green_without_agents_md():
    # Hooks CI and modular rules without strict AGENTS.md
    git_act = {"context_files": {"agents_md": False, "rules_count": 2, "skills_count": 1, "hooks_count": 2}}
    score = QuantitativeScorer.score_harness(git_act, {})
    assert score.level == "green"
    assert score.rank == 3


def test_score_harness_copper_with_auto_loops():
    # Auto-loops in CI or scripts with hooks
    git_act = {"context_files": {"agents_md": False, "rules_count": 0, "skills_count": 0, "hooks_count": 2, "has_auto_loops": True}}
    score = QuantitativeScorer.score_harness(git_act, {})
    assert score.level == "copper"
    assert score.rank == 4


def test_score_harness_aider_config():
    # Repository using .aider.conf.yml and benchmark auto-loops
    repo_files = {".aider.conf.yml": "model: gpt-4o", "CONVENTIONS.md": "Code style"}
    git_act = {"context_files": {"agents_md": True, "skills_count": 2, "rules_count": 2, "hooks_count": 2, "has_auto_loops": True}}
    score = QuantitativeScorer.score_harness(git_act, repo_files)
    assert score.level in ["copper", "silver"]
    assert score.rank >= 4


def test_vibe_risk_zero_for_non_ai_developer():
    from api.scorer.fusion import EvaluationEngine
    # Profile of a developer at Level 0 (White) who never uses AI
    profile_data = {
        "profile_id": "traditional_dev",
        "profile_info": {"role": "Backend Dev", "stack": ["Python"]},
        "git_activity": {
            "pull_requests": {"total": 5, "size_distribution": {"xs": 5, "s": 0, "m": 0, "l": 0, "xl": 0}, "median_lines_changed": 10, "median_correction_commits_after_open": 2},
            "commits": {"total": 20, "ai_coauthored_ratio": 0.0},
            "context_files": {"agents_md": False, "rules_count": 0, "skills_count": 0, "hooks_count": 0, "has_auto_loops": False},
            "assistant_usage": {"declared_tools": [], "sessions_per_week": 0},
            "parallelism": {"median_concurrent_branches": 1, "max_concurrent_branches": 1},
            "ci": {"failure_rate": 0.20},
        },
        "repo_context_files": {},
        "declaratif": "Je développe en Python classique avec vim sans outils IA.",
        "session": None,
        "available_sources": ["git_activity"],
    }
    scores = QuantitativeScorer.score_all(profile_data)
    result = EvaluationEngine.evaluate(profile_data, scores)
    
    assert result.level.id == "white"
    assert result.vibe_risk is not None
    assert result.vibe_risk.risk_score == 0
    assert result.vibe_risk.risk_level == "Nul (Non exposé)"


def test_code_health_archetypes():
    from api.analyzers.code_health import CodeHealthAnalyzer
    
    # 1. Clean Craft without AI (Modular code with tests, 0% AI)
    clean_files = {
        "src/auth.py": "def login(user, pwd):\n    if not user: return False\n    return True\n",
        "tests/test_auth.py": "def test_login():\n    assert login('alice', 'secret') == True\n    assert login('', '') == False\n",
    }
    m_clean = CodeHealthAnalyzer.analyze_repository_or_files(clean_files, ai_ratio=0.0, has_harness=False)
    assert m_clean.archetype == "CLEAN_CRAFT_NO_AI"
    assert m_clean.maintainability_score >= 70
    assert m_clean.technical_debt_index < 35

    # 2. Legacy Manual Debt without AI (God function >50 lines with deep complexity, 0 tests, 0% AI)
    god_fn = "def do_everything():\n" + ("    if True:\n        for i in range(10):\n            x = i\n" * 15)
    debt_files = {
        "legacy/god_module.py": god_fn
    }
    m_debt = CodeHealthAnalyzer.analyze_repository_or_files(debt_files, ai_ratio=0.0, has_harness=False)
    assert m_debt.archetype == "LEGACY_MANUAL_DEBT"
    assert m_debt.god_functions_count >= 1
    assert m_debt.technical_debt_index >= 30

    # 3. Vibe Coding Debt (AI ratio 80%, no harness, high corrective rework)
    m_vibe = CodeHealthAnalyzer.analyze_repository_or_files(debt_files, ai_ratio=0.8, has_harness=False, correction_commits_rate=3.5)
    assert m_vibe.archetype == "VIBE_CODING_DEBT"

    # 4. Certified AIDD (AI ratio 70%, AGENTS.md harness, rich tests)
    m_aidd = CodeHealthAnalyzer.analyze_repository_or_files(clean_files, ai_ratio=0.7, has_harness=True, correction_commits_rate=0.2)
    assert m_aidd.archetype == "CERTIFIED_AIDD"



