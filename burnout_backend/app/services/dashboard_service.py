from burnout_backend.app.models.dashboard import DashboardResponse
from burnout_backend.app.models.user_input import UserInput
from burnout_backend.app.services.burnout_engine import calculate_burnout_risk
from burnout_backend.app.services.recommendation_engine import generate_recommendations
from burnout_backend.app.services.recovery_calculator import calculate_recovery_metrics
from burnout_backend.app.services.schedule_calculator import calculate_schedule_metrics
from burnout_backend.app.services.sleep_calculator import calculate_sleep_metrics
from burnout_backend.app.services.workload_calculator import calculate_workload_metrics
from burnout_backend.app.utils.date_utils import get_utc_timestamp


def analyze_dashboard(user_input: UserInput) -> DashboardResponse:
    sleep = calculate_sleep_metrics(user_input.average_sleep_hours)
    workload = calculate_workload_metrics(
        work_hours=user_input.work_hours,
        class_hours=user_input.class_hours,
        assignment_hours=user_input.assignment_hours,
    )
    recovery = calculate_recovery_metrics(
        break_minutes=user_input.break_minutes,
        hobby_minutes=user_input.hobby_minutes,
    )
    schedule = calculate_schedule_metrics(
        meeting_count=user_input.meeting_count,
        deadline_count=user_input.deadline_count,
        commute_hours=user_input.commute_hours,
    )

    burnout_risk = calculate_burnout_risk(
        sleep=sleep,
        workload=workload,
        recovery=recovery,
        schedule=schedule,
    )

    recommendations = generate_recommendations(
        user_input=user_input,
        sleep=sleep,
        workload=workload,
        recovery=recovery,
        schedule=schedule,
    )

    return DashboardResponse(
        generated_at=get_utc_timestamp(),
        burnout_risk=burnout_risk,
        sleep=sleep,
        workload=workload,
        recovery=recovery,
        schedule=schedule,
        recommendations=recommendations,
    )


def build_dashboard(user_data: dict | UserInput) -> DashboardResponse:
    if isinstance(user_data, UserInput):
        validated_user_input = user_data
    else:
        validated_user_input = UserInput(**user_data)

    return analyze_dashboard(validated_user_input)
