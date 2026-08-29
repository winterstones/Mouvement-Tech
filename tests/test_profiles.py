import pytest
from pathlib import Path
from api.collectors.profile import ProfileCollector, MissingMandatoryProfileDataError
from api.scorer.algo import QuantitativeScorer
from api.scorer.fusion import EvaluationEngine


# Path to reference profiles in laivel-up-sujet
PROFILES_DIR = Path(__file__).resolve().parent.parent.parent / "laivel-up-sujet" / "profiles"


def evaluate_profile_by_id(profile_id: str):
    profile_path = PROFILES_DIR / profile_id
    profile_data = ProfileCollector.load_profile(profile_path)
    quantitative_scores = QuantitativeScorer.score_all(profile_data)
    result = EvaluationEngine.evaluate(profile_data, quantitative_scores)
    return result


def test_perceval_is_red():
    result = evaluate_profile_by_id("perceval")
    assert result.level.id == "red"
    assert result.level.rank == 1
    assert result.axes.taille.level == "red"
    assert result.axes.harness.level == "red"
    assert result.axes.intervention.level == "red"
    assert len(result.warnings) > 0  # Inconsistency detected between self-claim and reality


def test_bohort_is_blue():
    result = evaluate_profile_by_id("bohort")
    assert result.level.id == "blue"
    assert result.level.rank == 2
    assert result.axes.taille.level == "blue"
    assert result.axes.harness.level == "blue"
    assert result.axes.intervention.level == "blue"
    assert result.progression.next_level.id == "green"


def test_leodagan_is_green():
    result = evaluate_profile_by_id("leodagan")
    assert result.level.id == "green"
    assert result.level.rank == 3
    assert result.axes.taille.rank >= 3
    assert result.axes.harness.rank >= 3
    assert result.axes.intervention.rank >= 3
    assert result.axes.parallele.rank == 3  # Parallelism 1 limits him to Green
    assert result.limiting_axis in ["parallele", "harness", "intervention", "taille"]


def test_arthur_is_copper():
    result = evaluate_profile_by_id("arthur")
    assert result.level.id == "copper"
    assert result.level.rank == 4
    assert result.axes.taille.rank >= 4
    assert result.axes.harness.rank >= 4
    assert result.axes.intervention.rank >= 4
    assert result.axes.parallele.rank >= 4  # Arthur runs 4 concurrent branches median, up to 7
    assert result.progression.next_level.id == "silver"


def test_missing_mandatory_file_raises_error(tmp_path):
    # Only profile.json, missing git-activity.json
    (tmp_path / "profile.json").write_text('{"profile_id": "test"}', encoding="utf-8")
    with pytest.raises(MissingMandatoryProfileDataError):
        ProfileCollector.load_profile(tmp_path)
