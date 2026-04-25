from __future__ import annotations

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from burnout_backend.app.services.dashboard_service import build_dashboard


st.set_page_config(
    page_title="Burnout Prevention Dashboard",
    page_icon="🌿",
    layout="wide",
)


DATA_DIR = Path("data")
ENTRIES_FILE = DATA_DIR / "user_entries.csv"
ENTRY_COLUMNS = [
    "timestamp",
    "average_sleep_hours",
    "work_hours",
    "class_hours",
    "assignment_hours",
    "break_minutes",
    "hobby_minutes",
    "commute_hours",
    "meeting_count",
    "deadline_count",
    "burnout_risk_percentage",
    "risk_level",
    "sleep_balance_percentage",
    "workload_pressure_percentage",
    "recovery_balance_percentage",
    "schedule_density_percentage",
]


def parse_list_input(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(103, 80, 164, 0.10), transparent 28%),
                radial-gradient(circle at top right, rgba(64, 156, 255, 0.12), transparent 24%),
                linear-gradient(180deg, #f7f8fc 0%, #eef2ff 100%);
            color: #18212f;
        }

        .block-container {
            max-width: 1140px;
            padding-top: 1.5rem;
            padding-bottom: 3rem;
        }

        h1, h2, h3 {
            letter-spacing: 0;
        }

        .hero-card,
        .panel-card,
        .metric-card,
        .recommendation-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(125, 136, 196, 0.16);
            border-radius: 24px;
            box-shadow: 0 24px 60px rgba(98, 108, 148, 0.12);
            backdrop-filter: blur(14px);
        }

        .hero-card {
            padding: 2rem 2rem 1.75rem 2rem;
            margin-bottom: 1.2rem;
        }

        .hero-kicker {
            display: inline-block;
            font-size: 0.83rem;
            font-weight: 600;
            color: #58627a;
            background: rgba(92, 103, 160, 0.10);
            border-radius: 999px;
            padding: 0.4rem 0.8rem;
            margin-bottom: 1rem;
        }

        .hero-title {
            font-size: clamp(2rem, 4vw, 3.3rem);
            line-height: 1.02;
            font-weight: 700;
            color: #192335;
            margin: 0 0 0.8rem 0;
            text-wrap: balance;
        }

        .hero-text {
            max-width: 42rem;
            font-size: 1rem;
            line-height: 1.65;
            color: #4d5870;
            margin: 0;
        }

        .panel-card {
            padding: 1.2rem 1.25rem;
            margin-bottom: 1rem;
        }

        .risk-card {
            padding: 1.5rem;
            min-height: 100%;
            background: linear-gradient(145deg, rgba(255,255,255,0.96), rgba(243,246,255,0.94));
        }

        .risk-card .eyebrow,
        .metric-card .eyebrow {
            color: #65728b;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .risk-card .value {
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 700;
            line-height: 1;
            color: #151d2d;
            margin: 0.2rem 0 0.4rem 0;
            font-variant-numeric: tabular-nums;
        }

        .risk-card .level {
            display: inline-block;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(83, 103, 220, 0.10);
            color: #3144a5;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .risk-card .message,
        .metric-card .subtext {
            color: #556177;
            line-height: 1.6;
            font-size: 0.95rem;
            margin: 0;
        }

        .metric-card {
            padding: 1rem 1.1rem;
            min-height: 132px;
            margin-bottom: 0.8rem;
        }

        .metric-card .metric-value {
            font-size: 1.7rem;
            line-height: 1.1;
            font-weight: 700;
            color: #1b2435;
            margin-bottom: 0.35rem;
            font-variant-numeric: tabular-nums;
        }

        .section-title {
            font-size: 1.2rem;
            font-weight: 700;
            color: #1d2637;
            margin: 0 0 0.25rem 0;
        }

        .section-copy {
            color: #5b667e;
            font-size: 0.95rem;
            line-height: 1.6;
            margin-bottom: 1rem;
        }

        .disclaimer {
            color: #5e6b83;
            font-size: 0.88rem;
            line-height: 1.6;
            padding-top: 0.75rem;
        }

        .recommendation-card {
            padding: 1rem 1.1rem;
            margin-bottom: 0.75rem;
        }

        .recommendation-card strong {
            display: block;
            color: #1b2435;
            margin-bottom: 0.25rem;
            font-size: 0.95rem;
        }

        div[data-testid="stMetric"] {
            background: transparent;
            border: 0;
            padding: 0;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_entries_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ENTRIES_FILE.exists():
        pd.DataFrame(columns=ENTRY_COLUMNS).to_csv(ENTRIES_FILE, index=False)


def load_entries() -> pd.DataFrame:
    ensure_entries_file()
    entries = pd.read_csv(ENTRIES_FILE)
    if entries.empty:
        return entries

    entries["timestamp"] = pd.to_datetime(entries["timestamp"], errors="coerce")
    entries = entries.sort_values("timestamp")
    return entries


def save_entry(user_data: dict, dashboard) -> pd.DataFrame:
    ensure_entries_file()

    entry = {
        "timestamp": dashboard.generated_at,
        "average_sleep_hours": user_data["average_sleep_hours"],
        "work_hours": user_data["work_hours"],
        "class_hours": user_data["class_hours"],
        "assignment_hours": user_data["assignment_hours"],
        "break_minutes": user_data["break_minutes"],
        "hobby_minutes": user_data["hobby_minutes"],
        "commute_hours": user_data["commute_hours"],
        "meeting_count": user_data["meeting_count"],
        "deadline_count": user_data["deadline_count"],
        "burnout_risk_percentage": dashboard.burnout_risk.percentage,
        "risk_level": dashboard.burnout_risk.risk_level,
        "sleep_balance_percentage": dashboard.sleep.sleep_balance_percentage,
        "workload_pressure_percentage": dashboard.workload.workload_pressure_percentage,
        "recovery_balance_percentage": dashboard.recovery.recovery_balance_percentage,
        "schedule_density_percentage": dashboard.schedule.schedule_density_percentage,
    }

    entries = load_entries()
    updated_entries = pd.concat([entries, pd.DataFrame([entry])], ignore_index=True)
    updated_entries.to_csv(ENTRIES_FILE, index=False)
    return load_entries()


def get_trend_message(entries: pd.DataFrame) -> str:
    if len(entries) < 2:
        return "Add another entry to start tracking whether your burnout risk is moving up or down."

    previous = float(entries.iloc[-2]["burnout_risk_percentage"])
    current = float(entries.iloc[-1]["burnout_risk_percentage"])
    difference = round(current - previous, 2)

    if difference > 2:
        return "Your burnout risk increased compared to your last entry."
    if difference < -2:
        return "Your burnout risk decreased compared to your last entry."
    return "Your burnout risk stayed about the same compared to your last entry."


def build_donut_chart(risk_percentage: float) -> go.Figure:
    remaining = max(0.0, 100.0 - risk_percentage)
    figure = go.Figure(
        data=[
            go.Pie(
                values=[risk_percentage, remaining],
                labels=["Burnout Risk", "Remaining"],
                hole=0.72,
                sort=False,
                direction="clockwise",
                marker=dict(colors=["#6b6ef9", "#e9ecf8"]),
                textinfo="none",
                hovertemplate="%{label}: %{value:.1f}%<extra></extra>",
            )
        ]
    )
    figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[
            dict(
                text=f"<b>{risk_percentage:.0f}%</b><br><span style='font-size:12px;color:#5f6b84;'>risk</span>",
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=24, color="#1b2435"),
            )
        ],
    )
    return figure


def build_risk_driver_chart(dashboard) -> go.Figure:
    driver_data = pd.DataFrame(
        {
            "Driver": [
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
    )
    figure = px.bar(
        driver_data,
        x="Driver",
        y="Percentage",
        color="Percentage",
        color_continuous_scale=["#c7d2fe", "#8b5cf6", "#ef4444"],
    )
    figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    figure.update_yaxes(range=[0, 100], gridcolor="rgba(148, 163, 184, 0.15)")
    return figure


def build_history_chart(entries: pd.DataFrame) -> go.Figure | None:
    if entries.empty:
        return None

    history = entries.copy()
    history["entry_label"] = history["timestamp"].dt.strftime("%b %d, %I:%M %p")
    figure = px.line(
        history,
        x="entry_label",
        y="burnout_risk_percentage",
        markers=True,
    )
    figure.update_traces(line=dict(color="#5b6dfb", width=3), marker=dict(size=8))
    figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334155"),
    )
    figure.update_yaxes(range=[0, 100], gridcolor="rgba(148, 163, 184, 0.15)")
    return figure


def render_metric_card(label: str, value: str, subtext: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="eyebrow">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="subtext">{subtext}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_recommendations(recommendations: list[str]) -> None:
    st.markdown('<div class="section-title">Recommended Actions</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">Suggestions are based on the strongest warning signs in your current routine.</div>',
        unsafe_allow_html=True,
    )
    for index, recommendation in enumerate(recommendations, start=1):
        st.markdown(
            f"""
            <div class="recommendation-card">
                <strong>Action {index}</strong>
                <div>{recommendation}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_breakdown(dashboard) -> None:
    with st.expander("Sleep Details", expanded=True):
        st.write(f"Average Sleep Hours: {dashboard.sleep.average_sleep_hours}")
        st.write(f"Recommended Sleep Hours: {dashboard.sleep.recommended_sleep_hours}")
        st.write(f"Sleep Balance: {dashboard.sleep.sleep_balance_percentage}%")
        st.write(f"Sleep Risk: {dashboard.sleep.sleep_risk_percentage}%")
        st.write(dashboard.sleep.explanation)

    with st.expander("Workload Details"):
        st.write(f"Work Hours: {dashboard.workload.work_hours}")
        st.write(f"Class Hours: {dashboard.workload.class_hours}")
        st.write(f"Assignment Hours: {dashboard.workload.assignment_hours}")
        st.write(f"Total Productive Hours: {dashboard.workload.total_productive_hours}")
        st.write(f"Workload Pressure: {dashboard.workload.workload_pressure_percentage}%")
        st.write(dashboard.workload.explanation)

    with st.expander("Recovery Details"):
        st.write(f"Break Minutes: {dashboard.recovery.break_minutes}")
        st.write(f"Hobby Minutes: {dashboard.recovery.hobby_minutes}")
        st.write(f"Total Recovery Minutes: {dashboard.recovery.total_recovery_minutes}")
        st.write(
            f"Recommended Recovery Minutes: {dashboard.recovery.recommended_recovery_minutes}"
        )
        st.write(f"Recovery Balance: {dashboard.recovery.recovery_balance_percentage}%")
        st.write(f"Recovery Risk: {dashboard.recovery.recovery_risk_percentage}%")
        st.write(dashboard.recovery.explanation)

    with st.expander("Schedule Details"):
        st.write(f"Meeting Count: {dashboard.schedule.meeting_count}")
        st.write(f"Deadline Count: {dashboard.schedule.deadline_count}")
        st.write(f"Commute Hours: {dashboard.schedule.commute_hours}")
        st.write(f"Schedule Density: {dashboard.schedule.schedule_density_percentage}%")
        st.write(dashboard.schedule.explanation)


def render_recent_entries(entries: pd.DataFrame) -> None:
    st.markdown('<div class="section-title">Recent Check-ins</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-copy">A quick log of your recent entries for hackathon demo purposes.</div>',
        unsafe_allow_html=True,
    )
    if entries.empty:
        st.info("No saved entries yet. Submit your first day to start building a trend line.")
        return

    recent_entries = entries.copy().tail(5).sort_values("timestamp", ascending=False)
    recent_entries["timestamp"] = recent_entries["timestamp"].dt.strftime("%b %d, %I:%M %p")
    st.dataframe(
        recent_entries[
            [
                "timestamp",
                "burnout_risk_percentage",
                "risk_level",
                "sleep_balance_percentage",
                "workload_pressure_percentage",
                "recovery_balance_percentage",
                "schedule_density_percentage",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


def get_default_user_data() -> dict:
    return {
        "average_sleep_hours": 7.0,
        "work_hours": 8.0,
        "class_hours": 2.0,
        "assignment_hours": 2.0,
        "break_minutes": 45,
        "hobby_minutes": 30,
        "commute_hours": 1.0,
        "meeting_count": 4,
        "deadline_count": 2,
        "hobbies": ["drawing", "basketball"],
        "stress_relievers": ["deep breathing", "listening to music"],
        "medication_reminders": ["9:00 AM", "8:00 PM"],
        "medication_info": "General reminders only. This field is not used for diagnosis.",
    }


inject_styles()
entries = load_entries()

if "latest_dashboard" not in st.session_state:
    st.session_state.latest_dashboard = None
if "latest_entries" not in st.session_state:
    st.session_state.latest_entries = entries
if "latest_user_data" not in st.session_state:
    st.session_state.latest_user_data = get_default_user_data()


st.markdown(
    """
    <div class="hero-card">
        <div class="hero-kicker">Burnout Prevention Dashboard</div>
        <div class="hero-title">A calmer way to spot warning signs in your daily workload.</div>
        <p class="hero-text">
            This dashboard estimates burnout risk from sleep, workload, recovery, and schedule
            patterns. It is meant to help you notice overload earlier, not provide a medical diagnosis.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander("Enter Daily Data", expanded=st.session_state.latest_dashboard is None):
    st.markdown(
        '<div class="section-copy">Type in your day instead of dragging controls. Your entry is saved locally for this hackathon demo.</div>',
        unsafe_allow_html=True,
    )

    defaults = st.session_state.latest_user_data
    with st.form("daily_dashboard_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        with col1:
            average_sleep_hours = st.number_input(
                "Average sleep hours",
                min_value=0.0,
                max_value=24.0,
                step=0.5,
                value=float(defaults["average_sleep_hours"]),
            )
            work_hours = st.number_input(
                "Work hours",
                min_value=0.0,
                max_value=24.0,
                step=0.5,
                value=float(defaults["work_hours"]),
            )
            class_hours = st.number_input(
                "Class hours",
                min_value=0.0,
                max_value=24.0,
                step=0.5,
                value=float(defaults["class_hours"]),
            )
            assignment_hours = st.number_input(
                "Assignment hours",
                min_value=0.0,
                max_value=24.0,
                step=0.5,
                value=float(defaults["assignment_hours"]),
            )
            commute_hours = st.number_input(
                "Commute hours",
                min_value=0.0,
                max_value=24.0,
                step=0.5,
                value=float(defaults["commute_hours"]),
            )
        with col2:
            break_minutes = st.number_input(
                "Break minutes",
                min_value=0,
                max_value=1440,
                step=5,
                value=int(defaults["break_minutes"]),
            )
            hobby_minutes = st.number_input(
                "Hobby minutes",
                min_value=0,
                max_value=1440,
                step=5,
                value=int(defaults["hobby_minutes"]),
            )
            meeting_count = st.number_input(
                "Meeting count",
                min_value=0,
                max_value=100,
                step=1,
                value=int(defaults["meeting_count"]),
            )
            deadline_count = st.number_input(
                "Deadline count",
                min_value=0,
                max_value=100,
                step=1,
                value=int(defaults["deadline_count"]),
            )

        hobbies_text = st.text_input(
            "Hobbies (comma-separated)",
            value=", ".join(defaults["hobbies"]),
        )
        stress_relievers_text = st.text_input(
            "Stress relievers (comma-separated)",
            value=", ".join(defaults["stress_relievers"]),
        )
        medication_reminders_text = st.text_input(
            "Medication reminders (comma-separated)",
            value=", ".join(defaults["medication_reminders"]),
        )
        medication_info = st.text_input(
            "Medication info",
            value=defaults["medication_info"],
        )

        # Future Firebase hook:
        # This form payload can later be routed through Firebase Auth and Firestore
        # so each user has personal history instead of shared local CSV storage.
        submitted = st.form_submit_button("Analyze My Day", use_container_width=True)

    if submitted:
        user_data = {
            "average_sleep_hours": average_sleep_hours,
            "work_hours": work_hours,
            "class_hours": class_hours,
            "assignment_hours": assignment_hours,
            "break_minutes": int(break_minutes),
            "hobby_minutes": int(hobby_minutes),
            "commute_hours": commute_hours,
            "meeting_count": int(meeting_count),
            "deadline_count": int(deadline_count),
            "hobbies": parse_list_input(hobbies_text),
            "stress_relievers": parse_list_input(stress_relievers_text),
            "medication_reminders": parse_list_input(medication_reminders_text),
            "medication_info": medication_info,
        }

        dashboard = build_dashboard(user_data)
        st.session_state.latest_dashboard = dashboard
        st.session_state.latest_user_data = user_data
        st.session_state.latest_entries = save_entry(user_data, dashboard)
        st.success("Your day was analyzed and saved locally for trend tracking.")


dashboard = st.session_state.latest_dashboard
entries = st.session_state.latest_entries

if dashboard is None:
    st.markdown(
        """
        <div class="panel-card">
            <div class="section-title">Ready for your first check-in</div>
            <div class="section-copy">
                Enter your daily data to generate your dashboard. Once you submit, the app will
                show your burnout risk, major warning signs, charts, and a saved history line.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not entries.empty:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Progress Over Time</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-copy">{get_trend_message(entries)}</div>',
            unsafe_allow_html=True,
        )
        history_chart = build_history_chart(entries)
        if history_chart is not None:
            st.plotly_chart(
                history_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )
        st.markdown("</div>", unsafe_allow_html=True)
else:
    top_col, donut_col = st.columns([1.5, 1])
    with top_col:
        st.markdown(
            f"""
            <div class="panel-card risk-card">
                <div class="eyebrow">Today's Burnout Risk</div>
                <div class="value">{dashboard.burnout_risk.percentage}%</div>
                <div class="level">{dashboard.burnout_risk.risk_level}</div>
                <p class="message">{dashboard.burnout_risk.explanation}</p>
                <div class="disclaimer">This is not a medical diagnosis. It is an estimate based on habit patterns and warning signs.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(dashboard.burnout_risk.percentage / 100)

    with donut_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Snapshot</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">A quick visual of today’s estimated burnout risk.</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_donut_chart(dashboard.burnout_risk.percentage),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown("</div>", unsafe_allow_html=True)

    metric_row_1 = st.columns(3)
    with metric_row_1[0]:
        render_metric_card(
            "Sleep Balance",
            f"{dashboard.sleep.sleep_balance_percentage}%",
            "How close your sleep is to the current target.",
        )
    with metric_row_1[1]:
        render_metric_card(
            "Workload Pressure",
            f"{dashboard.workload.workload_pressure_percentage}%",
            "Daily productive load compared with a healthier range.",
        )
    with metric_row_1[2]:
        render_metric_card(
            "Recovery Balance",
            f"{dashboard.recovery.recovery_balance_percentage}%",
            "Breaks and hobbies that help you reset.",
        )

    metric_row_2 = st.columns(3)
    with metric_row_2[0]:
        render_metric_card(
            "Schedule Density",
            f"{dashboard.schedule.schedule_density_percentage}%",
            "Meetings, deadlines, and commute pressure in the same day.",
        )
    with metric_row_2[1]:
        render_metric_card(
            "Risk Level",
            dashboard.burnout_risk.risk_level,
            "A simple label for the current warning-sign range.",
        )
    with metric_row_2[2]:
        render_metric_card(
            "Recommended Recovery",
            f"{dashboard.recovery.recommended_recovery_minutes} min",
            "A healthy daily recovery target for this version of the demo.",
        )

    charts_left, charts_right = st.columns([1.15, 1])
    with charts_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Drivers</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">These categories are contributing most to your current burnout risk estimate.</div>',
            unsafe_allow_html=True,
        )
        st.plotly_chart(
            build_risk_driver_chart(dashboard),
            use_container_width=True,
            config={"displayModeBar": False},
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with charts_right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Progress Over Time</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div class="section-copy">{get_trend_message(entries)}</div>',
            unsafe_allow_html=True,
        )
        history_chart = build_history_chart(entries)
        if history_chart is None:
            st.info("Your trend line will appear after you save at least one entry.")
        else:
            st.plotly_chart(
                history_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )
        st.markdown("</div>", unsafe_allow_html=True)

    detail_col, recommendation_col = st.columns([1.1, 0.9])
    with detail_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Daily Breakdown</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Open each section for the detailed numbers coming directly from the backend service.</div>',
            unsafe_allow_html=True,
        )
        render_breakdown(dashboard)
        st.markdown("</div>", unsafe_allow_html=True)

    with recommendation_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        render_recommendations(dashboard.recommendations)
        st.markdown("</div>", unsafe_allow_html=True)

render_recent_entries(entries)
