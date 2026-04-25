from burnout_backend.app.models.metrics import ScheduleSection
from burnout_backend.app.utils.percentage_utils import clamp_percentage, round_percentage


MEETING_THRESHOLD = 8
DEADLINE_THRESHOLD = 5
COMMUTE_THRESHOLD_HOURS = 3.0


def calculate_schedule_metrics(
    meeting_count: int,
    deadline_count: int,
    commute_hours: float,
) -> ScheduleSection:
    meeting_score = clamp_percentage((meeting_count / MEETING_THRESHOLD) * 100)
    deadline_score = clamp_percentage((deadline_count / DEADLINE_THRESHOLD) * 100)
    commute_score = clamp_percentage((commute_hours / COMMUTE_THRESHOLD_HOURS) * 100)

    schedule_density = clamp_percentage(
        (meeting_score * 0.35) + (deadline_score * 0.4) + (commute_score * 0.25)
    )

    if schedule_density <= 30:
        explanation = (
            "Your schedule looks relatively open, with fewer obligations competing for attention."
        )
    elif schedule_density <= 65:
        explanation = (
            "Your schedule has a moderate amount of meetings, deadlines, or commute load."
        )
    else:
        explanation = (
            "Your schedule looks dense, which can leave less room for recovery and focus."
        )

    return ScheduleSection(
        meeting_count=meeting_count,
        deadline_count=deadline_count,
        commute_hours=round(commute_hours, 1),
        schedule_density_percentage=round_percentage(schedule_density),
        explanation=explanation,
    )
