"""Baseline tests for Flask application routes.

Documents current behavior of web endpoints and request/response handling.
"""

import copy

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


class TestHintRoute:
    """Test hint endpoint."""

    def test_hint_returns_json(self, client):
        """GET /hint should return JSON response."""
        client.get("/new")
        response = client.get("/hint")
        assert response.content_type.startswith("application/json")

    def test_hint_returns_correct_structure(self, client):
        """GET /hint should return row, col, value, and hints_used."""
        client.get("/new")
        response = client.get("/hint")
        assert response.status_code == 200
        data = response.get_json()
        assert "row" in data
        assert "col" in data
        assert "value" in data
        assert "hints_used" in data

    def test_hint_returns_valid_coordinates(self, client):
        """Hint coordinates should be within 0-8."""
        client.get("/new")
        response = client.get("/hint")
        data = response.get_json()
        assert 0 <= data["row"] < 9
        assert 0 <= data["col"] < 9

    def test_hint_returns_valid_value(self, client):
        """Hint value should be 1-9."""
        client.get("/new")
        response = client.get("/hint")
        data = response.get_json()
        assert 1 <= data["value"] <= 9

    def test_hint_increments_hints_used(self, client):
        """Each hint should increment hints_used count."""
        client.get("/new")
        response1 = client.get("/hint")
        hints1 = response1.get_json()["hints_used"]
        assert hints1 == 1

        response2 = client.get("/hint")
        hints2 = response2.get_json()["hints_used"]
        assert hints2 == 2

    def test_hint_error_without_game(self, client):
        """GET /hint without a game in progress should return error."""
        response = client.get("/hint")
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert data["error"] == "no_game"

    def test_hint_returns_valid_cell_from_puzzle(self, client):
        """Hint should return a cell that is empty in the puzzle."""
        client.get("/new")
        puzzle = CURRENT["puzzle"]
        response = client.get("/hint")
        data = response.get_json()
        row, col = data["row"], data["col"]
        # The hint should be from an empty cell (0 in puzzle)
        assert puzzle[row][col] == 0

    def test_hint_matches_solution(self, client):
        """Hint value should match the solution at that position."""
        client.get("/new")
        solution = CURRENT["solution"]
        response = client.get("/hint")
        data = response.get_json()
        row, col, value = data["row"], data["col"], data["value"]
        assert value == solution[row][col]

    def test_hint_resets_on_new_game(self, client):
        """Hints count should reset to 0 on new game."""
        client.get("/new")
        client.get("/hint")
        client.get("/hint")
        response1 = client.get("/hint")
        hints_before = response1.get_json()["hints_used"]
        assert hints_before == 3

        # Start new game
        client.get("/new")
        response2 = client.get("/hint")
        hints_after = response2.get_json()["hints_used"]
        assert hints_after == 1

    def test_hint_does_not_expose_solution(self, client):
        """Hint should return one value, not expose entire solution."""
        client.get("/new")
        response = client.get("/hint")
        data = response.get_json()
        # Should only contain specific keys, not the whole solution
        assert "solution" not in data
        assert "puzzle" not in data
        # Should only have specific cell info
        assert len(data) == 4  # row, col, value, hints_used

    def test_hint_uses_updated_board_for_sequential_requests(self, client):
        """Sequential hints should return different empty cells from the current board."""
        client.get("/new")
        board = copy.deepcopy(CURRENT["puzzle"])

        first_response = client.post("/hint", json={"board": board})
        assert first_response.status_code == 200
        first_data = first_response.get_json()

        row_one, col_one = first_data["row"], first_data["col"]
        board[row_one][col_one] = first_data["value"]

        second_response = client.post("/hint", json={"board": board})
        assert second_response.status_code == 200
        second_data = second_response.get_json()

        assert (second_data["row"], second_data["col"]) != (row_one, col_one)
        assert second_data["value"] == CURRENT["solution"][second_data["row"]][second_data["col"]]

