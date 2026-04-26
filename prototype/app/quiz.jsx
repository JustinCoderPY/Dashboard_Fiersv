// Guided quiz: one question per card, with progress + back/next
const { useState, useEffect, useRef } = React;

const QUESTIONS = [
  { key: "sleep", icon: "moon", title: "How many hours did you sleep last night?", helper: "Rest is the strongest signal we'll look at.", unit: "hrs", min: 0, max: 14, step: 0.5, default: 7, healthy: [7, 9] },
  { key: "work", icon: "briefcase", title: "How many hours did you work or study?", helper: "Focused work, classes, lectures — anything productive.", unit: "hrs", min: 0, max: 16, step: 0.5, default: 8, healthy: [0, 9] },
  { key: "breaks", icon: "leaf", title: "How many minutes did you spend on real breaks?", helper: "Stepping away from screens, eating without working.", unit: "min", min: 0, max: 240, step: 5, default: 30, healthy: [45, 240] },
  { key: "commute", icon: "compass", title: "How long was your commute today?", helper: "Door to door, both ways.", unit: "min", min: 0, max: 240, step: 5, default: 45, healthy: [0, 60] },
  { key: "deadlines", icon: "flag", title: "How many deadlines are on your mind?", helper: "Even ones a few days out count if they're occupying space.", unit: "", min: 0, max: 15, step: 1, default: 3, healthy: [0, 3], isCount: true },
  { key: "hobby", icon: "palette", title: "How many minutes on hobbies or personal time?", helper: "Things you do because you want to, not because you have to.", unit: "min", min: 0, max: 360, step: 5, default: 30, healthy: [30, 360] },
  { key: "mood", icon: "smile", title: "How would you describe your day overall?", helper: "Trust your gut on this one.", type: "choice", default: "okay",
    options: [
      { v: "great", label: "Pretty good", emoji: "◯" },
      { v: "okay", label: "Just okay", emoji: "◐" },
      { v: "drained", label: "Drained", emoji: "●" },
      { v: "rough", label: "Really rough", emoji: "✕" },
    ] },
  { key: "relievers", icon: "sparkle", title: "What helps you decompress?", helper: "Pick anything that genuinely works for you.", type: "multi", default: ["walking"],
    options: ["walking", "music", "tea or coffee", "journaling", "drawing", "deep breathing", "calling a friend", "stretching", "cooking", "reading"] },
];

function Icon({ name, size = 22, color = SAGE_DEEP }) {
  const s = size, c = color, sw = 1.6;
  const props = { width: s, height: s, viewBox: "0 0 24 24", fill: "none", stroke: c, strokeWidth: sw, strokeLinecap: "round", strokeLinejoin: "round" };
  switch (name) {
    case "moon": return <svg {...props}><path d="M20 14.5A8 8 0 1 1 9.5 4 a6.5 6.5 0 0 0 10.5 10.5z"/></svg>;
    case "briefcase": return <svg {...props}><rect x="3" y="7" width="18" height="13" rx="2"/><path d="M9 7V5a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v2"/><path d="M3 13h18"/></svg>;
    case "leaf": return <svg {...props}><path d="M5 19c10 0 16-6 16-16-10 0-16 6-16 16z"/><path d="M5 19l8-8"/></svg>;
    case "compass": return <svg {...props}><circle cx="12" cy="12" r="9"/><path d="M15.5 8.5l-2 5-5 2 2-5z"/></svg>;
    case "flag": return <svg {...props}><path d="M5 21V4"/><path d="M5 4h12l-2 4 2 4H5"/></svg>;
    case "palette": return <svg {...props}><path d="M12 3a9 9 0 1 0 0 18 3 3 0 0 0 0-6 3 3 0 0 1 3-3h3a3 3 0 0 0 3-3 9 9 0 0 0-9-6z"/><circle cx="7.5" cy="11" r="1"/><circle cx="10" cy="7" r="1"/><circle cx="15" cy="7" r="1"/></svg>;
    case "smile": return <svg {...props}><circle cx="12" cy="12" r="9"/><path d="M9 14s1 2 3 2 3-2 3-2"/><circle cx="9" cy="10" r="0.5" fill={c}/><circle cx="15" cy="10" r="0.5" fill={c}/></svg>;
    case "sparkle": return <svg {...props}><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8z"/></svg>;
    default: return null;
  }
}

function NumberStepper({ value, onChange, min, max, step, isCount }) {
  const dec = () => onChange(Math.max(min, +(value - step).toFixed(1)));
  const inc = () => onChange(Math.min(max, +(value + step).toFixed(1)));
  const display = isCount || step >= 1 ? Math.round(value) : value.toFixed(1).replace(/\.0$/, "");
  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "space-between",
      padding: "8px 8px",
      background: "rgba(255,255,255,0.7)",
      borderRadius: 28,
      border: `1px solid ${STROKE}`,
    }}>
      <button onClick={dec} aria-label="decrease" style={stepperBtn}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={FOREST} strokeWidth="2.4" strokeLinecap="round"><path d="M5 12h14"/></svg>
      </button>
      <div style={{
        flex: 1, textAlign: "center",
        fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
        fontSize: 54, lineHeight: 1, color: FOREST, fontWeight: 500, letterSpacing: "-0.04em",
        fontVariantNumeric: "tabular-nums",
      }}>
        {display}
      </div>
      <button onClick={inc} aria-label="increase" style={stepperBtn}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={FOREST} strokeWidth="2.4" strokeLinecap="round"><path d="M12 5v14M5 12h14"/></svg>
      </button>
    </div>
  );
}
const stepperBtn = {
  width: 56, height: 56, borderRadius: "50%",
  border: "none", background: CREAM_2, cursor: "pointer",
  display: "grid", placeItems: "center",
  flexShrink: 0,
};

function HealthyRangeBar({ value, min, max, healthy, unit, isCount }) {
  const pct = ((value - min) / (max - min)) * 100;
  const hStart = ((healthy[0] - min) / (max - min)) * 100;
  const hEnd = ((healthy[1] - min) / (max - min)) * 100;
  const inHealthy = value >= healthy[0] && value <= healthy[1];
  return (
    <div style={{ marginTop: 18 }}>
      <div style={{ position: "relative", height: 8, borderRadius: 4, background: CREAM_2, overflow: "hidden" }}>
        <div style={{
          position: "absolute", top: 0, bottom: 0,
          left: `${hStart}%`, width: `${hEnd - hStart}%`,
          background: "rgba(123,169,143,0.45)",
        }} />
        <div style={{
          position: "absolute", top: -4, bottom: -4,
          left: `calc(${Math.min(100, Math.max(0, pct))}% - 6px)`,
          width: 12, height: 16, borderRadius: 6,
          background: FOREST, boxShadow: "0 2px 6px rgba(42,61,52,0.3)",
        }} />
      </div>
      <div style={{
        marginTop: 10, fontSize: 12, color: MUTED,
        display: "flex", justifyContent: "space-between",
      }}>
        <span>{min}{unit && ` ${unit}`}</span>
        <span style={{ color: inHealthy ? SAGE_DEEP : MUTED, fontWeight: inHealthy ? 500 : 400 }}>
          {inHealthy ? "✓ in healthy range" : `healthy: ${healthy[0]}–${healthy[1]}${unit ? " " + unit : ""}`}
        </span>
        <span>{max}{unit && ` ${unit}`}</span>
      </div>
    </div>
  );
}

function ChoiceList({ options, value, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
      {options.map((o) => {
        const active = value === o.v;
        return (
          <button key={o.v} onClick={() => onChange(o.v)} style={{
            display: "flex", alignItems: "center", gap: 14,
            padding: "16px 18px",
            borderRadius: 18,
            border: `1.5px solid ${active ? SAGE_DEEP : STROKE}`,
            background: active ? "rgba(123,169,143,0.14)" : "rgba(255,255,255,0.6)",
            cursor: "pointer", textAlign: "left",
            fontFamily: "inherit", color: FOREST,
            transition: "all 0.15s",
          }}>
            <span style={{
              fontSize: 18, width: 28, height: 28, borderRadius: "50%",
              background: active ? SAGE_DEEP : CREAM_2,
              color: active ? CREAM : FOREST,
              display: "grid", placeItems: "center",
            }}>{o.emoji}</span>
            <span style={{ flex: 1, fontSize: 15, fontWeight: 500 }}>{o.label}</span>
            <span style={{
              width: 20, height: 20, borderRadius: "50%",
              border: `1.5px solid ${active ? SAGE_DEEP : "rgba(42,61,52,0.2)"}`,
              background: active ? SAGE_DEEP : "transparent",
              display: "grid", placeItems: "center",
            }}>
              {active && <span style={{ width: 8, height: 8, borderRadius: "50%", background: CREAM }} />}
            </span>
          </button>
        );
      })}
    </div>
  );
}

function MultiChip({ options, value, onChange }) {
  const toggle = (o) => {
    if (value.includes(o)) onChange(value.filter(x => x !== o));
    else onChange([...value, o]);
  };
  return (
    <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
      {options.map((o) => {
        const active = value.includes(o);
        return (
          <button key={o} onClick={() => toggle(o)} style={{
            padding: "10px 16px", borderRadius: 999,
            border: `1.5px solid ${active ? SAGE_DEEP : STROKE}`,
            background: active ? SAGE_DEEP : "rgba(255,255,255,0.7)",
            color: active ? CREAM : FOREST,
            fontFamily: "inherit", fontSize: 13, fontWeight: 500,
            cursor: "pointer",
            transition: "all 0.15s",
          }}>
            {active ? "✓ " : ""}{o}
          </button>
        );
      })}
    </div>
  );
}

function QuizScreen({ answers, setAnswers, step, setStep, onComplete, onBack }) {
  const total = QUESTIONS.length;
  const q = QUESTIONS[step];
  const value = answers[q.key];
  const setValue = (v) => setAnswers({ ...answers, [q.key]: v });
  const progress = ((step + 1) / total) * 100;

  const next = () => {
    if (step < total - 1) setStep(step + 1);
    else onComplete();
  };
  const back = () => {
    if (step === 0) onBack();
    else setStep(step - 1);
  };

  return (
    <ScreenShell bg={CREAM}>
      {/* Header */}
      <div style={{ padding: "60px 24px 0", display: "flex", alignItems: "center", gap: 16 }}>
        <button onClick={back} style={{
          width: 40, height: 40, borderRadius: "50%",
          background: "rgba(255,255,255,0.7)", border: `1px solid ${STROKE}`,
          display: "grid", placeItems: "center", cursor: "pointer",
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={FOREST} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 18l-6-6 6-6"/></svg>
        </button>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: MUTED, marginBottom: 6 }}>
            <span>Question {step + 1} of {total}</span>
            <span>{Math.round(progress)}%</span>
          </div>
          <div style={{ height: 4, borderRadius: 2, background: CREAM_2, overflow: "hidden" }}>
            <div style={{
              height: "100%", width: `${progress}%`,
              background: `linear-gradient(90deg, ${SAGE} 0%, ${SAGE_DEEP} 100%)`,
              borderRadius: 2, transition: "width 0.4s ease",
            }} />
          </div>
        </div>
      </div>

      {/* Question card */}
      <div style={{ flex: 1, padding: "32px 24px 24px", display: "flex", flexDirection: "column" }}>
        <div style={{
          width: 48, height: 48, borderRadius: 14,
          background: "rgba(123,169,143,0.18)",
          display: "grid", placeItems: "center", marginBottom: 22,
        }}>
          <Icon name={q.icon} size={22} color={SAGE_DEEP} />
        </div>

        <h2 style={{
          fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
          fontSize: 31, lineHeight: 1.08, letterSpacing: "-0.045em",
          margin: 0, marginBottom: 10, color: FOREST, fontWeight: 500,
          textWrap: "balance",
        }}>
          {q.title}
        </h2>
        <p style={{ margin: 0, color: MUTED, fontSize: 14, lineHeight: 1.55, marginBottom: 28 }}>
          {q.helper}
        </p>

        <div style={{ flex: 1 }}>
          {q.type === "choice" ? (
            <ChoiceList options={q.options} value={value} onChange={setValue} />
          ) : q.type === "multi" ? (
            <MultiChip options={q.options} value={value} onChange={setValue} />
          ) : (
            <div>
              <NumberStepper value={value} onChange={setValue} min={q.min} max={q.max} step={q.step} isCount={q.isCount} />
              <div style={{ textAlign: "center", marginTop: 8, fontSize: 13, color: MUTED }}>
                {q.unit}
              </div>
              <HealthyRangeBar value={value} min={q.min} max={q.max} healthy={q.healthy} unit={q.unit} isCount={q.isCount} />
            </div>
          )}
        </div>

        {/* Footer CTA */}
        <button onClick={next} style={{
          marginTop: 20,
          height: 56, borderRadius: 28, border: "none",
          background: FOREST, color: CREAM,
          fontSize: 16, fontWeight: 500, fontFamily: "inherit",
          cursor: "pointer",
          boxShadow: "0 12px 28px rgba(42,61,52,0.22)",
          display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
        }}>
          {step === total - 1 ? "See my results" : "Continue"}
          <span style={{ fontSize: 18 }}>→</span>
        </button>
      </div>
    </ScreenShell>
  );
}

window.QuizScreen = QuizScreen;
window.QUESTIONS = QUESTIONS;
window.Icon = Icon;
