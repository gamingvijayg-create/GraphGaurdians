"""
agents.py
---------
Multi-step Agentic Pipeline for GraphGuardians:
1. DetectorAgent: Wraps fraud_detector.py pipeline.
2. InvestigatorAgent: Performs structured risk-tier classification & reasoning.
3. CountermeasureAgent: Executes auto actions (CRITICAL/HIGH) or queues human approval (MEDIUM/LOW).
4. Persists the reasoning chain into SQLite via db.save_agent_log.
"""

import os
import time
import json
import requests
import pandas as pd
from typing import Dict, Any, List, Tuple

from graph_builder import build_transaction_graph
from fraud_detector import (
    compute_node_features,
    score_anomalies,
    detect_communities,
    score_communities,
    flag_fraud_rings,
)
from explainability import compute_feature_contributions
import countermeasures
import db


# ---------------------------------------------------------------------------
# API KEY RESOLUTION (PRIORITY 0 SECURITY REQUIREMENT)
# ---------------------------------------------------------------------------
def resolve_api_key(user_key: str = None) -> str:
    """
    Resolves API key securely in order of precedence:
    1. Explicit user_key passed in session (if not empty)
    2. st.secrets["GROQ_API_KEY"] (if available in Streamlit runtime)
    3. os.environ.get("GROQ_API_KEY")
    4. None (triggers local template/rule-based fallback)
    """
    if user_key and user_key.strip():
        return user_key.strip()
    
    # Try streamlit secrets
    try:
        import streamlit as st
        if "GROQ_API_KEY" in st.secrets:
            return st.secrets["GROQ_API_KEY"]
    except Exception:
        pass
    
    # Try environment variable
    env_key = os.environ.get("GROQ_API_KEY")
    if env_key:
        return env_key.strip()
        
    return ""


# ---------------------------------------------------------------------------
# 1. DETECTOR AGENT
# ---------------------------------------------------------------------------
class DetectorAgent:
    """Wraps ML & Graph Community detection core."""
    
    def run(self, df: pd.DataFrame, risk_threshold: float = 0.55, contamination: float = 0.10) -> Tuple[Any, pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
        G = build_transaction_graph(df)
        features = compute_node_features(G)
        anomaly_scores = score_anomalies(features, contamination=contamination)
        communities = detect_communities(G)
        community_report = score_communities(G, communities, anomaly_scores)
        flagged_rings = flag_fraud_rings(community_report, threshold=risk_threshold)
        feature_contributions = compute_feature_contributions(features)
        
        return G, features, anomaly_scores, community_report, flagged_rings, feature_contributions


# ---------------------------------------------------------------------------
# 2. INVESTIGATOR AGENT
# ---------------------------------------------------------------------------
class InvestigatorAgent:
    """Analyzes each flagged ring, produces risk tier, reasoning, and suggested actions."""
    
    def _rule_based_investigation(self, ring_row: pd.Series, contributions: Dict[str, List[str]]) -> Dict[str, Any]:
        risk_score = float(ring_row["risk_score"])
        r_id = int(ring_row["community_id"])
        members = list(ring_row["members"])
        
        if risk_score >= 0.85:
            tier = "CRITICAL"
        elif risk_score >= 0.65:
            tier = "HIGH"
        elif risk_score >= 0.55:
            tier = "MEDIUM"
        else:
            tier = "LOW"
            
        sample_member = members[0] if members else "N/A"
        reasons = contributions.get(str(sample_member), ["High behavioral transaction anomaly"])
        reason_snippet = "; ".join(reasons[:2])

        reasoning = (
            f"Ring #{r_id} exhibits {tier} risk severity (Composite Score: {risk_score:.2f}). "
            f"Key anomaly factors for member accounts include: {reason_snippet}. "
            f"Total volume of ₹{ring_row['total_amount_moved']:,.2f} moved across {len(members)} colluding accounts with internal density {ring_row['internal_density']*100:.1f}%."
        )

        actions = ["freeze_account", "revoke_tokens", "file_sar_report"]
        return {"tier": tier, "reasoning": reasoning, "suggested_actions": actions}

    def investigate_ring(self, ring_row: pd.Series, contributions: Dict[str, List[str]], api_key: str = "") -> Dict[str, Any]:
        """Calls LLM for structured JSON investigation or falls back to rule-based classification."""
        if not api_key:
            return self._rule_based_investigation(ring_row, contributions)
            
        headers = {
            "Authorization": f"Bearer {api_key.strip()}",
            "Content-Type": "application/json"
        }
        
        system_prompt = (
            "You are a Lead Financial Intelligence Investigator. Analyze the suspicious fraud ring data. "
            "You MUST respond ONLY with a valid JSON object matching this exact schema:\n"
            "{\n"
            '  "tier": "CRITICAL" | "HIGH" | "MEDIUM" | "LOW",\n'
            '  "reasoning": "<Concise 2-sentence risk explanation>",\n'
            '  "suggested_actions": ["freeze_account", "revoke_tokens", "file_sar_report"]\n'
            "}"
        )
        
        r_id = int(ring_row["community_id"])
        members = list(ring_row["members"])
        sample_reasons = contributions.get(str(members[0]), ["High behavioral anomaly"])
        
        user_prompt = f"""
        Ring ID: #{r_id}
        Members: {members}
        Composite Risk Score: {ring_row['risk_score']}
        Avg Node Anomaly Score: {ring_row['avg_anomaly_score']}
        Internal Density: {ring_row['internal_density']}
        Total Amount Moved: ₹{ring_row['total_amount_moved']:,.2f}
        Sample Account Feature Reasons: {sample_reasons}
        """

        payload = {
            "model": "llama-3.3-70b-versatile",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,
            "max_tokens": 400
        }

        # Attempt up to 2 calls for valid JSON
        for attempt in range(2):
            try:
                res = requests.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=15)
                if res.status_code == 200:
                    text_resp = res.json()["choices"][0]["message"]["content"].strip()
                    # Clean markdown fence if present
                    if text_resp.startswith("```"):
                        text_resp = text_resp.split("```")[1].replace("json", "").strip()
                    parsed = json.loads(text_resp)
                    if "tier" in parsed and "reasoning" in parsed:
                        return parsed
            except Exception:
                pass
                
        # Fallback to rule-based on failure
        return self._rule_based_investigation(ring_row, contributions)


# ---------------------------------------------------------------------------
# 3. COUNTERMEASURE AGENT
# ---------------------------------------------------------------------------
class CountermeasureAgent:
    """Determines auto-execution vs queued human approval based on risk tier."""
    
    def process(self, ring_id: int, members: List[str], tier: str, total_amount: float, batch_id: int, reasoning: str) -> Dict[str, Any]:
        executed_actions = []
        pending_actions = []
        sar_file_path = ""

        if tier == "CRITICAL":
            # Auto-execute freeze for all accounts + file SAR report
            for acc in members:
                res = countermeasures.freeze_account(acc, ring_id, batch_id, reason=f"CRITICAL Ring #{ring_id}: {reasoning}", auto=True)
                executed_actions.append(res)
            
            sar_file_path = countermeasures.file_sar_report(ring_id, batch_id, members, total_amount)
            
        elif tier == "HIGH":
            # Auto-execute token revocation, queue account freeze for human approval
            for acc in members:
                res_tok = countermeasures.revoke_tokens(acc, batch_id, ring_id=ring_id, reason=f"HIGH Risk Ring #{ring_id}")
                executed_actions.append(res_tok)
                
                res_frz = countermeasures.freeze_account(acc, ring_id, batch_id, reason=f"HIGH Risk Ring #{ring_id} pending freeze", auto=False)
                pending_actions.append(res_frz)

        else: # MEDIUM or LOW
            # Queue for officer review
            for acc in members:
                res = countermeasures.freeze_account(acc, ring_id, batch_id, reason=f"{tier} Risk Ring #{ring_id} review", auto=False)
                pending_actions.append(res)

        return {
            "tier": tier,
            "executed_actions": executed_actions,
            "pending_actions": pending_actions,
            "sar_file_path": sar_file_path
        }


# ---------------------------------------------------------------------------
# 4. ORCHESTRATED AGENTIC PIPELINE FUNCTION
# ---------------------------------------------------------------------------
def run_agentic_pipeline(df: pd.DataFrame, bank_name: str, risk_threshold: float = 0.55, contamination: float = 0.10, user_api_key: str = None, batch_id: int = 1) -> Dict[str, Any]:
    """
    Executes the full 3-agent reasoning pipeline:
    DetectorAgent -> InvestigatorAgent -> CountermeasureAgent -> SQLite Logging
    """
    api_key = resolve_api_key(user_api_key)

    # Step 1: Detection
    detector = DetectorAgent()
    G, features, anomaly_scores, community_report, flagged_rings, feature_contributions = detector.run(df, risk_threshold, contamination)
    
    db.save_agent_log(batch_id, "DetectorAgent", "RUN_DETECTION", {
        "total_nodes": G.number_of_nodes(),
        "total_edges": G.number_of_edges(),
        "communities_count": len(community_report),
        "flagged_rings_count": len(flagged_rings)
    })

    # Step 2: Investigation & Countermeasure Execution
    investigator = InvestigatorAgent()
    cm_agent = CountermeasureAgent()

    ring_analyses = {}
    
    for idx, row in flagged_rings.iterrows():
        r_id = int(row["community_id"])
        members = list(row["members"])
        total_amount = float(row["total_amount_moved"])

        # Investigator reasoning
        inv_res = investigator.investigate_ring(row, feature_contributions, api_key=api_key)
        tier = inv_res.get("tier", "HIGH")
        reasoning = inv_res.get("reasoning", "")

        db.save_agent_log(batch_id, "InvestigatorAgent", f"INVESTIGATE_RING_#{r_id}", {
            "ring_id": r_id,
            "tier": tier,
            "reasoning": reasoning
        })

        # Countermeasure execution
        cm_res = cm_agent.process(r_id, members, tier, total_amount, batch_id, reasoning)

        db.save_agent_log(batch_id, "CountermeasureAgent", f"EXECUTE_ACTIONS_RING_#{r_id}", {
            "ring_id": r_id,
            "executed_count": len(cm_res["executed_actions"]),
            "pending_count": len(cm_res["pending_actions"]),
            "sar_file_path": cm_res["sar_file_path"]
        })

        ring_analyses[r_id] = {
            "ring_data": row.to_dict(),
            "tier": tier,
            "reasoning": reasoning,
            "countermeasures": cm_res
        }

    return {
        "G": G,
        "features": features,
        "anomaly_scores": anomaly_scores,
        "community_report": community_report,
        "flagged_rings": flagged_rings,
        "feature_contributions": feature_contributions,
        "ring_analyses": ring_analyses,
        "batch_id": batch_id,
        "api_key_used": bool(api_key)
    }
