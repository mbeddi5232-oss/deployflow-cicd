"""FastAPI entry point for DeployFlow."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Response, status

from app.models import Task, TaskCreate, TaskUpdate
from app.repository import TaskRepository


def create_app(repository: TaskRepository | None = None) -> FastAPI:
    """Create an application with an optionally supplied task repository."""

    app = FastAPI(
        title="DeployFlow Task API",
        description="Minimal API used to demonstrate an automated delivery workflow.",
        version="0.1.0",
    )
    app.state.task_repository = repository or TaskRepository()

    def get_repository() -> TaskRepository:
        return app.state.task_repository

    repository_dependency = Annotated[TaskRepository, Depends(get_repository)]

    @app.get("/health", tags=["operations"])
    def health() -> dict[str, str]:
        """Report that the process is ready to serve requests."""

        return {"status": "healthy"}

    @app.get("/tasks", response_model=list[Task], tags=["tasks"])
    def list_tasks(repository: repository_dependency) -> list[Task]:
        """List all tasks."""

        return repository.list()

    @app.get("/tasks/{task_id}", response_model=Task, tags=["tasks"])
    def get_task(task_id: int, repository: repository_dependency) -> Task:
        """Return one task."""

        task = repository.get(task_id)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @app.post(
        "/tasks",
        response_model=Task,
        status_code=status.HTTP_201_CREATED,
        tags=["tasks"],
    )
    def create_task(payload: TaskCreate, repository: repository_dependency) -> Task:
        """Create a task."""

        return repository.create(payload)

    @app.put("/tasks/{task_id}", response_model=Task, tags=["tasks"])
    def update_task(task_id: int, payload: TaskUpdate, repository: repository_dependency) -> Task:
        """Replace a task."""

        task = repository.update(task_id, payload)
        if task is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return task

    @app.delete(
        "/tasks/{task_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["tasks"],
    )
    def delete_task(task_id: int, repository: repository_dependency) -> Response:
        """Delete a task."""

        if not repository.delete(task_id):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
        return Response(status_code=status.HTTP_204_NO_CONTENT)

    return app


app = create_app()
