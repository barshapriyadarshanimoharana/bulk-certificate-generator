import time

def sample_payload():
    return {
        "event_name": "Python Workshop",
        "certificate_title": "Certificate of Completion",
        "recipients": [
            {"name": "Rahul Kumar", "email": "rahul@example.com"},
            {"name": "Priya Sharma", "email": "priya@example.com"},
        ],
    }

def wait_for_completion(client, job_id, attempts=30):
    for _ in range(attempts):
        response = client.get(f"/jobs/{job_id}")
        data = response.json()
        if data["status"] in {"completed", "completed_with_errors"}:
            return data
        time.sleep(0.05)
    return data

def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["docs"] == "/docs"

def test_create_generation_job(client):
    response = client.post("/jobs", json=sample_payload())
    assert response.status_code == 202
    data = response.json()
    assert data["job_id"] > 0
    assert data["total"] == 2

def test_validation_rejects_invalid_email(client):
    payload = sample_payload()
    payload["recipients"][0]["email"] = "not-an-email"
    response = client.post("/jobs", json=payload)
    assert response.status_code == 422

def test_generation_and_status(client):
    response = client.post("/jobs", json=sample_payload())
    job_id = response.json()["job_id"]

    data = wait_for_completion(client, job_id)
    assert data["status"] == "completed"
    assert data["successful"] == 2
    assert data["failed"] == 0
    assert data["progress_percent"] == 100
    assert all(r["status"] == "success" for r in data["recipients"])

def test_certificate_retrieval(client):
    response = client.post("/jobs", json=sample_payload())
    job_id = response.json()["job_id"]
    data = wait_for_completion(client, job_id)

    recipient_id = data["recipients"][0]["recipient_id"]
    certificate = client.get(f"/certificates/{recipient_id}")

    assert certificate.status_code == 200
    assert certificate.headers["content-type"] == "application/pdf"
    assert certificate.content.startswith(b"%PDF")
