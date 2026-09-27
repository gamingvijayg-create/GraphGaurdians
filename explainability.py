"""
explainability.py
------------------
Computes per-account feature contribution for IsolationForest anomaly scores.
Helps explain WHY an account was flagged (e.g. high net outflow, high degree ratio, uniform transaction amounts).
"""

import numpy as np
import pandas as pd
from typing import Dict, List


def compute_feature_contributions(features: pd.DataFrame) -> Dict[str, List[str]]:
    """
    Computes normalized feature z-scores across all accounts and extracts
    the top 2-3 most anomalous feature contributors per account.
    
    Returns:
        dict: { account_id: ["High net outflow (+3.2σ)", "Unusually large transfer amount (+2.8σ)", ...] }
    """
    contributions = {}
    
    # Calculate population means and standard deviations
    means = features.mean()
    stds = features.std().replace(0, 1e-6) # avoid zero division
    
    feature_labels = {
        "in_degree": ("High incoming link degree", "Low incoming link degree"),
        "out_degree": ("High outgoing fan-out degree", "Low outgoing degree"),
        "total_sent": ("Unusually high total sent volume", "Low sent volume"),
        "total_received": ("Unusually high total received volume", "Low received volume"),
        "txn_count": ("High transaction velocity", "Low transaction velocity"),
        "avg_txn_amount": ("Unusually high average transfer amount", "Low average transfer amount"),
        "net_flow": ("High net inflow imbalance", "High net outflow imbalance"),
    }

    for account in features.index:
        row = features.loc[account]
        z_scores = (row - means) / stds
        
        # Rank features by absolute magnitude of z-score
        abs_z = z_scores.abs().sort_values(ascending=False)
        top_reasons = []

        for feat_name in abs_z.index[:3]:
            z_val = z_scores[feat_name]
            val = row[feat_name]
            
            if abs(z_val) < 0.5:
                continue

            pos_label, neg_label = feature_labels.get(feat_name, (feat_name, feat_name))
            
            if feat_name == "net_flow":
                label = pos_label if z_val > 0 else neg_label
            else:
                label = pos_label if z_val > 0 else neg_label

            top_reasons.append(f"{label} ({z_val:+.1f}σ, val={val:,.2f})")

        if not top_reasons:
            top_reasons = ["Behavioral outlier across composite transaction metrics"]

        contributions[str(account)] = top_reasons

    return contributions


def get_account_hover_summary(account: str, contributions: Dict[str, List[str]], anomaly_score: float) -> str:
    """Formats top reasons for graph hover tooltips and UI inspection."""
    reasons = contributions.get(str(account), ["Behavioral outlier"])
    reasons_str = "<br>• ".join(reasons)
    return f"Anomaly Score: {anomaly_score:.4f}<br>Top Reasons:<br>• {reasons_str}"
