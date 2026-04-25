from fastapi import APIRouter

from burnout_backend.app.models.dashboard import DashboardResponse
from burnout_backend.app.models.user_input import UserInput
from burnout_backend.app.services.dashboard_service import analyze_dashboard


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.post("/analyze", response_model=DashboardResponse)
def analyze_user_dashboard(user_input: UserInput) -> DashboardResponse:
    return analyze_dashboard(user_input)
