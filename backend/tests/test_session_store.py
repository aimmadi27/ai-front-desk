import pytest
from unittest.mock import MagicMock, patch
from app.models.session import Session, Message
from app.services import session_store


@pytest.fixture
def mock_db():
    with patch("app.services.session_store.get_db") as mock:
        db = MagicMock()
        mock.return_value = db
        yield db


def test_create_session(mock_db):
    mock_db.collection.return_value.document.return_value.set = MagicMock()

    session = session_store.create_session(
        call_sid="CA123",
        business_id="biz1",
        caller_number="+17045551234",
    )

    assert session.call_sid == "CA123"
    assert session.business_id == "biz1"
    assert session.messages == []
    assert session.status == "active"


def test_get_session_not_found(mock_db):
    mock_db.collection.return_value.document.return_value.get.return_value.exists = False
    result = session_store.get_session("nonexistent")
    assert result is None


def test_get_session_found(mock_db):
    fake_data = {
        "call_sid": "CA123",
        "business_id": "biz1",
        "caller_number": "+17045551234",
        "messages": [],
        "language": "en",
        "status": "active",
    }
    doc = MagicMock()
    doc.exists = True
    doc.to_dict.return_value = fake_data
    mock_db.collection.return_value.document.return_value.get.return_value = doc

    result = session_store.get_session("CA123")
    assert result is not None
    assert result.call_sid == "CA123"


def test_append_message_raises_on_missing_session(mock_db):
    mock_db.collection.return_value.document.return_value.get.return_value.exists = False
    with pytest.raises(ValueError, match="not found"):
        session_store.append_message("missing", Message(role="user", content="hi"))
