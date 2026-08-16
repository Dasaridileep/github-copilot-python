from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hints_used': 0,
    'locked_cells': set()  # (row, col) tuples of hint cells
}


def _validate_board_payload(board):
    """Validate a Sudoku board payload and return the normalized 9x9 board."""
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return None

    normalized = []
    for row in board:
        if not isinstance(row, list) or len(row) != sudoku_logic.SIZE:
            return None
        normalized_row = []
        for value in row:
            if value in (None, ''):
                normalized_row.append(sudoku_logic.EMPTY)
            elif isinstance(value, bool) or not isinstance(value, int):
                return None
            elif value < sudoku_logic.EMPTY or value > sudoku_logic.SIZE:
                return None
            else:
                normalized_row.append(value)
        normalized.append(normalized_row)
    return normalized


def _find_next_hint_cell(board):
    """Return the first blank cell in the provided board, or None if the board is full."""
    for row in range(sudoku_logic.SIZE):
        for col in range(sudoku_logic.SIZE):
            if board[row][col] == sudoku_logic.EMPTY:
                return row, col
    return None

# Difficulty levels: Easy, Medium, Hard
DIFFICULTY_LEVELS = {
    'easy': 45,
    'medium': 38,
    'hard': 32
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Support both difficulty parameter and legacy clues parameter
    difficulty = request.args.get('difficulty', '').lower()
    clues = request.args.get('clues')
    
    # If difficulty is specified, use it
    if difficulty:
        if difficulty not in DIFFICULTY_LEVELS:
            return jsonify({'error': 'invalid_difficulty', 'message': f'Difficulty must be one of: {", ".join(DIFFICULTY_LEVELS.keys())}'}), 400
        clues = DIFFICULTY_LEVELS[difficulty]
    else:
        # Fall back to clues parameter (default 35 for backward compatibility)
        clues = int(clues) if clues else 35
    
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['hints_used'] = 0
    CURRENT['locked_cells'] = set()
    return jsonify({'puzzle': puzzle})

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'invalid_board', 'message': 'Board must be a 9x9 grid.'}), 400

    incorrect = []
    for i in range(sudoku_logic.SIZE):
        if not isinstance(board[i], list) or len(board[i]) != sudoku_logic.SIZE:
            return jsonify({'error': 'invalid_board', 'message': 'Board must be a 9x9 grid.'}), 400
        for j in range(sudoku_logic.SIZE):
            value = board[i][j]
            if value in (None, '', 0):
                continue
            if value != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

@app.route('/hint', methods=['GET', 'POST'])
def get_hint():
    """Return one correct value for an empty cell without exposing the solution.

    Accepts either a stored puzzle (legacy GET) or a submitted board payload from the
    current game view. The selected cell must currently be blank in the submitted board.
    """
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')

    if puzzle is None or solution is None:
        return jsonify({'error': 'no_game', 'message': 'No game in progress'}), 400

    board = None
    if request.method == 'POST':
        data = request.get_json(silent=True) or {}
        board = data.get('board')
        if board is None:
            return jsonify({'error': 'invalid_board', 'message': 'Board payload is required.'}), 400
    else:
        board = puzzle

    board = _validate_board_payload(board)
    if board is None:
        return jsonify({'error': 'invalid_board', 'message': 'Board must be a 9x9 grid of integers or blanks.'}), 400

    hint_cell = _find_next_hint_cell(board)
    if hint_cell is None:
        return jsonify({'error': 'no_empty_cells', 'message': 'No empty cells remaining.'}), 400

    row, col = hint_cell
    value = solution[row][col]
    CURRENT['puzzle'] = board
    CURRENT['hints_used'] += 1
    CURRENT['locked_cells'].add((row, col))
    return jsonify({
        'row': row,
        'col': col,
        'value': value,
        'hints_used': CURRENT['hints_used']
    })

if __name__ == '__main__':
    app.run(debug=True)