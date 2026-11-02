# DeployFlow

DeployFlow is a recruiter-ready CI/CD portfolio project built around a minimal Task Management API. The application stays intentionally small so the engineering evidence is concentrated in automated tests, reproducible containers, security scanning, versioned image publishing, deployment smoke tests, and rollback.

## Current scope

M1 provides:

- A typed FastAPI service with OpenAPI documentation.
- A `/health` endpoint for operational checks.
- In-memory task CRUD endpoints.
- Request validation and consistent HTTP status codes.
- pytest API coverage and Ruff configuration.
- Architecture, milestone, and progress documentation.

Task data is process-local and is reset when the service restarts. Persistence is outside the MVP scope.

## API

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check service health |
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks/{id}` | Read a task |
| `PUT` | `/tasks/{id}` | Replace a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

Interactive API documentation is available at `/docs` while the service is running.

## Local development

Prerequisites: Python 3.12+ and Git.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` or check health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

On macOS or Linux, activate or invoke the virtual environment from `.venv/bin` instead.

## Quality checks

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m pytest
```

Against a running service, execute the dependency-free health smoke test:

```powershell
.\.venv\Scripts\python scripts/smoke_test.py
```

Set `DEPLOYFLOW_BASE_URL` to target a non-default host or port.

## Delivery roadmap

- **M1:** API and automated tests.
- **M2:** Dockerfile, Compose deployment, health checks, and local smoke tests.
- **M3:** GitHub Actions for lint, tests, image build, and Trivy scanning.
- **M4:** Versioned GHCR publishing, deployment, smoke tests, and rollback.
- **M5:** Authentic screenshots, CI evidence, documentation review, and portfolio polish.

Detailed acceptance criteria are in [docs/tasks.md](docs/tasks.md). The system design and decisions are in [docs/architecture.md](docs/architecture.md), and verified progress is recorded in [docs/progress.md](docs/progress.md).

## Security

Do not commit `.env` files, registry tokens, credentials, or private keys. Later GitHub workflows will use least-privilege permissions and GitHub-provided secrets. Publishing and remote deployment require explicit approval.

## License

No license has been selected yet. All rights are reserved until a license file is added.
