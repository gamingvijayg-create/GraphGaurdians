"""
countermeasures.py
--------------------
Automated and human-in-the-loop countermeasure engine.
Makes real persisted state changes in SQLite database (simulating core banking system APIs).

Actions:
- freeze_account: Freeze debit/transfer permissions for an account.
- revoke_tokens: Invalidate active mobile banking and API session tokens.
- file_sar_report: Generate downloadable Suspicious Activity Report (SAR) document.
- unfreeze_account: Human override to reverse freeze actions.
"""

import os
import time
from typing import List, Dict, Any
import db

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "outputs")


def freeze_account(account_id: str, ring_id: int, batch_id: int, reason: str, auto: bool = True, approved_by: str = "SYSTEM_AUTO") -> dict:
    """Freezes account debit/transfer permissions and records state change in SQLite."""
    status = "EXECUTED" if auto else "PENDING_APPROVAL"
    action_type = "FREEZE_ACCOUNT"
    
    action_id = db.save_action(
        batch_id=batch_id,
        account_id=account_id,
        ring_id=ring_id,
        action_type=action_type,
        status=status,
        reason=reason,
        approved_by=approved_by
    )
    
    return {
        "action_id": action_id,
        "account_id": account_id,
        "ring_id": ring_id,
        "action_type": action_type,
        "status": status,
        "message": f"Account {account_id} status set to {status} ({reason})"
    }


def revoke_tokens(account_id: str, batch_id: int, ring_id: int = 0, reason: str = "High risk security mitigation", approved_by: str = "SYSTEM_AUTO") -> dict:
    """Invalidates active mobile banking & web API session tokens."""
    action_type = "REVOKE_TOKENS"
    status = "EXECUTED"
    
    action_id = db.save_action(
        batch_id=batch_id,
        account_id=account_id,
        ring_id=ring_id,
        action_type=action_type,
        status=status,
        reason=reason,
        approved_by=approved_by
    )
    
    return {
        "action_id": action_id,
        "account_id": account_id,
        "action_type": action_type,
        "status": status,
        "message": f"Active session tokens revoked for account {account_id}"
    }


def file_sar_report(ring_id: int, batch_id: int, members: List[str], total_amount: float, institution_name: str = "FINANCIAL INSTITUTION", officer_name: str = "SOC ANALYST") -> str:
    """Generates an official Suspicious Activity Report (SAR) text file and returns its path."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_name = f"SAR_Report_Ring_{ring_id}_Batch_{batch_id}.txt"
    file_path = os.path.join(OUTPUT_DIR, file_name)
    
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC")
    
    lines = [
        "================================================================================",
        "          FINANCIAL CRIMES ENFORCEMENT NETWORK (FinCEN) — SAR DRAFT             ",
        "                   SUSPICIOUS ACTIVITY REPORT (AUTOMATED)                       ",
        "================================================================================",
        f"FILING INSTITUTION : {institution_name.upper()}",
        f"FILING OFFICER     : {officer_name.upper()}",
        f"DATE OF FILING     : {ts}",
        f"BATCH REFERENCE ID : BATCH #{batch_id}",
        f"TARGET FRAUD RING  : RING #{ring_id}",
        "--------------------------------------------------------------------------------",
        "SUBJECT ACCOUNTS INVOLVED:",
        f"  Total Accounts : {len(members)}",
        f"  Account List   : {', '.join(members)}",
        "--------------------------------------------------------------------------------",
        "FINANCIAL IMPACT & EVIDENCE:",
        f"  Total Capital Volume Moved : ₹{total_amount:,.2f}",
        "  Primary Typology Identified : Rapid Circular Fund Routing / Money Mule Ring",
        "  Detection Method           : IsolationForest Anomaly Scoring + Louvain Community Mining",
        "--------------------------------------------------------------------------------",
        "EXECUTIVE NARRATIVE:",
        f"  An automated network graph analysis identified a tightly connected syndicate of",
        f"  {len(members)} accounts exhibiting rapid velocity fund transfers totalling ₹{total_amount:,.2f}.",
        "  Individual accounts exhibited severe balance drain and high degree imbalance.",
        "  Immediate account freeze and token revocation countermeasures were enacted.",
        "================================================================================\n"
    ]
    
    content = "\n".join(lines)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
        
    # Log action to SQLite
    db.save_action(
        batch_id=batch_id,
        account_id=f"RING_# {ring_id}",
        ring_id=ring_id,
        action_type="FILE_SAR_REPORT",
        status="EXECUTED",
        reason=f"Filed official FinCEN SAR document ({file_name})",
        approved_by=officer_name
    )
    
    return file_path


def unfreeze_account(account_id: str, approved_by: str = "HUMAN_OFFICER") -> dict:
    """Human override to unfreeze an account and reverse freeze status."""
    return db.reverse_action_for_account(account_id, approved_by)
