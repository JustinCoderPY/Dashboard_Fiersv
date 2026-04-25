from burnout_backend.app.models.metrics import (
    BurnoutRiskSummary,
    RecoverySection,
    ScheduleSection,
    SleepSection,
    WorkloadSection,
)
from burnout_backend.app.utils.percentage_utils import clamp_percentage, round_percentage


SLEEP_WEIGHT = 0.30
WORKLOAD_WEIGHT = 0.30
RECOVERY_WEIGHT = 0.25
SCHEDULE_WEIGHT = 0.15


def _get_risk_level(percentage: float) -> str:
    if percentage <= 25:
        return "Low Risk"
    if percentage <= 50:
        return "Moderate Risk"
    if percentage <= 75:
        return "High Risk"
    return "Critical Risk"


def calculate_burnout_risk(
    sleep: SleepSection,
    workload: WorkloadSection,
    recovery: RecoverySection,
    schedule: ScheduleSection,
) -> BurnoutRiskSummary:
    final_percentage = clamp_percentage(
        (sleep.sleep_risk_percentage * SLEEP_WEIGHT)
        + (workload.workload_pressure_percentage * WORKLOAD_WEIGHT)
        + (recovery.recovery_risk_percentage * RECOVERY_WEIGHT)
        + (schedule.schedule_density_percentage * SCHEDULE_WEIGHT)
    )
    risk_level = _get_risk_level(final_percentage)

    drivers = sorted(
        [
            ("sleep", sleep.sleep_risk_percentage),
            ("workload", workload.workload_pressure_percentage),
            ("recovery", recovery.recovery_risk_percentage),
            ("schedule", schedule.schedule_density_percentage),
        ],
        key=lambda item: item[1],
        reverse=True,
    )
    top_driver, top_score = drivers[0]

    if final_percentage <= 25:
        explanation = (
            "Your current habits look fairly balanced overall, with limited warning signs."
        )
    elif final_percentage <= 50:
        explanation = (
            f"Your burnout risk is moderate right now, with {top_driver} patterns adding the most pressure."
        )
    elif final_percentage <= 75:
        explanation = (
            f"Your burnout risk is elevated, and {top_driver} is one of the strongest warning signs."
        )
    else:
        explanation = (
            f"Your pattern shows strong warning signs, especially in {top_driver}, which scored {round_percentage(top_score)}%."
        )

    return BurnoutRiskSummary(
        percentage=round_percentage(final_percentage),
        risk_level=risk_level,
        explanation=explanation,
    )
