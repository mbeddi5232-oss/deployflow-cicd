# Delivery Milestones

## M1 — API and automated tests

- [x] Create a typed FastAPI application.
- [x] Implement `GET /health`.
- [x] Implement list, create, read, replace, and delete task endpoints.
- [x] Validate request bodies and return appropriate HTTP status codes.
- [x] Add isolated pytest API tests for health, CRUD, errors, and validation.
- [x] Configure Ruff and pytest in `pyproject.toml`.
- [x] Run Ruff and pytest successfully in an available Python 3.12 environment.

Acceptance criteria: the API starts with Uvicorn, `/health` returns HTTP 200, CRUD behavior is covered by passing tests, and lint checks pass.

## M2 — Containerized local deployment

- [x] Add a small, non-root, production-oriented Dockerfile.
- [x] Add `.dockerignore`.
- [x] Add Docker Compose service configuration with a health check.
- [x] Build and start the service locally.
- [x] Execute health and CRUD smoke tests against the container.
- [x] Document local build, run, stop, and troubleshooting commands.

Acceptance criteria: a clean checkout can run the API through Docker Compose and becomes healthy without a host Python installation.

## M3 — Continuous integration and security scanning

- [x] Add a GitHub Actions workflow for pull requests and the default branch.
- [x] Run Ruff formatting and lint checks.
- [x] Run pytest.
- [x] Build the container image without publishing it on pull requests.
- [x] Scan the built image with Trivy and fail on the documented severity policy.
- [x] Use pinned action versions and least-privilege workflow permissions.
- [x] Confirm quality, container-security, and publishing jobs pass on GitHub-hosted runners after an approved push.

Acceptance criteria: one reproducible workflow provides lint, test, build, and vulnerability evidence for every proposed change.

## M4 — Versioned publishing, deployment, and rollback

- [x] Implement immutable commit-tag publishing to GHCR from trusted `main` pushes only.
- [x] Document required repository settings and workflow permissions.
- [x] Add a reproducible deployment procedure using an explicit image tag.
- [x] Run local health and CRUD smoke tests through the explicit-image deployment path.
- [x] Document rollback to a known-good image tag.
- [x] Require approval before any real push, publication, or remote deployment.
- [x] Verify two distinct GHCR publications and a local baseline → candidate → baseline rollback after explicit approval.

Optional follow-up: verify deployment on a non-local host only after separate approval; this is outside the current portfolio scope.

Acceptance criteria: an authorized release produces a traceable GHCR image, deployment consumes an immutable version, smoke tests validate it, and rollback does not rebuild source.

## M5 — Portfolio evidence and polish

- [x] Link the successful GitHub Actions run, GHCR package, image digests, and rollback record.
- [x] Add a genuine CI badge; omit screenshots and license badges when no authentic artifact or license exists.
- [x] Document the end-to-end delivery flow and security controls.
- [x] Review setup, verification, deployment, rollback, and troubleshooting commands.
- [x] Record limitations and sensible production evolution paths.
- [x] Review the repository for recruiter-facing clarity and evidence traceability.

Acceptance criteria: a recruiter can understand the architecture, run the project, inspect authentic CI evidence, and explain the release and rollback process from the repository alone.
