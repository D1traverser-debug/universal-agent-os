import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def test_financial_business_authority_is_external_and_unique():
    system_map = _json("config/SYSTEM_MAP.json")
    registry = _json("config/AGENT_REGISTRY.json")
    financial = system_map["domains"]["financial_writing"]
    assert financial["repository"] == "D1traverser-debug/financial-writing-agent"
    assert financial["entrypoint"] == "UAOS_SKILL.md"
    assert financial["business_contract"] == "config/EXECUTION_CONTRACT.json"
    assert financial["business_state"] == "workspaces/articles/{task_id}/STATE.json"
    registered = next(item for item in registry["agents"] if item["domain_id"] == "financial_writing")
    assert registered["repository"] == financial["repository"]
    assert registered["agent_manifest_ref"] == ".uaos/MANIFEST.json"
    assert registered["capability_ref"] == ".uaos/CAPABILITIES.json"
    assert registered["uaos_adapter_ref"] == ".uaos/ADAPTER.json"
    assert not (ROOT / "domains" / "financial_writing").exists()


def test_binding_policy_does_not_redefine_hierarchical_mutation_semantics():
    binding = _json("config/BINDING_POLICY.json")
    authority = _json("config/AUTHORITY_WRITE_POLICY.json")
    assert binding["authority_write_policy"] == "config/AUTHORITY_WRITE_POLICY.json"
    assert binding["mutation_rule"] == "DELEGATE_TO_AUTHORITY_WRITE_POLICY__BINDING_VALIDATION_MUST_NOT_REDEFINE_MUTATION_HIERARCHY"
    assert authority["context_model"]["hierarchy"] == "UAOS_PARENT_OF_REGISTERED_DOMAINS"
    rules = "\n".join(authority["mutation_admission"]["rules"])
    assert "registered ancestor may mutate a descendant" in rules
    assert "DOMAIN:X -> UAOS" in rules
    assert "DOMAIN:X -> DOMAIN:Y" in rules


def test_financial_binding_requires_current_common_capability_inheritance():
    binding = _json("config/BINDING_POLICY.json")
    common = _json("config/COMMON_CAPABILITIES.json")
    ids = {item["capability_id"] for item in common["capabilities"]}
    assert "CAPABILITY_COMMON_INHERITANCE" in binding["checks"]
    assert {
        "cross_chat_continuity_and_recovery",
        "hierarchical_authority_governance",
        "adaptive_deliberation_and_parent_guidance",
        "governed_self_evolution",
    }.issubset(ids)


def test_financial_router_does_not_own_child_article_identity_or_implementation_details():
    binding = _json("config/BINDING_POLICY.json")
    router = _json("state/tasks/financial-writing-main.json")
    index = _json("state/TASK_INDEX.json")
    indexed = next(item for item in index["tasks"] if item["task_id"] == "financial-writing:main")

    assert "DISTINCT_BY_DEFAULT" in binding["identity_boundary_rule"]
    assert router["task_type"] == "article_workspace_router"
    assert router["active_domain_state_ref"] is None
    assert "DISTINCT_NAMESPACES" in router["identity_boundary"]
    assert "OPAQUE_REFERENCE" in router["domain_reference_semantics"]
    assert "same task_id" not in router["next_action"].lower()
    assert "article_binding_validator" not in router
    assert "package_version" not in json.dumps(router)
    assert "capability_profile_version" not in json.dumps(router)
    assert "release_commit" not in json.dumps(router)
    assert "ci_run" not in json.dumps(router)
    assert indexed["state_model"] == "UAOS_NATIVE"
    assert indexed["task_type"] == "article_workspace_router"
    assert "owns its own article identity/state" in indexed["semantic_summary"]
