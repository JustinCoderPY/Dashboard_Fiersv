from typing import Optional

from pydantic import BaseModel, Field


class UserInput(BaseModel):
    average_sleep_hours: float = Field(..., ge=0, le=24)
    work_hours: float = Field(..., ge=0, le=24)
    class_hours: float = Field(..., ge=0, le=24)
    assignment_hours: float = Field(..., ge=0, le=24)
    break_minutes: int = Field(..., ge=0, le=1440)
    hobby_minutes: int = Field(..., ge=0, le=1440)
    commute_hours: float = Field(..., ge=0, le=24)
    meeting_count: int = Field(..., ge=0)
    deadline_count: int = Field(..., ge=0)
    hobbies: list[str] = Field(default_factory=list)
    stress_relievers: list[str] = Field(default_factory=list)
    medication_reminders: Optional[list[str]] = None
    medication_info: Optional[str] = None

