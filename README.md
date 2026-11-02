# DeployFlow

DeployFlow is a recruiter-ready CI/CD portfolio project built around a minimal Task Management API. The application stays intentionally small so the engineering evidence is concentrated in automated tests, reproducible containers, security scanning, versioned image publishing, deployment smoke tests, and rollback.

## Current scope

M1 through M3 provide:

- A typed FastAPI service with OpenAPI documentation.
- A `/health` endpoint for operational checks.
- In-memory task CRUD endpoints.
- Request validation and consistent HTTP status codes.
- pytest API coverage and Ruff configuration.
- A pinned, multi-stage container build with a non-root runtime user.
- Docker Compose deployment with an application health check and runtime hardening.
- Dependency-free health and CRUD smoke tests against the deployed container.
- GitHub Actions CI for Ruff, pytest, container builds, and Trivy vulnerability scanning.
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

## Containerized deployment

Prerequisites: Docker Desktop or Docker Engine with Docker Compose.

Validate, build, and start the service:

```powershell
docker compose config --quiet
docker compose build --pull
docker compose up --detach --wait --wait-timeout 60
docker compose ps
```

The API is available at `http://127.0.0.1:8000`. Compose waits until `/health` returns the expected response. To use another host port:

```powershell
$env:DEPLOYFLOW_PORT = "8080"
docker compose up --detach --wait --wait-timeout 60
```

Run health and full CRUD smoke tests without installing Python on the host:

```powershell
docker compose run --rm --no-deps `
  --volume "${PWD}\scripts:/smoke:ro" `
  --env DEPLOYFLOW_BASE_URL=http://api:8000 `
  api python /smoke/smoke_test.py
```

The smoke test creates, lists, reads, updates, and deletes a task, verifies the final `404`, and removes its test data. Stop the local deployment with:

```powershell
docker compose down
```

For troubleshooting:

```powershell
docker compose ps
docker compose logs --tail 100 api
docker compose config
```

If port 8000 is already in use, set `DEPLOYFLOW_PORT` before starting Compose. If dependencies or application code changed, rerun `docker compose build --pull` before `docker compose up`.

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

Against any running service, execute the dependency-free smoke test with a local Python runtime:

```powershell
.\.venv\Scripts\python scripts/smoke_test.py
```

Set `DEPLOYFLOW_BASE_URL` to target a non-default host or port.

## Continuous integration

`.github/workflows/ci.yml` runs for every pull request and every push to `main`. It provides two ordered jobs:

1. `Ruff and pytest` installs the development dependencies, checks lint and formatting, and runs the API tests.
2. `Container build and Trivy scan` builds a commit-tagged local image and scans it without logging in, publishing, or pushing.

Workflow permissions are limited to `contents: read`. Checkout credentials are not persisted, jobs have explicit timeouts, duplicate runs are cancelled, and every external action is pinned to a full commit SHA.

### Vulnerability policy

Trivy 0.76.1 scans operating-system and Python package vulnerabilities in the final image. CI fails when a fixable `HIGH` or `CRITICAL` vulnerability is present. Unfixed findings do not block this MVP because no actionable upgrade exists, but they remain a maintenance concern and the policy should be reviewed before a production release. `LOW`, `MEDIUM`, and `UNKNOWN` findings are outside the blocking gate.

The workflow does not publish images. GHCR publication belongs to M4 and requires explicit approval.

## Delivery roadmap

- **M1:** API and automated tests.
- **M2:** Dockerfile, Compose deployment, health checks, and local smoke tests.
- **M3:** GitHub Actions for lint, tests, image build, and Trivy scanning.
- **M4:** Versioned GHCR publishing, deployment, smoke tests, and rollback.
- **M5:** Authentic screenshots, CI evidence, documentation review, and portfolio polish.

Detailed acceptance criteria are in [docs/tasks.md](docs/tasks.md). The system design and decisions are in [docs/architecture.md](docs/architecture.md), and verified progress is recorded in [docs/progress.md](docs/progress.md).

## Security

Do not commit `.env` files, registry tokens, credentials, or private keys. The CI workflow uses read-only repository permissions and requires no project secrets. Publishing and remote deployment require explicit approval.

## License

No license has been selected yet. All rights are reserved until a license file is added.
