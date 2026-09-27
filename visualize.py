"""
visualize.py
-------------
Renders the account graph with flagged fraud rings highlighted in red
and normal accounts in grey/blue. Saves a PNG so it can be dropped
straight into your PPT / report screenshots.
"""

import os
import matplotlib.pyplot as plt
import networkx as nx

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def plot_fraud_rings(G: nx.DiGraph, community_report, flagged_rings,
                      out_path: str = None, max_nodes_to_label: int = 40):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    out_path = out_path or os.path.join(OUTPUT_DIR, "fraud_ring_graph.png")

    flagged_members = set()
    for members in flagged_rings["members"]:
        flagged_members.update(members)

    undirected = G.to_undirected()
    pos = nx.spring_layout(undirected, seed=42, k=0.4)

    plt.figure(figsize=(12, 9))

    node_colors = []
    node_sizes = []
    for node in undirected.nodes():
        if node in flagged_members:
            node_colors.append("#e74c3c")   # red = flagged fraud ring member
            node_sizes.append(220)
        else:
            node_colors.append("#95a5a6")   # grey = normal account
            node_sizes.append(60)

    nx.draw_networkx_edges(undirected, pos, alpha=0.15, width=0.6)
    nx.draw_networkx_nodes(undirected, pos, node_color=node_colors,
                            node_size=node_sizes, linewidths=0)

    if undirected.number_of_nodes() <= max_nodes_to_label:
        nx.draw_networkx_labels(undirected, pos, font_size=7)
    else:
        flagged_pos = {n: p for n, p in pos.items() if n in flagged_members}
        flagged_labels = {n: n for n in flagged_pos}
        nx.draw_networkx_labels(undirected, flagged_pos, labels=flagged_labels,
                                 font_size=7, font_color="#922b21")

    plt.title(f"Fraud Ring Detection — {len(flagged_rings)} ring(s) flagged "
              f"({len(flagged_members)} accounts)", fontsize=13)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f"[visualize] Saved graph visualization to {out_path}")
    return out_path


if __name__ == "__main__":
    from data_utils import load_transactions
    from graph_builder import build_transaction_graph
    from fraud_detector import (compute_node_features, score_anomalies,
                                 detect_communities, score_communities,
                                 flag_fraud_rings)

    df = load_transactions()
    G = build_transaction_graph(df)
    features = compute_node_features(G)
    anomaly_scores = score_anomalies(features)
    communities = detect_communities(G)
    report = score_communities(G, communities, anomaly_scores)
    rings = flag_fraud_rings(report)
    plot_fraud_rings(G, report, rings)
