"""Baseline tests for Flask application routes.

Documents current behavior of web endpoints and request/response handling.
"""

import pytest
from app import CURRENT, app


@pytest.fixture(autouse=True)
def reset_current_state():
    """Ensure each Flask route test starts with a clean in-memory game state."""
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None
    yield
    CURRENT["puzzle"] = None
    CURRENT["solution"] = None


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

    def test_new_game_with_easy_difficulty(self, client):
        """GET /new?difficulty=easy should return 45-clue puzzle."""
        response = client.get("/new?difficulty=easy")
        assert response.status_code == 200
        data = response.get_json()
        assert "puzzle" in data
        puzzle = data["puzzle"]
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 45

    def test_new_game_with_medium_difficulty(self, client):
        """GET /new?difficulty=medium should return 38-clue puzzle."""
        response = client.get("/new?difficulty=medium")
        assert response.status_code == 200
        data = response.get_json()
        assert "puzzle" in data
        puzzle = data["puzzle"]
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 38

    def test_new_game_with_hard_difficulty(self, client):
        """GET /new?difficulty=hard should return 32-clue puzzle."""
        response = client.get("/new?difficulty=hard")
        assert response.status_code == 200
        data = response.get_json()
        assert "puzzle" in data
        puzzle = data["puzzle"]
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 32

    def test_new_game_with_invalid_difficulty(self, client):
        """GET /new?difficulty=impossible should return 400 error."""
        response = client.get("/new?difficulty=impossible")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "invalid_difficulty"
        assert "message" in data

    def test_new_game_difficulty_case_insensitive(self, client):
        """GET /new?difficulty=EASY should work (case-insensitive)."""
        response = client.get("/new?difficulty=EASY")
        assert response.status_code == 200
        data = response.get_json()
        puzzle = data["puzzle"]
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 45

    def test_new_game_default_clues_when_no_params(self, client):
        """GET /new with no parameters should use default 35 clues."""
        response = client.get("/new")
        assert response.status_code == 200
        data = response.get_json()
        puzzle = data["puzzle"]
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 35


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

    def test_check_solution_ignores_blank_editable_cells(self, client):
        """Blank editable cells should not be counted as incorrect."""
        client.get("/new")
        solution = CURRENT["solution"]
        board = [row[:] for row in solution]
        board[0][0] = 0
        response = client.post(
            "/check",
            json={"board": board},
            content_type="application/json",
        )
        data = response.get_json()
        assert data["incorrect"] == []

    def test_check_solution_reports_non_empty_incorrect_cells(self, client):
        """Only non-empty mismatches should be reported as incorrect."""
        client.get("/new")
        solution = CURRENT["solution"]
        board = [row[:] for row in solution]
        board[0][0] = 1 if solution[0][0] != 1 else 2
        response = client.post(
            "/check",
            json={"board": board},
            content_type="application/json",
        )
        data = response.get_json()
        assert [0, 0] in data["incorrect"]
        assert len(data["incorrect"]) == 1

    def test_check_solution_error_without_game(self, client):
        """POST /check without a game in progress should return error."""
        board = [[0] * 9 for _ in range(9)]
        response = client.post(
            "/check",
            json={"board": board},
            content_type="application/json",
        )
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data

