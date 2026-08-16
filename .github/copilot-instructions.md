Project-specific Copilot instructions — Flask Sudoku
===================================================

Purpose
- Provide concise, actionable suggestions that follow the project's style, testing, and accessibility requirements.
- Explain non-obvious suggestions and trade-offs briefly whenever a change is proposed.

Python & Code Quality
- Follow PEP 8 formatting and idioms. Prefer Black/Flake8 compatible output.
- Use meaningful, descriptive names for functions, classes, variables and tests.
- Add type hints for public functions and complex internal functions. Keep signatures readable.
- Include docstrings for modules, classes, and public functions (one-line summary + short params/returns when non-trivial).
- Keep functions small and single-responsibility. Aim for 20-50 lines for complex functions.
- Prefer composition over large monolithic modules.

Project structure & modular separation
- Separate web layer (Flask routes/views) from game logic:
  - Put Flask routes and request/response handling under an app/routes (or app/views) module.
  - Put Sudoku logic, board generation, solvers, validators under sudoku/ or core/ modules.
- Routes should adapt inputs, call pure logic functions, and return rendered templates or JSON. Logic modules should be pure and testable.

Error handling & API responses
- Use consistent error handling:
  - Define app-specific exceptions for predictable error cases (e.g., InvalidMoveError, PuzzleNotFound).
  - Register Flask error handlers to return consistent JSON or rendered error pages with appropriate HTTP codes.
  - API JSON error format: { "error": "short-code", "message": "Human-friendly explanation" }.
- Avoid leaking internal traceback to users; log details server-side.

Testing & CI
- Add pytest tests for logic and integration-level tests for routes.
- Keep tests focused and small; one behavior per test.
- Use fixtures to create sample boards and client requests.
- Maintain >= 80% coverage for core logic; run coverage locally before PRs.
- Run tests after every change. Example Windows workflow:
  - python -m venv .venv
  - .venv\Scripts\activate
  - pip install -r requirements-dev.txt
  - pytest -q
  - coverage run -m pytest && coverage report -m
- Include tests that assert error handling and edge cases.

Commits & PRs
- Make small, focused changes per PR. Each PR should implement one logical change.
- Write clear commit messages and PR descriptions explaining why, not just what.
- When suggesting non-obvious refactors, include a short rationale and potential downside.

Front-end: HTML, CSS, Accessibility & Responsiveness
- Use semantic HTML (button, input, main, nav, header, footer).
- Ensure keyboard navigation for the grid (tab order, arrow-key support).
- Provide ARIA attributes and labels where necessary (aria-label on Sudoku cells when input elements are not explicit).
- Ensure color contrast meets accessibility guidelines. Prefer relative units (rem, %) and responsive layout (flex/grid).
- Implement light/dark mode using CSS custom properties and prefers-color-scheme. Example: toggle class on body or rely on system preference.
- Keep HTML/CSS responsive — grid should scale and remain usable on small screens.

JavaScript guidelines
- Use unobtrusive JS and progressive enhancement.
- Prefer event delegation for grid interactions: attach listeners to a container and use data-* attributes for row/col ids.
- Keep DOM access minimal and batch updates where possible.
- Validate user input client-side but enforce validation server-side as authoritative.
- Avoid storing sensitive data in localStorage or exposing server secrets.

localStorage & persistence
- Namespace keys (e.g., "sudoku:v1:currentBoard") and include a version to handle migrations.
- Protect from malformed data: wrap JSON.parse in try/catch and fallback to defaults.
- Limit size and duration of stored state; provide explicit clear/reset UI.
- Never store secrets or server tokens in localStorage.

Security & safety
- Sanitize and validate all inputs server-side.
- Use Flask's built-in templating safe practices (avoid unsafe string concatenation into templates).
- Rate-limit endpoints that generate puzzles or attempt solves if public-facing.

Code suggestions & explanations
- For every non-trivial code suggestion, include:
  - A short explanation (1–3 sentences) of why the change helps.
  - Any trade-offs or follow-up tasks (e.g., additional tests, performance checks).
- When suggesting renames or refactors, provide a small diff or exact replacement snippet.

Style & tooling
- Prefer type hints and small helper functions over long inline logic.
- Suggest unit tests with pytest and meaningful asserts.
- Recommend running linters and formatters locally before committing (black, isort, flake8).

Developer workflow reminders (Windows)
- To run dev server locally:
  - .venv\Scripts\activate
  - set FLASK_APP=app
  - set FLASK_ENV=development
  - flask run
- To run tests and coverage:
  - .venv\Scripts\activate
  - pytest -q
  - coverage run -m pytest && coverage report -m

When to propose UI changes
- Propose UI/UX changes only when they are small and improve accessibility, responsiveness, or clarity.
- Provide screenshots or animated GIFs for visual changes when possible, plus before/after descriptions.

Final note
- Keep suggestions minimal, modular, and easily reviewable.
- Run tests and linters after applying each suggested change and report results in the PR description.
