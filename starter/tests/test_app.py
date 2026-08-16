"""Baseline tests for Flask application routes.

Documents current behavior of web endpoints and request/response handling.
"""

import pytest
from app import app


@pytest.fixture
def client():
    """Provide a test client for the Flask app."""
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


class TestIndexRoute:
    """Test home page route."""

    def test_index_returns_200(self, client):
        """GET / should return 200 OK."""
        response = client.get("/")
        assert response.status_code == 200

    def test_index_returns_html(self, client):
        """GET / should return HTML content."""
        response = client.get("/")
        assert response.content_type.startswith("text/html")


class TestNewGameRoute:
    """Test new game puzzle generation endpoint."""

    def test_new_game_returns_200(self, client):
        """GET /new should return 200 OK."""
        response = client.get("/new")
        assert response.status_code == 200

    def test_new_game_returns_json(self, client):
        """GET /new should return JSON response."""
        response = client.get("/new")
        assert response.content_type.startswith("application/json")

    def test_new_game_returns_puzzle(self, client):
        """GET /new should return a puzzle."""
        response = client.get("/new")
        data = response.get_json()
        assert data is not None
        assert "puzzle" in data

    def test_new_game_with_clues_parameter(self, client):
        """GET /new?clues=40 should accept clues parameter."""
        response = client.get("/new?clues=40")
        assert response.status_code == 200
        data = response.get_json()
        assert "puzzle" in data


class TestCheckSolutionRoute:
    """Test solution checking endpoint."""

    def test_check_returns_json(self, client):
        """POST /check should return JSON response."""
        # First create a game
        client.get("/new")
        board = [[0] * 9 for _ in range(9)]
        response = client.post(
            "/check",
            json={"board": board},
            content_type="application/json",
        )
        assert response.content_type.startswith("application/json")

    def test_check_response_has_incorrect(self, client):
        """POST /check should return incorrect cells."""
        # First create a game
        client.get("/new")
        board = [[0] * 9 for _ in range(9)]
        response = client.post(
            "/check",
            json={"board": board},
            content_type="application/json",
        )
        data = response.get_json()
        assert data is not None
        assert "incorrect" in data
