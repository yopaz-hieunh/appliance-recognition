# fastapi-template

A minimal, well-structured FastAPI application template. This README explains how to run the project and describes the purpose of each folder and important files so you can quickly build and extend APIs.

## Quick summary
- Purpose: a starter template for building FastAPI services with clear separation of concerns (configuration, DB, routers, models, services).
- Language: Python
- Run: development via Uvicorn; production via an ASGI server (e.g. Gunicorn + Uvicorn workers) or container.

## Contract (what this template provides)
- Inputs: environment variables (e.g. `DATABASE_URL`, `SECRET_KEY`), optional `.env` file.
- Outputs: a running FastAPI app exposing OpenAPI docs and your endpoints.
- Error modes: misconfigured environment variables, database unavailable, missing dependencies.

## Requirements
- Python 3.10+ (or the version used by your team)
- pip
- Recommended: virtual environment (venv/virtualenv)

## Quick start (development)
1. Create and activate a virtual environment (macOS / zsh):

```bash
python -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. (Optional) Create an `.env` file in the project root with at least these variables:

```env
APP_ENV=development
DATABASE_URL=sqlite:///./dev.db
SECRET_KEY=replace-me
```

4. Start the app in dev mode (reload enabled):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Open the interactive docs:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

Note: the command above assumes the ASGI app object is `app` in `app/main.py`.

## Project structure and purpose of each folder/file
Here is the repository layout (partial) and what each part is for. Adjust names if your copy differs.

```
app/
  __init__.py
  main.py
  dependencies.py
  core/
    config.py
  db/
    database.py
  internal/
    admin.py
  models/
  routers/
  schemas/
  services/
tests/
requirements.txt
run.sh
```

Detailed file/folder explanations:

- `app/main.py`
  - Application entrypoint. Typically instantiates FastAPI, includes routers, configures middlewares (CORS, error handlers), and mounts any sub-apps.
  - Example responsibilities: read settings from `core/config.py`, attach DB startup/shutdown events from `db/database.py`.

- `app/dependencies.py`
  - Central place for dependency-injection helper functions used by route handlers (for example: `get_db`, `get_current_user`, shared service factories).
  - Keep lightweight logic and wiring here — complex logic belongs in `services/`.

- `app/core/config.py`
  - Application configuration (Pydantic settings or similar). Loads values from env vars or `.env` and exposes typed settings objects (e.g., `settings.DATABASE_URL`).
  - Use Pydantic's `BaseSettings` for easy validation and defaults.

- `app/db/database.py`
  - Database connection and session management. If using SQLAlchemy, this file usually contains engine creation, session factory, and helper `get_db()`.
  - Also used to run DB startup/shutdown lifecycle hooks registered in `main.py`.

- `app/internal/admin.py`
  - Internal-only or administrative endpoints and utilities. Keep privileged admin code here and protect it with auth or a separate environment.

- `app/models/`
  - ORM models (e.g., SQLAlchemy models) or domain model definitions used to persist data.
  - Each model file should contain a single concern when practical.

- `app/schemas/`
  - Pydantic request/response schemas (DTOs). Keep input validation separate from DB models and use schema classes in routers and services.

- `app/routers/`
  - Route definitions (FastAPI APIRouter instances). Organize routers by resource (e.g., `users.py`, `items.py`) and include them from `main.py`.

- `app/services/`
  - Business logic and domain operations. Services should be plain Python classes/functions that take repositories/DB sessions and return results — this keeps routers thin.

- `tests/`
  - Test suite (unit and integration). Use pytest. Put test fixtures and test clients here. Example: tests/test_users.py.

- `requirements.txt`
  - Project dependencies used by `pip install -r requirements.txt`.

- `run.sh`
  - Convenience script to run or deploy the app (may wrap uvicorn/gunicorn commands or docker-compose). Check its contents and adapt permissions (`chmod +x run.sh`).

## Testing
- Run the test suite with pytest:

```bash
pytest -q
```

Useful tips:
- Use `pytest -k <pattern>` to run a subset of tests.
- Add CI (GitHub Actions) to run tests on push/PR.

## Linting & formatting
- Recommended tools: `black`, `isort`, `flake8`, `ruff`.

Example usage:

```bash
black .
isort .
flake8
```

## Docker
If you add a `Dockerfile`, a simple build/run cycle looks like:

```bash
docker build -t fastapi-app .
docker run -p 8000:8000 --env-file .env fastapi-app
```

For production, prefer a multi-worker setup using Gunicorn + Uvicorn workers:

```bash
gunicorn -k uvicorn.workers.UvicornWorker app.main:app --workers 4 --bind 0.0.0.0:8000
```

## Deployment notes
- Ensure environment variables are set (e.g., `DATABASE_URL`, `SECRET_KEY`, `APP_ENV=production`).
- Use a managed database in production; do not use SQLite for high-traffic apps.
- Configure logging and monitoring (Application Insights, Sentry, or another provider).
- Use HTTPS and secure credentials/secrets via a secret manager or platform-provided env secrets.

## Edge cases & gotchas
- Missing `.env` or wrong `DATABASE_URL` will cause DB connection errors at startup.
- Circular imports: keep wiring (including router includes) in `main.py` and avoid heavy imports in `__init__.py`.
- Long-running startup operations should be asynchronous and timeout-protected.

## Contributing
- Open issues for feature requests or bugs.
- Create PRs against `main` (or configured branch). Include tests and follow formatting/lint rules.

## License
Check the repository `LICENSE` file for licensing terms.
