"""Shared fixtures for API tests."""

import pytest

from src import data
from src.app import create_app


@pytest.fixture
def client():
    data.reset_students()
    app = create_app()
    app.config.update(TESTING=True)
    with app.test_client() as test_client:
        yield test_client
    data.reset_students()


@pytest.fixture
def valid_student():
    return {"firstName": "Nora", "lastName": "Dupont", "email": "nora.dupont@example.com", "grade": 15.5, "field": "physique"}
