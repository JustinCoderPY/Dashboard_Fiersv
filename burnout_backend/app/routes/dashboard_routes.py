from fastapi import APIRouter

from burnout_backend.app.models.api_models import (
    CheckInHistoryEntry,
    PrototypeCheckInPayload,
)
from burnout_backend.app.models.dashboard import DashboardResponse
from burnout_backend.app.models.user_input import UserInput
from burnout_backend.app.services.checkin_storage import (
    append_api_checkin,
    read_api_history,
)
from burnout_backend.app.services.dashboard_service import analyze_dashboard, build_dashboard


router = APIRouter(tags=["dashboard"])


@router.post("/dashboard/analyze", response_model=DashboardResponse)
def analyze_user_dashboard(user_input: UserInput) -> DashboardResponse:
    return analyze_dashboard(user_input)


@router.post("/api/dashboard", response_model=DashboardResponse)
def dashboard_check_in(payload: PrototypeCheckInPayload) -> DashboardResponse:
    user_data = {
        "average_sleep_hours": payload.sleep_hours,
        "work_hours": payload.work_study_hours,
        "class_hours": payload.class_hours,
        "assignment_hours": payload.assignment_hours,
        "break_minutes": payload.break_minutes,
        "hobby_minutes": payload.hobby_minutes,
        "commute_hours": round(payload.commute_minutes / 60, 2),
        "meeting_count": payload.meeting_count,
        "deadline_count": payload.deadline_count,
        "hobbies": payload.hobbies,
        "stress_relievers": payload.stress_relievers,
    }
    dashboard = build_dashboard(user_data)
    append_api_checkin(payload, dashboard)
    return dashboard


@router.get("/api/history", response_model=list[CheckInHistoryEntry])
def dashboard_history(limit: int = 7) -> list[CheckInHistoryEntry]:
    return read_api_history(limit=limit)
