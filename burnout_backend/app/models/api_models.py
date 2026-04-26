from pydantic import BaseModel, Field


class PrototypeCheckInPayload(BaseModel):
    sleep_hours: float = Field(..., ge=0, le=24)
    work_study_hours: float = Field(..., ge=0, le=24)
    break_minutes: int = Field(..., ge=0, le=1440)
    commute_minutes: int = Field(..., ge=0, le=1440)
    deadline_count: int = Field(..., ge=0)
    hobby_minutes: int = Field(..., ge=0, le=1440)
    mood: str | None = None
    hobbies: list[str] = Field(default_factory=list)
    stress_relievers: list[str] = Field(default_factory=list)
    class_hours: float = Field(default=0, ge=0, le=24)
    assignment_hours: float = Field(default=0, ge=0, le=24)
    meeting_count: int = Field(default=0, ge=0)


class CheckInHistoryEntry(BaseModel):
    timestamp: str
    sleep_hours: float
    work_study_hours: float
    class_hours: float
    assignment_hours: float
    break_minutes: int
    hobby_minutes: int
    commute_minutes: int
    meeting_count: int
    deadline_count: int
    mood: str | None = None
    hobbies: list[str] = Field(default_factory=list)
    stress_relievers: list[str] = Field(default_factory=list)
    burnout_risk_percentage: float
    risk_level: str
    sleep_balance_percentage: float
    workload_pressure_percentage: float
    recovery_balance_percentage: float
    schedule_density_percentage: float
