import streamlit as st

st.set_page_config(
    page_title="Burnout Prevention Dashboard",
    page_icon="🔥",
    layout="wide"
)

st.title("Burnout Prevention Dashboard")
st.write(
    "This dashboard analyzes sleep and work-hour habits to estimate burnout risk "
    "and recommend recovery time."
)

st.divider()

col1, col2 = st.columns(2)

with col1:
    sleep_hours = st.slider("Average sleep per night", 0.0, 12.0, 7.0, 0.5)

with col2:
    work_hours = st.slider("Average work hours per day", 0.0, 16.0, 8.0, 0.5)

sleep_risk = max(0, (7 - sleep_hours) / 7) * 50
work_risk = max(0, (work_hours - 8) / 8) * 50
burnout_risk = min(100, round(sleep_risk + work_risk))

if burnout_risk <= 25:
    risk_label = "Low Risk"
    explanation = "Your current sleep and work-hour pattern looks balanced."
    recovery = "A short break or normal rest should be enough."
elif burnout_risk <= 50:
    risk_label = "Mild Risk"
    explanation = "Some habits may be creating stress, but the risk is still manageable."
    recovery = "Consider taking a few hours of intentional rest."
elif burnout_risk <= 75:
    risk_label = "High Risk"
    explanation = "Your sleep and work balance is becoming unhealthy."
    recovery = "You may need 1–2 days of lighter work or recovery time."
else:
    risk_label = "Critical Risk"
    explanation = "Your pattern shows strong burnout risk indicators."
    recovery = "You may need several days of recovery and a major workload adjustment."

st.subheader("Burnout Risk Result")

metric1, metric2, metric3 = st.columns(3)

metric1.metric("Burnout Risk", f"{burnout_risk}%")
metric2.metric("Risk Level", risk_label)
metric3.metric("Recommended Sleep", "7–9 hrs")

st.progress(burnout_risk / 100)

st.write(explanation)

st.subheader("Recommended Recovery Time")
st.info(recovery)

st.subheader("Risk Percentage Guide")
st.write(
    """
    **0–25%:** Low Risk — Your habits look balanced.  
    **26–50%:** Mild Risk — Some stress patterns may be forming.  
    **51–75%:** High Risk — Your routine may be pushing you toward burnout.  
    **76–100%:** Critical Risk — Strong burnout indicators are present.
    """
)
