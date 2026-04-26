import csv
import json
from pathlib import Path

from burnout_backend.app.models.api_models import (
    CheckInHistoryEntry,
    PrototypeCheckInPayload,
)
from burnout_backend.app.models.dashboard import DashboardResponse


ROOT_DIR = Path(__file__).resolve().parents[3]
DATA_DIR = ROOT_DIR / "data"
API_CHECKINS_FILE = DATA_DIR / "api_checkins.csv"
API_CHECKIN_FIELDS = [
    "timestamp",
    "sleep_hours",
    "work_study_hours",
    "class_hours",
    "assignment_hours",
    "break_minutes",
    "hobby_minutes",
    "commute_minutes",
    "meeting_count",
    "deadline_count",
    "mood",
    "hobbies",
    "stress_relievers",
    "burnout_risk_percentage",
    "risk_level",
    "sleep_balance_percentage",
    "workload_pressure_percentage",
    "recovery_balance_percentage",
    "schedule_density_percentage",
]


def ensure_api_checkins_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not API_CHECKINS_FILE.exists():
        with API_CHECKINS_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=API_CHECKIN_FIELDS)
            writer.writeheader()


def append_api_checkin(
    payload: PrototypeCheckInPayload,
    dashboard: DashboardResponse,
) -> None:
    ensure_api_checkins_file()
    row = {
        "timestamp": dashboard.generated_at,
        "sleep_hours": payload.sleep_hours,
        "work_study_hours": payload.work_study_hours,
        "class_hours": payload.class_hours,
        "assignment_hours": payload.assignment_hours,
        "break_minutes": payload.break_minutes,
        "hobby_minutes": payload.hobby_minutes,
        "commute_minutes": payload.commute_minutes,
        "meeting_count": payload.meeting_count,
        "deadline_count": payload.deadline_count,
        "mood": payload.mood or "",
        "hobbies": json.dumps(payload.hobbies),
        "stress_relievers": json.dumps(payload.stress_relievers),
        "burnout_risk_percentage": dashboard.burnout_risk.percentage,
        "risk_level": dashboard.burnout_risk.risk_level,
        "sleep_balance_percentage": dashboard.sleep.sleep_balance_percentage,
        "workload_pressure_percentage": dashboard.workload.workload_pressure_percentage,
        "recovery_balance_percentage": dashboard.recovery.recovery_balance_percentage,
        "schedule_density_percentage": dashboard.schedule.schedule_density_percentage,
    }

    with API_CHECKINS_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=API_CHECKIN_FIELDS)
        writer.writerow(row)


def read_api_history(limit: int = 7) -> list[CheckInHistoryEntry]:
    ensure_api_checkins_file()

    with API_CHECKINS_FILE.open("r", newline="", encoding="utf-8") as file:
        rows = list(csv.DictReader(file))

    latest_rows = rows[-limit:] if limit > 0 else rows
    history_entries: list[CheckInHistoryEntry] = []
    for row in latest_rows:
        history_entries.append(
            CheckInHistoryEntry(
                timestamp=row["timestamp"],
                sleep_hours=float(row["sleep_hours"]),
                work_study_hours=float(row["work_study_hours"]),
                class_hours=float(row["class_hours"]),
                assignment_hours=float(row["assignment_hours"]),
                break_minutes=int(float(row["break_minutes"])),
                hobby_minutes=int(float(row["hobby_minutes"])),
                commute_minutes=int(float(row["commute_minutes"])),
                meeting_count=int(float(row["meeting_count"])),
                deadline_count=int(float(row["deadline_count"])),
                mood=row["mood"] or None,
                hobbies=_parse_json_list(row["hobbies"]),
                stress_relievers=_parse_json_list(row["stress_relievers"]),
                burnout_risk_percentage=float(row["burnout_risk_percentage"]),
                risk_level=row["risk_level"],
                sleep_balance_percentage=float(row["sleep_balance_percentage"]),
                workload_pressure_percentage=float(row["workload_pressure_percentage"]),
                recovery_balance_percentage=float(row["recovery_balance_percentage"]),
                schedule_density_percentage=float(row["schedule_density_percentage"]),
            )
        )

    return history_entries


def _parse_json_list(value: str) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        return parsed if isinstance(parsed, list) else []
    except json.JSONDecodeError:
        return []
