# DeployFlow

[![CI](https://github.com/mbeddi5232-oss/deployflow-cicd/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/mbeddi5232-oss/deployflow-cicd/actions/workflows/ci.yml)

DeployFlow is a production-minded CI/CD portfolio project built around a deliberately small FastAPI Task API. The application is simple; the engineering focus is the delivery system around it: automated quality gates, hardened containers, trusted publishing, explicit-version deployment, smoke testing, and verified rollback.

## What This Project Demonstrates

- Typed FastAPI health and task CRUD endpoints with isolated pytest coverage.
- Ruff lint and formatting gates on every pull request and `main` push.
- A pinned multi-stage Docker build with a non-root runtime.
- Docker Compose health checks and runtime hardening.
- Trivy enforcement for fixable `HIGH` and `CRITICAL` vulnerabilities.
- Least-privilege GitHub Actions with full-SHA action pins.
- GHCR publishing only from trusted `main` pushes after all gates pass.
- Full-commit image tags, explicit deployment versions, and no `latest` tag.
- Health and CRUD smoke tests after deployment.
- A genuine two-image rollback verified locally without rebuilding source.

## Verified Delivery Evidence

Evidence is linked to live resources or recorded command output; no screenshots or results are fabricated.

| Evidence | Verified result |
| --- | --- |
| [GitHub Actions run 41494769554](https://github.com/mbeddi5232-oss/deployflow-cicd/actions/runs/41494769554) | Ruff/pytest, container build/Trivy, and GHCR publishing jobs succeeded for commit `a7f2b2437c8eba0daa7a4ef29bac46301d7df848` |
| [GHCR package](https://github.com/mbeddi5232-oss/deployflow-cicd/pkgs/container/deployflow-cicd) | Two anonymous-pullable, commit-tagged images with distinct digests and matching OCI revision labels |
| Baseline image | `sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5` → `sha256:607995610eac0044361280e96296df68a472ef742718c83b9a6cfa03a25bd755` |
| Candidate image | `sha-a7f2b2437c8eba0daa7a4ef29bac46301d7df848` → `sha256:d672768378b6d8e86863d2de634d76fed57b645860040c28f7a2b4711a343bac` |
| Local rollback | Baseline → candidate → baseline; exact image, health, and complete CRUD smoke checks passed at every stage |

The complete commands and raw result summaries are maintained in [docs/progress.md](docs/progress.md).

## Architecture

DeployFlow is a single-service modular monolith. GitHub Actions validates source and containers, publishes trusted commits to GHCR, and a deployment operator selects one immutable image version for Compose. The same deployment path is used for release and rollback.

See [docs/architecture.md](docs/architecture.md) for the Mermaid delivery diagram, runtime design, and engineering decisions.

## API Contract

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Check service health |
| `GET` | `/tasks` | List tasks |
| `POST` | `/tasks` | Create a task |
| `GET` | `/tasks/{id}` | Read a task |
| `PUT` | `/tasks/{id}` | Replace a task |
| `DELETE` | `/tasks/{id}` | Delete a task |

Interactive OpenAPI documentation is available at `/docs` while the service is running.

## Quick Start with Docker Compose

Prerequisite: Docker Engine or Docker Desktop with Docker Compose.

```powershell
docker compose config --quiet
docker compose build --pull
docker compose up --detach --wait --wait-timeout 60
Invoke-RestMethod http://127.0.0.1:8000/health
```

Run the full health and CRUD smoke test without installing Python on the host:

```powershell
docker compose run --rm --no-deps `
  --volume "${PWD}\scripts:/smoke:ro" `
  --env DEPLOYFLOW_BASE_URL=http://api:8000 `
  api python /smoke/smoke_test.py
```

Stop the deployment:

```powershell
docker compose down
```

Set `DEPLOYFLOW_PORT` before startup to use another loopback port.

## Deploy a Published Version

Deployments require an explicit full-commit GHCR tag. The script pulls the image, starts Compose with `--no-build`, waits for health, and runs the complete CRUD smoke test.

```sh
sh scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-a7f2b2437c8eba0daa7a4ef29bac46301d7df848
```

Git for Windows can invoke its bundled shell directly:

```powershell
& "C:\Program Files\Git\bin\sh.exe" scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-a7f2b2437c8eba0daa7a4ef29bac46301d7df848
```

Rollback uses the identical command with the recorded known-good tag. See [docs/deployment.md](docs/deployment.md) for image verification, rollback evidence, authentication, and failure handling.

## Local Python Development

Prerequisites: Python 3.12+ and Git.

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m uvicorn app.main:app --reload
```

Quality checks:

```powershell
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m pytest
```

On macOS or Linux, invoke the equivalent executables from `.venv/bin`.

## CI/CD Flow

The workflow runs on pull requests and pushes to `main`:

1. **Ruff and pytest** — installs development dependencies, verifies lint and formatting, and runs API tests.
2. **Container build and Trivy scan** — builds the production Dockerfile and enforces the vulnerability policy.
3. **Publish immutable GHCR image** — runs only for trusted `main` pushes after both previous jobs succeed, rescans the exact candidate, rejects tag reuse, and pushes one `sha-<full-commit>` tag.

Pull requests never receive package write permission, authenticate to GHCR, or execute the publishing steps.

### Vulnerability Policy

Trivy 0.76.1 scans operating-system and Python packages. CI blocks fixable `HIGH` and `CRITICAL` findings and reports the scan in the job log. Unfixed findings are non-blocking for this MVP because no actionable patch exists; the policy must be reconsidered for a production release. `LOW`, `MEDIUM`, and `UNKNOWN` findings are outside the blocking gate.

## Security Controls

| Area | Control |
| --- | --- |
| Workflow trust | Publishing is job-gated to pushes on `refs/heads/main`; pull requests remain read-only |
| Permissions | Global `contents: read`; only the publish job adds `packages: write` |
| Action integrity | Every external GitHub Action is pinned to a full commit SHA |
| Credentials | Checkout credentials are not persisted; publishing uses the repository-scoped `GITHUB_TOKEN`; no project secret is required |
| Image traceability | Full-commit tag plus OCI source and revision labels; existing or ambiguous tags fail closed |
| Supply chain | Python base image pinned by digest; publish candidate scanned before push |
| Runtime identity | Container runs as UID/GID `10001`, not root |
| Runtime isolation | Read-only root filesystem, dropped capabilities, `no-new-privileges`, PID limit, constrained temporary filesystem |
| Exposure | Compose binds the API to host loopback by default |
| Verification | Application health check and full CRUD smoke test run after deployment and rollback |

## Limitations and Production Evolution

This is a CI/CD portfolio MVP, not a production task platform.

- Task state is in memory and is lost when the container is replaced.
- The API has no authentication, authorization, rate limiting, or tenant isolation.
- Compose provides a single local instance without zero-downtime orchestration.
- TLS termination, DNS, monitoring, alerting, centralized logs, backups, and disaster recovery are not included.
- Images are vulnerability-scanned but are not yet signed and no SBOM or provenance attestation is published.
- Dependency ranges are constrained but there is no fully locked Python dependency file.

A sensible production path is to add PostgreSQL with migrations and backups, API authentication and authorization, TLS through a managed ingress or reverse proxy, structured observability, environment approvals, signed images with SBOM/provenance, and a deployment platform selected from actual scale and availability requirements. Kubernetes is intentionally not introduced without those requirements.

## Troubleshooting

| Symptom | Check or resolution |
| --- | --- |
| Port 8000 is unavailable | Set `DEPLOYFLOW_PORT` before `docker compose up` |
| Container is unhealthy | Run `docker compose ps` and `docker compose logs --tail 100 api` |
| Compose model is invalid | Run `docker compose config` and inspect missing or malformed environment values |
| GHCR pull is denied | Confirm package visibility or authenticate with a token that has `read:packages`; never store it in the repository |
| Deployment script rejects an image | Use a lowercase GHCR reference with `sha-` followed by the full 40-character commit |
| Git Bash rewrites container paths | Use the current stdin-based `scripts/deploy.sh`; it contains no smoke-test bind mount |
| CI refuses an existing tag | The immutable tag already exists; investigate the prior run instead of overwriting it |
| Smoke test fails | Inspect API logs, keep the failed version unaccepted, and redeploy the recorded known-good tag |

## Repository Guide

```text
app/                    FastAPI application, models, and repository
tests/                  pytest API contract tests
scripts/smoke_test.py   dependency-free health and CRUD smoke test
scripts/deploy.sh       immutable-image deployment and verification
.github/workflows/      CI, security scan, and trusted GHCR publication
Dockerfile              pinned multi-stage non-root image
compose.yaml            health check and runtime hardening
docs/architecture.md    system design and decisions
docs/deployment.md      deployment, evidence checks, and rollback
docs/progress.md        commands and verified results
docs/tasks.md           milestone acceptance criteria
```

## Project Status

M1 through M5 are implemented and locally verified. Portfolio evidence uses live links and reproducible command records without inventing screenshots or unsupported claims. See [docs/tasks.md](docs/tasks.md) for milestone status.

## License

No license has been selected. No license badge is displayed, and all rights remain reserved until a license file is added.
