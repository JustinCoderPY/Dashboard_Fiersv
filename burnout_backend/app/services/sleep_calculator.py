from burnout_backend.app.models.metrics import SleepSection
from burnout_backend.app.utils.percentage_utils import clamp_percentage, round_percentage


DEFAULT_RECOMMENDED_SLEEP_HOURS = 8.0


def calculate_sleep_metrics(average_sleep_hours: float) -> SleepSection:
    sleep_balance = clamp_percentage(
        (average_sleep_hours / DEFAULT_RECOMMENDED_SLEEP_HOURS) * 100
    )
    sleep_risk = clamp_percentage(100 - sleep_balance)

    if average_sleep_hours >= DEFAULT_RECOMMENDED_SLEEP_HOURS:
        explanation = (
            "Your average sleep is meeting the current target, which lowers burnout risk."
        )
    elif average_sleep_hours >= 6.5:
        explanation = (
            "Your sleep is a little below the target, so it may be adding some warning signs."
        )
    else:
        explanation = (
            "Your average sleep is well below the target, which is raising your burnout risk."
        )

    return SleepSection(
        average_sleep_hours=round(average_sleep_hours, 1),
        recommended_sleep_hours=DEFAULT_RECOMMENDED_SLEEP_HOURS,
        sleep_balance_percentage=round_percentage(sleep_balance),
        sleep_risk_percentage=round_percentage(sleep_risk),
        explanation=explanation,
    )
