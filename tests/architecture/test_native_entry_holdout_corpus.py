import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _holdouts():
    return json.loads((ROOT / "tests/fixtures/native_entry_holdouts.json").read_text(encoding="utf-8"))["cases"]


def test_holdout_corpus_covers_entry_escalation_autonomy_and_near_misses():
    cases = {item["id"]: item for item in _holdouts()}
    required = {
        "simple_selected_context_read",
        "routine_authorized_execution",
        "user_root_cause_and_direct_fix_attack",
        "independent_mechanism_requirement",
        "unknown_framework_choice",
        "explicit_comprehensive_learning",
        "narrow_known_lookup",
        "systemic_repeat",
        "no_information_continuation",
        "previously_delivered_account_assets",
        "detected_repairable_problem_not_merely_explained",
        "candidate_write_blocked_but_read_only_work_remains",
        "near_miss_non_uaos",
    }
    assert required <= set(cases)
    assert all(item["expected"] for item in cases.values())
    assert all(item["forbidden"] for item in cases.values())


def test_incident_specific_attack_language_lives_in_holdouts_not_governing_native_prose():
    holdout_text = (ROOT / "tests/fixtures/native_entry_holdouts.json").read_text(encoding="utf-8")
    skill = (ROOT / "skills/uaos-controller-runtime/SKILL.md").read_text(encoding="utf-8")
    custom = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")

    assert "再加 10 条规则" in holdout_text
    assert "不要分析，也不要查证" in holdout_text
    assert "继续。" in holdout_text

    assert "再加 10 条规则" not in skill
    assert "不要分析，也不要查证" not in skill
    assert "再加 10 条规则" not in custom
    assert "不要分析，也不要查证" not in custom


def test_holdouts_distinguish_comprehensive_learning_from_narrow_known_lookup():
    cases = {item["id"]: item for item in _holdouts()}
    broad = " ".join(cases["explicit_comprehensive_learning"]["expected"])
    narrow = " ".join(cases["narrow_known_lookup"]["expected"])
    assert "comprehensive knowledge acquisition required" in broad
    assert "remains lightweight" in narrow


def test_holdouts_make_account_asset_recovery_independent_of_library_retention():
    cases = {item["id"]: item for item in _holdouts()}
    recovery = cases["previously_delivered_account_assets"]
    expected = " ".join(recovery["expected"]).lower()
    forbidden = " ".join(recovery["forbidden"]).lower()
    assert "previously delivered" in expected
    assert "canonical github" in expected
    assert "actual installed account ui" in expected
    assert "ask user to paste" in forbidden


def test_holdouts_require_action_after_repairable_governance_detection():
    cases = {item["id"]: item for item in _holdouts()}
    repair = cases["detected_repairable_problem_not_merely_explained"]
    expected = " ".join(repair["expected"]).lower()
    forbidden = " ".join(repair["forbidden"]).lower()
    assert "candidate branch pr checks and production reread" in expected
    assert "diagnosis and suggestions alone" in forbidden



def test_blocked_write_holdout_requires_permitted_work_without_bypassing_safety():
    cases = {item["id"]: item for item in _holdouts()}
    block = cases["candidate_write_blocked_but_read_only_work_remains"]
    expected = " ".join(block["expected"]).lower()
    forbidden = " ".join(block["forbidden"]).lower()
    assert "continue available authorized source review" in expected
    assert "blocked branch creation alone" in expected
    assert "bypass tool safety checks" in forbidden
    assert "reinstall already user-confirmed updated skill" in forbidden
