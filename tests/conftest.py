import pytest
from app import create_app
from unittest.mock import patch, MagicMock
from util import TestConfig


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(TestConfig)
    with flask_app.test_client() as testing_client:
        with flask_app.app_context():
            yield testing_client


@pytest.fixture
def mock_firestore():
    with patch('firebase_admin.firestore.client') as mock_client:
        mock_db = MagicMock()
        mock_client.return_value = mock_db
        mock_doc_ref = MagicMock()
        mock_db.collection.return_value.document.return_value = mock_doc_ref
        yield mock_db, mock_doc_ref
