# Agentic Fraud Ring Detection — ML Core

Pure ML + graph pipeline for detecting fraud rings (groups of colluding
accounts), no API key or internet connection required.

## What it does

```
Transactions (CSV)
      |
      v
Account Graph (nodes=accounts, edges=transactions)
      |
      v
Node-level ML anomaly scoring  (IsolationForest)
      |
      v
Ring/community detection       (Louvain, networkx)
      |
      v
Composite risk score per community
      |
      v
Flagged fraud rings + graph visualization (PNG) + CSV report
```

## 1. Setup (one time)

```bash
cd fraud_ring_detector
pip install -r requirements.txt
```

Needs Python 3.9+. No API key, no internet needed for this part.

## 2. Get a dataset (optional — demo mode works without this)

**Option A — use the real PaySim dataset (recommended for your submission):**
1. Download "Synthetic Financial Datasets For Fraud Detection" (PaySim) from Kaggle:
   https://www.kaggle.com/datasets/ealaxi/paysim1
2. Place the CSV at: `fraud_ring_detector/data/paysim.csv`
3. Run the pipeline — it will automatically detect and load it.

**Option B — just run it, no download needed:**
If `data/paysim.csv` isn't found, the pipeline auto-generates a
synthetic PaySim-style dataset (4000 transactions, with 4 fraud rings
deliberately injected) so you can demo the whole system immediately.

## 3. Run

```bash
python main.py
```

This will:
- Print a console report (top anomalous accounts, detected communities, flagged rings)
- Save `outputs/fraud_ring_graph.png` — the graph visualization (red = flagged ring members)
- Save `outputs/community_risk_report.csv` — full report for every community, for your report appendix

## 4. Files

| File | Purpose |
|---|---|
| `data_utils.py` | Loads real PaySim CSV, or generates synthetic demo data |
| `graph_builder.py` | Builds the account transaction graph |
| `fraud_detector.py` | IsolationForest anomaly scoring + Louvain ring detection + risk scoring |
| `visualize.py` | Renders the graph, highlighting flagged rings |
| `main.py` | Runs the full pipeline end-to-end |

## 5. Tuning

In `main.py`, `run_pipeline(risk_threshold=0.55)` — lower this (e.g. 0.4)
to flag more communities as suspicious, raise it (e.g. 0.7) to be stricter.

In `fraud_detector.py`, `score_anomalies(contamination=0.1)` controls what
fraction of accounts IsolationForest treats as anomalous outliers.

## 6. Where the LLM/agent layer plugs in (optional, needs API key)

This repo covers the **detection core only** — no LLM needed. If you want
to add the "agentic" explanation layer for your demo (an agent that turns
a flagged ring into a human-readable investigation note and recommended
action), that would call an LLM API (OpenAI/Anthropic/local Ollama model)
on the `outputs/community_risk_report.csv` rows — that's the only place
an API key would come in, and it's entirely optional/separate from this
ML core.
