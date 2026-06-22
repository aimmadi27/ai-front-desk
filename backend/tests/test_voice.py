import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.main import app

client = TestClient(app)


@patch("app.api.routes.voice.session_store.create_session")
@patch("app.api.routes.voice._get_business", return_value={"name": "Test Salon", "services": [], "hours": {}})
def test_incoming_call_returns_twiml(mock_biz, mock_create):
    mock_create.return_value = MagicMock()
    response = client.post(
        "/voice/incoming",
        data={"CallSid": "CA123", "From": "+17045551234", "To": "+17045559999"},
    )
    assert response.status_code == 200
    assert "Gather" in response.text or "gather" in response.text.lower()
    assert "application/xml" in response.headers["content-type"]


@patch("app.api.routes.voice.session_store.get_session", return_value=None)
def test_respond_no_session_returns_error(mock_get):
    response = client.post(
        "/voice/respond",
        data={
            "CallSid": "CA_MISSING",
            "SpeechResult": "hello",
            "From": "+17045551234",
        },
    )
    assert response.status_code == 200
    assert "wrong" in response.text.lower() or "hangup" in response.text.lower()
