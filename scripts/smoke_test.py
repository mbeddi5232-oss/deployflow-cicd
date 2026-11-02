"""Health and CRUD smoke tests for a running DeployFlow instance."""

import json
import os
import time
import urllib.error
import urllib.request
from contextlib import suppress

BASE_URL = os.getenv("DEPLOYFLOW_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
MAX_ATTEMPTS = 30
RETRY_DELAY_SECONDS = 0.2


def request_json(
    method: str,
    path: str,
    *,
    payload: dict[str, object] | None = None,
    expected_status: int,
) -> object:
    """Send a JSON request and validate the HTTP status."""

    body = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(
        f"{BASE_URL}{path}",
        data=body,
        headers={"Content-Type": "application/json"} if body is not None else {},
        method=method,
    )

    try:
        response = urllib.request.urlopen(request, timeout=2)  # noqa: S310
    except urllib.error.HTTPError as error:
        response = error

    with response:
        response_body = response.read()
        status = response.status

    parsed_body = json.loads(response_body) if response_body else None
    if status != expected_status:
        raise RuntimeError(
            f"{method} {path} returned {status}, expected {expected_status}: {parsed_body}"
        )
    return parsed_body


def require(condition: bool, message: str) -> None:
    """Raise a readable smoke-test failure when a contract is not met."""

    if not condition:
        raise RuntimeError(message)


def check_health() -> None:
    """Wait for the API and validate its health response."""

    url = f"{BASE_URL}/health"
    last_error: Exception | None = None

    for _ in range(MAX_ATTEMPTS):
        try:
            body = request_json("GET", "/health", expected_status=200)
            require(body == {"status": "healthy"}, f"Unexpected health response: {body}")
            print(f"Health smoke test passed: GET {url} -> 200 {body}")
            return
        except (OSError, RuntimeError, json.JSONDecodeError) as error:
            last_error = error
            time.sleep(RETRY_DELAY_SECONDS)

    raise RuntimeError(f"Smoke test failed after {MAX_ATTEMPTS} attempts: {last_error}")


def check_crud() -> None:
    """Validate a complete task lifecycle against the running API."""

    task_id: int | None = None
    try:
        created = request_json(
            "POST",
            "/tasks",
            payload={"title": "M2 smoke task", "description": "Created by smoke test"},
            expected_status=201,
        )
        require(isinstance(created, dict), f"Unexpected create response: {created}")
        task_id_value = created.get("id")
        require(isinstance(task_id_value, int), f"Create response has no integer ID: {created}")
        task_id = task_id_value
        require(created.get("completed") is False, f"New task is not incomplete: {created}")

        fetched = request_json("GET", f"/tasks/{task_id}", expected_status=200)
        require(fetched == created, f"Fetched task differs from created task: {fetched}")

        listed = request_json("GET", "/tasks", expected_status=200)
        require(isinstance(listed, list), f"Unexpected task list: {listed}")
        require(any(task.get("id") == task_id for task in listed), "Created task is not listed")

        updated = request_json(
            "PUT",
            f"/tasks/{task_id}",
            payload={
                "title": "M2 smoke task",
                "description": "Updated by smoke test",
                "completed": True,
            },
            expected_status=200,
        )
        require(isinstance(updated, dict), f"Unexpected update response: {updated}")
        require(updated.get("completed") is True, f"Task was not completed: {updated}")

        request_json("DELETE", f"/tasks/{task_id}", expected_status=204)
        task_id = None

        missing = request_json("GET", f"/tasks/{created['id']}", expected_status=404)
        require(
            missing == {"detail": "Task not found"},
            f"Unexpected not-found response: {missing}",
        )
    except Exception:
        if task_id is not None:
            with suppress(Exception):
                request_json("DELETE", f"/tasks/{task_id}", expected_status=204)
        raise

    print("CRUD smoke test passed: create, list, read, update, delete, and 404 verified")


if __name__ == "__main__":
    check_health()
    check_crud()
