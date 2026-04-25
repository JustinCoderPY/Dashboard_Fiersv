from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from burnout_backend.app.services.dashboard_service import build_dashboard


st.set_page_config(
    page_title="Burnout Prevention Dashboard",
    layout="wide",
)


DATA_DIR = Path("data")
ENTRIES_FILE = DATA_DIR / "user_entries.csv"
DRAFT_FILE = DATA_DIR / "user_draft.json"
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
QUESTION_STEPS = [
    {
        "key": "average_sleep_hours",
        "title": "How many hours did you sleep last night?",
        "helper": "Rest is one of the strongest signals in your daily check-in.",
        "type": "number",
        "min_value": 0.0,
        "max_value": 24.0,
        "step": 0.5,
    },
    {
        "key": "work_hours",
        "title": "How many hours did you spend working today?",
        "helper": "Include focused work, shifts, or professional tasks.",
        "type": "number",
        "min_value": 0.0,
        "max_value": 24.0,
        "step": 0.5,
    },
    {
        "key": "class_hours",
        "title": "How many hours did you spend in class?",
        "helper": "Add lectures, labs, or other scheduled learning time.",
        "type": "number",
        "min_value": 0.0,
        "max_value": 24.0,
        "step": 0.5,
    },
    {
        "key": "assignment_hours",
        "title": "How many hours did you spend on assignments?",
        "helper": "Count homework, studying, projects, and preparation.",
        "type": "number",
        "min_value": 0.0,
        "max_value": 24.0,
        "step": 0.5,
    },
    {
        "key": "commute_hours",
        "title": "How long was your commute today?",
        "helper": "Travel time can quietly add to overload across the week.",
        "type": "number",
        "min_value": 0.0,
        "max_value": 24.0,
        "step": 0.5,
    },
    {
        "key": "break_minutes",
        "title": "How many minutes did you spend taking breaks?",
        "helper": "Short pauses still matter. Add up the total you actually took.",
        "type": "number",
        "min_value": 0,
        "max_value": 1440,
        "step": 5,
    },
    {
        "key": "hobby_minutes",
        "title": "How many minutes did you spend on hobbies or personal time?",
        "helper": "This includes recovery time that feels enjoyable or grounding.",
        "type": "number",
        "min_value": 0,
        "max_value": 1440,
        "step": 5,
    },
    {
        "key": "meeting_count",
        "title": "How many meetings did you have today?",
        "helper": "Even short meetings can make a day feel more crowded.",
        "type": "number",
        "min_value": 0,
        "max_value": 100,
        "step": 1,
    },
    {
        "key": "deadline_count",
        "title": "How many deadlines are currently on your mind?",
        "helper": "Use the number that feels true, even if some are still a few days away.",
        "type": "number",
        "min_value": 0,
        "max_value": 100,
        "step": 1,
    },
    {
        "key": "recharge_step",
        "title": "What hobbies or activities helped you recharge today?",
        "helper": "This step is a little more personal. It helps the dashboard sound more supportive.",
        "type": "text_group",
    },
]


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(78, 169, 146, 0.12), transparent 26%),
                radial-gradient(circle at top right, rgba(230, 244, 239, 0.95), transparent 22%),
                linear-gradient(180deg, #f6f8f7 0%, #edf3f1 100%);
            color: #172126;
        }

        .block-container {
            max-width: 1120px;
            padding-top: 1.5rem;
            padding-bottom: 3.5rem;
        }

        .hero-shell,
        .survey-card,
        .panel-card,
        .metric-card,
        .recommendation-card,
        .transition-card {
            background: rgba(255, 255, 255, 0.92);
            border: 1px solid rgba(48, 88, 79, 0.10);
            border-radius: 28px;
            box-shadow: 0 28px 70px rgba(36, 59, 53, 0.10);
        }

        .hero-shell {
            padding: 1.8rem 1.8rem 1.6rem 1.8rem;
            margin-bottom: 1.1rem;
        }

        .hero-kicker {
            display: inline-block;
            padding: 0.42rem 0.78rem;
            border-radius: 999px;
            background: rgba(53, 125, 105, 0.10);
            color: #335e54;
            font-size: 0.8rem;
            font-weight: 600;
            margin-bottom: 0.9rem;
        }

        .hero-title {
            font-size: clamp(2rem, 4vw, 3.4rem);
            line-height: 1.02;
            font-weight: 700;
            color: #182126;
            margin: 0 0 0.7rem 0;
            text-wrap: balance;
        }

        .hero-copy {
            max-width: 42rem;
            margin: 0;
            color: #52636a;
            line-height: 1.7;
            font-size: 1rem;
        }

        .survey-wrap {
            max-width: 720px;
            margin: 0 auto 1.25rem auto;
        }

        .survey-meta {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
            margin-bottom: 0.65rem;
            color: #5b6d72;
            font-size: 0.9rem;
            font-weight: 600;
        }

        .survey-card,
        .transition-card {
            padding: 1.55rem;
        }

        .survey-title {
            font-size: clamp(1.5rem, 4vw, 2.15rem);
            line-height: 1.08;
            font-weight: 700;
            color: #162126;
            margin: 0 0 0.65rem 0;
            text-wrap: balance;
        }

        .survey-helper {
            color: #5e6e74;
            font-size: 0.98rem;
            line-height: 1.65;
            margin-bottom: 1.35rem;
        }

        .survey-note {
            color: #67797e;
            font-size: 0.88rem;
            line-height: 1.55;
            margin-top: 1rem;
        }

        .transition-card {
            max-width: 700px;
            margin: 0 auto 1rem auto;
            text-align: center;
        }

        .transition-title {
            font-size: clamp(1.8rem, 4vw, 2.5rem);
            color: #172126;
            font-weight: 700;
            line-height: 1.05;
            margin: 0 0 0.8rem 0;
        }

        .transition-copy {
            color: #5a6b71;
            line-height: 1.7;
            max-width: 34rem;
            margin: 0 auto 1rem auto;
        }

        .panel-card {
            padding: 1.2rem 1.25rem;
            margin-bottom: 1rem;
        }

        .risk-card {
            padding: 1.5rem;
            min-height: 100%;
            background: linear-gradient(150deg, rgba(255,255,255,0.97), rgba(242,247,245,0.95));
        }

        .risk-card .eyebrow,
        .metric-card .eyebrow {
            color: #607175;
            font-size: 0.82rem;
            font-weight: 600;
            margin-bottom: 0.5rem;
        }

        .risk-card .value {
            font-size: clamp(2.5rem, 6vw, 4rem);
            font-weight: 700;
            color: #162126;
            line-height: 1;
            margin: 0.15rem 0 0.45rem 0;
            font-variant-numeric: tabular-nums;
        }

        .risk-card .level {
            display: inline-block;
            padding: 0.45rem 0.78rem;
            border-radius: 999px;
            background: rgba(53, 125, 105, 0.10);
            color: #2f5f53;
            font-size: 0.9rem;
            font-weight: 600;
            margin-bottom: 0.95rem;
        }

        .risk-card .message,
        .metric-card .subtext,
        .section-copy {
            color: #57686f;
            line-height: 1.65;
            font-size: 0.95rem;
            margin: 0;
        }

        .metric-card {
            padding: 1rem 1.05rem;
            min-height: 132px;
            margin-bottom: 0.8rem;
        }

        .metric-card .metric-value {
            font-size: 1.65rem;
            line-height: 1.1;
            font-weight: 700;
            color: #162126;
            margin-bottom: 0.35rem;
            font-variant-numeric: tabular-nums;
        }

        .section-title {
            font-size: 1.16rem;
            font-weight: 700;
            color: #182126;
            margin: 0 0 0.25rem 0;
        }

        .section-copy {
            margin-bottom: 1rem;
        }

        .disclaimer {
            color: #627379;
            font-size: 0.88rem;
            line-height: 1.6;
            padding-top: 0.8rem;
        }

        .recommendation-card {
            padding: 1rem 1.05rem;
            margin-bottom: 0.72rem;
        }

        .recommendation-card strong {
            display: block;
            color: #182126;
            margin-bottom: 0.25rem;
            font-size: 0.94rem;
        }

        label, .stNumberInput label, .stTextInput label, .stTextArea label {
            color: #223138 !important;
            font-weight: 600 !important;
        }

        .stNumberInput input, .stTextInput input, .stTextArea textarea {
            border-radius: 16px !important;
            border: 1px solid rgba(47, 84, 76, 0.16) !important;
            background: rgba(250, 252, 251, 0.98) !important;
            color: #172126 !important;
        }

        div[data-testid="stButton"] > button {
            border-radius: 16px !important;
            border: 1px solid rgba(39, 75, 67, 0.12) !important;
            min-height: 48px !important;
            font-weight: 600 !important;
        }

        div[data-testid="stFormSubmitButton"] > button {
            border-radius: 16px !important;
            min-height: 50px !important;
            font-weight: 600 !important;
        }

        div[data-testid="stProgressBar"] > div > div {
            background: linear-gradient(90deg, #4d9f8b 0%, #6db39c 100%);
        }

        @media (max-width: 768px) {
            .block-container {
                padding-top: 1rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .hero-shell,
            .survey-card,
            .transition-card,
            .panel-card {
                border-radius: 24px;
            }

            .hero-shell,
            .survey-card,
            .transition-card {
                padding: 1.25rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def ensure_data_files() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not ENTRIES_FILE.exists():
        pd.DataFrame(columns=ENTRY_COLUMNS).to_csv(ENTRIES_FILE, index=False)
    if not DRAFT_FILE.exists():
        DRAFT_FILE.write_text("{}", encoding="utf-8")


def load_entries() -> pd.DataFrame:
    ensure_data_files()
    entries = pd.read_csv(ENTRIES_FILE)
    if entries.empty:
        return entries

    entries["timestamp"] = pd.to_datetime(entries["timestamp"], errors="coerce")
    entries = entries.sort_values("timestamp")
    return entries


def save_entry(user_data: dict, dashboard) -> pd.DataFrame:
    ensure_data_files()

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


def load_draft() -> dict:
    ensure_data_files()
    try:
        content = DRAFT_FILE.read_text(encoding="utf-8").strip()
        return json.loads(content) if content else {}
    except json.JSONDecodeError:
        return {}


def save_draft(answers: dict, index: int) -> None:
    ensure_data_files()
    DRAFT_FILE.write_text(
        json.dumps({"current_question": index, "answers": answers}, indent=2),
        encoding="utf-8",
    )


def clear_draft() -> None:
    ensure_data_files()
    DRAFT_FILE.write_text("{}", encoding="utf-8")


def parse_list_input(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def get_default_answers() -> dict:
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
        "hobbies_text": "drawing, journaling",
        "stress_relievers_text": "deep breathing, listening to music",
        "medication_reminders_text": "",
        "medication_info": "",
    }


def initialize_state() -> pd.DataFrame:
    entries = load_entries()
    draft = load_draft()
    draft_answers = draft.get("answers", {})
    draft_index = draft.get("current_question", 0)

    if "survey_answers" not in st.session_state:
        st.session_state.survey_answers = {**get_default_answers(), **draft_answers}
    if "current_question" not in st.session_state:
        st.session_state.current_question = min(
            max(int(draft_index), 0), len(QUESTION_STEPS)
        )
    if "survey_stage" not in st.session_state:
        st.session_state.survey_stage = "questions"
    if "latest_dashboard" not in st.session_state:
        st.session_state.latest_dashboard = None
    if "latest_entries" not in st.session_state:
        st.session_state.latest_entries = entries

    return entries


def build_user_data(answers: dict) -> dict:
    return {
        "average_sleep_hours": float(answers["average_sleep_hours"]),
        "work_hours": float(answers["work_hours"]),
        "class_hours": float(answers["class_hours"]),
        "assignment_hours": float(answers["assignment_hours"]),
        "break_minutes": int(answers["break_minutes"]),
        "hobby_minutes": int(answers["hobby_minutes"]),
        "commute_hours": float(answers["commute_hours"]),
        "meeting_count": int(answers["meeting_count"]),
        "deadline_count": int(answers["deadline_count"]),
        "hobbies": parse_list_input(answers["hobbies_text"]),
        "stress_relievers": parse_list_input(answers["stress_relievers_text"]),
        "medication_reminders": parse_list_input(answers["medication_reminders_text"]),
        "medication_info": answers["medication_info"].strip(),
    }


def complete_check_in() -> None:
    user_data = build_user_data(st.session_state.survey_answers)
    dashboard = build_dashboard(user_data)
    st.session_state.latest_dashboard = dashboard
    st.session_state.latest_entries = save_entry(user_data, dashboard)
    st.session_state.survey_stage = "complete"
    clear_draft()


def reset_check_in() -> None:
    st.session_state.survey_answers = get_default_answers()
    st.session_state.current_question = 0
    st.session_state.survey_stage = "questions"
    st.session_state.latest_dashboard = None
    clear_draft()


def get_trend_message(entries: pd.DataFrame) -> str:
    if len(entries) < 2:
        return "Add another check-in to start spotting whether your burnout risk is moving up or down."

    previous = float(entries.iloc[-2]["burnout_risk_percentage"])
    current = float(entries.iloc[-1]["burnout_risk_percentage"])
    difference = round(current - previous, 2)

    if difference > 2:
        return "Your burnout risk increased compared to your last entry."
    if difference < -2:
        return "Your burnout risk decreased compared to your last entry."
    return "Your burnout risk stayed about the same compared to your last entry."


def build_donut_chart(risk_percentage: float) -> go.Figure:
    figure = go.Figure(
        data=[
            go.Pie(
                values=[risk_percentage, max(0.0, 100.0 - risk_percentage)],
                labels=["Burnout Risk", "Remaining"],
                hole=0.74,
                sort=False,
                direction="clockwise",
                marker=dict(colors=["#f28c6b", "#e7efec"]),
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
                text=(
                    f"<b>{risk_percentage:.0f}%</b><br>"
                    "<span style='font-size:12px;color:#607175;'>risk</span>"
                ),
                x=0.5,
                y=0.5,
                showarrow=False,
                font=dict(size=24, color="#172126"),
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
        color_continuous_scale=["#d8ebe3", "#8cbfae", "#ef8a62"],
    )
    figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        coloraxis_showscale=False,
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334046"),
    )
    figure.update_yaxes(range=[0, 100], gridcolor="rgba(123, 146, 140, 0.12)")
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
    figure.update_traces(line=dict(color="#4f9d88", width=3), marker=dict(size=8))
    figure.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#334046"),
    )
    figure.update_yaxes(range=[0, 100], gridcolor="rgba(123, 146, 140, 0.12)")
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
        '<div class="section-copy">A quick look at your recent entries from this local demo.</div>',
        unsafe_allow_html=True,
    )
    if entries.empty:
        st.info("No saved entries yet. Finish a check-in to start building your trend line.")
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


def render_intro() -> None:
    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-kicker">Burnout Prevention Dashboard</div>
            <div class="hero-title">A daily check-in that feels more human than a form.</div>
            <p class="hero-copy">
                Move through one gentle question at a time, then review your burnout risk,
                warning signs, and recovery patterns in a calmer dashboard. This is not a
                medical diagnosis.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_questionnaire() -> None:
    current_index = st.session_state.current_question
    total_questions = len(QUESTION_STEPS)
    step = QUESTION_STEPS[current_index]
    answers = st.session_state.survey_answers

    st.markdown('<div class="survey-wrap">', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="survey-meta">
            <span>{current_index + 1}/{total_questions}</span>
            <span>Daily check-in</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.progress((current_index + 1) / total_questions)
    st.markdown('<div class="survey-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="survey-title">{step["title"]}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="survey-helper">{step["helper"]}</div>',
        unsafe_allow_html=True,
    )

    with st.form(f"question_step_{current_index}"):
        if step["type"] == "number":
            input_value = st.number_input(
                "Your answer",
                min_value=step["min_value"],
                max_value=step["max_value"],
                step=step["step"],
                value=answers[step["key"]],
                label_visibility="collapsed",
            )
        else:
            hobbies_value = st.text_input(
                "Hobbies or recharge activities",
                value=answers["hobbies_text"],
                placeholder="walking, drawing, music",
            )
            stress_relievers_value = st.text_input(
                "Optional: quick stress relievers",
                value=answers["stress_relievers_text"],
                placeholder="deep breathing, tea, quiet time",
            )
            medication_reminders_value = st.text_input(
                "Optional: reminders you want to keep in mind",
                value=answers["medication_reminders_text"],
                placeholder="8:00 AM, 8:00 PM",
            )
            medication_info_value = st.text_input(
                "Optional: general note",
                value=answers["medication_info"],
                placeholder="General reminder only",
            )

        st.markdown(
            '<div class="survey-note">Your answers are saved as you move, so you can pick up where you left off in this local demo.</div>',
            unsafe_allow_html=True,
        )
        back_col, spacer_col, next_col = st.columns([1, 1.2, 1])
        back_clicked = back_col.form_submit_button(
            "Back",
            use_container_width=True,
            disabled=current_index == 0,
        )
        next_label = "Finish Check-in" if current_index == total_questions - 1 else "Next"
        next_clicked = next_col.form_submit_button(next_label, use_container_width=True)

    if back_clicked:
        if step["type"] == "number":
            answers[step["key"]] = input_value
        else:
            answers["hobbies_text"] = hobbies_value
            answers["stress_relievers_text"] = stress_relievers_value
            answers["medication_reminders_text"] = medication_reminders_value
            answers["medication_info"] = medication_info_value

        st.session_state.current_question = max(current_index - 1, 0)
        save_draft(answers, st.session_state.current_question)
        st.rerun()

    if next_clicked:
        if step["type"] == "number":
            answers[step["key"]] = input_value
        else:
            if not hobbies_value.strip():
                st.error("Add at least one hobby or recharge activity before continuing.")
                st.markdown("</div></div>", unsafe_allow_html=True)
                return
            answers["hobbies_text"] = hobbies_value
            answers["stress_relievers_text"] = stress_relievers_value
            answers["medication_reminders_text"] = medication_reminders_value
            answers["medication_info"] = medication_info_value

        if current_index == total_questions - 1:
            complete_check_in()
        else:
            st.session_state.current_question = current_index + 1
            save_draft(answers, st.session_state.current_question)
        st.rerun()

    st.markdown("</div></div>", unsafe_allow_html=True)


def render_completion() -> None:
    st.markdown(
        """
        <div class="transition-card">
            <div class="transition-title">Thanks for checking in. Your results are ready.</div>
            <div class="transition-copy">
                We turned your answers into a dashboard that highlights burnout risk, warning
                signs, and recovery patterns without making medical claims.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    view_col, restart_col = st.columns([1.2, 1])
    if view_col.button("View My Dashboard", use_container_width=True):
        st.session_state.survey_stage = "results"
        st.rerun()
    if restart_col.button("Start Over", use_container_width=True):
        reset_check_in()
        st.rerun()


def render_results() -> None:
    dashboard = st.session_state.latest_dashboard
    entries = st.session_state.latest_entries

    top_col, donut_col = st.columns([1.45, 1])
    with top_col:
        st.markdown(
            f"""
            <div class="panel-card risk-card">
                <div class="eyebrow">Today's Burnout Risk</div>
                <div class="value">{dashboard.burnout_risk.percentage}%</div>
                <div class="level">{dashboard.burnout_risk.risk_level}</div>
                <p class="message">{dashboard.burnout_risk.explanation}</p>
                <div class="disclaimer">
                    This is not a medical diagnosis. It is an estimate based on workload, rest,
                    recovery, and schedule patterns.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.progress(dashboard.burnout_risk.percentage / 100)

    with donut_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Snapshot</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class=\"section-copy\">A quick visual of today's estimated burnout risk.</div>",
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
            "The amount of productive load your day carried.",
        )
    with metric_row_1[2]:
        render_metric_card(
            "Recovery Balance",
            f"{dashboard.recovery.recovery_balance_percentage}%",
            "How much recovery time showed up in your day.",
        )

    metric_row_2 = st.columns(3)
    with metric_row_2[0]:
        render_metric_card(
            "Schedule Density",
            f"{dashboard.schedule.schedule_density_percentage}%",
            "How crowded the day feels across meetings, deadlines, and commute.",
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
            "A daily recovery target for this hackathon version.",
        )

    charts_left, charts_right = st.columns([1.15, 1])
    with charts_left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Risk Drivers</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">These areas are contributing most to your current burnout risk estimate.</div>',
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
            st.info("Your trend line will appear after you save your first check-in.")
        else:
            st.plotly_chart(
                history_chart,
                use_container_width=True,
                config={"displayModeBar": False},
            )
        st.markdown("</div>", unsafe_allow_html=True)

    detail_col, recommendation_col = st.columns([1.08, 0.92])
    with detail_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">Daily Breakdown</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-copy">Open each section for the detailed values returned by the backend service.</div>',
            unsafe_allow_html=True,
        )
        render_breakdown(dashboard)
        st.markdown("</div>", unsafe_allow_html=True)

    with recommendation_col:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        render_recommendations(dashboard.recommendations)
        if st.button("Start Another Check-in", use_container_width=True):
            reset_check_in()
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    render_recent_entries(entries)


inject_styles()
initialize_state()
render_intro()

if st.session_state.survey_stage == "questions":
    render_questionnaire()
elif st.session_state.survey_stage == "complete":
    render_completion()
else:
    render_results()
