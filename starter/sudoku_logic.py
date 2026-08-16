import copy
import random

SIZE = 9
EMPTY = 0


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def validate_board(board):
    """Return True when a board is a valid 9x9 Sudoku layout."""
    return _validate_board(board)


def is_safe(board, row, col, num):
    if num < 1 or num > SIZE:
        return False
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def _validate_board(board):
    """Validate board dimensions, cell values, and conflict-free placement."""
    if not isinstance(board, list) or len(board) != SIZE:
        return False

    for row in board:
        if not isinstance(row, list) or len(row) != SIZE:
            return False
        for value in row:
            if isinstance(value, bool) or not isinstance(value, int):
                return False
            if value < EMPTY or value > SIZE:
                return False

    for row in board:
        seen = set()
        for value in row:
            if value == EMPTY:
                continue
            if value in seen:
                return False
            seen.add(value)

    for col in range(SIZE):
        seen = set()
        for row in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            if value in seen:
                return False
            seen.add(value)

    for box_row in range(0, SIZE, 3):
        for box_col in range(0, SIZE, 3):
            seen = set()
            for row in range(box_row, box_row + 3):
                for col in range(box_col, box_col + 3):
                    value = board[row][col]
                    if value == EMPTY:
                        continue
                    if value in seen:
                        return False
                    seen.add(value)

    return True


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def count_solutions(board, max_count=2):
    """Count valid Sudoku solutions without mutating the input board."""
    if not isinstance(max_count, int) or max_count < 1:
        raise ValueError("max_count must be a positive integer.")
    if not validate_board(board):
        return 0

    working = deep_copy(board)
    solution_count = 0

    def backtrack():
        nonlocal solution_count
        if solution_count >= max_count:
            return

        best_row = None
        best_col = None
        best_candidates = None

        for row in range(SIZE):
            for col in range(SIZE):
                if working[row][col] != EMPTY:
                    continue
                candidates = [
                    num for num in range(1, SIZE + 1) if is_safe(working, row, col, num)
                ]
                if not candidates:
                    return
                if best_candidates is None or len(candidates) < len(best_candidates):
                    best_row = row
                    best_col = col
                    best_candidates = candidates
                    if len(best_candidates) == 1:
                        break
            if best_candidates is not None and len(best_candidates) == 1:
                break

        if best_candidates is None:
            solution_count += 1
            return

        for num in best_candidates:
            working[best_row][best_col] = num
            backtrack()
            working[best_row][best_col] = EMPTY
            if solution_count >= max_count:
                return

    backtrack()
    return solution_count


def remove_cells(board, clues, max_attempts=None):
    """Remove cells only when the puzzle still has exactly one solution."""
    if not isinstance(clues, int) or not 17 <= clues <= SIZE * SIZE:
        raise ValueError(
            f"clues must be an integer between 17 and {SIZE * SIZE}, got {clues}."
        )

    if max_attempts is None:
        max_attempts = max(1, (SIZE * SIZE - clues) * 10)

    puzzle = deep_copy(board)
    current_clues = sum(1 for row in puzzle for cell in row if cell != EMPTY)
    if current_clues < clues:
        raise ValueError(
            f"Board has {current_clues} clues, which is fewer than the requested {clues}."
        )

    attempts = 0
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    for row, col in cells:
        if current_clues == clues:
            return puzzle
        if attempts >= max_attempts:
            break
        if puzzle[row][col] == EMPTY:
            continue

        value = puzzle[row][col]
        puzzle[row][col] = EMPTY
        attempts += 1

        if count_solutions(puzzle, max_count=2) == 1:
            current_clues -= 1
        else:
            puzzle[row][col] = value

    if current_clues != clues:
        raise ValueError(
            f"Could not reach exactly {clues} clues while preserving uniqueness. "
            f"Reached {current_clues} clues instead."
        )

    return puzzle


def generate_puzzle(clues=35, max_retries=8):
    """Generate a new unique Sudoku puzzle and its solution as a tuple."""
    if not isinstance(clues, int) or not 17 <= clues <= SIZE * SIZE:
        raise ValueError(
            f"clues must be an integer between 17 and {SIZE * SIZE}, got {clues}."
        )
    if not isinstance(max_retries, int) or max_retries < 1:
        raise ValueError("max_retries must be a positive integer.")

    last_error = None
    for _ in range(max_retries):
        board = create_empty_board()
        if not fill_board(board):
            raise ValueError("Failed to generate a valid completed Sudoku board.")

        solution = deep_copy(board)
        try:
            puzzle = remove_cells(board, clues)
        except ValueError as exc:
            last_error = exc
            continue

        if sum(1 for row in puzzle for cell in row if cell != EMPTY) != clues:
            last_error = ValueError(
                f"Generated puzzle does not have exactly {clues} clues."
            )
            continue

        if count_solutions(puzzle, max_count=2) != 1:
            last_error = ValueError("Generated puzzle does not have exactly one solution.")
            continue

        for row in range(SIZE):
            for col in range(SIZE):
                if puzzle[row][col] != EMPTY and puzzle[row][col] != solution[row][col]:
                    last_error = ValueError("Puzzle clue does not match the solution.")
                    break
            if last_error is not None:
                break
        if last_error is not None:
            continue

        return puzzle, solution

    if last_error is None:
        last_error = ValueError(
            f"Could not generate a puzzle with {clues} clues after {max_retries} retries."
        )
    raise ValueError(
        f"Could not generate puzzle with {clues} clues after {max_retries} retries. "
        f"Last error: {last_error}"
    ) from last_error
