const { useState } = React;

const DEFAULT_ANSWERS = {
  sleep: 6,
  work: 10,
  breaks: 20,
  commute: 60,
  deadlines: 4,
  hobby: 15,
  mood: "drained",
  relievers: ["walking", "music"],
};

function LiveAppShell({ children }) {
  return (
    <div className="live-shell">
      <div className="live-copy">
        <div className="live-kicker">
          <span style={{ width: 8, height: 8, borderRadius: "50%", background: "#7BA98F", display: "inline-block" }} />
          Burnout Prevention Dashboard
        </div>
        <h1 className="live-title">A working daily check-in, not a storyboard.</h1>
        <p>
          Reset helps users reflect on their daily routine, understand what may be
          contributing to stress, and receive simple recommendations to prevent
          burnout before it builds up.
        </p>
        <div className="live-meta">
          <div className="meta-pill">Live quiz flow</div>
          <div className="meta-pill">Backend-connected results</div>
          <div className="meta-pill">Mock fallback included</div>
        </div>
      </div>

      <div className="device-stage">
        <div className="device-float">{children}</div>
      </div>

      <a className="board-link" href="./unwind.html">
        Open design board reference
      </a>
    </div>
  );
}

function PhoneApp({ initialStage = "intro", initialQuizStep = 0, initialAnswers = DEFAULT_ANSWERS }) {
  const [stage, setStage] = useState(initialStage);
  const [step, setStep] = useState(initialQuizStep);
  const [answers, setAnswers] = useState(initialAnswers);
  const [useBackend, setUseBackend] = useState(false);

  const screenKey = `${stage}-${step}-${useBackend ? "live" : "mock"}`;

  return (
    <LiveAppShell>
      <div className="screen-enter" key={screenKey}>
        <IOSDevice width={402} height={874}>
          {stage === "intro" && (
            <IntroScreen onStart={() => { setStage("quiz"); setStep(0); setUseBackend(false); }} />
          )}
          {stage === "quiz" && (
            <QuizScreen
              answers={answers}
              setAnswers={setAnswers}
              step={step}
              setStep={setStep}
              onComplete={() => { setUseBackend(true); setStage("results"); }}
              onBack={() => setStage("intro")}
            />
          )}
          {stage === "results" && (
            <ResultsScreen
              answers={answers}
              useBackend={useBackend}
              onRestart={() => {
                setStage("intro");
                setStep(0);
                setAnswers(DEFAULT_ANSWERS);
                setUseBackend(false);
              }}
            />
          )}
        </IOSDevice>
      </div>
    </LiveAppShell>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<PhoneApp initialStage="intro" />);
