import pytest
from fastapi.testclient import TestClient
from main import app
import json

client = TestClient(app)

def test_github_webhook_ping():
    response = client.post(
        "/api/webhook/github",
        headers={"X-GitHub-Event": "ping"},
        json={"zen": "Test ping event"}
    )
    assert response.status_code == 200
    assert "message" in response.json()