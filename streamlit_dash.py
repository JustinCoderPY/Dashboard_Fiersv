import pandas as pd
import streamlit as st

from burnout_backend.app.services.dashboard_service import build_dashboard


def parse_list_input(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


st.set_page_config(
    page_title="Burnout Prevention Dashboard",
    page_icon="🔥",
    layout="wide",
)

st.title("Burnout Prevention Dashboard")
st.write(
    "Use the sidebar to enter daily habits and review a backend-generated burnout risk dashboard."
)

st.sidebar.header("Daily Inputs")

average_sleep_hours = st.sidebar.slider("Average sleep hours", 0.0, 12.0, 7.0, 0.5)
work_hours = st.sidebar.slider("Work hours", 0.0, 16.0, 8.0, 0.5)
class_hours = st.sidebar.slider("Class hours", 0.0, 12.0, 2.0, 0.5)
assignment_hours = st.sidebar.slider("Assignment hours", 0.0, 12.0, 2.0, 0.5)
break_minutes = st.sidebar.slider("Break minutes", 0, 240, 45, 5)
hobby_minutes = st.sidebar.slider("Hobby minutes", 0, 240, 30, 5)
commute_hours = st.sidebar.slider("Commute hours", 0.0, 4.0, 1.0, 0.5)
meeting_count = st.sidebar.number_input("Meeting count", min_value=0, max_value=20, value=4)
deadline_count = st.sidebar.number_input("Deadline count", min_value=0, max_value=20, value=2)
hobbies_text = st.sidebar.text_input("Hobbies (comma-separated)", value="drawing, basketball")
stress_relievers_text = st.sidebar.text_input(
    "Stress relievers (comma-separated)",
    value="deep breathing, listening to music",
)
medication_reminders_text = st.sidebar.text_input(
    "Medication reminders (comma-separated)",
    value="9:00 AM, 8:00 PM",
)
medication_info = st.sidebar.text_input(
    "Medication info",
    value="General reminders only. This field is not used for diagnosis.",
)

user_data = {
    "average_sleep_hours": average_sleep_hours,
    "work_hours": work_hours,
    "class_hours": class_hours,
    "assignment_hours": assignment_hours,
    "break_minutes": break_minutes,
    "hobby_minutes": hobby_minutes,
    "commute_hours": commute_hours,
    "meeting_count": int(meeting_count),
    "deadline_count": int(deadline_count),
    "hobbies": parse_list_input(hobbies_text),
    "stress_relievers": parse_list_input(stress_relievers_text),
    "medication_reminders": parse_list_input(medication_reminders_text),
    "medication_info": medication_info,
}

dashboard = build_dashboard(user_data)

st.subheader("Burnout Risk Overview")

summary_col1, summary_col2, summary_col3 = st.columns(3)
summary_col1.metric("Burnout Risk Percentage", f"{dashboard.burnout_risk.percentage}%")
summary_col2.metric("Risk Level", dashboard.burnout_risk.risk_level)
summary_col3.metric("Sleep Balance", f"{dashboard.sleep.sleep_balance_percentage}%")

st.progress(dashboard.burnout_risk.percentage / 100)
st.write(dashboard.burnout_risk.explanation)

detail_col1, detail_col2, detail_col3 = st.columns(3)
detail_col1.metric("Workload Pressure", f"{dashboard.workload.workload_pressure_percentage}%")
detail_col2.metric("Recovery Balance", f"{dashboard.recovery.recovery_balance_percentage}%")
detail_col3.metric("Schedule Density", f"{dashboard.schedule.schedule_density_percentage}%")

chart_data = pd.DataFrame(
    {
        "Category": [
            "Sleep Risk",
            "Workload Pressure",
            "Recovery Risk",
            "Schedule Density",
        ],
        "Percentage": [
            dashboard.sleep.sleep_risk_percentage,
            dashboard.workload.workload_pressure_percentage,
            dashboard.recovery.recovery_risk_percentage,
            dashboard.schedule.schedule_density_percentage,
        ],
    }
).set_index("Category")

st.subheader("Risk Drivers")
st.bar_chart(chart_data)

with st.expander("Sleep Breakdown", expanded=True):
    st.write(f"Average Sleep Hours: {dashboard.sleep.average_sleep_hours}")
    st.write(f"Recommended Sleep Hours: {dashboard.sleep.recommended_sleep_hours}")
    st.write(f"Sleep Balance: {dashboard.sleep.sleep_balance_percentage}%")
    st.write(f"Sleep Risk: {dashboard.sleep.sleep_risk_percentage}%")
    st.write(dashboard.sleep.explanation)

with st.expander("Workload Breakdown"):
    st.write(f"Work Hours: {dashboard.workload.work_hours}")
    st.write(f"Class Hours: {dashboard.workload.class_hours}")
    st.write(f"Assignment Hours: {dashboard.workload.assignment_hours}")
    st.write(f"Total Productive Hours: {dashboard.workload.total_productive_hours}")
    st.write(f"Workload Pressure: {dashboard.workload.workload_pressure_percentage}%")
    st.write(dashboard.workload.explanation)

with st.expander("Recovery Breakdown"):
    st.write(f"Break Minutes: {dashboard.recovery.break_minutes}")
    st.write(f"Hobby Minutes: {dashboard.recovery.hobby_minutes}")
    st.write(f"Total Recovery Minutes: {dashboard.recovery.total_recovery_minutes}")
    st.write(
        f"Recommended Recovery Minutes: {dashboard.recovery.recommended_recovery_minutes}"
    )
    st.write(f"Recovery Balance: {dashboard.recovery.recovery_balance_percentage}%")
    st.write(f"Recovery Risk: {dashboard.recovery.recovery_risk_percentage}%")
    st.write(dashboard.recovery.explanation)

with st.expander("Schedule Breakdown"):
    st.write(f"Meeting Count: {dashboard.schedule.meeting_count}")
    st.write(f"Deadline Count: {dashboard.schedule.deadline_count}")
    st.write(f"Commute Hours: {dashboard.schedule.commute_hours}")
    st.write(f"Schedule Density: {dashboard.schedule.schedule_density_percentage}%")
    st.write(dashboard.schedule.explanation)

st.subheader("Recommended Actions")
for recommendation in dashboard.recommendations:
    st.write(f"- {recommendation}")
