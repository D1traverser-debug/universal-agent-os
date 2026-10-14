import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_all_twenty_frozen_scenarios_have_semantic_evidence_entries():
    data=json.loads((ROOT/'docs/assurance/FROZEN_SCENARIO_COVERAGE.json').read_text())
    entries=data['scenarios']
    assert [entry['id'] for entry in entries]==[f'S{i:02d}' for i in range(1,21)]
    assert all(entry['evidence'] for entry in entries)
    assert all(entry['local_status'] in {'CONTRACT_PASS','STRUCTURAL_PASS','POLICY_PASS','MULTIFAULT_PASS'} for entry in entries)

def test_readiness_does_not_confuse_scoped_evidence_with_global_production_readiness():
    data=json.loads((ROOT/'docs/assurance/PRODUCTION_READINESS.json').read_text())
    assert 'PRODUCTION_READY' not in data['status']
    expected={f'docs/requirements/FROZEN_REQUIREMENTS_v1.{i}.md' for i in range(5)}
    assert expected.issubset(set(data['requirements_authority']))
    assert data['verification']['phase0_18_prior_baseline']=='PASS_RETAINED'
    assert data['mandatory_external_services']==[]
    assert any('same-model self-critique' in item for item in data['known_limitations'])
