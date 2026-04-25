from burnout_backend.app.models.metrics import WorkloadSection
from burnout_backend.app.utils.percentage_utils import clamp_percentage, round_percentage


HIGH_WORKLOAD_THRESHOLD_HOURS = 10.0


def calculate_workload_metrics(
    work_hours: float,
    class_hours: float,
    assignment_hours: float,
) -> WorkloadSection:
    total_productive_hours = work_hours + class_hours + assignment_hours
    workload_pressure = clamp_percentage(
        (total_productive_hours / HIGH_WORKLOAD_THRESHOLD_HOURS) * 100
    )

    if total_productive_hours <= 7:
        explanation = (
            "Your productive hours look manageable for now and do not show heavy workload pressure."
        )
    elif total_productive_hours <= HIGH_WORKLOAD_THRESHOLD_HOURS:
        explanation = (
            "Your workload is building up and may start creating pressure if this pattern continues."
        )
    else:
        explanation = (
            "Your total productive hours are above the high-workload threshold, which is a strong risk driver."
        )

    return WorkloadSection(
        work_hours=round(work_hours, 1),
        class_hours=round(class_hours, 1),
        assignment_hours=round(assignment_hours, 1),
        total_productive_hours=round(total_productive_hours, 1),
        workload_pressure_percentage=round_percentage(workload_pressure),
        explanation=explanation,
    )
