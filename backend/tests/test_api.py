"""Basic API checks for Milestone 2."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_load_sample_and_list_streams():
    load_response = client.post("/api/streams/load-sample")
    assert load_response.status_code == 200
    assert load_response.json()["loaded_rows"] >= 40

    streams_response = client.get("/api/streams")
    assert streams_response.status_code == 200
    streams = streams_response.json()
    assert len(streams) >= 40
    assert "stream_name" in streams[0]


def test_get_single_stream():
    client.post("/api/streams/load-sample")
    response = client.get("/api/streams/S001")
    assert response.status_code == 200
    assert response.json()["stream_id"] == "S001"


def test_summary_metrics():
    client.post("/api/streams/load-sample")
    response = client.get("/api/streams/summary")
    assert response.status_code == 200
    summary = response.json()
    assert summary["total_streams"] >= 40
    assert summary["total_annual_quantity_kg"] > 0
