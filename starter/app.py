from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}

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

if __name__ == '__main__':
    app.run(debug=True)