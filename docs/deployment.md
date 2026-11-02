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

Anonymous pulls and the repository package page were verified on 2026-11-02. No remote package setting is changed automatically by this project; package linkage and visibility should still be reviewed after repository or ownership changes.

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

## Verified Two-Version Rollback

The published artifacts used in the local rollback exercise were:

| Role | Image tag | Registry digest |
| --- | --- | --- |
| Known-good baseline | `sha-e35f6393d6be2157ab9efcfa3a2c0a6527364eb5` | `sha256:607995610eac0044361280e96296df68a472ef742718c83b9a6cfa03a25bd755` |
| Candidate | `sha-a7f2b2437c8eba0daa7a4ef29bac46301d7df848` | `sha256:d672768378b6d8e86863d2de634d76fed57b645860040c28f7a2b4711a343bac` |

Both images were produced by successful trusted `main` workflows. Their OCI revision labels matched their full commit tags and their registry digests were distinct. The local sequence baseline → candidate → baseline passed container health, host health, and the complete CRUD smoke test at every stage. Compose resources were removed afterward. The detailed commands and results are preserved in `docs/progress.md`.

## Repeat the Rollback Test Safely

A future genuine rollback test requires two images produced by the trusted `main` workflow from different approved commits. A local retag, an abbreviated commit, or two tags resolving to the same digest does not qualify.

After a separate approval to push and publish a candidate commit:

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

Do not proceed if a tag is missing, a revision label does not match, the digests are equal, or either image has not passed its trusted CI security gate. Publishing a future candidate and any remote deployment require explicit approval.

## Troubleshooting

| Failure | Diagnostic or action |
| --- | --- |
| Image reference rejected before pull | Use lowercase `ghcr.io/<owner>/<image>:sha-<40-character-commit>` syntax |
| `manifest unknown` | Confirm the full commit tag exists in the successful publishing run and GHCR package |
| GHCR returns `denied` | Confirm public visibility or authenticate the host with `read:packages`; never save the token in this repository |
| Compose validation fails | Run `docker compose config` and inspect `DEPLOYFLOW_IMAGE` and `DEPLOYFLOW_PORT` |
| API never becomes healthy | Run `docker compose ps` and `docker compose logs --tail 100 api` |
| Smoke test fails after startup | Do not accept the version; preserve logs and redeploy the recorded known-good tag |
| Port 8000 is occupied | Set `DEPLOYFLOW_PORT` to another loopback port before deployment |
| Git for Windows has no `sh` on `PATH` | Invoke `C:\Program Files\Git\bin\sh.exe` explicitly as documented above |
| Rollback loses task data | Expected for this in-memory MVP; production requires persistent storage and backup/restore |

## Stop the Deployment

```sh
docker compose down
```

This removes the project container and network but retains pulled images for later rollback.
