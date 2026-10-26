import json
from streaming.producer import demo_events


def test_demo_events_have_stable_ids_and_json_primitives():
    events = list(demo_events(8))
    assert len(events) == 8
    assert len({x['transaction_id'] for x in events}) == 8
    assert all('is_fraud' not in x for x in events)
    for item in events:
        assert json.loads(json.dumps(item)) == item


def test_process_message_only_commits_success_and_duplicate(monkeypatch):
    # consumer module only imports the optional dependency when installed.
    import sys
    from types import ModuleType
    fake = ModuleType('confluent_kafka')
    fake.Consumer = object
    fake.KafkaException = RuntimeError
    monkeypatch.setitem(sys.modules, 'confluent_kafka', fake)
    from streaming.consumer import process_message

    class Response:
        def __init__(self, code): self.status_code = code
        def raise_for_status(self):
            if self.status_code >= 400: raise ValueError(self.status_code)

    event = json.dumps({'transaction_id': 'DEMO-1', 'amount': 8}).encode()
    assert process_message(event, 'http://api', post=lambda *a, **k: Response(201)) == 201
    assert process_message(event, 'http://api', post=lambda *a, **k: Response(409)) == 409
    import pytest
    with pytest.raises(ValueError):
        process_message(event, 'http://api', post=lambda *a, **k: Response(503))
    with pytest.raises(ValueError, match='transaction_id'):
        process_message(b'{}', 'http://api', post=lambda *a, **k: Response(201))
