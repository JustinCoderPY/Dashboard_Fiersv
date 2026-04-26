// Main app — orchestrates Intro → Quiz → Results inside iPhone frames on a design canvas
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

function PhoneApp({ initialStage = "intro", initialQuizStep = 0, initialAnswers = DEFAULT_ANSWERS, label }) {
  const [stage, setStage] = useState(initialStage);
  const [step, setStep] = useState(initialQuizStep);
  const [answers, setAnswers] = useState(initialAnswers);
  const [useBackend, setUseBackend] = useState(false);

  return (
    <IOSDevice width={402} height={874}>
      {stage === "intro" && (
        <IntroScreen onStart={() => { setStage("quiz"); setStep(0); setUseBackend(false); }} />
      )}
      {stage === "quiz" && (
        <QuizScreen
          answers={answers} setAnswers={setAnswers}
          step={step} setStep={setStep}
          onComplete={() => { setUseBackend(true); setStage("results"); }}
          onBack={() => setStage("intro")}
        />
      )}
      {stage === "results" && (
        <ResultsScreen
          answers={answers}
          useBackend={useBackend}
          onRestart={() => { setStage("intro"); setStep(0); setAnswers(DEFAULT_ANSWERS); setUseBackend(false); }}
        />
      )}
    </IOSDevice>
  );
}

function App() {
  return (
    <DesignCanvas title="unwind — burnout prevention" subtitle="Mobile wellness app · 3 stages of the experience">
      <DCSection id="flow" title="Full flow" subtitle="Tap through any phone — they're all live">
        <DCArtboard id="intro" label="1. Landing / intro" width={402} height={874}>
          <PhoneApp initialStage="intro" />
        </DCArtboard>
        <DCArtboard id="quiz" label="2. Guided quiz (start)" width={402} height={874}>
          <PhoneApp initialStage="quiz" initialQuizStep={0} />
        </DCArtboard>
        <DCArtboard id="quiz-mid" label="3. Quiz (mood)" width={402} height={874}>
          <PhoneApp initialStage="quiz" initialQuizStep={6} />
        </DCArtboard>
        <DCArtboard id="quiz-multi" label="4. Quiz (relievers)" width={402} height={874}>
          <PhoneApp initialStage="quiz" initialQuizStep={7} />
        </DCArtboard>
        <DCArtboard id="results" label="5. Results dashboard" width={402} height={874}>
          <PhoneApp initialStage="results" />
        </DCArtboard>
      </DCSection>

      <DCSection id="states" title="Risk states" subtitle="Same dashboard, different burnout levels">
        <DCArtboard id="steady" label="Steady (low risk)" width={402} height={874}>
          <PhoneApp initialStage="results" initialAnswers={{
            sleep: 8, work: 7, breaks: 60, commute: 30, deadlines: 1, hobby: 60, mood: "great", relievers: ["walking", "reading"],
          }} />
        </DCArtboard>
        <DCArtboard id="watching" label="Watching (medium)" width={402} height={874}>
          <PhoneApp initialStage="results" initialAnswers={{
            sleep: 6.5, work: 9, breaks: 30, commute: 45, deadlines: 3, hobby: 25, mood: "okay", relievers: ["music"],
          }} />
        </DCArtboard>
        <DCArtboard id="critical" label="Critical (high)" width={402} height={874}>
          <PhoneApp initialStage="results" initialAnswers={{
            sleep: 4.5, work: 12, breaks: 10, commute: 90, deadlines: 6, hobby: 0, mood: "rough", relievers: [],
          }} />
        </DCArtboard>
      </DCSection>
    </DesignCanvas>
  );
}

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(<App />);
