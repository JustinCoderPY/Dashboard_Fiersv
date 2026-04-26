# unwind — Burnout Prevention UI prototype

A high-fidelity, interactive prototype for the redesigned Burnout Prevention Dashboard. Built as a single static HTML app — no build step, no install, just open in a browser.

## What's here

```
prototype/
├── unwind.html              # Entry point — open this
├── design-canvas.jsx        # Pan/zoom canvas that hosts all phone frames
├── ios-frame.jsx            # iPhone device chrome (status bar, home indicator)
└── app/
    ├── main.jsx             # Composes the 8 artboards
    ├── screens.jsx          # Intro screen + design tokens (colors, shells)
    ├── quiz.jsx             # Guided one-question-per-card quiz
    └── results.jsx          # Results dashboard (ring, charts, recs)
```

## Run it locally

No npm, no pip — open `prototype/unwind.html` directly in any modern browser.

If your browser blocks Babel from loading `.jsx` over `file://`, serve the folder with Python:

```bash
cd prototype
python3 -m http.server 8000
# then open http://localhost:8000/unwind.html
```

## What you'll see

A pan/zoom canvas with **8 interactive iPhone frames**:

**Full flow** (tap through any of these — they're all live):
1. Landing / intro
2. Guided quiz — start (sleep question)
3. Quiz — mood card (choice list)
4. Quiz — relievers (multi-select chips)
5. Results dashboard

**Risk states** (same dashboard, different inputs):
6. Steady — low risk
7. Watching — medium risk
8. Critical — high risk

## Design system

| Token         | Value          | Use                                  |
|---------------|----------------|--------------------------------------|
| `CREAM`       | `#F6F1E8`      | Page background                      |
| `CREAM_2`     | `#EFE8DA`      | Inset surfaces, tracks               |
| `FOREST`      | `#2A3D34`      | Primary text, primary CTA            |
| `SAGE_DEEP`   | `#3F6B5A`      | Accent, success ring, headings       |
| `SAGE`        | `#7BA98F`      | Healthy-range fills, light accents   |
| `TERRACOTTA`  | `#D98E6B`      | Warnings, overloaded states          |
| `DUSTY`       | `#8FA8C4`      | Sleep, schedule chart fills          |
| `MUTED`       | `#6B7872`      | Helper / caption text                |

**Type**: `Instrument Serif` (italic display, headings) + `Geist` (UI body).
**Radius scale**: 18 / 22 / 24 / 28 — softer than typical web, matches wellness app feel.
**Card surface**: `rgba(255,255,255,0.85)` over the cream bg with a 1px `rgba(42,61,52,0.10)` stroke.

All tokens live at the top of `app/screens.jsx` — change once, propagated everywhere.

## How the burnout score works (in the prototype)

The prototype runs `calculateBurnout()` in `app/results.jsx` purely client-side. It uses the same **shape** as your existing `burnout_backend` (sleep risk, workload pressure, recovery balance, schedule density) but with simplified weights so the demo feels live without a backend.

```
burnout = 0.30·sleepRisk + 0.25·workPressure + 0.22·recoveryRisk
        + 0.18·scheduleDensity + moodAdjustment
```

When you wire it to the real backend (see `INTEGRATION.md`), this function gets replaced with a `fetch('/api/dashboard', ...)` call and the rest of the UI doesn't need to change.

## Charts

All charts are hand-drawn SVG — no chart library:
- **Risk ring** — circular progress, animated stroke-dashoffset
- **Day donut** — 24-hour breakdown with a center label
- **Driver bars** — horizontal bars showing per-area contribution
- **7-day trend** — area + line chart with marked latest point

Light enough to embed inside Streamlit via `components.html()` if you want to keep that route, or drop straight into a React/Next frontend.
