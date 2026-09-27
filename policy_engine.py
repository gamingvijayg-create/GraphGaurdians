"""
policy_engine.py
----------------
Configurable Fraud Policy & Threshold Engine for FRAUDX.
Evaluates configurable rules (Velocity, Shared Device, High Risk Outflow, Risk Threshold)
persisted in SQLite policies table.
"""

import json
from typing import Dict, Any, List
import pandas as pd
import db


def get_active_policies() -> List[Dict[str, Any]]:
    """Fetches enabled policies from SQLite."""
    all_policies = db.fetch_policies()
    return [p for p in all_policies if p["is_enabled"] == 1]


def evaluate_policy_rules(df: pd.DataFrame, anomaly_scores: pd.Series, risk_threshold: float = 0.55) -> Dict[str, Any]:
    """
    Evaluates enabled policies on transactions and anomaly scores.
    Returns triggered policy alerts and rule violations.
    """
    active_rules = get_active_policies()
    rule_results = []
    flagged_accounts = set()

    for rule in active_rules:
        name = rule["rule_name"]
        params = json.loads(rule["parameters_json"]) if isinstance(rule["parameters_json"], str) else rule["parameters_json"]
        triggered = []

        if name == "VelocityRule":
            if "nameOrig" in df.columns:
                counts = df.groupby("nameOrig").size()
                max_txns = params.get("max_txns", 10)
                high_vel = counts[counts > max_txns].index.tolist()
                triggered = high_vel
                flagged_accounts.update(high_vel)

        elif name == "SharedDeviceRule":
            if "device_id" in df.columns and "nameOrig" in df.columns:
                dev_map = df.groupby("device_id")["nameOrig"].nunique()
                max_dev = params.get("max_accounts_per_device", 3)
                suspicious_devices = dev_map[dev_map >= max_dev].index
                suspects = df[df["device_id"].isin(suspicious_devices)]["nameOrig"].unique().tolist()
                triggered = suspects
                flagged_accounts.update(suspects)

        elif name == "HighRiskOutflowRule":
            if "amount" in df.columns and "nameOrig" in df.columns:
                max_amt = params.get("max_amount", 1000000)
                outflows = df[df["amount"] >= max_amt]["nameOrig"].unique().tolist()
                triggered = outflows
                flagged_accounts.update(outflows)

        elif name == "CompositeRiskThresholdRule":
            cutoff = params.get("cutoff_score", risk_threshold)
            high_risk = anomaly_scores[anomaly_scores >= cutoff].index.tolist()
            triggered = high_risk
            flagged_accounts.update(high_risk)

        rule_results.append({
            "rule_id": rule["id"],
            "rule_name": name,
            "category": rule["category"],
            "description": rule["description"],
            "triggered_count": len(triggered),
            "triggered_accounts": triggered[:10]
        })

    return {
        "active_rules_count": len(active_rules),
        "rule_results": rule_results,
        "total_flagged_accounts": list(flagged_accounts)
    }
