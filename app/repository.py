"""Thread-safe in-memory task repository."""

from threading import Lock

from app.models import Task, TaskCreate, TaskUpdate, utc_now


class TaskRepository:
    """Store task state for the lifetime of one application process."""

    def __init__(self) -> None:
        self._tasks: dict[int, Task] = {}
        self._next_id = 1
        self._lock = Lock()

    def list(self) -> list[Task]:
        """Return all tasks ordered by identifier."""

        with self._lock:
            return list(self._tasks.values())

    def get(self, task_id: int) -> Task | None:
        """Return a task by identifier, if present."""

        with self._lock:
            return self._tasks.get(task_id)

    def create(self, payload: TaskCreate) -> Task:
        """Create and store a task."""

        with self._lock:
            now = utc_now()
            task = Task(
                id=self._next_id,
                title=payload.title,
                description=payload.description,
                completed=False,
                created_at=now,
                updated_at=now,
            )
            self._tasks[task.id] = task
            self._next_id += 1
            return task

    def update(self, task_id: int, payload: TaskUpdate) -> Task | None:
        """Replace an existing task, or return None when it is unknown."""

        with self._lock:
            current = self._tasks.get(task_id)
            if current is None:
                return None

            task = current.model_copy(
                update={
                    "title": payload.title,
                    "description": payload.description,
                    "completed": payload.completed,
                    "updated_at": utc_now(),
                }
            )
            self._tasks[task_id] = task
            return task

    def delete(self, task_id: int) -> bool:
        """Delete a task and report whether it existed."""

        with self._lock:
            return self._tasks.pop(task_id, None) is not None
