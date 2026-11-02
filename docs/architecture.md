# Architecture

## System Context

DeployFlow is intentionally a single-service application. The Task API provides a small, testable workload while the portfolio project demonstrates the delivery controls around it.

```mermaid
flowchart LR
    Developer[Developer] -->|git push / pull request| GitHub[GitHub repository]
    GitHub --> Actions[GitHub Actions]
    Actions --> Lint[Ruff lint and format checks]
    Actions --> Tests[pytest API tests]
    Actions --> Build[Docker image build]
    Build --> Scan[Trivy vulnerability scan]
    Scan -->|versioned image| GHCR[GitHub Container Registry]
    GHCR -->|docker compose pull| Host[Deployment host]
    Host --> API[FastAPI Task API]
    Smoke[Smoke test] -->|GET /health and CRUD check| API
    User[API client] -->|HTTP /health and /tasks| API
```

The CI, registry, deployment, and smoke-test nodes describe the target architecture for M2-M4. In M1, the implemented runtime consists of the API and automated tests only.

## Runtime Design

The FastAPI process exposes:

- `GET /health` for runtime health checks.
- `GET /tasks` and `GET /tasks/{id}` for reads.
- `POST /tasks`, `PUT /tasks/{id}`, and `DELETE /tasks/{id}` for writes.
- `/docs` for generated OpenAPI documentation.

Tasks are stored in a thread-safe in-memory repository. State is process-local and is lost when the process restarts. This is deliberate for the CI/CD MVP: it removes database operations from the critical path and keeps attention on build, verification, publishing, deployment, and rollback.

## Design Decisions

### Single service

A modular monolith is sufficient for one small bounded context. Microservices would add network, deployment, and observability complexity without improving the portfolio evidence.

### Application factory

`create_app` accepts a repository instance. Tests receive isolated state without global resets or external services, while production uses a default in-memory repository.

### Replace semantics for updates

`PUT /tasks/{id}` requires a complete mutable task representation. This keeps the contract explicit. Partial updates can be introduced later only if a real client requires `PATCH`.

### Immutable response models

Stored task models are immutable. Updates create a new value, reducing accidental mutation of shared in-memory state.

### Versioned container images

M4 will publish immutable version tags to GHCR. Deployments will reference an explicit tag so rollback means redeploying a previously verified image rather than rebuilding source.

### Security boundary

No secret belongs in the image or repository. GitHub authentication will use repository-provided tokens with least-privilege workflow permissions. Trivy will scan the final image before publication or deployment.
