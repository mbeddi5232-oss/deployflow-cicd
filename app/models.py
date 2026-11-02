"""API models for task resources."""

from datetime import UTC, datetime

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """Fields accepted when creating a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2_000)


class TaskUpdate(BaseModel):
    """Fields accepted when replacing a task."""

    title: str = Field(min_length=1, max_length=200)
    description: str = Field(default="", max_length=2_000)
    completed: bool = False


class Task(BaseModel):
    """Stored task representation returned by the API."""

    model_config = ConfigDict(frozen=True)

    id: int = Field(ge=1)
    title: str
    description: str
    completed: bool
    created_at: datetime
    updated_at: datetime


def utc_now() -> datetime:
    """Return a timezone-aware timestamp in UTC."""

    return datetime.now(UTC)
