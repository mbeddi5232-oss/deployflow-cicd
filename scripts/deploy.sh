#!/bin/sh

set -eu

usage() {
    echo "Usage: sh scripts/deploy.sh ghcr.io/<owner>/<image>:sha-<40-character-commit>" >&2
}

if [ "$#" -ne 1 ]; then
    usage
    exit 2
fi

image_ref=$1
if ! printf '%s\n' "$image_ref" \
    | grep -Eq '^ghcr\.io/[a-z0-9._-]+/[a-z0-9._/-]+:sha-[0-9a-f]{40}$'; then
    echo "Error: image must be a lowercase GHCR reference with an immutable full commit tag." >&2
    usage
    exit 2
fi

if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is required." >&2
    exit 1
fi

project_dir=$(CDPATH='' cd -- "$(dirname -- "$0")/.." && pwd)
cd "$project_dir"

export DEPLOYFLOW_IMAGE="$image_ref"

docker compose config --quiet
docker compose pull api
docker compose up --detach --no-build --force-recreate --wait --wait-timeout 60
docker compose run --rm --no-deps --no-TTY \
    --env DEPLOYFLOW_BASE_URL=http://api:8000 \
    api python - < "$project_dir/scripts/smoke_test.py"

echo "Deployment verified: $image_ref"
