import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_progress_timestamp_is_rendered_in_beijing_time():
    policy = json.loads((ROOT / "config/SESSION_INTERACTION_POLICY.json").read_text(encoding="utf-8"))
    report = policy["inherited_session_progress_report"]
    assert report["timestamp_timezone"] == "Asia/Shanghai"
    assert "UTC+08:00" in report["timestamp_timezone_rule"]
    assert "freshest authoritative timestamp" in report["timestamp_timezone_rule"]
    assert policy["policy_version"] == "1.7.1"
