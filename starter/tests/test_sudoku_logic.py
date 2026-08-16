"""Baseline tests for sudoku_logic module.

Documents current behavior of puzzle generation, board creation, and validation.
"""

from sudoku_logic import (
    deep_copy,
    create_empty_board,
    is_safe,
    fill_board,
    generate_puzzle,
)


def _is_valid_sudoku(board: list[list[int]]) -> bool:
    """Check if a filled board satisfies all Sudoku constraints.

    Args:
        board: A 9x9 Sudoku board.

    Returns:
        True if each row, column, and 3x3 box contains digits 1–9 exactly once.
    """
    # Check rows
    for row in board:
        if sorted(row) != list(range(1, 10)):
            return False

    # Check columns
    for col in range(9):
        column = [board[row][col] for row in range(9)]
        if sorted(column) != list(range(1, 10)):
            return False

    # Check 3x3 boxes
    for box_row in range(3):
        for box_col in range(3):
            box = []
            for i in range(3):
                for j in range(3):
                    box.append(board[box_row * 3 + i][box_col * 3 + j])
            if sorted(box) != list(range(1, 10)):
                return False

    return True


class TestCreateEmptyBoard:
    """Test empty board creation."""

    def test_returns_9x9_board(self):
        """create_empty_board should return a 9x9 board."""
        board = create_empty_board()
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

    def test_contains_only_zeros(self):
        """create_empty_board should initialize all cells to 0."""
        board = create_empty_board()
        flat = [cell for row in board for cell in row]
        assert all(cell == 0 for cell in flat)


class TestIsSafe:
    """Test is_safe validation for placing numbers."""

    def test_accepts_number_in_empty_cell(self):
        """is_safe should return True when placing a number in empty board."""
        board = create_empty_board()
        assert is_safe(board, 0, 0, 5) is True

    def test_rejects_duplicate_in_row(self):
        """is_safe should return False when number already in row."""
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 0, 8, 5) is False

    def test_rejects_duplicate_in_column(self):
        """is_safe should return False when number already in column."""
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 8, 0, 5) is False

    def test_rejects_duplicate_in_3x3_box(self):
        """is_safe should return False when number already in 3x3 box."""
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 1, 1, 5) is False

    def test_accepts_number_in_different_box(self):
        """is_safe should return True when number in different 3x3 box."""
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 3, 3, 5) is True

    def test_detects_all_row_conflicts(self):
        """is_safe should reject all digits 1–9 when row is full."""
        board = create_empty_board()
        for col in range(9):
            board[0][col] = col + 1
        for num in range(1, 10):
            assert is_safe(board, 0, 0, num) is False


class TestFillBoard:
    """Test complete board generation."""

    def test_returns_true_on_success(self):
        """fill_board should return True when successfully filled."""
        board = create_empty_board()
        result = fill_board(board)
        assert result is True

    def test_modifies_board_in_place(self):
        """fill_board should modify the board parameter directly."""
        board = create_empty_board()
        original_id = id(board)
        fill_board(board)
        assert id(board) == original_id

    def test_fills_all_cells(self):
        """fill_board should result in no empty cells (no zeros)."""
        board = create_empty_board()
        fill_board(board)
        flat = [cell for row in board for cell in row]
        assert 0 not in flat

    def test_places_only_valid_digits(self):
        """fill_board should only place digits 1–9."""
        board = create_empty_board()
        fill_board(board)
        flat = [cell for row in board for cell in row]
        assert all(1 <= cell <= 9 for cell in flat)

    def test_creates_valid_sudoku(self):
        """fill_board should produce a valid Sudoku board."""
        board = create_empty_board()
        fill_board(board)
        assert _is_valid_sudoku(board)


class TestGeneratePuzzle:
    """Test puzzle generation with clues."""

    def test_returns_tuple_of_two_boards(self):
        """generate_puzzle should return (puzzle, solution) tuple."""
        puzzle, solution = generate_puzzle(40)
        assert isinstance(puzzle, list)
        assert isinstance(solution, list)

    def test_puzzle_and_solution_are_9x9(self):
        """Both puzzle and solution should be 9x9 boards."""
        puzzle, solution = generate_puzzle(40)
        for board in [puzzle, solution]:
            assert len(board) == 9
            assert all(len(row) == 9 for row in board)

    def test_solution_is_complete(self):
        """Solution should have no empty cells."""
        puzzle, solution = generate_puzzle(40)
        flat_solution = [cell for row in solution for cell in row]
        assert 0 not in flat_solution

    def test_solution_is_valid(self):
        """Solution should satisfy all Sudoku constraints."""
        puzzle, solution = generate_puzzle(40)
        assert _is_valid_sudoku(solution)

    def test_puzzle_has_requested_clue_count(self):
        """Puzzle should contain exactly the requested number of clues."""
        clue_count = 40
        puzzle, solution = generate_puzzle(clue_count)
        flat_puzzle = [cell for row in puzzle for cell in row]
        actual_clues = sum(1 for cell in flat_puzzle if cell != 0)
        assert actual_clues == clue_count

    def test_puzzle_clues_match_solution(self):
        """Every non-empty puzzle cell must match the solution."""
        puzzle, solution = generate_puzzle(40)
        for row in range(9):
            for col in range(9):
                if puzzle[row][col] != 0:
                    assert puzzle[row][col] == solution[row][col]

    def test_generates_different_clue_counts(self):
        """generate_puzzle should handle multiple clue counts correctly."""
        for clues in [20, 30, 40, 50]:
            puzzle, solution = generate_puzzle(clues)
            flat_puzzle = [cell for row in puzzle for cell in row]
            actual = sum(1 for cell in flat_puzzle if cell != 0)
            assert actual == clues


class TestDeepCopy:
    """Test board deep copying."""

    def test_creates_independent_copy(self):
        """deep_copy should produce a completely independent copy."""
        original = create_empty_board()
        original[0][0] = 5
        copied = deep_copy(original)
        copied[0][0] = 9
        assert original[0][0] == 5
        assert copied[0][0] == 9

    def test_preserves_9x9_structure(self):
        """deep_copy should preserve board dimensions."""
        original = create_empty_board()
        copied = deep_copy(original)
        assert len(copied) == 9
        assert all(len(row) == 9 for row in copied)
