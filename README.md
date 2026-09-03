# Maintora: Predictive Maintenance Intelligence Platform

Maintora watches your machine sensors and flags issues before they fail:

> **Pump #3 Failure Risk: 87%, Recommended Maintenance within 7 days**

👉 **[Live Demo](https://maintora-olive.vercel.app/)**

| Fleet Overview | ML Analytics |
| :---: | :---: |
| <img src="https://github.com/user-attachments/assets/48a72b3c-720c-443a-be22-98401827f01f" alt="Maintora Overview" width="100%" /> | <img src="https://github.com/user-attachments/assets/ad662304-c98d-4ed9-b130-9c11988fdceb" alt="Maintora Analytics" width="100%" /> |

---

## The problem

Most facilities (hospitals, malls, factories, hotels, universities) run maintenance reactively, fix it after it fails. That means unplanned downtime, emergency repair costs, and safety risk on equipment like elevators, HVAC units, pumps, and generators.

Maintora makes maintenance predictive instead: feed it sensor readings, and it tells you how likely a failure is, how much life a machine has left, whether current behavior is abnormal, and where key readings are trending before anything breaks.

**Who it's for:** facility and maintenance managers who need an early-warning system. The dashboard is split into two views, a **plain-language Overview** for day-to-day fleet monitoring, and a deeper **Analytics** view for anyone who wants to see the model output directly.

---

## What it actually does

| Capability | Question it answers | Technique | Trained on | Benchmark Metric (F1 / RMSE) |
|---|---|---|---|---|
| **Failure classification** | Will this machine fail, and how? | XGBoost (binary + multi-class) | AI4I 2020 | F1 (binary): 0.45 · Macro F1 (multi-class): 0.85 |
| **Remaining useful life (RUL)** | How many cycles/days until failure? | XGBoost + LSTM ensemble | NASA C-MAPSS (FD001) | RMSE: 14.4 cycles |
| **Anomaly detection** | Is this reading abnormal right now? | Isolation Forest + Autoencoder | AI4I 2020 | F1: 0.16 |
| **Sensor forecasting** | Where is this sensor trending next? | Rolling-window features + LSTM | NASA C-MAPSS (FD001) | RMSE: 0.11 (normalized) |

Both datasets are public, well-known benchmarks in predictive maintenance research (UCI's AI4I 2020 set, and NASA's C-MAPSS turbofan degradation simulation), which keeps the modeling choices defensible and reproducible rather than tuned to one arbitrary dataset.

Every prediction returns both a number and a decision.

### Bring-your-own-data

You don't need to use the demo datasets. Every analytics tab has an upload box that accepts a `.csv`, `.xlsx`, or raw sensor export. The API tries to auto-detect whether it looks like machine-process data (temperature/torque/speed-shaped) or a sensor time series, then applies a flexible column mapper for common sensor field names (e.g. temperature, torque, vibration) to line your columns up with what the model expects.

---

## How it's built

```
┌─────────────┐      HTTP/JSON       ┌──────────────┐      loads      ┌──────────────────┐
│   React      │ ───────────────────▶│   FastAPI     │────────────────▶│   ml/artifacts    │
│   frontend   │◀─────────────────── │   backend     │◀─────────────── │  (trained models) │
└─────────────┘                      └──────────────┘                 └──────────────────┘
```

- **`ml/`**: training pipeline (feature engineering, model training, evaluation) for all four tasks, and the resulting trained artifacts (`.joblib` for XGBoost/scikit-learn, `.pt` for PyTorch state dicts).
- **`backend/`**: FastAPI service that loads those artifacts once at startup and exposes them as `/predict/*` endpoints, plus `/assets` for fleet data and `/upload/parse` for user-supplied files.
- **`frontend/`**: React + TypeScript + Tailwind dashboard: an Overview page for fleet-wide health, and an Analytics page with one tab per ML capability.
- **`data/`**: raw and processed versions of the two source datasets, used to reproduce training.

**Why this stack:** XGBoost for the tabular/structured tasks (classification, regression) because gradient-boosted trees are the standard for tabular data and are fast enough to serve in real time; LSTMs for the sequence tasks (RUL, forecasting) because they capture degradation trends over time that a tree model would miss; FastAPI for a typed, self-documenting API (`/docs` is auto-generated); React/Tailwind for a dashboard that reads as a real product rather than a notebook.

---

## Running it locally

**With Docker:**
```bash
docker compose up --build
```
Frontend: `http://localhost:5173` · Backend: `http://localhost:8000` · API docs: `http://localhost:8000/docs`

**Without Docker:**
```bash
# backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

# frontend (separate terminal)
cd frontend
npm install
npm run dev
```

Copy `.env.example` to `.env` first in both cases if you need to change ports or the artifacts path.

---

## Project layout

```
backend/     FastAPI app: routers, services, schemas
frontend/    React dashboard: Overview + Analytics views
ml/          training pipeline + trained model artifacts
data/        raw + processed datasets
docs/        architecture notes, model cards, design decisions
```

---

## License

MIT - see [LICENSE](./LICENSE).
