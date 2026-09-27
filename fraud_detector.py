"""
fraud_detector.py
------------------
The core detection engine. Two signals are combined:

1. NODE-LEVEL ML (IsolationForest, unsupervised anomaly detection)
   -> flags individual accounts with unusual transaction behavior
      (e.g. balance always emptied to zero, very high txn amounts).

2. GRAPH-LEVEL RING DETECTION (Louvain community detection)
   -> groups accounts into communities; a community is flagged as a
      suspected "fraud ring" if it is small, tightly connected, and its
      average node-level anomaly score is high.

Final output: a per-community risk report (this is what downstream
"agents" -- investigation / reasoning / countermeasure -- would consume).
"""

import networkx as nx
import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler


# ---------- Step 1: node-level ML anomaly scoring ----------

def compute_node_features(G: nx.DiGraph) -> pd.DataFrame:
    """Build a feature table, one row per account."""
    rows = []
    for node, data in G.nodes(data=True):
        in_deg = G.in_degree(node)
        out_deg = G.out_degree(node)
        total_sent = data.get("total_sent", 0.0)
        total_received = data.get("total_received", 0.0)
        txn_count = data.get("txn_count", 0)
        avg_txn = (total_sent + total_received) / max(txn_count, 1)
        net_flow = total_received - total_sent

        rows.append({
            "node": node,
            "in_degree": in_deg,
            "out_degree": out_deg,
            "total_sent": total_sent,
            "total_received": total_received,
            "txn_count": txn_count,
            "avg_txn_amount": avg_txn,
            "net_flow": net_flow,
        })
    return pd.DataFrame(rows).set_index("node")


def score_anomalies(features: pd.DataFrame, contamination: float = 0.1) -> pd.Series:
    """Run IsolationForest on account features -> anomaly score per account.

    Higher score = more anomalous (we flip sklearn's convention, where
    lower/negative = more anomalous, so higher is more intuitive here).
    """
    X = features.values
    X_scaled = StandardScaler().fit_transform(X)

    clf = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    clf.fit(X_scaled)

    # decision_function: higher = more normal. We invert so higher = more anomalous.
    raw_scores = clf.decision_function(X_scaled)
    anomaly_score = -raw_scores
    # normalize to 0-1 for easy interpretation
    anomaly_score = (anomaly_score - anomaly_score.min()) / (
        anomaly_score.max() - anomaly_score.min() + 1e-9
    )
    return pd.Series(anomaly_score, index=features.index, name="anomaly_score")


# ---------- Step 2: graph-level community / ring detection ----------

def detect_communities(G: nx.DiGraph):
    """Run Louvain community detection on the undirected view of the graph."""
    undirected = G.to_undirected()
    communities = nx.algorithms.community.louvain_communities(
        undirected, weight="weight", seed=42
    )
    return communities


def score_communities(G: nx.DiGraph, communities, anomaly_scores: pd.Series,
                       max_ring_size: int = 15) -> pd.DataFrame:
    """
    For each community, compute a ring-risk score combining:
      - average member anomaly score
      - internal density (how tightly connected members are to EACH OTHER,
        as opposed to the rest of the network) -- classic mule-ring signature
      - size penalty (very large "communities" are usually just normal
        clusters of everyday users, not rings)
    """
    undirected = G.to_undirected()
    rows = []

    for i, community in enumerate(communities):
        members = list(community)
        size = len(members)

        avg_anomaly = float(anomaly_scores.loc[members].mean())

        # internal density: edges within community / possible edges within community
        subgraph = undirected.subgraph(members)
        possible_edges = size * (size - 1) / 2 if size > 1 else 1
        internal_density = subgraph.number_of_edges() / possible_edges

        # total money volume moved inside this community
        total_amount = sum(
            d.get("amount", 0.0) for _, _, d in subgraph.edges(data=True)
        )

        size_penalty = 1.0 if size <= max_ring_size else max_ring_size / size

        # weighted composite risk score (0-1 range, tunable weights)
        risk_score = (
            0.5 * avg_anomaly +
            0.35 * internal_density +
            0.15 * size_penalty
        )

        rows.append({
            "community_id": i,
            "members": members,
            "size": size,
            "avg_anomaly_score": round(avg_anomaly, 4),
            "internal_density": round(internal_density, 4),
            "total_amount_moved": round(total_amount, 2),
            "risk_score": round(risk_score, 4),
        })

    result = pd.DataFrame(rows).sort_values("risk_score", ascending=False)
    return result.reset_index(drop=True)


def flag_fraud_rings(community_report: pd.DataFrame, threshold: float = 0.55) -> pd.DataFrame:
    """Anything above the risk threshold is reported as a suspected fraud ring."""
    return community_report[community_report["risk_score"] >= threshold].copy()


if __name__ == "__main__":
    from data_utils import load_transactions
    from graph_builder import build_transaction_graph, graph_summary

    df = load_transactions()
    G = build_transaction_graph(df)
    graph_summary(G)

    features = compute_node_features(G)
    anomaly_scores = score_anomalies(features)

    communities = detect_communities(G)
    print(f"[fraud_detector] Detected {len(communities)} communities")

    report = score_communities(G, communities, anomaly_scores)
    print("\nTop 5 riskiest communities:")
    print(report[["community_id", "size", "avg_anomaly_score",
                   "internal_density", "risk_score"]].head())

    rings = flag_fraud_rings(report)
    print(f"\n[fraud_detector] Flagged {len(rings)} suspected fraud ring(s)")
