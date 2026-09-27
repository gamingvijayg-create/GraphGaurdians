"""
🛡️ GraphGuardians - Multi-Page Enterprise Agentic Fraud Ring Detection & Countermeasure Engine

Full Agentic Pipeline:
- Step 0: Real SQLite User Authentication
- Page 1: Guide & Input Dataset Upload Setup (Custom CSV file uploader + Schema detection + Data summary preview)
- Page 2: Dual 3D/2D Graph Topology + Multi-Agent Reasoning + Dynamic Account Freeze Controls
  - Top KPI Strip: Total Amount Scammed & Accounts To Freeze (Computed from user input dataset)
  - Clear Dual Graph Views: 3D Fiber-Optic Wire Connections + 2D High-Contrast Interactive Node-Edge Graph
  - Agent Actions Panel: Freeze target accounts in the user's uploaded dataset, human override (Approve/Reverse), SAR downloads, CSV export
- Page 3: About Team & SQLite Audit Trail Logs
"""

import os
import re
import time
import json
import numpy as np
import pandas as pd
import networkx as nx
import plotly.graph_objects as go
import streamlit as st
import importlib

# Backend Modules
from data_utils import load_transactions
from graph_builder import build_transaction_graph, detect_transaction_columns
from explainability import get_account_hover_summary
import agents
import countermeasures
import db
importlib.reload(db)  # Ensure fresh module reload

# ---------------------------------------------------------------------------
# STREAMLIT PAGE CONFIG & TVA SACRED TIMELINE STYLES
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="GraphGuardians - Agentic Fraud Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">

<style>
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }

    .stApp {
        background-color: #0c0a09;
        color: #f5f5f4;
    }

    .bank-header {
        background: linear-gradient(135deg, #1c1917, #292524);
        border: 1px solid #d97706;
        border-radius: 12px;
        padding: 16px 24px;
        margin-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 0 20px rgba(217, 119, 6, 0.15);
    }
    .bank-title {
        font-size: 1.6rem;
        font-weight: 800;
        color: #f59e0b;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .bank-badge {
        background-color: #292524;
        color: #f59e0b;
        padding: 6px 14px;
        border-radius: 8px;
        border: 1px solid #78350f;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.88rem;
    }

    .login-portal {
        max-width: 440px;
        margin: 40px auto;
        background: #1c1917;
        border: 1px solid #d97706;
        border-radius: 16px;
        padding: 36px;
        box-shadow: 0 0 35px rgba(217, 119, 6, 0.25);
    }
    .login-portal-title {
        font-size: 2.1rem;
        font-weight: 800;
        color: #f59e0b;
        text-align: center;
        margin-bottom: 6px;
    }
    .login-portal-sub {
        font-size: 0.88rem;
        color: #a8a29e;
        text-align: center;
        margin-bottom: 24px;
    }

    .guide-card {
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 16px;
    }
    .step-number {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 1.5rem;
        font-weight: 700;
        color: #f59e0b;
        margin-bottom: 8px;
    }
    .step-title {
        font-size: 1.1rem;
        font-weight: 700;
        color: #f5f5f4;
        margin-bottom: 6px;
    }
    .step-desc {
        font-size: 0.9rem;
        color: #a8a29e;
        line-height: 1.5;
    }

    .tva-kpi-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 20px;
    }
    .tva-kpi-card {
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 10px;
        padding: 18px;
    }
    .tva-kpi-label {
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.78rem;
        color: #a8a29e;
        text-transform: uppercase;
        margin-bottom: 6px;
    }
    .tva-kpi-value {
        font-size: 2rem;
        font-weight: 800;
        color: #f59e0b;
        margin: 0;
    }
    .tva-kpi-value.danger { color: #ef4444; }

    .tier-badge {
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 800;
        font-size: 0.8rem;
        font-family: 'Share Tech Mono', monospace !important;
    }
    .tier-CRITICAL { background: #ef4444; color: #ffffff; }
    .tier-HIGH { background: #f97316; color: #ffffff; }
    .tier-MEDIUM { background: #eab308; color: #0c0a09; }
    .tier-LOW { background: #10b981; color: #ffffff; }

    .agent-action-card {
        background: #1c1917;
        border: 1px solid #44403c;
        border-radius: 10px;
        padding: 16px;
        margin-bottom: 14px;
    }

    .db-badge {
        background: #064e3b;
        color: #34d399;
        border: 1px solid #059669;
        padding: 6px 12px;
        border-radius: 6px;
        font-family: 'Share Tech Mono', monospace !important;
        font-size: 0.85rem;
        margin-bottom: 16px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# SESSION ROUTER INITIALIZATION
# ---------------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "login"
if "user_api_key" not in st.session_state:
    st.session_state["user_api_key"] = ""
if "uploaded_df" not in st.session_state:
    st.session_state["uploaded_df"] = None

# ---------------------------------------------------------------------------
# STEP 0: REAL USER AUTHENTICATION GATE
# ---------------------------------------------------------------------------
if not st.session_state["logged_in"]:
    st.markdown("""
    <div class="login-portal">
        <div class="login-portal-title">🛡️ GraphGuardians</div>
        <div class="login-portal-sub">Agentic Fraud Operations Command Portal</div>
    </div>
    """, unsafe_allow_html=True)

    col_l1, col_l2, col_l3 = st.columns([1, 2, 1])
    with col_l2:
        with st.form("real_auth_form"):
            st.markdown("##### 🔑 Officer Authentication")
            username_input = st.text_input("Username", value="admin")
            password_input = st.text_input("Password", type="password", value="admin123")
            
            login_submit = st.form_submit_button("🔓 Sign In to SOC Portal", type="primary", use_container_width=True)

            if login_submit:
                user_record = db.authenticate_user(username_input, password_input)
                if user_record:
                    st.session_state["logged_in"] = True
                    st.session_state["user_info"] = user_record
                    st.session_state["current_page"] = "page1"

                    # Save login session
                    db.save_login(user_record["bank_name"], user_record["username"], user_record["officer_email"])

                    st.success(f"Authenticated as {user_record['username']} ({user_record['role']})")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("⚠️ Invalid username or password. (Demo credentials -> admin / admin123)")
        st.info("💡 **Demo Credentials**: Username: `admin` | Password: `admin123`")
    st.stop()


# ---------------------------------------------------------------------------
# TOP BANKING HEADER & NAVIGATION BAR
# ---------------------------------------------------------------------------
user_info = st.session_state.get("user_info") or {"bank_name": "GraphGuardians Bank", "username": "admin", "role": "Security Officer"}
st.markdown(f"""
<div class="bank-header">
    <div>
        <div class="bank-title">🛡️ GraphGuardians SOC &middot; {user_info['bank_name']}</div>
        <div style="color:#a8a29e; font-size:0.85rem; margin-top:2px;">Agentic Fraud Ring Detection & Countermeasure Engine</div>
    </div>
    <div class="bank-badge">
        👤 Officer: {user_info['username']} ({user_info['role']})
    </div>
</div>
""", unsafe_allow_html=True)

# Page Router Navigation
col_nav1, col_nav2, col_nav3, col_nav4 = st.columns([1, 1, 1, 1])

with col_nav1:
    if st.button("📌 Page 1: Guide & Input Setup", use_container_width=True, type="primary" if st.session_state["current_page"] == "page1" else "secondary"):
        st.session_state["current_page"] = "page1"
        st.rerun()

with col_nav2:
    if st.button("📊 Page 2: Agent Dashboard", use_container_width=True, type="primary" if st.session_state["current_page"] == "page2" else "secondary"):
        st.session_state["current_page"] = "page2"
        st.rerun()

with col_nav3:
    if st.button("👥 Page 3: About & Audit", use_container_width=True, type="primary" if st.session_state["current_page"] == "page3" else "secondary"):
        st.session_state["current_page"] = "page3"
        st.rerun()

with col_nav4:
    if st.button("🚪 Logout Portal", use_container_width=True):
        st.session_state["logged_in"] = False
        st.session_state["current_page"] = "login"
        st.rerun()

st.markdown("<hr style='border-color:#44403c; margin:16px 0 24px 0;'>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# GRAPH RENDERERS (CLEAR 3D WIRE VIEW & CLEAR 2D HIGH-CONTRAST VIEW)
# ---------------------------------------------------------------------------
def render_wire_3d_graph(G: nx.DiGraph, flagged_members: set, anomaly_scores: pd.Series, feature_contributions: dict, title: str = "3D Network Graph", only_fraud: bool = False):
    """Renders 3D Plotly network graph with crisp, glowing wire/circuit connections."""
    
    graph_to_render = G
    if only_fraud and len(flagged_members) > 0:
        graph_to_render = G.subgraph(flagged_members)

    if len(graph_to_render.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title=title, paper_bgcolor='#0c0a09', plot_bgcolor='#0c0a09', height=420)
        return fig

    # Compute 3D Spring Layout with wide node separation
    undirected = graph_to_render.to_undirected()
    pos_3d = nx.spring_layout(undirected, dim=3, seed=42, k=2.5, iterations=120)

    # Crisp Wire Connections
    edge_x, edge_y, edge_z = [], [], []
    for u, v in graph_to_render.edges():
        x0, y0, z0 = pos_3d[u]
        x1, y1, z1 = pos_3d[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])

    edge_color = 'rgba(244, 63, 94, 0.85)' if only_fraud else 'rgba(245, 158, 11, 0.55)'
    edge_width = 3.5 if only_fraud else 2.2

    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        line=dict(width=edge_width, color=edge_color),
        hoverinfo='none',
        mode='lines',
        name='Transaction Wires'
    )

    fraud_x, fraud_y, fraud_z, fraud_txt = [], [], [], []
    normal_x, normal_y, normal_z, normal_txt = [], [], [], []

    for node in graph_to_render.nodes():
        x, y, z = pos_3d[node]
        score = float(anomaly_scores.get(node, 0.0))
        hover_html = get_account_hover_summary(node, feature_contributions, score)

        if node in flagged_members:
            fraud_x.append(x); fraud_y.append(y); fraud_z.append(z); fraud_txt.append(f"<b>Account: {node}</b><br>{hover_html}")
        else:
            normal_x.append(x); normal_y.append(y); normal_z.append(z); normal_txt.append(f"<b>Account: {node}</b><br>{hover_html}")

    data_traces = [edge_trace]

    if len(normal_x) > 0 and not only_fraud:
        normal_trace = go.Scatter3d(
            x=normal_x, y=normal_y, z=normal_z, mode='markers', name='👤 Normal Timeline Account',
            hoverinfo='text', hovertext=normal_txt,
            marker=dict(size=6, color='#38bdf8', symbol='circle', opacity=0.85)
        )
        data_traces.append(normal_trace)

    if len(fraud_x) > 0:
        fraud_trace = go.Scatter3d(
            x=fraud_x, y=fraud_y, z=fraud_z, mode='markers', name='🚨 Fraud Ring Account',
            hoverinfo='text', hovertext=fraud_txt,
            marker=dict(size=13, color='#ef4444', symbol='diamond', line=dict(width=2, color='#ffffff'))
        )
        data_traces.append(fraud_trace)

    fig = go.Figure(
        data=data_traces,
        layout=go.Layout(
            title=dict(text=title, font=dict(size=18, color='#f8fafc')),
            showlegend=True,
            legend=dict(
                font=dict(color='#e2e8f0'),
                bgcolor='rgba(15, 23, 42, 0.85)',
                bordercolor='#334155',
                borderwidth=1,
                x=0.01, y=0.99
            ),
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor='#0c0a09',
            plot_bgcolor='#0c0a09',
            scene=dict(
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                bgcolor='#0c0a09',
                camera=dict(eye=dict(x=1.7, y=1.7, z=1.4))
            ),
            height=580
        )
    )
    return fig


def render_wire_2d_graph(G: nx.DiGraph, flagged_members: set, anomaly_scores: pd.Series, feature_contributions: dict, title: str = "2D High-Contrast Network Graph", only_fraud: bool = False):
    """Renders 2D Plotly network graph with explicit account node labels and crisp connection lines."""
    
    graph_to_render = G
    if only_fraud and len(flagged_members) > 0:
        graph_to_render = G.subgraph(flagged_members)

    if len(graph_to_render.nodes) == 0:
        fig = go.Figure()
        fig.update_layout(title=title, paper_bgcolor='#0c0a09', plot_bgcolor='#0c0a09', height=420)
        return fig

    undirected = graph_to_render.to_undirected()
    pos_2d = nx.spring_layout(undirected, seed=42, k=0.6, iterations=100)

    edge_x, edge_y = [], []
    for u, v in graph_to_render.edges():
        x0, y0 = pos_2d[u]
        x1, y1 = pos_2d[v]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_color = 'rgba(244, 63, 94, 0.85)' if only_fraud else 'rgba(245, 158, 11, 0.55)'
    edge_width = 3.0 if only_fraud else 1.8

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=edge_width, color=edge_color),
        hoverinfo='none',
        mode='lines',
        name='Transaction Connections'
    )

    normal_nodes = [n for n in graph_to_render.nodes() if n not in flagged_members]
    fraud_nodes = [n for n in graph_to_render.nodes() if n in flagged_members]

    data_traces = [edge_trace]

    if normal_nodes and not only_fraud:
        nx_norm = [pos_2d[n][0] for n in normal_nodes]
        ny_norm = [pos_2d[n][1] for n in normal_nodes]
        txt_norm = [f"<b>Account: {n}</b><br>{get_account_hover_summary(n, feature_contributions, float(anomaly_scores.get(n, 0.0)))}" for n in normal_nodes]
        labels_norm = [str(n) if len(graph_to_render.nodes) <= 60 else "" for n in normal_nodes]

        normal_trace = go.Scatter(
            x=nx_norm, y=ny_norm, mode='markers+text', name='👤 Normal Account',
            hoverinfo='text', hovertext=txt_norm,
            text=labels_norm, textposition="top center",
            textfont=dict(color="#94a3b8", size=9),
            marker=dict(size=11, color='#38bdf8', symbol='circle', line=dict(width=1.5, color='#0284c7'))
        )
        data_traces.append(normal_trace)

    if fraud_nodes:
        fx_fraud = [pos_2d[n][0] for n in fraud_nodes]
        fy_fraud = [pos_2d[n][1] for n in fraud_nodes]
        txt_fraud = [f"<b>Account: {n}</b><br>{get_account_hover_summary(n, feature_contributions, float(anomaly_scores.get(n, 0.0)))}" for n in fraud_nodes]
        labels_fraud = [str(n) for n in fraud_nodes]

        fraud_trace = go.Scatter(
            x=fx_fraud, y=fy_fraud, mode='markers+text', name='🚨 Fraud Ring Account',
            hoverinfo='text', hovertext=txt_fraud,
            text=labels_fraud, textposition="top center",
            textfont=dict(color="#f87171", size=11, family="Share Tech Mono"),
            marker=dict(size=18, color='#ef4444', symbol='diamond', line=dict(width=2, color='#ffffff'))
        )
        data_traces.append(fraud_trace)

    fig = go.Figure(
        data=data_traces,
        layout=go.Layout(
            title=dict(text=title, font=dict(size=18, color='#f8fafc')),
            showlegend=True,
            legend=dict(
                font=dict(color='#e2e8f0'),
                bgcolor='rgba(15, 23, 42, 0.85)',
                bordercolor='#334155',
                borderwidth=1,
                x=0.01, y=0.99
            ),
            margin=dict(l=20, r=20, b=20, t=50),
            paper_bgcolor='#0c0a09',
            plot_bgcolor='#0c0a09',
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            height=580
        )
    )
    return fig


# ===========================================================================
# PAGE 1 — LANDING & INPUT DATASET SETUP PAGE
# ===========================================================================
if st.session_state["current_page"] == "page1":
    st.markdown("### 📘 Welcome to GraphGuardians Agentic Fraud Engine")
    st.markdown("Multi-agent system: **DetectorAgent** $\\rightarrow$ **InvestigatorAgent** $\\rightarrow$ **CountermeasureAgent**.")

    g1, g2 = st.columns(2)
    with g1:
        st.markdown("""
        <div class="guide-card">
            <div class="step-number">01 / STEP</div>
            <div class="step-title">📤 Input Your Dataset (User CSV Upload)</div>
            <div class="step-desc">Upload any financial bank transaction CSV dataset. The system auto-detects sender, receiver, and amount columns.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="guide-card">
            <div class="step-number">03 / STEP</div>
            <div class="step-title">🤖 InvestigatorAgent & Risk Tiers</div>
            <div class="step-desc">Classifies risk severity into tiers (CRITICAL, HIGH, MEDIUM, LOW) with structured feature contribution explanations.</div>
        </div>
        """, unsafe_allow_html=True)

    with g2:
        st.markdown("""
        <div class="guide-card">
            <div class="step-number">02 / STEP</div>
            <div class="step-title">🌲 DetectorAgent ML & Graph Core</div>
            <div class="step-desc">IsolationForest anomaly scoring + Louvain graph modularity algorithms flag colluding money-mule rings.</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class="guide-card">
            <div class="step-number">04 / STEP</div>
            <div class="step-title">🛡️ CountermeasureAgent Execution</div>
            <div class="step-desc">Auto-freezes CRITICAL accounts, revokes session tokens, generates downloadable FinCEN SAR reports, and logs human overrides.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 🚀 Step 1: Input Dataset Selection & Upload")
    
    with st.expander("📥 Upload Custom CSV Dataset or Load Sample Data", expanded=True):
        st.markdown("##### Choose Your Input Dataset Mode:")

        mode_choice = st.radio(
            "Select Data Source Mode:",
            ["📁 Upload My Own CSV Dataset", "⚡ Use Default PaySim Dataset", "⚡ Synthetic Money Mule Dataset"],
            horizontal=True
        )

        curr_df = st.session_state.get("uploaded_df")

        if mode_choice == "📁 Upload My Own CSV Dataset":
            uploaded_file = st.file_uploader("Upload Bank Transaction CSV File (.csv)", type=["csv"])
            if uploaded_file is not None:
                try:
                    curr_df = pd.read_csv(uploaded_file)
                    st.session_state["uploaded_df"] = curr_df
                    st.success(f"✅ Successfully loaded custom CSV: **{uploaded_file.name}** ({len(curr_df):,} rows)")
                except Exception as e:
                    st.error(f"⚠️ Error parsing CSV file: {e}")

        elif mode_choice == "⚡ Use Default PaySim Dataset":
            curr_df = load_transactions()
            st.session_state["uploaded_df"] = curr_df
            st.info(f"ℹ️ Loaded PaySim Dataset ({len(curr_df):,} transactions)")

        elif mode_choice == "⚡ Synthetic Money Mule Dataset":
            curr_df = load_transactions(n_synthetic=2500)
            st.session_state["uploaded_df"] = curr_df
            st.info(f"ℹ️ Loaded Synthetic Mule Ring Dataset ({len(curr_df):,} transactions)")

        # Display Dataset Summary & Auto-Detected Schema
        if curr_df is not None:
            st.markdown("---")
            st.markdown("##### 🔍 Uploaded Dataset Summary & Auto-Detected Columns:")

            orig_col, dest_col, amt_col = detect_transaction_columns(curr_df)

            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            with col_s1:
                st.metric("Total Transactions", f"{len(curr_df):,}")
            with col_s2:
                sender_cnt = curr_df[orig_col].nunique() if orig_col in curr_df else 0
                st.metric("Sender Accounts", f"{sender_cnt:,}")
            with col_s3:
                dest_cnt = curr_df[dest_col].nunique() if dest_col in curr_df else 0
                st.metric("Receiver Accounts", f"{dest_cnt:,}")
            with col_s4:
                try:
                    total_vol = float(curr_df[amt_col].sum()) if amt_col in curr_df else 0.0
                    st.metric("Total Volume Moved", f"₹{total_vol/100000.0:,.1f}L")
                except Exception:
                    st.metric("Total Volume Moved", "N/A")

            st.caption(f"**Auto-Detected Schema**: Sender Column = `{orig_col}` | Receiver Column = `{dest_col}` | Amount Column = `{amt_col}`")

            with st.expander("👀 View First 5 Rows of Input Dataset"):
                st.dataframe(curr_df.head(5), use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 Run Fraud Ring Detection on This Input Dataset", type="primary", use_container_width=True):
                st.session_state["current_page"] = "page2"
                st.session_state["trigger_analysis"] = True
                st.rerun()


# ===========================================================================
# PAGE 2 — MAIN ANALYSIS DASHBOARD & DYNAMIC ACCOUNT FREEZE PANEL
# ===========================================================================
elif st.session_state["current_page"] == "page2":
    
    df = st.session_state.get("uploaded_df")
    if df is None:
        df = load_transactions()
        st.session_state["uploaded_df"] = df

    # SIDEBAR CONTROLS
    st.sidebar.header("⚙️ Agent Controls")
    risk_threshold = st.sidebar.slider("Risk Cutoff Threshold", 0.20, 0.90, 0.55, step=0.05)
    contamination = st.sidebar.slider("IsolationForest Contamination", 0.01, 0.25, 0.10, step=0.01)

    st.sidebar.markdown("---")
    st.sidebar.markdown("##### 📂 Change Input Dataset")
    sidebar_file = st.sidebar.file_uploader("Upload New Dataset (.csv)", type=["csv"], key="sidebar_csv")
    if sidebar_file is not None:
        try:
            df = pd.read_csv(sidebar_file)
            st.session_state["uploaded_df"] = df
            st.sidebar.success("New CSV Loaded!")
        except Exception as e:
            st.sidebar.error(f"Upload error: {e}")

    # Live Stream Feed Simulation Mode Toggle
    simulate_live = st.sidebar.toggle("⚡ Simulate Live Stream Feed Mode", value=False)

    st.sidebar.markdown("---")
    run_pipeline_btn = st.sidebar.button("🚀 Re-Run Fraud Ring Engine", type="primary", use_container_width=True)

    if run_pipeline_btn:
        st.session_state["trigger_analysis"] = True

    # TRIGGER AGENTIC PIPELINE EXECUTION ON THE USER INPUT DATASET
    if st.session_state.get("trigger_analysis", False):
        st.markdown("### ⚡ Analyzing Input Dataset with Multi-Agent Reasoning...")
        progress_bar = st.progress(0)
        status_text = st.empty()

        steps = [
            ("🌐 Step 1/4 DetectorAgent: Parsing user input dataset & mapping transaction graph...", 25),
            ("🌲 Step 2/4 DetectorAgent: Computing IsolationForest & Louvain graph community scores...", 50),
            ("🤖 Step 3/4 InvestigatorAgent: Evaluating feature contributions & risk tier classification...", 75),
            ("🛡️ Step 4/4 CountermeasureAgent: Enacting auto-freezes, token revocations, and FinCEN SAR drafts...", 100),
        ]

        for msg, val in steps:
            status_text.markdown(f"**{msg}**")
            progress_bar.progress(val)
            time.sleep(0.2)

        # Execute Multi-Step Agent Pipeline on the user uploaded dataset!
        agent_results = agents.run_agentic_pipeline(
            df=df,
            bank_name=user_info["bank_name"],
            risk_threshold=risk_threshold,
            contamination=contamination,
            user_api_key=st.session_state.get("user_api_key", "")
        )

        st.session_state["agent_results"] = agent_results
        st.session_state["trigger_analysis"] = False
        st.rerun()

    # IF PIPELINE NOT RUN YET
    if "agent_results" not in st.session_state:
        st.info("📥 Dataset loaded! Click **'🚀 Run Fraud Ring Detection'** below to analyze this dataset.")
        if st.button("🚀 Run Fraud Ring Detection Now", type="primary", use_container_width=True):
            st.session_state["trigger_analysis"] = True
            st.rerun()
        st.stop()

    res = st.session_state["agent_results"]
    G = res["G"]
    anomaly_scores = res["anomaly_scores"]
    community_report = res["community_report"]
    flagged_rings = res["flagged_rings"]
    feature_contributions = res["feature_contributions"]
    ring_analyses = res["ring_analyses"]
    batch_id = res["batch_id"]

    # LIVE STREAM SIMULATION
    if simulate_live:
        st.info("⚡ Live Stream Feed Simulation Active: Replaying transaction stream...")

    # DATABASE CONFIRMATION BADGE
    st.markdown(f'<div class="db-badge">✅ Fraud Engine Output Saved to SQLite Database (Batch #{batch_id})</div>', unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # TOP KPI STRIP (TOTAL SCAM AMOUNT & ACCOUNTS TO FREEZE FROM USER DATASET)
    # ---------------------------------------------------------------------------
    total_accounts = G.number_of_nodes()
    flagged_count = len(flagged_rings)
    total_amount_scammed = flagged_rings["total_amount_moved"].sum() if flagged_count > 0 else 0.0
    scam_in_lakhs = total_amount_scammed / 100000.0

    flagged_members = set()
    for members in flagged_rings["members"]:
        flagged_members.update(members)
        
    freeze_accounts_count = len(flagged_members)

    st.markdown(f"""
    <div class="tva-kpi-row">
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Accounts Monitored</div>
            <div class="tva-kpi-value">{total_accounts:,}</div>
        </div>
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Flagged Fraud Rings</div>
            <div class="tva-kpi-value danger">{flagged_count}</div>
        </div>
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Total Amount Scammed</div>
            <div class="tva-kpi-value danger">&#8377;{scam_in_lakhs:.1f}L</div>
        </div>
        <div class="tva-kpi-card">
            <div class="tva-kpi-label">Accounts To Freeze</div>
            <div class="tva-kpi-value danger">{freeze_accounts_count} Accounts</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---------------------------------------------------------------------------
    # MAIN DASHBOARD: DUAL CLEAR GRAPH VIEWS & DYNAMIC FREEZE PANEL
    # ---------------------------------------------------------------------------
    c_left, c_right = st.columns([1.45, 1.0])

    with c_left:
        st.markdown("#### 🌐 Transaction Network Topology Graphs (User Dataset)")
        
        # Dual View Mode Selector (3D Wire View vs 2D High-Contrast View)
        view_tab = st.radio("Select Graph View Mode:", ["🌐 3D Fiber-Optic Wire View", "🗺️ 2D High-Contrast Interactive View"], horizontal=True)

        if "3D" in view_tab:
            st.markdown("##### 1. Overall Account Network Topology (All Accounts)")
            st.caption("Hover over nodes for anomaly scores & key suspicion metrics")
            fig_overall = render_wire_3d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="🌐 Overall Account Network Topology (3D Wire View)", only_fraud=False
            )
            st.plotly_chart(fig_overall, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("##### 2. Isolated High-Risk Fraud Accounts Subgraph")
            st.caption("Plotting ONLY the flagged fraud ring accounts in the user dataset")
            fig_fraud = render_wire_3d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="🎯 High-Risk Fraud Accounts Subgraph (3D View)", only_fraud=True
            )
            st.plotly_chart(fig_fraud, use_container_width=True)

        else:
            st.markdown("##### 1. Overall Account Network Topology (2D View)")
            st.caption("High-contrast node layout with account labels on hover & zoom")
            fig_overall_2d = render_wire_2d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="🗺️ Overall Account Network Topology (2D View)", only_fraud=False
            )
            st.plotly_chart(fig_overall_2d, use_container_width=True)

            st.markdown("<br>", unsafe_allow_html=True)

            st.markdown("##### 2. Isolated High-Risk Fraud Accounts Subgraph (2D View)")
            st.caption("High-contrast subgraph of flagged fraud ring accounts")
            fig_fraud_2d = render_wire_2d_graph(
                G, flagged_members, anomaly_scores, feature_contributions,
                title="🎯 High-Risk Fraud Accounts Subgraph (2D View)", only_fraud=True
            )
            st.plotly_chart(fig_fraud_2d, use_container_width=True)

    with c_right:
        # AGENT ACTIONS & ACCOUNT FREEZE PANEL
        st.markdown("#### 🛡️ Agent Actions & Account Freeze Panel")
        st.caption("Actions strictly generated for the target accounts in your uploaded dataset")

        if flagged_count > 0:
            # Download Full Risk CSV Report Button
            csv_data = community_report.to_csv(index=False)
            st.download_button(
                label="📊 Export Full Community Risk CSV Report",
                data=csv_data,
                file_name="Fraud_Community_Risk_Report.csv",
                mime="text/csv",
                use_container_width=True
            )
            st.markdown("<br>", unsafe_allow_html=True)

            for r_id, analysis in ring_analyses.items():
                tier = analysis["tier"]
                reasoning = analysis["reasoning"]
                cm = analysis["countermeasures"]
                r_data = analysis["ring_data"]

                target_accs_str = ", ".join(r_data['members'])

                st.markdown(f"""
                <div class="agent-action-card">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <strong style="font-size:1.05rem;">Fraud Ring #{r_id} ({r_data['size']} Accounts)</strong>
                        <span class="tier-badge tier-{tier}">{tier} SEVERITY</span>
                    </div>
                    <p style="font-size:0.85rem; color:#d6d3d1; margin-bottom:6px;"><b>Scammed Amount:</b> ₹{r_data['total_amount_moved']:,.2f}</p>
                    <p style="font-size:0.85rem; color:#d6d3d1; margin-bottom:8px;"><b>Investigator Reasoning:</b> {reasoning}</p>
                    <p style="font-size:0.82rem; color:#ef4444; margin-bottom:8px; font-family:Share Tech Mono, monospace;"><b>❄️ Freeze Target Accounts:</b><br>{target_accs_str}</p>
                    <div style="font-size:0.8rem; color:#a8a29e; margin-bottom:10px;">
                        • Executed Actions: {len(cm['executed_actions'])} | Pending Approval: {len(cm['pending_actions'])}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # HUMAN OVERRIDE CONTROLS (FREEZE / UNFREEZE ACTIONS)
                db_actions = db.fetch_actions_for_batch(batch_id)
                ring_actions = [a for a in db_actions if a["ring_id"] == r_id]

                if ring_actions:
                    with st.expander(f"⚙️ Manage Freeze Overrides for Ring #{r_id}"):
                        for act in ring_actions:
                            act_id = act["id"]
                            status = act["status"]
                            acc_id = act["account_id"]
                            a_type = act["action_type"]

                            st.write(f"• **{a_type}** for `{acc_id}` — Status: `{status}`")
                            
                            b_col1, b_col2 = st.columns(2)
                            with b_col1:
                                if status == "PENDING_APPROVAL":
                                    if st.button(f"✅ Freeze / Approve {acc_id}", key=f"app_{act_id}"):
                                        db.approve_pending_action(act_id, approved_by=user_info["username"])
                                        st.success(f"Frozen account {acc_id}!")
                                        st.rerun()
                            with b_col2:
                                if status in ["EXECUTED", "PENDING_APPROVAL"]:
                                    if st.button(f"↺ Reverse / Unfreeze", key=f"rev_{act_id}"):
                                        db.reverse_action(act_id, approved_by=user_info["username"])
                                        countermeasures.unfreeze_account(acc_id, approved_by=user_info["username"])
                                        st.warning(f"Unfrozen account {acc_id}!")
                                        st.rerun()

                # DOWNLOAD SAR REPORT BUTTON FOR THIS SPECIFIC RING IN USER DATASET
                sar_path = cm.get("sar_file_path", "")
                if sar_path and os.path.exists(sar_path):
                    with open(sar_path, "r", encoding="utf-8") as f:
                        sar_text = f.read()
                    st.download_button(
                        label=f"📥 Download FinCEN SAR Report (Ring #{r_id})",
                        data=sar_text,
                        file_name=f"FinCEN_SAR_Report_Ring_{r_id}.txt",
                        mime="text/plain",
                        key=f"sar_dl_{r_id}"
                    )
                st.markdown("<br>", unsafe_allow_html=True)

        else:
            st.success("✅ Security Status Clean: No fraud rings detected in this dataset.")


# ===========================================================================
# PAGE 3 — ABOUT & AUDIT TRAIL PAGE
# ===========================================================================
elif st.session_state["current_page"] == "page3":
    st.markdown("### 👥 About GraphGuardians & Audit Trail")
    st.markdown("GraphGuardians is an Agentic Fraud Ring Detection & Countermeasure Engine.")

    st.markdown("#### 🎯 Mission Statement")
    st.info("""
    **Our Mission**: Traditional rules-based fraud detection fails against modern money-mule syndicates. 
    By combining **Unsupervised Machine Learning (IsolationForest)** with **Graph Modularity Analytics (Louvain Algorithm)**, 
    **Multi-Agent Reasoning (Detector -> Investigator -> Countermeasure)**, and **Real State Persistence**, 
    GraphGuardians empowers financial institutions to detect, isolate, and neutralize complex fraud networks in real-time.
    """)

    st.markdown("---")
    st.markdown("#### 👨‍💻 Team Behind GraphGuardians")

    t1, t2, t3 = st.columns(3)
    with t1:
        st.markdown("""
        <div class="guide-card" style="text-align:center;">
            <div style="font-size:3rem; margin-bottom:10px;">👤</div>
            <div class="step-title">Lead AI / ML Engineer</div>
            <div class="step-desc">Designed IsolationForest Anomaly Engine, Feature Attribution, & Louvain Graph Analytics.</div>
        </div>
        """, unsafe_allow_html=True)

    with t2:
        st.markdown("""
        <div class="guide-card" style="text-align:center;">
            <div style="font-size:3rem; margin-bottom:10px;">🛡️</div>
            <div class="step-title">Countermeasure Architecture Lead</div>
            <div class="step-desc">Architected Countermeasure Engine, SQLite Persistence, and Human Override Controls.</div>
        </div>
        """, unsafe_allow_html=True)

    with t3:
        st.markdown("""
        <div class="guide-card" style="text-align:center;">
            <div style="font-size:3rem; margin-bottom:10px;">🤖</div>
            <div class="step-title">Multi-Agent Pipeline Lead</div>
            <div class="step-desc">Orchestrated DetectorAgent, InvestigatorAgent, and CountermeasureAgent reasoning chain.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("#### 💾 SQLite Countermeasure Actions Audit Trail")
    
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions ORDER BY id DESC LIMIT 20;")
    action_rows = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if action_rows:
        st.dataframe(pd.DataFrame(action_rows), use_container_width=True)
    else:
        st.caption("No countermeasure actions logged in SQLite database yet.")

    st.markdown("#### 💾 SQLite Analysis Batches Audit Trail")
    recent_records = db.fetch_latest_records(5)
    if recent_records:
        st.dataframe(pd.DataFrame(recent_records), use_container_width=True)
    else:
        st.caption("No historical records saved in SQLite yet.")
