def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_decode_happy_path(client):
    response = client.post("/v1/briefs/decode", json={"text": "We need a landing page"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "succeeded"
    assert body["run_id"] >= 1
    assert body["result"]["summary"]
    assert body["error_code"] is None
    assert "raw_output" not in body
    assert "input_text" not in body


def test_decode_provider_failure(client):
    response = client.post("/v1/briefs/decode", json={"text": "FAIL:provider x"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["error_code"] == "provider_error"
    assert body["result"] is None


def test_decode_validation_failure(client):
    response = client.post("/v1/briefs/decode", json={"text": "FAIL:malformed x"})
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "failed"
    assert body["error_code"] == "validation_error"


def test_decode_empty_text_rejected(client):
    response = client.post("/v1/briefs/decode", json={"text": ""})
    assert response.status_code == 422


def test_get_run_roundtrip(client):
    created = client.post("/v1/briefs/decode", json={"text": "roundtrip"}).json()
    response = client.get(f"/v1/briefs/runs/{created['run_id']}")
    assert response.status_code == 200
    assert response.json()["run_id"] == created["run_id"]
    assert response.json()["status"] == "succeeded"


def test_get_run_not_found(client):
    assert client.get("/v1/briefs/runs/99999").status_code == 404
