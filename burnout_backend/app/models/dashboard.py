from pydantic import BaseModel

from burnout_backend.app.models.metrics import (
    BurnoutRiskSummary,
    RecoverySection,
    ScheduleSection,
    SleepSection,
    WorkloadSection,
)


class DashboardResponse(BaseModel):
    generated_at: str
    burnout_risk: BurnoutRiskSummary
    sleep: SleepSection
    workload: WorkloadSection
    recovery: RecoverySection
    schedule: ScheduleSection
    recommendations: list[str]
