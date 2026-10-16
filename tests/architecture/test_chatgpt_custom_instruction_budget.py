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
