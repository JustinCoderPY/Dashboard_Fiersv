// Burnout Prevention — three screens: Intro, Quiz, Results
// All screens render inside a fixed 402×874 iPhone viewport.

const SAGE = "#7BA98F";
const SAGE_DEEP = "#3F6B5A";
const FOREST = "#2A3D34";
const CREAM = "#F6F1E8";
const CREAM_2 = "#EFE8DA";
const TERRACOTTA = "#D98E6B";
const DUSTY = "#8FA8C4";
const MUTED = "#6B7872";
const STROKE = "rgba(42, 61, 52, 0.10)";
const APP_FONT = '"Sofia Sans", "Aptos", "Segoe UI", system-ui, sans-serif';

// ─── Screen scaffolding ───────────────────────────────────────────
function ScreenShell({ children, bg = CREAM, statusColor = "dark" }) {
  return (
    <div style={{
      width: "100%", height: "100%",
      background: bg,
      fontFamily: APP_FONT,
      color: FOREST,
      display: "flex", flexDirection: "column",
      overflow: "hidden",
      position: "relative",
    }}>
      {children}
    </div>
  );
}

// ─── INTRO SCREEN ─────────────────────────────────────────────────
function IntroScreen({ onStart }) {
  return (
    <ScreenShell bg={CREAM}>
      {/* Decorative blob */}
      <div style={{
        position: "absolute", top: -80, right: -60, width: 280, height: 280,
        borderRadius: "50%",
        background: "radial-gradient(circle at 30% 30%, rgba(123,169,143,0.35), rgba(123,169,143,0) 70%)",
        pointerEvents: "none",
      }} />
      <div style={{
        position: "absolute", bottom: -100, left: -80, width: 320, height: 320,
        borderRadius: "50%",
        background: "radial-gradient(circle at 60% 40%, rgba(217,142,107,0.22), rgba(217,142,107,0) 70%)",
        pointerEvents: "none",
      }} />

      <div style={{
        flex: 1, display: "flex", flexDirection: "column",
        padding: "72px 28px 32px",
        position: "relative", zIndex: 1,
      }}>
        {/* Logo mark */}
        <div style={{
          display: "flex", alignItems: "center", gap: 10, marginBottom: 56,
        }}>
          <div style={{
            width: 32, height: 32, borderRadius: 10,
            background: `linear-gradient(135deg, ${SAGE} 0%, ${SAGE_DEEP} 100%)`,
            display: "grid", placeItems: "center",
            boxShadow: "0 8px 20px rgba(63,107,90,0.25)",
          }}>
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <path d="M8 2 C5 5, 5 8, 8 11 C11 8, 11 5, 8 2 Z M8 11 C8 11.8, 8 13, 8 14" stroke="white" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
          <div style={{
            fontFamily: APP_FONT,
            fontSize: 21, letterSpacing: -0.04 + "em", color: FOREST, fontWeight: 500,
          }}>
            Reset
          </div>
        </div>

        {/* Hero copy */}
        <div style={{ flex: 1, display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div style={{
            display: "inline-flex", alignSelf: "flex-start",
            padding: "6px 12px", borderRadius: 999,
            background: "rgba(63,107,90,0.10)", color: SAGE_DEEP,
            fontSize: 12, fontWeight: 500, letterSpacing: 0.2,
            marginBottom: 20,
          }}>
            ◐ &nbsp;Daily check-in · 90 seconds
          </div>

          <h1 style={{
            fontFamily: APP_FONT,
            fontSize: 47, lineHeight: 0.98, letterSpacing: "-0.05em",
            margin: 0, color: FOREST, fontWeight: 500,
            textWrap: "balance",
          }}>
            What in your routine<br/>
            <span style={{ color: SAGE_DEEP }}>might be wearing you down?</span>
          </h1>

          <p style={{
            marginTop: 22, fontSize: 16, lineHeight: 1.65, color: MUTED, fontWeight: 450,
            maxWidth: 320,
          }}>
            Reset helps users reflect on their daily routine, understand what may be
            contributing to stress, and receive simple recommendations to prevent
            burnout before it builds up.
          </p>

          {/* Three-step preview */}
          <div style={{ marginTop: 36, display: "flex", flexDirection: "column", gap: 14 }}>
            {[
              { n: "1", t: "Answer 9 quick questions", s: "One at a time, no long forms" },
              { n: "2", t: "See your burnout risk", s: "A clear percentage with context" },
              { n: "3", t: "Get gentle next steps", s: "Personalized to your day" },
            ].map((s) => (
              <div key={s.n} style={{
                display: "flex", alignItems: "center", gap: 14,
                padding: "14px 16px",
                background: "rgba(255,255,255,0.6)",
                borderRadius: 18,
                border: `1px solid ${STROKE}`,
              }}>
                <div style={{
                  width: 28, height: 28, borderRadius: "50%",
                  background: CREAM_2, color: SAGE_DEEP,
                  display: "grid", placeItems: "center",
                  fontFamily: APP_FONT,
                  fontSize: 14, fontWeight: 700,
                }}>{s.n}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 14, fontWeight: 500, color: FOREST, marginBottom: 2 }}>{s.t}</div>
                  <div style={{ fontSize: 12, color: MUTED }}>{s.s}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <button onClick={onStart} style={{
          marginTop: 28,
          height: 56, borderRadius: 28, border: "none",
          background: FOREST, color: CREAM,
          fontSize: 16, fontWeight: 500, letterSpacing: 0.1,
          fontFamily: "inherit",
          cursor: "pointer",
          boxShadow: "0 12px 28px rgba(42,61,52,0.22)",
          display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
        }}>
          Start today's check-in
          <span style={{ fontSize: 18 }}>→</span>
        </button>
        <div style={{ textAlign: "center", marginTop: 14, fontSize: 12, color: MUTED }}>
          Not a medical diagnosis · Your data stays on your device
        </div>
      </div>
    </ScreenShell>
  );
}

window.IntroScreen = IntroScreen;
window.SAGE = SAGE;
window.SAGE_DEEP = SAGE_DEEP;
window.FOREST = FOREST;
window.CREAM = CREAM;
window.CREAM_2 = CREAM_2;
window.TERRACOTTA = TERRACOTTA;
window.DUSTY = DUSTY;
window.MUTED = MUTED;
window.STROKE = STROKE;
window.ScreenShell = ScreenShell;
