// Results dashboard — burnout risk ring + metric cards + charts + recommendations
const { useEffect, useState } = React;
const API_BASE = window.UNWIND_API_BASE || "http://127.0.0.1:8000";

// ─── Burnout calculation (mirrors backend logic, simplified) ────
function calculateBurnout(a) {
  // Sleep balance: target 7-9 hrs
  const sleepDeficit = Math.max(0, 8 - a.sleep);
  const sleepRisk = Math.min(100, sleepDeficit * 18 + Math.max(0, a.sleep - 9.5) * 8);
  const sleepBalance = Math.max(0, Math.min(100, 100 - sleepRisk));

  // Workload: 8 is fine, >10 is heavy
  const workPressure = Math.min(100, Math.max(0, (a.work - 6) * 11));

  // Recovery: breaks + hobby vs target 75 min
  const recoveryMins = a.breaks + a.hobby;
  const recoveryTarget = 75;
  const recoveryBalance = Math.min(100, (recoveryMins / recoveryTarget) * 100);
  const recoveryRisk = Math.max(0, 100 - recoveryBalance);

  // Schedule density: deadlines + commute
  const scheduleDensity = Math.min(100, a.deadlines * 12 + (a.commute / 60) * 18);

  // Mood adjustment
  const moodAdj = { great: -8, okay: 0, drained: 12, rough: 22 }[a.mood] || 0;

  const burnout = Math.min(100, Math.max(0,
    sleepRisk * 0.30 + workPressure * 0.25 + recoveryRisk * 0.22 + scheduleDensity * 0.18 + moodAdj * 0.05 + moodAdj
  ));

  return {
    burnout: Math.round(burnout),
    sleepBalance: Math.round(sleepBalance),
    workPressure: Math.round(workPressure),
    recoveryBalance: Math.round(recoveryBalance),
    scheduleDensity: Math.round(scheduleDensity),
    recoveryMins,
    recoveryTarget,
  };
}

function mapAnswersToPayload(a) {
  return {
    sleep_hours: a.sleep,
    work_study_hours: a.work,
    break_minutes: a.breaks,
    commute_minutes: a.commute,
    deadline_count: a.deadlines,
    hobby_minutes: a.hobby,
    mood: a.mood,
    hobbies: a.relievers || [],
    stress_relievers: a.relievers || [],
    class_hours: 0,
    assignment_hours: 0,
    meeting_count: 0,
  };
}

function transformDashboardResponse(d) {
  return {
    burnout: Math.round(d.burnout_risk.percentage),
    sleepBalance: Math.round(d.sleep.sleep_balance_percentage),
    workPressure: Math.round(d.workload.workload_pressure_percentage),
    recoveryBalance: Math.round(d.recovery.recovery_balance_percentage),
    scheduleDensity: Math.round(d.schedule.schedule_density_percentage),
    recoveryMins: d.recovery.total_recovery_minutes,
    recoveryTarget: d.recovery.recommended_recovery_minutes,
  };
}

function buildMockTrend(calc) {
  const arr = [];
  const labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
  for (let i = 6; i >= 0; i--) {
    const noise = (Math.sin(i * 1.7) * 12) + (Math.cos(i * 2.3) * 8);
    const day = i === 0 ? calc.burnout : Math.max(15, Math.min(85, calc.burnout + noise + (i * -2)));
    arr.unshift({ label: labels[6 - i] || `D${i}`, value: Math.round(day) });
  }
  arr[arr.length - 1] = { label: "Today", value: calc.burnout };
  return arr;
}

function historyToTrend(history, fallbackCalc) {
  if (!Array.isArray(history) || history.length === 0) {
    return buildMockTrend(fallbackCalc);
  }
  return history.slice(-7).map((entry, index, rows) => {
    const date = new Date(entry.timestamp);
    const label = index === rows.length - 1
      ? "Today"
      : date.toLocaleDateString(undefined, { weekday: "short" });
    return {
      label,
      value: Math.round(entry.burnout_risk_percentage),
    };
  });
}

function riskLabel(pct) {
  if (pct < 30) return { label: "Steady", tone: SAGE_DEEP, bg: "rgba(123,169,143,0.16)", message: "Your routine looks balanced today. Nothing urgent to change — keep protecting what's working." };
  if (pct < 55) return { label: "Watching", tone: "#B89540", bg: "rgba(184,149,64,0.14)", message: "A few warning signs are showing. Small adjustments now will keep things from building up." };
  if (pct < 75) return { label: "Overloaded", tone: TERRACOTTA, bg: "rgba(217,142,107,0.16)", message: "Your routine may be showing signs of overload. Consider what could be eased before tomorrow." };
  return { label: "Critical", tone: "#C25A4D", bg: "rgba(194,90,77,0.14)", message: "Several areas are stretched thin. Real recovery time today isn't optional — it's the priority." };
}

// ─── Circular progress ring ────────────────────────────────────
function RiskRing({ value, size = 200, stroke = 14, color = SAGE_DEEP, track = "rgba(42,61,52,0.08)" }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - value / 100);
  return (
    <svg width={size} height={size} style={{ display: "block" }}>
      <defs>
        <linearGradient id="ringGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor={color} stopOpacity="0.95"/>
          <stop offset="100%" stopColor={color} stopOpacity="0.7"/>
        </linearGradient>
      </defs>
      <circle cx={size/2} cy={size/2} r={r} stroke={track} strokeWidth={stroke} fill="none"/>
      <circle cx={size/2} cy={size/2} r={r}
        stroke="url(#ringGrad)" strokeWidth={stroke} fill="none"
        strokeDasharray={c} strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`}
        style={{ transition: "stroke-dashoffset 0.8s ease" }}
      />
    </svg>
  );
}

// ─── Mini progress ring for metric cards ───────────────────────
function MiniRing({ value, size = 44, stroke = 4, color }) {
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - value / 100);
  return (
    <svg width={size} height={size} style={{ display: "block" }}>
      <circle cx={size/2} cy={size/2} r={r} stroke="rgba(42,61,52,0.08)" strokeWidth={stroke} fill="none"/>
      <circle cx={size/2} cy={size/2} r={r}
        stroke={color} strokeWidth={stroke} fill="none"
        strokeDasharray={c} strokeDashoffset={offset}
        strokeLinecap="round"
        transform={`rotate(-90 ${size/2} ${size/2})`}
      />
    </svg>
  );
}

// ─── Bar chart (drivers) ──────────────────────────────────────
function DriverBars({ data }) {
  const max = 100;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
      {data.map((d) => (
        <div key={d.label}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, color: FOREST, marginBottom: 6 }}>
            <span style={{ fontWeight: 500 }}>{d.label}</span>
            <span style={{ color: MUTED, fontVariantNumeric: "tabular-nums" }}>{d.value}%</span>
          </div>
          <div style={{ height: 8, background: CREAM_2, borderRadius: 4, overflow: "hidden" }}>
            <div style={{
              height: "100%", width: `${(d.value / max) * 100}%`,
              background: d.color, borderRadius: 4,
              transition: "width 0.6s ease",
            }} />
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Donut: how the day was spent ─────────────────────────────
function DayDonut({ slices, size = 160 }) {
  const total = slices.reduce((s, x) => s + x.value, 0);
  const r = size / 2 - 12;
  const cx = size / 2, cy = size / 2;
  let acc = 0;
  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size}>
        {slices.map((s, i) => {
          const start = (acc / total) * 2 * Math.PI - Math.PI / 2;
          acc += s.value;
          const end = (acc / total) * 2 * Math.PI - Math.PI / 2;
          const large = end - start > Math.PI ? 1 : 0;
          const x1 = cx + r * Math.cos(start), y1 = cy + r * Math.sin(start);
          const x2 = cx + r * Math.cos(end), y2 = cy + r * Math.sin(end);
          // inner radius for donut effect
          const ir = r - 22;
          const ix1 = cx + ir * Math.cos(end), iy1 = cy + ir * Math.sin(end);
          const ix2 = cx + ir * Math.cos(start), iy2 = cy + ir * Math.sin(start);
          const path = `M ${x1} ${y1} A ${r} ${r} 0 ${large} 1 ${x2} ${y2} L ${ix1} ${iy1} A ${ir} ${ir} 0 ${large} 0 ${ix2} ${iy2} Z`;
          return <path key={i} d={path} fill={s.color} />;
        })}
      </svg>
      <div style={{
        position: "absolute", inset: 0,
        display: "grid", placeItems: "center",
      }}>
        <div style={{ textAlign: "center" }}>
          <div style={{ fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif', fontSize: 24, fontWeight: 500, letterSpacing: "-0.04em", color: FOREST, lineHeight: 1 }}>24h</div>
          <div style={{ fontSize: 11, color: MUTED, marginTop: 2 }}>tracked today</div>
        </div>
      </div>
    </div>
  );
}

// ─── Trend line (mock 7-day history) ──────────────────────────
function TrendLine({ data, size = { w: 320, h: 90 } }) {
  const max = 100, min = 0;
  const pad = { l: 8, r: 8, t: 8, b: 18 };
  const w = size.w - pad.l - pad.r;
  const h = size.h - pad.t - pad.b;
  const pts = data.map((d, i) => {
    const x = pad.l + (i / (data.length - 1)) * w;
    const y = pad.t + h - ((d.value - min) / (max - min)) * h;
    return [x, y];
  });
  const path = pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p[0]} ${p[1]}`).join(" ");
  const areaPath = `${path} L ${pts[pts.length-1][0]} ${pad.t + h} L ${pts[0][0]} ${pad.t + h} Z`;
  return (
    <svg width={size.w} height={size.h} style={{ display: "block" }}>
      <defs>
        <linearGradient id="trendGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={SAGE} stopOpacity="0.35"/>
          <stop offset="100%" stopColor={SAGE} stopOpacity="0"/>
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#trendGrad)"/>
      <path d={path} stroke={SAGE_DEEP} strokeWidth="2" fill="none" strokeLinecap="round" strokeLinejoin="round"/>
      {pts.map((p, i) => (
        <circle key={i} cx={p[0]} cy={p[1]} r={i === pts.length - 1 ? 4 : 2.5}
          fill={i === pts.length - 1 ? FOREST : SAGE_DEEP}
          stroke={i === pts.length - 1 ? CREAM : "none"} strokeWidth="2"/>
      ))}
      {data.map((d, i) => (
        <text key={i} x={pts[i][0]} y={size.h - 4}
          fontSize="9" fill={MUTED} textAnchor="middle"
          fontFamily="inherit">{d.label}</text>
      ))}
    </svg>
  );
}

// ─── Recommendations ─────────────────────────────────────────
function buildRecommendations(answers, calc) {
  const recs = [];
  // Sort drivers
  const drivers = [
    { k: "sleep", v: 100 - calc.sleepBalance },
    { k: "workload", v: calc.workPressure },
    { k: "recovery", v: 100 - calc.recoveryBalance },
    { k: "schedule", v: calc.scheduleDensity },
  ].sort((a, b) => b.v - a.v);

  const recMap = {
    sleep: { icon: "moon", title: "Protect your sleep tonight", body: `Aim for at least ${Math.max(7, Math.ceil(8))} hours. Wind down 30 minutes before bed — no screens.` },
    workload: { icon: "briefcase", title: "Trim tomorrow's workload", body: "Look at tomorrow's plan. Are there 1–2 things that could move to later in the week?" },
    recovery: { icon: "leaf", title: "Build in real recovery time", body: `You logged ${calc.recoveryMins} min of breaks/hobbies. Aim for ${calc.recoveryTarget}+ min — even a short walk counts.` },
    schedule: { icon: "compass", title: "Space out your day", body: "Stack meetings or deadlines back-to-back makes recovery harder. Try buffer blocks tomorrow." },
  };

  drivers.filter(d => d.v >= 35).slice(0, 2).forEach(d => recs.push(recMap[d.k]));

  if (answers.relievers && answers.relievers.length > 0) {
    const r = answers.relievers[0];
    recs.push({ icon: "sparkle", title: `Lean on ${r} this evening`, body: `You said ${r} helps you decompress. Block 20 minutes for it before bed.` });
  }

  if (recs.length === 0) {
    recs.push({ icon: "leaf", title: "Hold the pattern", body: "Today looks balanced. Keep protecting sleep, breaks, and a manageable load to stay here." });
  }

  return recs.slice(0, 3);
}

function ResultsScreen({ answers, onRestart, useBackend = false }) {
  const fallbackCalc = calculateBurnout(answers);
  const [calc, setCalc] = useState(fallbackCalc);
  const [trend, setTrend] = useState(buildMockTrend(fallbackCalc));
  const [dataSource, setDataSource] = useState(useBackend ? "loading" : "mock");

  useEffect(() => {
    let active = true;
    const localCalc = calculateBurnout(answers);
    setCalc(localCalc);

    if (!useBackend) {
      setTrend(buildMockTrend(localCalc));
      setDataSource("mock");
      return () => {
        active = false;
      };
    }

    async function loadDashboard() {
      try {
        setDataSource("loading");
        const dashboardResponse = await fetch(`${API_BASE}/api/dashboard`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(mapAnswersToPayload(answers)),
        });
        if (!dashboardResponse.ok) {
          throw new Error(`Dashboard request failed: ${dashboardResponse.status}`);
        }

        const dashboardJson = await dashboardResponse.json();
        const backendCalc = transformDashboardResponse(dashboardJson);
        if (!active) return;
        setCalc(backendCalc);
        setDataSource("backend");

        const historyResponse = await fetch(`${API_BASE}/api/history?limit=7`);
        if (!historyResponse.ok) {
          throw new Error(`History request failed: ${historyResponse.status}`);
        }

        const historyJson = await historyResponse.json();
        if (!active) return;
        setTrend(historyToTrend(historyJson, backendCalc));
      } catch (error) {
        if (!active) return;
        console.warn("Falling back to mock burnout calculation.", error);
        setCalc(localCalc);
        setTrend(buildMockTrend(localCalc));
        setDataSource("mock");
      }
    }

    loadDashboard();
    return () => {
      active = false;
    };
  }, [answers, useBackend]);

  const risk = riskLabel(calc.burnout);
  const recs = buildRecommendations(answers, calc);

  // Day donut: hours breakdown
  const slept = answers.sleep;
  const worked = answers.work;
  const commute = answers.commute / 60;
  const recovery = (answers.breaks + answers.hobby) / 60;
  const other = Math.max(0, 24 - slept - worked - commute - recovery);
  const slices = [
    { label: "Sleep", value: slept, color: "#5A7E9C" },
    { label: "Work/Study", value: worked, color: FOREST },
    { label: "Commute", value: commute, color: TERRACOTTA },
    { label: "Recovery", value: recovery, color: SAGE },
    { label: "Other", value: other, color: CREAM_2 },
  ].filter(s => s.value > 0);

  return (
    <div style={{
      width: "100%", height: "100%",
      background: CREAM,
      fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
      color: FOREST,
      overflowY: "auto",
      overflowX: "hidden",
    }}>
      <style>{`
        .res-scroll::-webkit-scrollbar { display: none; }
      `}</style>

      {/* Header */}
      <div style={{ padding: "60px 24px 16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <div style={{ fontSize: 12, color: MUTED, marginBottom: 2 }}>Today · April 25</div>
          <div style={{
            fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
            fontSize: 23, color: FOREST, fontWeight: 500, letterSpacing: "-0.04em",
          }}>Your check-in</div>
          <div style={{ fontSize: 11, color: MUTED, marginTop: 4 }}>
            {dataSource === "backend" ? "Connected to dashboard API" : dataSource === "loading" ? "Loading your results..." : "Showing local demo results"}
          </div>
        </div>
        <button onClick={onRestart} style={{
          width: 40, height: 40, borderRadius: "50%",
          background: "rgba(255,255,255,0.7)", border: `1px solid ${STROKE}`,
          display: "grid", placeItems: "center", cursor: "pointer",
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={FOREST} strokeWidth="2" strokeLinecap="round"><path d="M3 12a9 9 0 1 0 3-6.7L3 8"/><path d="M3 3v5h5"/></svg>
        </button>
      </div>

      {/* Hero risk card */}
      <div style={{ padding: "0 20px" }}>
        <div style={{
          background: "linear-gradient(160deg, rgba(255,255,255,0.95) 0%, rgba(239,232,218,0.7) 100%)",
          border: `1px solid ${STROKE}`,
          borderRadius: 28,
          padding: "24px 22px 22px",
          boxShadow: "0 16px 40px rgba(42,61,52,0.07)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 4, marginBottom: 6 }}>
            <span style={{ fontSize: 12, color: MUTED, letterSpacing: 0.3, textTransform: "uppercase" }}>Burnout risk</span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: 18 }}>
            <div style={{ position: "relative", width: 140, height: 140, flexShrink: 0 }}>
              <RiskRing value={calc.burnout} size={140} stroke={12} color={risk.tone} />
              <div style={{
                position: "absolute", inset: 0,
                display: "grid", placeItems: "center",
              }}>
                <div style={{ textAlign: "center" }}>
                  <div style={{
                    fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
                    fontSize: 44, lineHeight: 1, color: FOREST, fontWeight: 500, letterSpacing: "-0.05em",
                    fontVariantNumeric: "tabular-nums",
                  }}>
                    {calc.burnout}<span style={{ fontSize: 18, color: MUTED }}>%</span>
                  </div>
                </div>
              </div>
            </div>

            <div style={{ flex: 1, minWidth: 0 }}>
              <div style={{
                display: "inline-flex", padding: "5px 12px", borderRadius: 999,
                background: risk.bg, color: risk.tone,
                fontSize: 12, fontWeight: 500, marginBottom: 8,
              }}>● {risk.label}</div>
              <div style={{ fontSize: 13, color: FOREST, lineHeight: 1.5, textWrap: "pretty" }}>
                {risk.message}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Metric cards 2×2 */}
      <div style={{ padding: "16px 20px 0", display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <MetricCard label="Sleep balance" value={`${calc.sleepBalance}%`} sub={`${answers.sleep} hrs slept`} ringValue={calc.sleepBalance} ringColor="#5A7E9C" />
        <MetricCard label="Workload" value={`${calc.workPressure}%`} sub={`${answers.work} hrs working`} ringValue={calc.workPressure} ringColor={calc.workPressure > 60 ? TERRACOTTA : FOREST} invertRing />
        <MetricCard label="Recovery time" value={`${calc.recoveryMins}`} unit="min" sub={`Target ${calc.recoveryTarget} min`} ringValue={calc.recoveryBalance} ringColor={SAGE_DEEP} />
        <MetricCard label="Schedule density" value={`${calc.scheduleDensity}%`} sub={`${answers.deadlines} deadlines`} ringValue={calc.scheduleDensity} ringColor={calc.scheduleDensity > 60 ? TERRACOTTA : DUSTY} invertRing />
      </div>

      {/* Day breakdown donut + legend */}
      <div style={{ padding: "16px 20px 0" }}>
        <CardShell>
          <CardHeader title="How you spent today" sub="A pie of your 24 hours" />
          <div style={{ display: "flex", alignItems: "center", gap: 18, marginTop: 14 }}>
            <DayDonut slices={slices} size={132} />
            <div style={{ flex: 1, display: "flex", flexDirection: "column", gap: 8 }}>
              {slices.map(s => (
                <div key={s.label} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 12 }}>
                  <span style={{ width: 8, height: 8, borderRadius: 2, background: s.color, flexShrink: 0 }} />
                  <span style={{ flex: 1, color: FOREST, fontWeight: 500 }}>{s.label}</span>
                  <span style={{ color: MUTED, fontVariantNumeric: "tabular-nums" }}>
                    {s.value < 1 ? `${Math.round(s.value * 60)}m` : `${s.value.toFixed(1).replace(/\.0$/, "")}h`}
                  </span>
                </div>
              ))}
            </div>
          </div>
        </CardShell>
      </div>

      {/* Risk drivers */}
      <div style={{ padding: "16px 20px 0" }}>
        <CardShell>
          <CardHeader title="What's pulling on you" sub="Each area's contribution to today's risk" />
          <div style={{ marginTop: 14 }}>
            <DriverBars data={[
              { label: "Sleep deficit", value: 100 - calc.sleepBalance, color: "#5A7E9C" },
              { label: "Workload pressure", value: calc.workPressure, color: calc.workPressure > 60 ? TERRACOTTA : FOREST },
              { label: "Recovery shortfall", value: 100 - calc.recoveryBalance, color: SAGE_DEEP },
              { label: "Schedule density", value: calc.scheduleDensity, color: DUSTY },
            ]}/>
          </div>
        </CardShell>
      </div>

      {/* 7-day trend */}
      <div style={{ padding: "16px 20px 0" }}>
        <CardShell>
          <CardHeader title="Last 7 days" sub="Burnout risk trend" />
          <div style={{ marginTop: 12, marginLeft: -8 }}>
            <TrendLine data={trend} size={{ w: 322, h: 100 }} />
          </div>
        </CardShell>
      </div>

      {/* Recommendations */}
      <div style={{ padding: "16px 20px 0" }}>
        <div style={{ marginBottom: 10, padding: "0 4px" }}>
          <div style={{
            fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
            fontSize: 22, color: FOREST, fontWeight: 500, letterSpacing: "-0.04em",
          }}>
            For today
          </div>
          <div style={{ fontSize: 13, color: MUTED, marginTop: 2 }}>
            Three small shifts based on your check-in.
          </div>
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {recs.map((r, i) => (
            <div key={i} style={{
              background: "rgba(255,255,255,0.85)",
              border: `1px solid ${STROKE}`,
              borderRadius: 22,
              padding: "16px 18px",
              display: "flex", gap: 14, alignItems: "flex-start",
            }}>
              <div style={{
                width: 38, height: 38, borderRadius: 12,
                background: "rgba(123,169,143,0.18)",
                display: "grid", placeItems: "center", flexShrink: 0,
              }}>
                <Icon name={r.icon} size={18} color={SAGE_DEEP} />
              </div>
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 14, fontWeight: 600, color: FOREST, marginBottom: 4 }}>{r.title}</div>
                <div style={{ fontSize: 13, color: MUTED, lineHeight: 1.5 }}>{r.body}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer disclaimer + restart */}
      <div style={{ padding: "20px 20px 60px" }}>
        <button onClick={onRestart} style={{
          width: "100%", height: 52, borderRadius: 26, border: `1px solid ${STROKE}`,
          background: "rgba(255,255,255,0.7)", color: FOREST,
          fontSize: 15, fontWeight: 500, fontFamily: "inherit", cursor: "pointer",
        }}>
          Log another check-in
        </button>
        <div style={{ fontSize: 11, color: MUTED, textAlign: "center", marginTop: 14, lineHeight: 1.5 }}>
          unwind is not a medical diagnosis tool. If you're struggling, please reach out to a professional.
        </div>
      </div>
    </div>
  );
}

function CardShell({ children }) {
  return (
    <div style={{
      background: "rgba(255,255,255,0.85)",
      border: `1px solid ${STROKE}`,
      borderRadius: 24,
      padding: "18px 20px 20px",
    }}>
      {children}
    </div>
  );
}

function CardHeader({ title, sub }) {
  return (
    <div>
      <div style={{ fontSize: 14, fontWeight: 600, color: FOREST }}>{title}</div>
      <div style={{ fontSize: 12, color: MUTED, marginTop: 2 }}>{sub}</div>
    </div>
  );
}

function MetricCard({ label, value, unit, sub, ringValue, ringColor, invertRing }) {
  // For pressure-like metrics, ring fills with the value (worse = more)
  // For balance-like metrics, ring fills with the value (better = more)
  const displayRing = invertRing ? ringValue : ringValue;
  return (
    <div style={{
      background: "rgba(255,255,255,0.85)",
      border: `1px solid ${STROKE}`,
      borderRadius: 22,
      padding: "16px 16px 14px",
      display: "flex", flexDirection: "column", gap: 8,
      minHeight: 118,
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div style={{ fontSize: 11, color: MUTED, fontWeight: 500, letterSpacing: 0.2, textTransform: "uppercase" }}>{label}</div>
        <MiniRing value={displayRing} color={ringColor} />
      </div>
      <div style={{ marginTop: "auto" }}>
        <div style={{
          fontFamily: '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif',
          fontSize: 30, lineHeight: 1, color: FOREST, fontWeight: 500, letterSpacing: "-0.04em",
          fontVariantNumeric: "tabular-nums",
        }}>
          {value}{unit && <span style={{ fontSize: 13, color: MUTED, marginLeft: 4 }}>{unit}</span>}
        </div>
        <div style={{ fontSize: 11, color: MUTED, marginTop: 4 }}>{sub}</div>
      </div>
    </div>
  );
}

window.ResultsScreen = ResultsScreen;
window.calculateBurnout = calculateBurnout;
