from burnout_backend.app.models.metrics import (
    RecoverySection,
    ScheduleSection,
    SleepSection,
    WorkloadSection,
)
from burnout_backend.app.models.user_input import UserInput


def generate_recommendations(
    user_input: UserInput,
    sleep: SleepSection,
    workload: WorkloadSection,
    recovery: RecoverySection,
    schedule: ScheduleSection,
) -> list[str]:
    recommendations: list[str] = []

    ranked_areas = sorted(
        [
            ("sleep", sleep.sleep_risk_percentage),
            ("workload", workload.workload_pressure_percentage),
            ("recovery", recovery.recovery_risk_percentage),
            ("schedule", schedule.schedule_density_percentage),
        ],
        key=lambda item: item[1],
        reverse=True,
    )

    for area, score in ranked_areas:
        if score < 40:
            continue

        if area == "sleep":
            recommendations.append(
                "Try improving sleep consistency by protecting a routine that gets you closer to 8 hours."
            )
        elif area == "workload":
            recommendations.append(
                "Look for non-urgent tasks, assignments, or obligations that can be moved, reduced, or grouped differently."
            )
        elif area == "recovery":
            recommendations.append(
                "Add a deliberate recovery block today, even if it starts as a short walk, quiet break, or screen-free reset."
            )
        elif area == "schedule":
            recommendations.append(
                "Space out meetings, deadlines, or commute-heavy obligations when possible to reduce schedule density."
            )

    if user_input.hobbies:
        hobby = user_input.hobbies[0]
        recommendations.append(
            f"Use {hobby} as an intentional recovery activity this week instead of waiting until you are already drained."
        )

    if user_input.stress_relievers:
        stress_reliever = user_input.stress_relievers[0]
        recommendations.append(
            f"When your day feels packed, try {stress_reliever} as a quick stress-relief option."
        )

    if not recommendations:
        recommendations.append(
            "Your current pattern looks fairly stable. Keep protecting sleep, recovery, and a manageable workload to hold that balance."
        )

    # Keep recommendations readable and avoid duplicates.
    unique_recommendations = list(dict.fromkeys(recommendations))
    return unique_recommendations[:6]
