# Progress Log

Last updated: 2026-11-02

## Current status

M1 through M3 are complete. The M4 image is published and its exact commit tag has been pulled, deployed locally, and smoke-tested successfully. The deployment script is verified under Git for Windows and Linux shells. A genuine rollback test remains blocked until a second immutable version is published with approval.

## Completed work

- Inspected the initial workspace; it was empty and was not a Git repository.
- Initialized the Git repository on `main`; the M1 commit is tracked by `origin/main`.
- Added repository conventions and safety rules in `AGENTS.md`.
- Added Python project metadata and tool configuration in `pyproject.toml`.
- Implemented health and task CRUD endpoints with validated Pydantic models.
- Implemented a thread-safe, process-local task repository.
- Added API tests for health, CRUD lifecycle, missing resources, invalid inputs, ID generation, and stable listing.
- Added a reusable HTTP health smoke test for local and future deployment verification.
- Added architecture, milestones, and initial project documentation.
- Added a pinned, multi-stage Dockerfile that installs from an offline wheel set and runs as UID/GID `10001`.
- Added a minimal `.dockerignore`; the final verified build context transfer was 4.68 kB.
- Added Docker Compose deployment with loopback-only port publishing, health checks, read-only root filesystem, dropped capabilities, `no-new-privileges`, init handling, restart behavior, and a PID limit.
- Extended the smoke test to verify health and the complete task CRUD lifecycle with cleanup.
- Documented container build, start, smoke-test, stop, and troubleshooting workflows.
- Reviewed the complete M2 diff, revalidated the Compose model, and confirmed that no project containers remain running.
- Audited tracked and untracked M2 content for common secret and private-key patterns; none were found.
- Added CI triggers for pull requests and pushes to `main` with concurrency cancellation and job timeouts.
- Added Ruff lint, Ruff format, pytest, Docker build, and Trivy scan jobs.
- Limited workflow permissions to `contents: read`, disabled persisted checkout credentials, and pinned every external action to a full commit SHA.
- Defined a blocking Trivy policy for fixable `HIGH` and `CRITICAL` OS and library vulnerabilities.
- Upgraded FastAPI to 0.162 and the test client to `httpx2` after Trivy identified three fixable Starlette vulnerabilities in the previous dependency line.
- Added a trusted `main` publishing job that runs only after quality and container-security jobs succeed.
- Limited package write permission to the publishing job; pull-request workflows remain read-only and never authenticate to GHCR.
- Added full-commit `sha-<40-character-commit>` image tags, OCI source and revision labels, an exact-candidate Trivy scan, and fail-closed tag-reuse protection.
- Added explicit image selection to Compose and a deployment script that pulls one immutable version, starts it with `--no-build`, waits for health, and runs the complete CRUD smoke test.
- Documented GHCR access, version selection, deployment failure inspection, known-good version recording, and rollback without rebuilding source.
- Removed host bind paths from the deployment smoke step by streaming the test source over standard input, resolving Git-for-Windows path conversion without adding a Linux-specific branch.

## Environment inspection

| Prerequisite | Result |
| --- | --- |
| Git | Installed: 2.56.0.windows.2 |
| Python | Missing from `PATH`; Windows Store alias responded instead |
| Python launcher (`py`) | Missing |
| pip | Missing |
| Ruff | Missing |
| pytest | Missing |
| Docker CLI and engine | Installed: 29.9.2; Desktop engine was initially stopped and was started for verification |
| Docker Compose | Installed: v5.6.1 |
| Trivy | Missing from host `PATH`; containerized v0.76.1 verified |
| GitHub CLI (`gh`) | Missing |
| Git repository | `main` tracks `origin/main` at `https://github.com/mbeddi5232-oss/deployflow-cicd.git` |

## Verification results

Executed on 2026-11-02 in `python:3.12-slim` because the Windows host has no usable Python installation:

```text
python -m ruff check .
All checks passed!

python -m ruff format --check .
6 files already formatted

python -m pytest
5 passed, 1 warning in 0.65s
```

The warning is an upstream Starlette use of a deprecated AnyIO type alias; it is not emitted by application code and does not affect test behavior.

Real-server smoke verification also passed with Uvicorn running in a Python 3.12 container:

```text
HTTP 200 {"status":"healthy"}
```

## M2 verification results

Commands executed on 2026-11-02:

```powershell
docker compose config --quiet
docker compose build --pull --progress plain
docker compose up --detach --wait --wait-timeout 60
docker compose ps
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000/health
docker compose exec --no-TTY api id
docker inspect <container-id>
docker compose run --rm --no-deps --volume "${PWD}\scripts:/smoke:ro" --env DEPLOYFLOW_BASE_URL=http://api:8000 api python /smoke/smoke_test.py
docker compose logs --no-color --tail 30 api
docker compose down
```

Verified results:

```text
Compose configuration: valid
Image: deployflow-api:local
Image ID: sha256:44298c77edbb063d70286aec7a6ee1c95a6abb9c1c027a47ac6fd3a24c93b9b4
Image size: 252,688,741 bytes
Container state: healthy
Host health request: HTTP 200 {"status":"healthy"}
Runtime identity: uid=10001(deployflow) gid=10001(deployflow)
ReadonlyRootfs=true
CapDrop=["ALL"]
NoNewPrivs=1
PidsLimit=100
Health smoke test: passed
CRUD smoke test: create, list, read, update, delete, and final 404 passed
Post-smoke GET /tasks: HTTP 200 []
Compose shutdown: container and project network removed successfully
```

Final source verification in `python:3.12-slim`:

```text
Ruff lint: passed
Ruff format check: 6 files already formatted
pytest: 5 passed, 1 warning in 0.65s
```

The first source verification attempt found one overlong line and one `SIM105` cleanup pattern in the new smoke script. Both were corrected before the final passing run.

## M3 verification results

Workflow dependencies were resolved from their official repositories and pinned as follows:

```text
actions/checkout v7.0.1: 3d3c42e5aac5ba805825da76410c181273ba90b1
actions/setup-python v7.1.0: 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0
aquasecurity/trivy-action v0.36.0: ed142fd0673e97e23eac54620cfb913e5ce36c25
Trivy: v0.76.1
```

Commands executed locally on 2026-11-02:

```powershell
docker run --rm --volume "${PWD}:/repo:ro" --workdir /repo rhysd/actionlint:1.7.12 -color
docker run --rm --volume "${PWD}:/workspace" --workdir /workspace python:3.12-slim sh -c "python -m pip install --disable-pip-version-check --quiet -e '.[dev]' && python -m ruff check . && python -m ruff format --check . && python -m pytest"
docker build --pull --tag deployflow-ci:local-m3 .
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.76.1 image --exit-code 1 --ignore-unfixed --scanners vuln --pkg-types os,library --severity HIGH,CRITICAL deployflow-ci:local-m3
docker compose build
docker compose up --detach --wait --wait-timeout 60
docker compose run --rm --no-deps --volume "${PWD}\scripts:/smoke:ro" --env DEPLOYFLOW_BASE_URL=http://api:8000 api python /smoke/smoke_test.py
docker compose down
```

Verified results:

```text
actionlint 1.7.12: passed with no findings
Ruff lint: passed
Ruff format check: 6 files already formatted
pytest: 5 passed in 0.75s with no warnings
Docker build: passed
Final CI image: sha256:04781eb14a5731edd571457b2fe84b5e1aa94d6e39d1619dfc3901cdab1d9a04
Trivy 0.76.1: 0 HIGH, 0 CRITICAL findings after remediation
Compose health regression: passed
Health and CRUD smoke regression: passed
Compose shutdown: passed
```

The initial Trivy run correctly failed with three fixable `HIGH` Starlette findings: CVE-2025-62727, CVE-2026-48818, and CVE-2026-54283. Upgrading from FastAPI 0.115/Starlette 0.46.2 to FastAPI 0.162/Starlette 1.10.0 resolved all three without weakening the policy.

Checks that require GitHub Actions and were not run locally:

- Trigger behavior for an actual pull request and push to `main`.
- Action download and execution on GitHub-hosted `ubuntu-24.04` runners.
- GitHub cache behavior and displayed job/status-check results.
- End-to-end confirmation that repository Actions settings allow the pinned Aqua Security action.

## M4 verification results

The publishing and deployment implementation was reviewed for trusted-ref isolation, least-privilege permissions, immutable version selection, fail-closed behavior, and rollback reproducibility.

Commands executed locally on 2026-11-02:

```powershell
docker run --rm --volume "${PWD}:/repo:ro" --workdir /repo rhysd/actionlint:1.7.12 -color
docker run --rm --volume "${PWD}:/mnt:ro" koalaman/shellcheck-alpine:v0.11.0 shellcheck /mnt/scripts/deploy.sh
docker run --rm --volume "${PWD}:/mnt:ro" --workdir /mnt alpine:3.22 sh -n scripts/deploy.sh
docker compose config --quiet
$env:DEPLOYFLOW_IMAGE = "ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-2862a9e01c97c171be2637298043d696dfef0d93"
docker compose config --quiet
docker run --rm --volume "${PWD}:/workspace" --workdir /workspace python:3.12-slim sh -c "python -m pip install --disable-pip-version-check --quiet -e '.[dev]' && python -m ruff check . && python -m ruff format --check . && python -m pytest"
docker build --pull --tag deployflow-ci:local-m4 .
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:0.76.1 image --exit-code 1 --ignore-unfixed --scanners vuln --pkg-types os,library --severity HIGH,CRITICAL deployflow-ci:local-m4
docker compose up --detach --no-build --force-recreate --wait --wait-timeout 60
docker compose run --rm --no-deps --volume "${PWD}\scripts:/smoke:ro" --env DEPLOYFLOW_BASE_URL=http://api:8000 api python /smoke/smoke_test.py
docker compose down
```

Verified results:

```text
actionlint 1.7.12: passed with no findings
ShellCheck 0.11.0: passed with no findings
POSIX shell syntax: passed
Invalid or abbreviated image reference: rejected with exit code 2
Default Compose configuration: valid
Explicit immutable-image Compose configuration: valid
Ruff lint: passed
Ruff format check: 6 files already formatted
pytest: 5 passed in 0.76s
Docker build: passed
Final M4 image: sha256:d5ebbad18d20ed8bb36250bdee7b1faa0bda3a2b5f929f8699df989f6cd28596
Trivy 0.76.1: passed the fixable HIGH/CRITICAL gate
Explicit-image deployment: healthy
Health and CRUD smoke test: passed
Compose shutdown: passed
```

The explicit deployment test used a local image retagged with the required GHCR commit-reference format. It did not contact GHCR, publish an image, or perform a remote deployment.

### Published M4 artifact verification

Commands executed locally on 2026-11-02 after the approved M4 push:

```powershell
docker pull ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5
$tokenResponse = Invoke-RestMethod -UseBasicParsing -Uri "https://ghcr.io/token?service=ghcr.io&scope=repository%3Ambeddi5232-oss%2Fdeployflow-cicd%3Apull"
$catalog = Invoke-RestMethod -UseBasicParsing -Headers @{ Authorization = "Bearer $($tokenResponse.token)" } -Uri "https://ghcr.io/v2/mbeddi5232-oss/deployflow-cicd/tags/list"
$env:DEPLOYFLOW_IMAGE = "ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5"
docker compose config --quiet
docker compose pull api
docker compose up --detach --no-build --force-recreate --wait --wait-timeout 60
Invoke-RestMethod -UseBasicParsing http://127.0.0.1:8000/health
docker compose run --rm --no-deps --volume "${PWD}\scripts:/smoke:ro" --env DEPLOYFLOW_BASE_URL=http://api:8000 api python /smoke/smoke_test.py
$containerId = docker compose ps --quiet api
docker inspect $containerId --format "{{.Config.Image}} {{.State.Health.Status}}"
docker compose down
```

Verified results:

```text
Anonymous GHCR pull: passed
Published tag: sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5
Registry digest: sha256:607995610eac0044361280e96296df68a472ef742718c83b9a6cfa03a25bd755
GHCR tag catalog: exactly one tag, matching the requested commit
Compose deployment: exact published tag running and healthy
Host health request: status=healthy
Health and CRUD smoke test: passed
Compose shutdown: passed
Rollback: not executed because no second published version exists
```

The original deployment script could not complete under Git for Windows because MSYS rewrote the container path `/smoke/smoke_test.py`; suppressing that rewrite then left the Git-Bash bind source unavailable to Docker. The script was corrected by streaming `scripts/smoke_test.py` to `python -` over standard input, removing both path-sensitive arguments.

### Cross-platform deployment script verification

Commands executed locally on 2026-11-02:

```powershell
docker run --rm --volume "${PWD}:/mnt:ro" koalaman/shellcheck-alpine:v0.11.0 shellcheck /mnt/scripts/deploy.sh
docker run --rm --volume "${PWD}:/mnt:ro" --workdir /mnt alpine:3.22 sh -n scripts/deploy.sh
& "C:\Program Files\Git\bin\sh.exe" scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5
docker run --rm --volume /var/run/docker.sock:/var/run/docker.sock --volume "${PWD}:/project:ro" --workdir /project docker:29-cli sh scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5
```

Verified results:

```text
ShellCheck 0.11.0: passed with no findings
POSIX shell syntax: passed
Invalid or mutable reference: rejected with exit code 2
Git-for-Windows deployment: healthy; health and CRUD smoke tests passed
Linux-shell deployment: healthy; health and CRUD smoke tests passed
Both deployments used the exact published e35f639 commit tag
Both Compose projects were removed successfully after verification
```

The two-version rollback procedure is documented in `docs/deployment.md`. It requires a separately approved commit and trusted GHCR publication, matching OCI revision labels, and two distinct registry digests. No second image was published and no rollback was executed during this work.

Remote verification still required:

- Confirm pull-request runs skip registry authentication and publishing.
- Confirm the package is linked to the repository and has the intended visibility.
- Deploy a newer published version, then roll back to the recorded known-good tag and pass the same smoke tests.

## Blockers

- Host-native development still requires Python 3.12+ with the development dependencies installed. Container-based verification is available because Docker Desktop is running.
- Trivy is not installed on the Windows host; the pinned containerized Trivy 0.76.1 scan passed locally.
- GitHub CLI is optional for local development but would simplify authenticated repository and workflow inspection in later milestones.
- A genuine rollback test is blocked because GHCR currently contains only the published `e35f6393d6be2157ab9efcfa3a2c0a6527364eb5` version. Publishing a second version requires separate approval.

## Next verification commands

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\python -m pip install -e ".[dev]"
.\.venv\Scripts\python -m ruff check .
.\.venv\Scripts\python -m ruff format --check .
.\.venv\Scripts\python -m pytest
```
