# HelioGuard

**Space Weather & GPS Drift Risk Tracker** — a live Streamlit dashboard that
monitors solar and geomagnetic activity and translates it into operational
risk guidance for GPS/GNSS users and LEO satellite operators.

HelioGuard pulls real telemetry from **NASA DONKI** (solar flare events) and
**NOAA SWPC** (planetary K index), scores the resulting ionospheric and
thermospheric risk, and presents it as headline metrics, a Kp time series, a
sector-specific impact playbook, and an interactive what-if storm simulator.

> **Advisory only.** HelioGuard is an informational monitoring aid. It is not
> certified for flight authorisation, and no operator should use it as the sole
> basis for a go/no-go decision.

---

## Features

| Capability | Detail |
| --- | --- |
| Live flare telemetry | Latest and strongest recent GOES flare class, active-event table |
| Kp time series | Last 100 readings with a Kp 5.0 storm threshold line and shaded storm band |
| GPS drift risk | LOW / MODERATE / HIGH-CRITICAL bands with drift magnitude and actions |
| LEO drag risk | 1–100 score blending flare energy injection with ambient Kp |
| Sector playbook | Guidance for drone pilots, precision farmers, aviation and grid operators |
| Storm simulator | Persistent 0–9 Kp slider for what-if GPS and LEO risk assessment |
| Resilient data layer | Per-source timeout, retry-free fallback and offline degradation notices |

### Dashboard tabs

1. **Solar Flare Telemetry** — recent flare events and class distribution.
2. **GPS & Industry Impact** — risk banding plus the sector-by-sector playbook.
3. **Storm Simulator (What-If Analysis)** — a sandbox slider that answers
   *"what would this look like at Kp 7?"* without touching the live banner.

The simulator is deliberately sandboxed: it never changes the live alert
banner, so a what-if reading can never be mistaken for a real event.

---

## Quick start

Requires Python 3.10 or newer (the code uses PEP 604 `X | Y` annotations).

```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# 3. Run the dashboard
python -m streamlit run app.py
```

Then open **<http://localhost:8501>**.

> On Windows, if PowerShell blocks activation, either run
> `Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned` once per
> session, or skip activation and call the interpreter directly as
> `.\.venv\Scripts\python.exe -m streamlit run app.py`.

To serve on a different port:

```powershell
python -m streamlit run app.py --server.port 8502
```

---

## Data sources

| Source | Endpoint | Used for |
| --- | --- | --- |
| NASA DONKI | `https://ccmc.gsfc.nasa.gov/DONKI-API/get/FLR` | Recent solar flare events |
| NASA DONKI (legacy) | `https://api.nasa.gov/DONKI/FLR` | Fallback if the primary is unavailable |
| NOAA SWPC | `https://services.swpc.noaa.gov/json/planetary_k_index_1m.json` | Planetary K index (1-minute cadence) |

All three endpoints are public and require no API key. Responses are cached for
five minutes (`CACHE_TTL_SECONDS = 300`) to stay well inside upstream rate
limits; use the sidebar refresh or reload the page to pull sooner.

> **Note on the DONKI URL.** The long-documented
> `https://api.nasa.gov/DONKI/FLR` endpoint now returns an HTML page rather than
> JSON. HelioGuard therefore treats `ccmc.gsfc.nasa.gov` as primary and keeps the
> old URL purely as a fallback.

### Offline behaviour

HelioGuard is built to fail safely rather than confidently:

- Every request has a 15-second timeout.
- A transport error, non-200 status or malformed body degrades that single
  panel to an empty typed DataFrame instead of raising.
- A **zero-row** result is also treated as a failure, because both feeds
  republish continuously — a blank panel means "unverified", not "quiet".
- When one or both feeds are unavailable, a banner reading
  `Using offline fallback mode...` names the affected sources, and every
  Kp-derived figure is rendered as `UNAVAILABLE` with operational guidance
  withheld. The dashboard never presents a stale or missing feed as a safe
  reading.

---

## Risk methodology

Both risk models are deterministic, dependency-free pure functions, so they are
straightforward to test and audit.

### GPS drift risk — `calculate_gps_drift_risk(kp_value)`

| Kp | Level | Indicative drift | Action |
| --- | --- | --- | --- |
| 0 – 3 | LOW | 0–1 m | Nominal ops; safe for precision drone and RTK AGV work |
| 4 – 5 | MODERATE | 2–5 m | Recalibrate RTK sensors; monitor GPS drift |
| 6 – 9 | HIGH / CRITICAL | 5–15+ m | Pause autonomous navigation |

### LEO atmospheric drag risk — `calculate_satellite_risk(flare_class, kp_value)`

Scored 1–100 as `0.65 × flare_factor + 0.35 × (Kp / 9)`. Flare class is the
energy-injection driver and Kp is the ambient geomagnetic state that modulates
thermospheric heating, so the two are blended.

The flare factor maps GOES X-ray flux onto a normalised scale. Flux is
logarithmic, and the C/M/X bands are contiguous decades:

| Class | Flux (W/m²) | Typical factor |
| --- | --- | --- |
| C1.0 – C9.9 | 1e-6 – 1e-5 | 0.00 – 0.11 |
| M1.0 – M9.9 | 1e-5 – 1e-4 | 0.11 – 0.44 |
| X1.0 – X10 | 1e-4 – 1e-3 | 0.44 – 1.00 |

Because the band offsets are contiguous, C9.9 and M1.0 score almost identically,
as their physical fluxes dictate. The normalised flux is squared
(`FLARE_CURVE = 2.0`) to reflect the superlinear thermospheric response to X-ray
energy injection.

| Score | Level |
| --- | --- |
| 1 – 33 | LOW |
| 34 – 66 | MODERATE |
| 67 – 100 | HIGH |

---

## Project structure

```
HelioGuard-webproj/
├── app.py                  # Entire application: data layer, risk models, UI
├── requirements.txt        # Runtime dependencies
├── .streamlit/
│   └── config.toml         # Dark theme (GitHub-inspired palette) + defaults
├── .gitignore
└── README.md
```

`app.py` is organised in clearly separated sections:

| Section | Contents |
| --- | --- |
| Metadata & theme | App identity and the colour constants shared with Plotly |
| Data layer | `_get_json`, `fetch_solar_flares`, `fetch_kp_index`, `_record_source_status` |
| Risk models | `_clamp`, `_clean_kp`, `_flare_factor`, `calculate_gps_drift_risk`, `calculate_satellite_risk` |
| Presentation | Metric cards, alert banner, offline notice, Kp chart, tab renderers |
| Shell | `configure_page`, `inject_custom_css`, `render_header`, `render_footer`, `main` |

---

## Theming

The dark palette is set in `.streamlit/config.toml`, because Streamlit only
accepts theme settings through configuration rather than `st.set_page_config`:

| Setting | Value |
| --- | --- |
| `backgroundColor` | `#0E1117` |
| `secondaryBackgroundColor` | `#161B22` |
| `textColor` | `#FAFAFA` |
| `primaryColor` | `#4FC3F7` |

`app.py` mirrors these colours in its own constants so custom CSS and Plotly
figures match the native theme. Risk states use `#00C853` (green), `#FFA000`
(orange) and `#FF1744` (red), chosen for contrast against the dark base.

---

## Verification

The dashboard is exercised with Streamlit's `AppTest` harness, which renders
the script headlessly and asserts on the resulting element tree:

```powershell
.\.venv\Scripts\python.exe -m pyflakes app.py
.\.venv\Scripts\python.exe -m py_compile app.py
```

The test matrix covers the healthy render path, theme colours, a simulated
total transport outage, a partial single-source outage, offline-flag recovery,
hostile payloads (nested values, scalar lists) that previously crashed
normalisation, and cache TTL wiring.

---

## Requirements

```
streamlit>=1.40
requests>=2.32
pandas>=2.2.3
plotly>=5.24.1
folium>=0.18.0
```

## License

Provided as-is for research, education and operational awareness. Not for
regulated decision-making.