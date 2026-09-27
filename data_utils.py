"""
data_utils.py
--------------
Loads transaction data for the fraud-ring detection pipeline.

Two modes:
1. REAL DATA: If you have downloaded PaySim (Kaggle: "PaySim1" /
   "Synthetic Financial Datasets For Fraud Detection") as a CSV, place it at
   data/paysim.csv and this script will load it.
2. DEMO MODE: If no CSV is found, we auto-generate a small synthetic
   PaySim-like dataset (with a few injected fraud rings) so the whole
   pipeline can be demoed without any download or internet access.

Columns used (matches PaySim schema):
    step, type, amount, nameOrig, oldbalanceOrg, newbalanceOrig,
    nameDest, oldbalanceDest, newbalanceDest, isFraud
"""

import os
import numpy as np
import pandas as pd

DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "paysim.csv")


def load_transactions(path: str = DATA_PATH, n_synthetic: int = 4000,
                       seed: int = 42) -> pd.DataFrame:
    """Load real PaySim CSV if present, else generate synthetic demo data."""
    if os.path.exists(path):
        print(f"[data_utils] Loading real dataset from {path}")
        df = pd.read_csv(path)
        return df

    print(f"[data_utils] No dataset found at {path}.")
    print("[data_utils] Generating synthetic PaySim-style demo data instead...")
    return _generate_synthetic(n_synthetic, seed)


def _generate_synthetic(n_rows: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    n_normal_accounts = 300
    accounts = [f"C{1000+i}" for i in range(n_normal_accounts)]

    # ---- inject a few "fraud rings": small tight clusters of accounts
    # that transact heavily with each other (classic money-mule pattern) ----
    n_rings = 4
    ring_size = 5
    ring_accounts = []
    for r in range(n_rings):
        ring = [f"R{r}_{i}" for i in range(ring_size)]
        ring_accounts.append(ring)
    all_ring_accounts = [a for ring in ring_accounts for a in ring]

    rows = []
    types = ["PAYMENT", "TRANSFER", "CASH_OUT", "CASH_IN", "DEBIT"]

    # normal, mostly legitimate transactions
    n_normal_txns = int(n_rows * 0.85)
    for i in range(n_normal_txns):
        orig, dest = rng.choice(accounts, size=2, replace=False)
        amount = round(float(rng.lognormal(mean=4.5, sigma=1.2)), 2)
        old_o = round(float(rng.uniform(0, 20000)), 2)
        new_o = max(0.0, round(old_o - amount, 2))
        old_d = round(float(rng.uniform(0, 20000)), 2)
        new_d = round(old_d + amount, 2)
        rows.append([rng.integers(1, 744), rng.choice(types), amount, orig,
                     old_o, new_o, dest, old_d, new_d, 0])

    # fraud-ring transactions: rapid transfers looping within each ring,
    # then a final CASH_OUT to exit the money — this is the pattern
    # the graph + community-detection layer is designed to catch
    n_ring_txns = n_rows - n_normal_txns
    for i in range(n_ring_txns):
        ring = ring_accounts[i % n_rings]
        orig, dest = rng.choice(ring, size=2, replace=False)
        amount = round(float(rng.uniform(8000, 15000)), 2)  # unusually large & uniform
        old_o = round(float(rng.uniform(0, 5000)), 2)
        new_o = 0.0  # ring members empty out balances (classic mule behavior)
        old_d = round(float(rng.uniform(0, 5000)), 2)
        new_d = round(old_d + amount, 2)
        txn_type = "CASH_OUT" if rng.random() < 0.3 else "TRANSFER"
        rows.append([rng.integers(1, 744), txn_type, amount, orig,
                     old_o, new_o, dest, old_d, new_d, 1])

    df = pd.DataFrame(rows, columns=[
        "step", "type", "amount", "nameOrig", "oldbalanceOrg", "newbalanceOrig",
        "nameDest", "oldbalanceDest", "newbalanceDest", "isFraud"
    ])
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = load_transactions()
    print(df.head())
    print(f"\nTotal transactions: {len(df)}")
    print(f"Labeled fraud transactions: {df['isFraud'].sum()}")
