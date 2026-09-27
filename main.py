"""
main.py
--------
End-to-end pipeline runner. This is the ML "core" of the project:

    Raw transactions
        -> account graph
        -> node-level anomaly scoring (IsolationForest)
        -> community/ring detection (Louvain)
        -> composite risk scoring per community
        -> flagged fraud rings + visualization

Run:
    python main.py

No API key, no internet connection needed -- this part of the system
is pure ML + graph algorithms. (The optional LLM "reasoning agent" that
turns a flagged ring into a plain-English investigation note lives in
llm_explainer.py and is a separate, optional add-on step.)
"""

from data_utils import load_transactions
from graph_builder import build_transaction_graph, graph_summary
from fraud_detector import (
    compute_node_features,
    score_anomalies,
    detect_communities,
    score_communities,
    flag_fraud_rings,
)
from visualize import plot_fraud_rings


def run_pipeline(risk_threshold: float = 0.55):
    print("=" * 60)
    print("AGENTIC FRAUD RING DETECTION -- ML CORE PIPELINE")
    print("=" * 60)

    # 1. Load data
    df = load_transactions()
    print(f"\n[main] Loaded {len(df)} transactions")

    # 2. Build graph
    G = build_transaction_graph(df)
    graph_summary(G)

    # 3. Node-level ML anomaly scoring
    features = compute_node_features(G)
    anomaly_scores = score_anomalies(features)
    print(f"\n[main] Computed anomaly scores for {len(anomaly_scores)} accounts")
    print("Top 5 most anomalous accounts:")
    print(anomaly_scores.sort_values(ascending=False).head())

    # 4. Ring / community detection
    communities = detect_communities(G)
    report = score_communities(G, communities, anomaly_scores)
    print(f"\n[main] Detected {len(communities)} communities total")

    # 5. Flag suspected fraud rings
    rings = flag_fraud_rings(report, threshold=risk_threshold)
    print(f"\n[main] >>> {len(rings)} community(ies) flagged as suspected FRAUD RINGS "
          f"(risk_score >= {risk_threshold}) <<<\n")

    if len(rings) > 0:
        for _, row in rings.iterrows():
            print(f"  Ring #{row['community_id']}: {row['size']} accounts, "
                  f"risk_score={row['risk_score']}, "
                  f"total_amount_moved={row['total_amount_moved']}")
            print(f"    members: {row['members']}")
    else:
        print("  (none above threshold -- try lowering risk_threshold)")

    # 6. Visualization
    plot_fraud_rings(G, report, rings)

    # 7. Save full report as CSV for your PPT / report appendix
    report.to_csv("outputs/community_risk_report.csv", index=False)
    print("\n[main] Full community risk report saved to outputs/community_risk_report.csv")

    return report, rings


if __name__ == "__main__":
    import os
    os.makedirs("outputs", exist_ok=True)
    run_pipeline()
