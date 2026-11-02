# Versioned Deployment and Rollback

## Artifact Contract

The trusted `main` publishing job produces one image reference per commit:

```text
ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-<40-character-commit>
```

No `latest` or branch tag is published. The workflow refuses to push when the commit tag already exists and fails closed when it cannot prove that the tag is unused.

Pull-request workflows never receive package write permission, never authenticate to GHCR, and never execute the publish job. The publish job receives only `contents: read` and `packages: write`, uses the repository `GITHUB_TOKEN`, and runs only after quality and image-security checks succeed on a push to `main`.

## GHCR Access

The workflow labels the image with its source repository so the first workflow publication can link the package to this repository. GitHub Container Registry package visibility is managed separately from repository visibility.

- Public packages can be pulled anonymously.
- Private packages require the deployment host to authenticate with a credential that has `read:packages` access.
- Never store a GHCR token in this repository or a Compose file.

The first approved publication must confirm that the package is linked to this repository and has the intended visibility. No remote package setting is changed automatically by this project.

## Deploy an Explicit Version

Prerequisites on the deployment host:

- Docker Engine with Docker Compose.
- Access to GHCR when the package is private.
- A clean checkout containing `compose.yaml` and `scripts/`.

Select the exact image from a successful trusted workflow run, then execute:

```sh
sh scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-0123456789abcdef0123456789abcdef01234567
```

The script performs these operations in order:

1. Rejects missing, mutable, uppercase, or abbreviated image references.
2. Validates the resolved Compose model.
3. Pulls the selected image.
4. Recreates the API with `--no-build` and waits for the Compose health check.
5. Runs health and full CRUD smoke tests through the Compose network.

The command exits nonzero if any step fails. Inspect a failure with:

```sh
docker compose ps
docker compose logs --tail 100 api
```

After a successful smoke test, record the exact image tag as the known-good version in the release or deployment record.

## Roll Back

Identify the most recent known-good commit tag. Do not rebuild its source and do not substitute `latest`.

```sh
sh scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-89abcdef0123456789abcdef0123456789abcdef
```

The same health and CRUD checks must pass before rollback is considered successful. Confirm the running image and service state:

```sh
docker compose ps
docker inspect "$(docker compose ps --quiet api)" --format '{{.Config.Image}}'
```

Because the MVP repository is in-memory, replacing the container discards all task data. A persistent datastore and backup/restore procedure are required before production use.

## Stop the Deployment

```sh
docker compose down
```

This removes the project container and network but retains pulled images for later rollback.
