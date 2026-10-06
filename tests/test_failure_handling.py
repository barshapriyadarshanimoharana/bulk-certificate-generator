from app.services import certificate_generator

def test_one_certificate_failure_does_not_stop_other_recipients(client, monkeypatch):
    original = certificate_generator.generate_certificate
    calls = {"count": 0}

    def sometimes_fails(name, email, event_name, certificate_title, recipient_id):
        calls["count"] += 1
        if name == "Bad Recipient":
            raise RuntimeError("Simulated certificate generation failure")
        return original(name, email, event_name, certificate_title, recipient_id)

    monkeypatch.setattr(
        "app.main.generate_certificate",
        sometimes_fails,
    )

    payload = {
        "event_name": "Testing Event",
        "recipients": [
            {"name": "Good Recipient", "email": "good@example.com"},
            {"name": "Bad Recipient", "email": "bad@example.com"},
            {"name": "Another Good", "email": "another@example.com"},
        ],
    }

    response = client.post("/jobs", json=payload)
    assert response.status_code == 202

    import time
    for _ in range(30):
        data = client.get(f"/jobs/{response.json()['job_id']}").json()
        if data["status"] in {"completed", "completed_with_errors"}:
            break
        time.sleep(0.05)

    assert data["status"] == "completed_with_errors"
    assert data["successful"] == 2
    assert data["failed"] == 1
    failed = [r for r in data["recipients"] if r["status"] == "failed"][0]
    assert "Simulated certificate generation failure" in failed["error"]
    assert calls["count"] == 3
