"""
graph_builder.py
-----------------
Converts any flat transaction table into an account-level graph:
    nodes = accounts (sender/origin, receiver/destination)
    edges = transactions between them (weighted by count + total amount)

Supports flexible CSV column auto-detection (PaySim, Custom Bank CSVs, etc.).
"""

import networkx as nx
import pandas as pd
from typing import Tuple


def detect_transaction_columns(df: pd.DataFrame) -> Tuple[str, str, str]:
    """Auto-detect sender, receiver, and amount columns regardless of input CSV schema."""
    cols = list(df.columns)
    cols_lower = [c.lower() for c in cols]

    orig_keywords = ["orig", "sender", "from", "source", "src", "account_from", "user_id", "from_account", "payer"]
    dest_keywords = ["dest", "receiver", "to", "target", "dst", "account_to", "payee", "to_account", "recipient"]
    amt_keywords = ["amount", "amt", "val", "value", "txn_amount", "transaction_amount", "price"]

    orig_col = None
    dest_col = None
    amt_col = None

    # Search for Origin / Sender
    for i, c in enumerate(cols_lower):
        if any(k in c for k in orig_keywords):
            orig_col = cols[i]
            break

    # Search for Destination / Receiver
    for i, c in enumerate(cols_lower):
        if any(k in c for k in dest_keywords):
            dest_col = cols[i]
            break

    # Search for Amount
    for i, c in enumerate(cols_lower):
        if any(k in c for k in amt_keywords):
            amt_col = cols[i]
            break

    # Fallbacks if auto-detect misses
    if not orig_col:
        orig_col = cols[0] if len(cols) > 0 else "nameOrig"
    if not dest_col:
        dest_col = cols[1] if len(cols) > 1 else "nameDest"
    if not amt_col:
        amt_col = cols[2] if len(cols) > 2 else "amount"

    return orig_col, dest_col, amt_col


def build_transaction_graph(df: pd.DataFrame) -> nx.DiGraph:
    """Build a directed, weighted multigraph-like graph of account transfers."""
    G = nx.DiGraph()

    orig_col, dest_col, amt_col = detect_transaction_columns(df)
    print(f"[graph_builder] Using columns -> Sender: '{orig_col}', Receiver: '{dest_col}', Amount: '{amt_col}'")

    for _, row in df.iterrows():
        orig = str(row[orig_col])
        dest = str(row[dest_col])
        
        try:
            amount = float(row[amt_col])
        except (ValueError, KeyError, TypeError):
            amount = 1000.0  # fallback default if non-numeric

        if not G.has_node(orig):
            G.add_node(orig, total_sent=0.0, total_received=0.0, txn_count=0)
        if not G.has_node(dest):
            G.add_node(dest, total_sent=0.0, total_received=0.0, txn_count=0)

        # accumulate node-level stats (used later as ML features)
        G.nodes[orig]["total_sent"] += amount
        G.nodes[orig]["txn_count"] += 1
        G.nodes[dest]["total_received"] += amount
        G.nodes[dest]["txn_count"] += 1

        if G.has_edge(orig, dest):
            G[orig][dest]["weight"] += 1
            G[orig][dest]["amount"] += amount
        else:
            G.add_edge(orig, dest, weight=1, amount=amount)

    return G


def graph_summary(G: nx.DiGraph) -> None:
    print(f"[graph_builder] Nodes (accounts): {G.number_of_nodes()}")
    print(f"[graph_builder] Edges (transaction links): {G.number_of_edges()}")


if __name__ == "__main__":
    from data_utils import load_transactions
    df = load_transactions()
    G = build_transaction_graph(df)
    graph_summary(G)
