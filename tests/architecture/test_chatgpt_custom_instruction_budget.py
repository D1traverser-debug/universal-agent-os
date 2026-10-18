from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_canonical_chatgpt_pointer_fits_all_plan_custom_instruction_budget():
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    recommended = text.split("## Recommended Custom Instructions", 1)[1].split("Do not paste", 1)[0]
    pointer_lines = []
    for line in recommended.splitlines():
        if line == ">":
            pointer_lines.append("")
        elif line.startswith("> "):
            pointer_lines.append(line[2:])
    pointer = "\n".join(pointer_lines).strip()
    assert pointer
    assert len(pointer) <= 1500


def test_portable_account_pointer_matches_canonical_recommendation_exactly():
    """The distributable file must never quietly lag the current bootstrap authority."""
    text = (ROOT / "docs/integration/CHATGPT_CUSTOM_INSTRUCTIONS.md").read_text(encoding="utf-8")
    recommended = text.split("## Recommended Custom Instructions", 1)[1].split("Do not paste", 1)[0]
    lines = []
    for line in recommended.splitlines():
        if line == ">":
            lines.append("")
        elif line.startswith("> "):
            lines.append(line[2:])
    canonical = "\n".join(lines).strip()
    export = (ROOT / "docs/integration/UAOS_CHATGPT_CUSTOM_INSTRUCTIONS.txt").read_text(encoding="utf-8")
    assert export == canonical
    assert "before every substantive response, tool call, or action" in export
    assert "Entry is unconditional; escalation is adaptive" in export
    assert "are work to continue, not blockers" in export
    assert len(export.strip()) <= 1500
