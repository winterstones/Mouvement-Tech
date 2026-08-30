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

