from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_kernel_does_not_import_domain_packages():
    kernel = ROOT / "src" / "uaos" / "kernel"
    offenders = []
    for path in kernel.rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        if "import domains" in text or "from domains" in text:
            offenders.append(str(path.relative_to(ROOT)))
    assert not offenders, f"kernel must not import domain packages: {offenders}"


def test_contracts_do_not_import_runtime_or_agent_frameworks():
    contracts = ROOT / "src" / "uaos" / "contracts"
    forbidden = ("dbos", "openai", "langgraph", "temporalio")
    offenders = []
    for path in contracts.rglob("*.py"):
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            if f"import {token}" in text or f"from {token}" in text:
                offenders.append((str(path.relative_to(ROOT)), token))
    assert not offenders, f"contracts must remain framework-independent: {offenders}"
