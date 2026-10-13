import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REQ = ROOT / "docs" / "requirements" / "FROZEN_REQUIREMENTS_v1.0.md"
LOCK = ROOT / "docs" / "requirements" / "FROZEN_REQUIREMENTS_v1.0.gitblob"


def test_frozen_requirements_file_exists_and_matches_locked_git_blob():
    assert REQ.exists(), "frozen requirements file is missing"
    assert LOCK.exists(), "frozen requirements lock is missing"
    expected = LOCK.read_text(encoding="utf-8").strip()
    actual = subprocess.check_output(["git", "hash-object", str(REQ)], cwd=ROOT, text=True).strip()
    assert actual == expected, "Frozen Requirements v1.0 changed. Do not edit it in place; create a new requirements version with an explicit user/evidence-driven reason."
