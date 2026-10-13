import pytest
from uaos.state import InMemoryAppendOnlyLedger


def test_ledger_is_append_only_and_sequences_events():
    ledger = InMemoryAppendOnlyLedger()
    e1 = ledger.append(event_id="e1", aggregate_type="task", aggregate_id="t1", event_type="created", payload={"v": 1})
    e2 = ledger.append(event_id="e2", aggregate_type="task", aggregate_id="t1", event_type="updated", payload={"v": 2})
    assert (e1.sequence, e2.sequence) == (1, 2)
    assert [e.event_type for e in ledger.events_for("task", "t1")] == ["created", "updated"]
    with pytest.raises(ValueError, match="duplicate event_id"):
        ledger.append(event_id="e2", aggregate_type="task", aggregate_id="t1", event_type="again", payload={})
