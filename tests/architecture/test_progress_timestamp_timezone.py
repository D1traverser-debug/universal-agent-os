import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_progress_timestamp_is_rendered_in_human_readable_beijing_time():
    policy = json.loads((ROOT / "config/SESSION_INTERACTION_POLICY.json").read_text(encoding="utf-8"))
    report = policy["inherited_session_progress_report"]
    assert report["timestamp_timezone"] == "Asia/Shanghai"
    assert report["timestamp_display_format"] == "YYYY-MM-DD HH:mm:ss（北京时间）"
    rule = report["timestamp_timezone_rule"]
    assert "human-readable format" in rule
    assert "Do not show ISO-8601 separators such as T" in rule
    assert "+08:00" in rule
    assert "freshest authoritative timestamp" in rule
    assert tuple(map(int, policy["policy_version"].split("."))) >= (1, 7, 2)
