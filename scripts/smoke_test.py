"""Minimal HTTP smoke test for a running DeployFlow instance."""

import json
import os
import time
import urllib.error
import urllib.request

BASE_URL = os.getenv("DEPLOYFLOW_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MAX_ATTEMPTS = 30
RETRY_DELAY_SECONDS = 0.2


def check_health() -> None:
    """Wait for the API and validate its health response."""

    url = f"{BASE_URL}/health"
    last_error: Exception | None = None

    for _ in range(MAX_ATTEMPTS):
        try:
            with urllib.request.urlopen(url, timeout=2) as response:  # noqa: S310
                body = json.load(response)
                if response.status != 200 or body != {"status": "healthy"}:
                    raise RuntimeError(
                        f"Unexpected health response: status={response.status}, body={body}"
                    )
                print(f"Smoke test passed: GET {url} -> 200 {body}")
                return
        except (OSError, RuntimeError, urllib.error.HTTPError, json.JSONDecodeError) as error:
            last_error = error
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Smoke test failed after {MAX_ATTEMPTS} attempts: {last_error}")


if __name__ == "__main__":
    check_health()
