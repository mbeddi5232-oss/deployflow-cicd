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
5. Streams the smoke-test source to the container over standard input and runs health and full CRUD checks through the Compose network.

Streaming the test avoids host bind-path conversion, so the same script works with POSIX shells on Linux and Git for Windows. When `sh` is not on the Windows `PATH`, invoke the bundled shell explicitly:

```powershell
& "C:\Program Files\Git\bin\sh.exe" scripts/deploy.sh ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-0123456789abcdef0123456789abcdef01234567
```

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

## Two-Version Rollback Test Plan

The current known-good baseline is:

```text
Image: ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5
Digest: sha256:607995610eac0044361280e96296df68a472ef742718c83b9a6cfa03a25bd755
```

A genuine rollback test requires a second image produced by the trusted `main` workflow from a different approved commit. A local retag, an abbreviated commit, or two tags resolving to the same digest does not qualify.

After a separate approval to push and publish the candidate commit:

1. Confirm both full-commit tags exist in GHCR.
2. Pull both images and verify each OCI revision label equals its tag's commit.
3. Verify the images have different registry digests.
4. Deploy the baseline tag and require health and CRUD smoke tests to pass.
5. Deploy the candidate tag and require the same tests to pass.
6. Roll back by deploying the baseline tag again; require the same tests to pass.
7. Inspect the running container and confirm it references the baseline tag before recording rollback success.
8. Run `docker compose down` after evidence is captured.

Use these preflight checks before deployment:

```sh
: "${CANDIDATE_SHA:?set CANDIDATE_SHA to the approved 40-character commit}"
baseline_image=ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5
candidate_image="ghcr.io/mbeddi5232-oss/deployflow-cicd:sha-${CANDIDATE_SHA}"

docker pull "$baseline_image"
docker pull "$candidate_image"
docker image inspect "$baseline_image" --format '{{index .Config.Labels "org.opencontainers.image.revision"}} {{index .RepoDigests 0}}'
docker image inspect "$candidate_image" --format '{{index .Config.Labels "org.opencontainers.image.revision"}} {{index .RepoDigests 0}}'
```

Do not proceed if a tag is missing, a revision label does not match, the digests are equal, or either image has not passed its trusted CI security gate. Publishing the candidate and any remote deployment require explicit approval.

## Stop the Deployment

```sh
docker compose down
```

This removes the project container and network but retains pulled images for later rollback.
