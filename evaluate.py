"""
evaluate.py
-----------
Evaluates the accuracy, precision, recall, and F1-score of the
Fraud Ring Detection pipeline against ground truth labels (isFraud).
"""

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

from data_utils import load_transactions
from graph_builder import build_transaction_graph
from fraud_detector import (
    compute_node_features,
    score_anomalies,
    detect_communities,
    score_communities,
    flag_fraud_rings,
)


def evaluate_pipeline(risk_threshold: float = 0.55):
    print("=" * 60)
    print("EVALUATING FRAUD RING DETECTOR ACCURACY & METRICS")
    print("=" * 60)

    # 1. Load Data
    df = load_transactions()

    # 2. Derive Ground Truth per Account
    # An account is truly fraud if involved in any isFraud == 1 transaction
    fraud_orig = set(df[df["isFraud"] == 1]["nameOrig"])
    fraud_dest = set(df[df["isFraud"] == 1]["nameDest"])
    true_fraud_accounts = fraud_orig.union(fraud_dest)

    all_accounts = set(df["nameOrig"]).union(set(df["nameDest"]))
    
    y_true = pd.Series(index=list(all_accounts), data=0)
    for acc in true_fraud_accounts:
        if acc in y_true.index:
            y_true[acc] = 1

    # 3. Run ML Pipeline
    G = build_transaction_graph(df)
    features = compute_node_features(G)
    anomaly_scores = score_anomalies(features)
    communities = detect_communities(G)
    report = score_communities(G, communities, anomaly_scores)
    flagged_rings = flag_fraud_rings(report, threshold=risk_threshold)

    # 4. Predict Fraud Accounts from Flagged Rings
    flagged_members = set()
    for members in flagged_rings["members"]:
        flagged_members.update(members)

    y_pred = pd.Series(index=list(all_accounts), data=0)
    for acc in flagged_members:
        if acc in y_pred.index:
            y_pred[acc] = 1

    # Ensure index alignment
    y_true = y_true.sort_index()
    y_pred = y_pred.sort_index()
    node_scores = anomaly_scores.reindex(y_true.index).fillna(0)

    # 5. Compute Metrics
    acc = accuracy_score(y_true, y_pred)
    prec = precision_score(y_true, y_pred, zero_division=0)
    rec = recall_score(y_true, y_pred, zero_division=0)
    f1 = f1_score(y_true, y_pred, zero_division=0)
    auc = roc_auc_score(y_true, node_scores)

    print("\n--- ACCOUNT-LEVEL EVALUATION RESULTS ---")
    print(f"Total Accounts Evaluated : {len(all_accounts)}")
    print(f"True Fraud Accounts      : {y_true.sum()}")
    print(f"Predicted Fraud Accounts : {y_pred.sum()}")
    print("-" * 40)
    print(f"Accuracy                 : {acc * 100:.2f}%")
    print(f"Precision                : {prec * 100:.2f}%")
    print(f"Recall                   : {rec * 100:.2f}%")
    print(f"F1 Score                 : {f1 * 100:.2f}%")
    print(f"ROC-AUC Score (Anomaly)  : {auc:.4f}")
    print("-" * 40)

    print("\nClassification Report:")
    print(classification_report(y_true, y_pred, target_names=["Legitimate", "Fraud Ring Member"]))

    return {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1_score": f1,
        "roc_auc": auc,
    }


if __name__ == "__main__":
    evaluate_pipeline()
