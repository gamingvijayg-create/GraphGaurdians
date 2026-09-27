"""
ingestion_pipeline.py
---------------------
Multi-format Data Ingestion & Schema Normalization Pipeline for FRAUDX.
Parses CSV/JSON transaction feeds, validates required columns, enriches with
synthetic hardware fingerprints (Device ID, IP address) for 3D topology graphing,
and persists batch records to SQLite.
"""

import os
import hashlib
import pandas as pd
import db
from graph_builder import detect_transaction_columns


def ingest_transaction_data(file_path_or_df, bank_name: str = "JPMorgan Chase", filename: str = "paysim.csv") -> dict:
    """
    Ingests, normalizes, and enriches transaction datasets.
    """
    if isinstance(file_path_or_df, str):
        df = pd.read_csv(file_path_or_df)
    else:
        df = file_path_or_df.copy()

    # Column Auto-detection
    cols = detect_transaction_columns(df)
    sender_col = cols["sender"]
    receiver_col = cols["receiver"]
    amount_col = cols["amount"]

    # Normalize column names
    df["nameOrig"] = df[sender_col].astype(str)
    df["nameDest"] = df[receiver_col].astype(str)
    df["amount"] = pd.to_numeric(df[amount_col], errors="coerce").fillna(0.0)

    # Enrich with deterministic synthetic Device ID & IP address based on Account ID if missing
    if "device_id" not in df.columns:
        df["device_id"] = df["nameOrig"].apply(lambda acc: f"DEV-{hashlib.md5(acc.encode()).hexdigest()[:6].upper()}")
    if "ip_address" not in df.columns:
        df["ip_address"] = df["nameOrig"].apply(lambda acc: f"192.168.1.{int(hashlib.md5(acc.encode()).hexdigest()[:2], 16) % 254 + 1}")

    # Compute stats
    txn_count = len(df)
    total_volume = float(df["amount"].sum())
    unique_accounts = len(set(df["nameOrig"]).union(set(df["nameDest"])))

    # Persist batch record into SQLite
    batch_id = db.save_batch_and_results(
        bank_name=bank_name,
        filename=filename,
        txn_count=txn_count,
        total_accounts=unique_accounts,
        flagged_rings_count=0,
        total_amount_at_risk=0.0,
        avg_risk_score=0.0
    )

    db.log_audit(
        actor_username="INGESTION_ENGINE",
        actor_role="SYSTEM",
        action_type="DATA_INGESTION",
        target_id=f"BATCH-{batch_id}",
        details_dict={"filename": filename, "txn_count": txn_count, "unique_accounts": unique_accounts, "total_volume": total_volume}
    )

    return {
        "batch_id": batch_id,
        "filename": filename,
        "txn_count": txn_count,
        "unique_accounts": unique_accounts,
        "total_volume": total_volume,
        "dataframe": df
    }
