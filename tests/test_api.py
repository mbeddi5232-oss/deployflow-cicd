"""API contract tests for DeployFlow."""

from fastapi.testclient import TestClient

from app.main import create_app
from app.repository import TaskRepository


def make_client() -> TestClient:
    """Create an isolated client with empty task state."""

    return TestClient(create_app(TaskRepository()))


def create_task(client: TestClient) -> dict[str, object]:
    response = client.post(
        "/tasks",
        json={"title": "Ship DeployFlow", "description": "Complete the MVP"},
    )
    assert response.status_code == 201
    return response.json()


def test_health() -> None:
    with make_client() as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_task_crud_lifecycle() -> None:
    with make_client() as client:
        created = create_task(client)
        task_id = created["id"]

        assert created["title"] == "Ship DeployFlow"
        assert created["description"] == "Complete the MVP"
        assert created["completed"] is False
        assert created["created_at"] == created["updated_at"]

        listed = client.get("/tasks")
        assert listed.status_code == 200
        assert listed.json() == [created]

        fetched = client.get(f"/tasks/{task_id}")
        assert fetched.status_code == 200
        assert fetched.json() == created

        updated = client.put(
            f"/tasks/{task_id}",
            json={
                "title": "Ship DeployFlow",
                "description": "M1 complete",
                "completed": True,
            },
        )
        assert updated.status_code == 200
        assert updated.json()["completed"] is True
        assert updated.json()["description"] == "M1 complete"

        deleted = client.delete(f"/tasks/{task_id}")
        assert deleted.status_code == 204
        assert deleted.content == b""
        assert client.get(f"/tasks/{task_id}").status_code == 404


def test_unknown_tasks_return_not_found() -> None:
    with make_client() as client:
        get_response = client.get("/tasks/999")
        update_response = client.put(
            "/tasks/999",
            json={"title": "Unknown", "description": "", "completed": False},
        )
        delete_response = client.delete("/tasks/999")

    assert get_response.status_code == 404
    assert update_response.status_code == 404
    assert delete_response.status_code == 404


def test_create_rejects_invalid_payload() -> None:
    with make_client() as client:
        empty_title = client.post("/tasks", json={"title": ""})
        missing_title = client.post("/tasks", json={})
        oversized_description = client.post(
            "/tasks", json={"title": "Valid", "description": "x" * 2_001}
        )

    assert empty_title.status_code == 422
    assert missing_title.status_code == 422
    assert oversized_description.status_code == 422


def test_task_ids_increase_and_list_order_is_stable() -> None:
    with make_client() as client:
        first = client.post("/tasks", json={"title": "First"}).json()
        second = client.post("/tasks", json={"title": "Second"}).json()
        tasks = client.get("/tasks").json()

    assert first["id"] == 1
    assert second["id"] == 2
    assert [task["id"] for task in tasks] == [1, 2]
