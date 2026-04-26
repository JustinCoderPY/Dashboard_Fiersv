# Wiring the prototype into Dashboard_Fiersv

Three paths from this prototype → the real repo. Pick one.

---

## Path A — Replace Streamlit with the React UI (recommended)

Best long-term. Frontend/backend split, keeps your existing `burnout_backend/` calculation logic, no Firebase needed (you said local CSV is fine for now).

### 1. Add a FastAPI endpoint

Create `burnout_backend/app/routes/dashboard_routes.py` (you already have a stub):

```python
from fastapi import APIRouter
from pydantic import BaseModel
from burnout_backend.app.services.dashboard_service import build_dashboard

router = APIRouter()

class CheckInPayload(BaseModel):
    average_sleep_hours: float
    work_hours: float
    class_hours: float = 0
    assignment_hours: float = 0
    break_minutes: int
    hobby_minutes: int
    commute_hours: float
    meeting_count: int = 0
    deadline_count: int
    hobbies: list[str] = []
    stress_relievers: list[str] = []

@router.post("/api/dashboard")
def dashboard(payload: CheckInPayload):
    return build_dashboard(payload.dict())
```

Register it in `burnout_backend/main.py`:

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from burnout_backend.app.routes.dashboard_routes import router

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.include_router(router)
```

Run it: `uvicorn burnout_backend.main:app --reload --port 8000`

### 2. Append a CSV row on each check-in

Add this to the same route:

```python
import csv, datetime
from pathlib import Path

ENTRIES = Path("data/user_entries.csv")

@router.post("/api/dashboard")
def dashboard(payload: CheckInPayload):
    result = build_dashboard(payload.dict())
    # append to CSV
    row = {
        "timestamp": datetime.datetime.now().isoformat(),
        **payload.dict(exclude={"hobbies", "stress_relievers"}),
        "burnout_risk_percentage": result.burnout_risk.percentage,
        "risk_level": result.burnout_risk.risk_level,
    }
    ENTRIES.parent.mkdir(exist_ok=True)
    new_file = not ENTRIES.exists()
    with ENTRIES.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=row.keys())
        if new_file:
            w.writeheader()
        w.writerow(row)
    return result
```

### 3. Add a `/api/history` endpoint for the 7-day trend

```python
import pandas as pd

@router.get("/api/history")
def history(limit: int = 7):
    if not ENTRIES.exists():
        return []
    df = pd.read_csv(ENTRIES).tail(limit)
    return df.to_dict(orient="records")
```

### 4. Swap the prototype's mock calc for real fetches

In `prototype/app/results.jsx`, replace the synchronous `calculateBurnout(answers)` call with:

```jsx
const [calc, setCalc] = useState(null);
const [history, setHistory] = useState([]);

useEffect(() => {
  fetch("http://localhost:8000/api/dashboard", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      average_sleep_hours: answers.sleep,
      work_hours: answers.work,
      break_minutes: answers.breaks,
      hobby_minutes: answers.hobby,
      commute_hours: answers.commute / 60,
      deadline_count: answers.deadlines,
      hobbies: answers.relievers,
      stress_relievers: answers.relievers,
    }),
  }).then(r => r.json()).then(d => setCalc({
    burnout: Math.round(d.burnout_risk.percentage),
    sleepBalance: Math.round(d.sleep.sleep_balance_percentage),
    workPressure: Math.round(d.workload.workload_pressure_percentage),
    recoveryBalance: Math.round(d.recovery.recovery_balance_percentage),
    scheduleDensity: Math.round(d.schedule.schedule_density_percentage),
    recoveryMins: d.recovery.total_recovery_minutes,
    recoveryTarget: d.recovery.recommended_recovery_minutes,
  }));
  fetch("http://localhost:8000/api/history").then(r => r.json()).then(setHistory);
}, [answers]);

if (!calc) return <LoadingState />;
```

### 5. Repo layout after the change

```
Dashboard_Fiersv/
├── burnout_backend/         # FastAPI (unchanged, just wire routes)
├── frontend/                # ← rename prototype/ to this
│   ├── unwind.html
│   ├── design-canvas.jsx
│   ├── ios-frame.jsx
│   └── app/
├── data/user_entries.csv    # local CSV log (unchanged)
├── streamlit_dash.py        # keep as a v1 reference, or delete
├── README.md
└── requirements.txt
```

---

## Path B — Keep Streamlit, port the visuals

Slower wins. You'd reuse the cream/sage palette + Instrument Serif + the question-per-card flow inside `streamlit_dash.py`. The big limitation: Streamlit can't do the smooth per-card transitions or the SVG ring animations cleanly. You can get ~70% of the look but not the feel.

If you go this route: copy the color tokens from `app/screens.jsx` into your existing `inject_styles()` in `streamlit_dash.py` and rebuild the metric cards using the same HTML structure.

---

## Path C — Ship the prototype as a static design demo

Drop `prototype/` into the repo and turn on **GitHub Pages** (Settings → Pages → Source: `main` branch, `/prototype` folder). Reviewers get a clickable link without running anything. Useful for your hackathon pitch even if you go with Path A in parallel.

The HTML loads React + Babel from a CDN, so it works on Pages with zero config.

---

## Recommendation

**Do Path C this week** (ship the demo for hackathon judging) **and Path A next week** (real integration). The prototype files don't need to change between the two — only the data source swaps.
