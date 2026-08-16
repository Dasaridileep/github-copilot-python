"""Baseline tests for sudoku_logic module.

These tests document the actual public API and the uniqueness guarantee for
Sudoku generation.
"""

import pytest

import sudoku_logic
from sudoku_logic import (
    count_solutions,
    create_empty_board,
    deep_copy,
    generate_puzzle,
    is_safe,
    fill_board,
)


def _completed_board():
    return [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]


def _known_puzzle_with_one_solution():
    return [
        [0, 0, 5, 3, 0, 0, 0, 0, 0],
        [8, 0, 0, 0, 0, 0, 0, 2, 0],
        [0, 7, 0, 0, 1, 0, 5, 0, 0],
        [4, 0, 0, 0, 0, 5, 3, 0, 0],
        [0, 1, 0, 0, 7, 0, 0, 0, 6],
        [0, 0, 3, 2, 0, 0, 0, 8, 0],
        [0, 6, 0, 5, 0, 0, 0, 0, 9],
        [0, 0, 4, 0, 0, 0, 0, 3, 0],
        [0, 0, 0, 0, 0, 9, 7, 0, 0],
    ]


def _board_with_multiple_solutions():
    board = create_empty_board()
    board[0][0] = 5
    return board


def _conflicting_board():
    board = create_empty_board()
    board[0][0] = 5
    board[0][1] = 5
    return board


def _is_valid_sudoku(board):
    """Return True if board is a valid, complete Sudoku solution."""
    for row in board:
        if sorted(row) != list(range(1, 10)):
            return False
    for col in range(9):
        if sorted(board[row][col] for row in range(9)) != list(range(1, 10)):
            return False
    for box_row in range(0, 9, 3):
        for box_col in range(0, 9, 3):
            values = []
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    values.append(board[row][col])
            if sorted(values) != list(range(1, 10)):
                return False
    return True


class TestCreateEmptyBoard:
    def test_returns_9x9_board(self):
        board = create_empty_board()
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)

    def test_contains_only_zeros(self):
        board = create_empty_board()
        flat = [cell for row in board for cell in row]
        assert all(cell == 0 for cell in flat)


class TestIsSafe:
    def test_accepts_number_in_empty_cell(self):
        board = create_empty_board()
        assert is_safe(board, 0, 0, 5) is True

    def test_rejects_duplicate_in_row(self):
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 0, 8, 5) is False

    def test_rejects_duplicate_in_column(self):
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 8, 0, 5) is False

    def test_rejects_duplicate_in_box(self):
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 1, 1, 5) is False

    def test_accepts_number_in_different_box(self):
        board = create_empty_board()
        board[0][0] = 5
        assert is_safe(board, 3, 3, 5) is True


class TestCountSolutions:
    def test_fixed_known_puzzle_has_one_solution(self):
        board = _known_puzzle_with_one_solution()
        assert count_solutions(board) == 1

    def test_board_with_multiple_solutions_stops_at_two(self):
        board = _board_with_multiple_solutions()
        assert count_solutions(board, max_count=2) == 2

    def test_conflicting_board_returns_zero(self):
        board = _conflicting_board()
        assert count_solutions(board) == 0

    def test_completed_board_returns_one(self):
        board = _completed_board()
        assert count_solutions(board) == 1

    def test_count_solutions_does_not_mutate_input(self):
        board = _known_puzzle_with_one_solution()
        original = deep_copy(board)
        assert count_solutions(board) == 1
        assert board == original


class TestGeneratePuzzle:
    def test_generate_puzzle_easy_medium_hard_targets(self):
        for clues in [45, 38, 32]:
            puzzle, solution = generate_puzzle(clues)
            assert count_solutions(puzzle, max_count=2) == 1
            assert sum(1 for row in puzzle for cell in row if cell != 0) == clues
            for row in range(9):
                for col in range(9):
                    if puzzle[row][col] != 0:
                        assert puzzle[row][col] == solution[row][col]
                    else:
                        assert solution[row][col] != 0

    def test_generate_puzzle_invalid_clue_count_raises(self):
        with pytest.raises(ValueError):
            generate_puzzle(16)
        with pytest.raises(ValueError):
            generate_puzzle(82)
        with pytest.raises(ValueError):
            generate_puzzle("45")

    def test_generate_puzzle_bounded_failure_raises_documented_exception(self, monkeypatch):
        valid_solution = _completed_board()

        def fake_fill_board(board):
            for row in range(9):
                for col in range(9):
                    board[row][col] = valid_solution[row][col]
            return True

        def fake_remove_cells(board, clues, max_attempts=None):
            raise ValueError("forced removal failure")

        monkeypatch.setattr(sudoku_logic, "fill_board", fake_fill_board)
        monkeypatch.setattr(sudoku_logic, "remove_cells", fake_remove_cells)

        with pytest.raises(ValueError, match="Could not generate puzzle"):
            sudoku_logic.generate_puzzle(45, max_retries=2)


class TestFillBoard:
    def test_fill_board_completes_board(self):
        board = create_empty_board()
        assert fill_board(board) is True
        flat = [cell for row in board for cell in row]
        assert 0 not in flat
        assert _is_valid_sudoku(board)
