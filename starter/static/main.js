// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateConflicts();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = 'sudoku-cell prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = 'sudoku-cell';
      }
    }
  }
}

function getConflictingCells(row, col, value) {
  /**
   * Return a set of [row, col] indices that conflict with the given cell.
   * Conflicts include: same row, same column, same 3x3 box.
   */
  if (value === '' || value === '0') {
    return new Set();
  }

  const conflicts = new Set();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  // Check row conflicts
  for (let j = 0; j < SIZE; j++) {
    if (j !== col) {
      const idx = row * SIZE + j;
      const otherVal = inputs[idx].value;
      if (otherVal === value) {
        conflicts.add(idx);
      }
    }
  }

  // Check column conflicts
  for (let i = 0; i < SIZE; i++) {
    if (i !== row) {
      const idx = i * SIZE + col;
      const otherVal = inputs[idx].value;
      if (otherVal === value) {
        conflicts.add(idx);
      }
    }
  }

  // Check 3x3 box conflicts
  const boxStartRow = Math.floor(row / 3) * 3;
  const boxStartCol = Math.floor(col / 3) * 3;
  for (let i = boxStartRow; i < boxStartRow + 3; i++) {
    for (let j = boxStartCol; j < boxStartCol + 3; j++) {
      if (i !== row || j !== col) {
        const idx = i * SIZE + j;
        const otherVal = inputs[idx].value;
        if (otherVal === value) {
          conflicts.add(idx);
        }
      }
    }
  }

  return conflicts;
}

function updateConflicts() {
  /**
   * Update visual feedback for conflicts as the user types.
   * Highlight cells that have conflicts with other cells.
   */
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');

  // Clear all conflict highlighting
  for (let i = 0; i < inputs.length; i++) {
    const inp = inputs[i];
    if (inp.disabled) continue;
    inp.classList.remove('row-conflict', 'column-conflict', 'box-conflict');
  }

  // Find all conflicts
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const inp = inputs[idx];
      if (inp.disabled) continue;

      const value = inp.value;
      if (value === '' || value === '0') {
        continue;
      }

      const conflicts = getConflictingCells(i, j, value);
      for (const conflictIdx of conflicts) {
        inputs[conflictIdx].classList.add('row-conflict');
      }

      // Also highlight the current cell if it has conflicts
      if (conflicts.size > 0) {
        inp.classList.add('row-conflict');
      }
    }
  }
}

async function newGame() {
  const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
  const res = await fetch(`/new?difficulty=${difficulty}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = `Error: ${data.message}`;
    document.getElementById('message').style.color = '#d32f2f';
    return;
  }
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  let hasBlankEditableCell = false;

  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const inp = inputs[idx];
      const val = inp.value;
      if (!inp.disabled && (val === '' || val === null || val === undefined)) {
        hasBlankEditableCell = true;
      }
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }

  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }

  const incorrect = new Set(data.incorrect.map(([row, col]) => row * SIZE + col));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect');
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }

  if (hasBlankEditableCell) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Puzzle is incomplete.';
    return;
  }

  if (incorrect.size > 0) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some entries are incorrect.';
    return;
  }

  msg.style.color = '#388e3c';
  msg.innerText = 'Congratulations! You solved the puzzle.';
}

// Wire buttons
window.addEventListener('load', () => {
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  // Initialize with easy difficulty
  const easyRadio = document.querySelector('input[name="difficulty"][value="easy"]');
  if (easyRadio) {
    easyRadio.checked = true;
  }
  newGame();
});