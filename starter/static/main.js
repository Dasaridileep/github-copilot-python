// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
let puzzle = [];
let currentDifficulty = 'easy';
let timerInterval = null;
let elapsedSeconds = 0;
let gameSolved = false;

// ============================================================================
// INITIALIZATION & SETUP
// ============================================================================

function initializeApp() {
    setupEventListeners();
    loadThemePreference();
    loadScoreboard();
    startNewGame();
}

function setupEventListeners() {
    document.getElementById('new-game').addEventListener('click', startNewGame);
    document.getElementById('hint-button').addEventListener('click', requestHint);
    document.getElementById('check-solution').addEventListener('click', checkSolution);
    document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
    
    // Initialize difficulty selector
    const diffRadios = document.querySelectorAll('input[name="difficulty"]');
    diffRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            currentDifficulty = e.target.value;
        });
    });
}

// ============================================================================
// THEME / DARK MODE
// ============================================================================

function loadThemePreference() {
    const savedTheme = localStorage.getItem('sudoku:v1:theme') || 'light';
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeToggleButton();
    }
}

function toggleTheme() {
    const isDark = document.body.classList.toggle('dark-mode');
    const theme = isDark ? 'dark' : 'light';
    localStorage.setItem('sudoku:v1:theme', theme);
    updateThemeToggleButton();
}

function updateThemeToggleButton() {
    const isDark = document.body.classList.contains('dark-mode');
    const btn = document.getElementById('theme-toggle');
    btn.textContent = isDark ? '☀️' : '🌙';
}

// ============================================================================
// TIMER
// ============================================================================

function startTimer() {
    stopTimer();
    elapsedSeconds = 0;
    updateTimerDisplay();
    timerInterval = setInterval(() => {
        if (!gameSolved) {
            elapsedSeconds++;
            updateTimerDisplay();
        }
    }, 1000);
}

function stopTimer() {
    if (timerInterval) {
        clearInterval(timerInterval);
        timerInterval = null;
    }
}

function updateTimerDisplay() {
    const minutes = Math.floor(elapsedSeconds / 60);
    const seconds = elapsedSeconds % 60;
    const timeStr = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
    document.getElementById('timer').textContent = timeStr;
}

function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${String(minutes).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
}

// ============================================================================
// BOARD RENDERING
// ============================================================================

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
    gameSolved = false;
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

// ============================================================================
// CONFLICT DETECTION
// ============================================================================

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

    // Clear all conflict highlighting (but preserve prefilled and hint classes)
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

// ============================================================================
// HINT SYSTEM
// ============================================================================

let hintRequestInFlight = false;

function getCurrentBoard() {
    const boardDiv = document.getElementById('sudoku-board');
    const inputs = boardDiv.getElementsByTagName('input');
    const board = [];

    for (let i = 0; i < SIZE; i++) {
        board[i] = [];
        for (let j = 0; j < SIZE; j++) {
            const inp = inputs[i * SIZE + j];
            const rawValue = inp.value.trim();
            board[i][j] = rawValue === '' ? 0 : parseInt(rawValue, 10) || 0;
        }
    }

    return board;
}

async function requestHint() {
    if (hintRequestInFlight) {
        return;
    }

    const hintButton = document.getElementById('hint-button');
    hintRequestInFlight = true;
    hintButton.disabled = true;

    try {
        const board = getCurrentBoard();
        const res = await fetch('/hint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ board })
        });
        const data = await res.json();

        if (res.status !== 200) {
            showMessage(`Error: ${data.message}`, true);
            return;
        }

        const { row, col, value, hints_used } = data;

        const boardDiv = document.getElementById('sudoku-board');
        const inputs = boardDiv.getElementsByTagName('input');
        const idx = row * SIZE + col;
        const inp = inputs[idx];

        inp.value = value;
        inp.disabled = true;
        inp.classList.add('hint');
        inp.classList.remove('row-conflict');

        document.getElementById('hints-count').textContent = hints_used;
        showMessage('Hint provided!', false);
    } finally {
        hintRequestInFlight = false;
        hintButton.disabled = false;
    }
}

// ============================================================================
// GAME START
// ============================================================================

async function startNewGame() {
    stopTimer();
    startTimer();
    gameSolved = false;
    document.getElementById('save-score').style.display = 'none';
    
    const difficulty = document.querySelector('input[name="difficulty"]:checked').value;
    currentDifficulty = difficulty;
    const res = await fetch(`/new?difficulty=${difficulty}`);
    const data = await res.json();
    if (data.error) {
        showMessage(`Error: ${data.message}`, true);
        return;
    }
    renderPuzzle(data.puzzle);
    document.getElementById('message').innerText = '';
    document.getElementById('hints-count').textContent = '0';
}

// ============================================================================
// SOLUTION CHECKING
// ============================================================================

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
        showMessage(data.error, true);
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
        showMessage('Puzzle is incomplete.', true);
        return;
    }

    if (incorrect.size > 0) {
        showMessage('Some entries are incorrect.', true);
        return;
    }

    // Success!
    gameSolved = true;
    stopTimer();
    showMessage('Congratulations! You solved the puzzle.', false);
    
    // Show save score button and enable it
    document.getElementById('save-score').style.display = 'inline-block';
    
    // Hook up the save-score button to save with the stored hints count
    document.getElementById('save-score').onclick = saveScore;
}

function showMessage(text, isError = false) {
    const msg = document.getElementById('message');
    msg.textContent = text;
    msg.className = isError ? '' : 'success';
    if (isError) {
        msg.style.color = '';
    }
}

// ============================================================================
// SCOREBOARD
// ============================================================================

function loadScoreboard() {
    try {
        const data = localStorage.getItem('sudoku:v1:topScores');
        if (!data) {
            renderScoreboard([]);
            return;
        }
        const scores = JSON.parse(data);
        if (!Array.isArray(scores)) {
            renderScoreboard([]);
            return;
        }
        renderScoreboard(scores);
    } catch (e) {
        console.error('Error loading scoreboard:', e);
        renderScoreboard([]);
    }
}

function renderScoreboard(scores) {
    const tbody = document.getElementById('scoreboard-body');
    tbody.innerHTML = '';
    
    if (scores.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="5">No scores yet. Complete a puzzle to get started!</td>';
        tbody.appendChild(tr);
        return;
    }
    
    scores.forEach((score, index) => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${index + 1}</td>
            <td>${escapeHtml(score.name)}</td>
            <td>${score.time}</td>
            <td>${score.difficulty}</td>
            <td>${score.hints}</td>
        `;
        tbody.appendChild(tr);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

async function saveScore() {
    const playerName = document.getElementById('player-name').value.trim();
    if (!playerName) {
        showMessage('Please enter your name to save your score.', true);
        return;
    }
    
    const hintsCountEl = document.getElementById('hints-count');
    const hintsUsed = parseInt(hintsCountEl.textContent, 10) || 0;
    
    const newScore = {
        name: playerName,
        time: formatTime(elapsedSeconds),
        difficulty: currentDifficulty,
        hints: hintsUsed,
        timestamp: Date.now()  // To detect duplicate submissions
    };
    
    try {
        let scores = [];
        const data = localStorage.getItem('sudoku:v1:topScores');
        if (data) {
            scores = JSON.parse(data);
        }
        
        if (!Array.isArray(scores)) {
            scores = [];
        }
        
        // Prevent duplicate submission for the same game (same elapsed time + hints)
        const isDuplicate = scores.some(s => 
            s.name === newScore.name && 
            s.time === newScore.time && 
            s.hints === newScore.hints &&
            Math.abs(s.timestamp - newScore.timestamp) < 5000  // Within 5 seconds
        );
        
        if (isDuplicate) {
            showMessage('This score has already been saved.', true);
            return;
        }
        
        // Add new score and sort by time (ascending - faster is better)
        scores.push(newScore);
        scores.sort((a, b) => {
            const aSeconds = timeToSeconds(a.time);
            const bSeconds = timeToSeconds(b.time);
            return aSeconds - bSeconds;
        });
        
        // Keep only top 10
        scores = scores.slice(0, 10);
        
        // Save to localStorage
        localStorage.setItem('sudoku:v1:topScores', JSON.stringify(scores));
        
        // Reload and display
        loadScoreboard();
        showMessage('Score saved! Check the scoreboard.', false);
        
        // Clear player name and hide save button
        document.getElementById('player-name').value = '';
        document.getElementById('save-score').style.display = 'none';
        
    } catch (e) {
        console.error('Error saving score:', e);
        showMessage('Error saving score.', true);
    }
}

function timeToSeconds(timeStr) {
    const parts = timeStr.split(':');
    return parseInt(parts[0], 10) * 60 + parseInt(parts[1], 10);
}

// ============================================================================
// LOAD ON PAGE READY
// ============================================================================

window.addEventListener('load', initializeApp);