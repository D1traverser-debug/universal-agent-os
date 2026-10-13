import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def test_all_twenty_frozen_scenarios_have_semantic_evidence_entries():
    data=json.loads((ROOT/'docs/assurance/FROZEN_SCENARIO_COVERAGE.json').read_text())
    entries=data['scenarios']
    assert [entry['id'] for entry in entries]==[f'S{i:02d}' for i in range(1,21)]
    assert all(entry['evidence'] for entry in entries)
    assert all(entry['local_status'] in {'CONTRACT_PASS','STRUCTURAL_PASS','POLICY_PASS','MULTIFAULT_PASS'} for entry in entries)

def test_readiness_does_not_confuse_local_contract_pass_with_production_readiness():
    data=json.loads((ROOT/'docs/assurance/PRODUCTION_READINESS.json').read_text())
    assert data['status']=='IMPLEMENTATION_BASELINE_COMPLETE__PRODUCTION_NOT_READY'
    blocker_ids={item['id'] for item in data['open_blockers']}
    assert {'R1','R2','R3','R4','R5','R6','R7','R8'}==blocker_ids
    assert data['local_integrated_test_status']=='PASS'
