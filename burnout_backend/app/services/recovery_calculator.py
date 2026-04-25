from burnout_backend.app.models.metrics import RecoverySection
from burnout_backend.app.utils.percentage_utils import clamp_percentage, round_percentage


HEALTHY_RECOVERY_TARGET_MINUTES = 120


def calculate_recovery_metrics(
    break_minutes: int,
    hobby_minutes: int,
) -> RecoverySection:
    total_recovery_minutes = break_minutes + hobby_minutes
    recovery_balance = clamp_percentage(
        (total_recovery_minutes / HEALTHY_RECOVERY_TARGET_MINUTES) * 100
    )
    recovery_risk = clamp_percentage(100 - recovery_balance)

    if total_recovery_minutes >= HEALTHY_RECOVERY_TARGET_MINUTES:
        explanation = (
            "Your recovery time is meeting the current target, which helps offset daily stress."
        )
    elif total_recovery_minutes >= 60:
        explanation = (
            "You are getting some recovery time, but it may not be enough to fully reset."
        )
    else:
        explanation = (
            "Your recovery time is low, which can make stress build up more quickly."
        )

    return RecoverySection(
        break_minutes=break_minutes,
        hobby_minutes=hobby_minutes,
        total_recovery_minutes=total_recovery_minutes,
        recommended_recovery_minutes=HEALTHY_RECOVERY_TARGET_MINUTES,
        recovery_balance_percentage=round_percentage(recovery_balance),
        recovery_risk_percentage=round_percentage(recovery_risk),
        explanation=explanation,
    )
