from pydantic import BaseModel, Field


class BurnoutRiskSummary(BaseModel):
    percentage: float = Field(..., ge=0, le=100)
    risk_level: str
    explanation: str


class SleepSection(BaseModel):
    average_sleep_hours: float
    recommended_sleep_hours: float
    sleep_balance_percentage: float = Field(..., ge=0, le=100)
    sleep_risk_percentage: float = Field(..., ge=0, le=100)
    explanation: str


class WorkloadSection(BaseModel):
    work_hours: float
    class_hours: float
    assignment_hours: float
    total_productive_hours: float
    workload_pressure_percentage: float = Field(..., ge=0, le=100)
    explanation: str


class RecoverySection(BaseModel):
    break_minutes: int
    hobby_minutes: int
    total_recovery_minutes: int
    recommended_recovery_minutes: int
    recovery_balance_percentage: float = Field(..., ge=0, le=100)
    recovery_risk_percentage: float = Field(..., ge=0, le=100)
    explanation: str


class ScheduleSection(BaseModel):
    meeting_count: int
    deadline_count: int
    commute_hours: float
    schedule_density_percentage: float = Field(..., ge=0, le=100)
    explanation: str

