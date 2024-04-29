from fastapi.testclient import TestClient

from nsls2api.main import app

client = TestClient(app)

def test_healthy_endpoint():
    response = client.get("/healthy")
    assert response.status_code == 200
    assert response.text == "OK"

