# DeployFlow Engineering Conventions

## Scope

- Work only inside this repository.
- Optimize for a recruiter-ready, working CI/CD MVP.
- Keep the architecture to one FastAPI service unless a documented requirement proves otherwise.
- Do not add Kubernetes, a database, a message broker, or cloud infrastructure without explicit approval.

## Python

- Target Python 3.12 or newer.
- Keep application code under `app/` and tests under `tests/`.
- Use type hints on public functions and models.
- Use FastAPI and Pydantic validation at API boundaries.
- Keep business logic independent from HTTP handling where doing so remains simple.
- Use Ruff for linting and formatting and pytest for tests.
- Add or update tests for every behavior change.

## API Conventions

- Expose health information at `GET /health`.
- Expose task CRUD operations under `/tasks`.
- Return JSON error responses through FastAPI's standard exception handling.
- Use `404 Not Found` for unknown task IDs and `204 No Content` for successful deletion.
- Keep OpenAPI metadata accurate and avoid breaking endpoint contracts without documenting the change.

## Documentation

- Update `README.md` when setup commands or user-facing behavior changes.
- Update `docs/architecture.md` when components or runtime flows change.
- Update `docs/tasks.md` as milestone scope or acceptance criteria change.
- Update `docs/progress.md` after implementation and verification. Record only commands actually run and their real results.

## Safety

- Never commit credentials, tokens, private keys, `.env` files, or generated secret material.
- Use environment variables or GitHub secrets for credentials.
- Request approval before pushing, publishing an image, deploying remotely, deleting material data, or performing a billable action.
- Do not use destructive Git commands such as `git reset --hard` or force-push without explicit approval.
- Preserve unrelated user changes and inspect `git status` before editing.
- Pin deployable image versions; do not rely on `latest` for rollback procedures.

## Verification

- Run Ruff and pytest after code changes when the required runtime is available.
- For deployment changes, verify health checks and a CRUD smoke test.
- Never report a command as passing unless it was executed successfully.
- If a prerequisite is unavailable, record the exact blocker and provide a reproducible command for later verification.
