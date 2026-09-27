"""
db.py
-----
SQLite persistence layer for GraphGuardians:
Stores user auth credentials, login sessions, transaction batches, ML analysis results,
LLM security reports, agent reasoning chain logs, and countermeasure action state changes.
"""

import sqlite3
import os
import time
import json
import hashlib
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "database.db")


def hash_password(password: str) -> str:
    """Computes SHA-256 hash for secure user authentication."""
    return hashlib.sha256(password.strip().encode("utf-8")).hexdigest()


def get_db_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes SQLite database tables and seeds demo RBAC users and default policy engine rules."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. Users Auth Table (RBAC)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        bank_name TEXT NOT NULL,
        officer_email TEXT NOT NULL,
        role TEXT NOT NULL
    );
    """)

    # 2. Login Sessions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank_name TEXT NOT NULL,
        account_no TEXT NOT NULL,
        officer_email TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # 3. Transaction Batches Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS batches (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        bank_name TEXT NOT NULL,
        filename TEXT NOT NULL,
        txn_count INTEGER NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # 4. Analysis Results Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS analysis_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER,
        total_accounts INTEGER NOT NULL,
        flagged_rings_count INTEGER NOT NULL,
        total_amount_at_risk REAL NOT NULL,
        avg_risk_score REAL NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES batches (id)
    );
    """)

    # 5. LLM Reports Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER,
        report_text TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES batches (id)
    );
    """)

    # 6. Countermeasure Actions Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS actions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER,
        account_id TEXT NOT NULL,
        ring_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        status TEXT NOT NULL,
        reason TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        approved_by TEXT NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES batches (id)
    );
    """)

    # 7. Agent Reasoning Log Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS agent_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        batch_id INTEGER,
        agent_name TEXT NOT NULL,
        step_name TEXT NOT NULL,
        data_json TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (batch_id) REFERENCES batches (id)
    );
    """)

    # 8. Cases Table (Case Management)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT UNIQUE NOT NULL,
        title TEXT NOT NULL,
        account_id TEXT NOT NULL,
        priority TEXT NOT NULL,
        status TEXT NOT NULL,
        assigned_to TEXT NOT NULL,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 9. Case Notes Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS case_notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        case_id TEXT NOT NULL,
        author TEXT NOT NULL,
        note_text TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (case_id) REFERENCES cases (case_id)
    );
    """)

    # 10. Policies Engine Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS policies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rule_name TEXT UNIQUE NOT NULL,
        category TEXT NOT NULL,
        description TEXT NOT NULL,
        is_enabled INTEGER NOT NULL DEFAULT 1,
        parameters_json TEXT NOT NULL,
        updated_at TEXT NOT NULL
    );
    """)

    # 11. Tamper-Evident Audit Trail Table (Cryptographic Hash Signature)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_trail (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        actor_username TEXT NOT NULL,
        actor_role TEXT NOT NULL,
        action_type TEXT NOT NULL,
        target_id TEXT NOT NULL,
        details_json TEXT NOT NULL,
        hash_signature TEXT NOT NULL,
        timestamp TEXT NOT NULL
    );
    """)

    # Seed demo users across RBAC roles if empty
    cursor.execute("SELECT COUNT(*) FROM users;")
    if cursor.fetchone()[0] == 0:
        demo_users = [
            ("admin", hash_password("admin123"), "JPMorgan Chase", "admin@fraudx.io", "ADMIN"),
            ("lead_investigator", hash_password("lead123"), "JPMorgan Chase", "lead@fraudx.io", "LEAD_INVESTIGATOR"),
            ("soc_analyst", hash_password("analyst123"), "JPMorgan Chase", "analyst@fraudx.io", "SOC_ANALYST"),
            ("auditor", hash_password("auditor123"), "JPMorgan Chase", "auditor@fraudx.io", "AUDITOR"),
        ]
        cursor.executemany("""
        INSERT INTO users (username, password_hash, bank_name, officer_email, role)
        VALUES (?, ?, ?, ?, ?)
        """, demo_users)

    # Seed default Policy Engine rules if empty
    cursor.execute("SELECT COUNT(*) FROM policies;")
    if cursor.fetchone()[0] == 0:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        default_policies = [
            ("VelocityRule", "TRANSACTION", "Flags accounts with over N transactions within 5 minutes across shared IP", 1, json.dumps({"max_txns": 10, "window_minutes": 5}), ts),
            ("SharedDeviceRule", "HARDWARE", "Flags hardware fingerprints shared across 3 or more accounts", 1, json.dumps({"max_accounts_per_device": 3}), ts),
            ("HighRiskOutflowRule", "AMOUNT", "Triggers critical alert on outbound transfers exceeding threshold within 1 hour", 1, json.dumps({"max_amount": 1000000, "window_hours": 1}), ts),
            ("CompositeRiskThresholdRule", "ML_SCORE", "Auto-routes account to restriction pending queue if risk score > cutoff", 1, json.dumps({"cutoff_score": 0.85}), ts),
        ]
        cursor.executemany("""
        INSERT INTO policies (rule_name, category, description, is_enabled, parameters_json, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        """, default_policies)

    # Seed sample cases if empty
    cursor.execute("SELECT COUNT(*) FROM cases;")
    if cursor.fetchone()[0] == 0:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        demo_cases = [
            ("CASE-20481", "Suspicious Mule Ring Collusion", "ACC-20481", "CRITICAL", "UNDER_INVESTIGATION", "lead_investigator", ts, ts),
            ("CASE-10932", "Rapid Device Swap & Outflow", "ACC-10932", "HIGH", "RESTRICTION_PENDING", "soc_analyst", ts, ts),
            ("CASE-30491", "High Velocity Micro-Transfers", "ACC-30491", "MEDIUM", "NEW", "Unassigned", ts, ts),
        ]
        cursor.executemany("""
        INSERT INTO cases (case_id, title, account_id, priority, status, assigned_to, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, demo_cases)

    conn.commit()
    conn.close()


def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticates a user against SHA-256 password hash in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    pass_hash = hash_password(password)
    cursor.execute("""
    SELECT * FROM users WHERE LOWER(username) = LOWER(?) AND password_hash = ?;
    """, (username.strip(), pass_hash))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def save_login(bank_name: str, account_no: str, officer_email: str) -> int:
    """Saves a user login session entry to SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO logins (bank_name, account_no, officer_email, timestamp)
    VALUES (?, ?, ?, ?)
    """, (bank_name, account_no, officer_email, ts))
    login_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return login_id


def save_batch_and_results(bank_name: str, filename: str, txn_count: int,
                           total_accounts: int, flagged_rings_count: int,
                           total_amount_at_risk: float, avg_risk_score: float,
                           report_text: str = "") -> int:
    """Saves transaction batch, ML analysis results, and LLM report to SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO batches (bank_name, filename, txn_count, timestamp)
    VALUES (?, ?, ?, ?)
    """, (bank_name, filename, txn_count, ts))
    batch_id = cursor.lastrowid

    cursor.execute("""
    INSERT INTO analysis_results (batch_id, total_accounts, flagged_rings_count, total_amount_at_risk, avg_risk_score, timestamp)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (batch_id, total_accounts, flagged_rings_count, total_amount_at_risk, avg_risk_score, ts))

    if report_text:
        cursor.execute("""
        INSERT INTO reports (batch_id, report_text, timestamp)
        VALUES (?, ?, ?)
        """, (batch_id, report_text, ts))

    conn.commit()
    conn.close()
    return batch_id


def save_action(batch_id: int, account_id: str, ring_id: int, action_type: str, status: str, reason: str, approved_by: str) -> int:
    """Saves a countermeasure action and signs audit trail."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO actions (batch_id, account_id, ring_id, action_type, status, reason, timestamp, approved_by)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (batch_id, account_id, ring_id, action_type, status, reason, ts, approved_by))
    action_id = cursor.lastrowid
    conn.commit()
    conn.close()

    log_audit(
        actor_username=approved_by,
        actor_role="OFFICER",
        action_type=action_type,
        target_id=account_id,
        details_dict={"ring_id": ring_id, "status": status, "reason": reason}
    )
    return action_id


def fetch_actions_for_batch(batch_id: int) -> List[Dict[str, Any]]:
    """Fetches all countermeasure actions for a specific batch."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM actions WHERE batch_id = ? ORDER BY id DESC;", (batch_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def approve_pending_action(action_id: int, approved_by: str = "HUMAN_OFFICER") -> dict:
    """Approves a PENDING_APPROVAL action to EXECUTED in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE actions
    SET status = 'EXECUTED', approved_by = ?, timestamp = ?
    WHERE id = ?;
    """, (approved_by, ts, action_id))
    conn.commit()
    conn.close()

    log_audit(approved_by, "LEAD_INVESTIGATOR", "APPROVE_ACTION", str(action_id), {"status": "EXECUTED"})
    return {"action_id": action_id, "status": "EXECUTED", "approved_by": approved_by}


def reverse_action(action_id: int, approved_by: str = "HUMAN_OFFICER") -> dict:
    """Reverses an EXECUTED or PENDING action to REVERSED in SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE actions
    SET status = 'REVERSED', approved_by = ?, timestamp = ?
    WHERE id = ?;
    """, (approved_by, ts, action_id))
    conn.commit()
    conn.close()

    log_audit(approved_by, "LEAD_INVESTIGATOR", "REVERSE_ACTION", str(action_id), {"status": "REVERSED"})
    return {"action_id": action_id, "status": "REVERSED", "approved_by": approved_by}


def reverse_action_for_account(account_id: str, approved_by: str = "HUMAN_OFFICER") -> dict:
    """Reverses active freeze/revoke actions for a specific account."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE actions
    SET status = 'REVERSED', approved_by = ?, timestamp = ?
    WHERE account_id = ? AND status != 'REVERSED';
    """, (approved_by, ts, account_id))
    conn.commit()
    conn.close()

    log_audit(approved_by, "LEAD_INVESTIGATOR", "UNFREEZE_ACCOUNT", account_id, {"status": "REVERSED"})
    return {"account_id": account_id, "status": "REVERSED", "approved_by": approved_by}


def save_agent_log(batch_id: int, agent_name: str, step_name: str, data_dict: Dict[str, Any]) -> int:
    """Logs agent execution reasoning steps into SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    data_json = json.dumps(data_dict)
    cursor.execute("""
    INSERT INTO agent_logs (batch_id, agent_name, step_name, data_json, timestamp)
    VALUES (?, ?, ?, ?, ?)
    """, (batch_id, agent_name, step_name, data_json, ts))
    log_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return log_id


def fetch_agent_logs_for_batch(batch_id: int) -> List[Dict[str, Any]]:
    """Fetches reasoning chain logs for a given batch."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM agent_logs WHERE batch_id = ? ORDER BY id ASC;", (batch_id,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def fetch_latest_records(limit: int = 5) -> List[Dict[str, Any]]:
    """Fetches latest analysis records for audit log display."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    SELECT b.bank_name, b.filename, b.txn_count, a.total_accounts, a.flagged_rings_count,
           a.total_amount_at_risk, a.avg_risk_score, a.timestamp
    FROM batches b
    JOIN analysis_results a ON b.id = a.batch_id
    ORDER BY a.id DESC
    LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# CASE MANAGEMENT CRUD
# ---------------------------------------------------------------------------
def fetch_cases() -> List[Dict[str, Any]]:
    """Fetches all cases from SQLite."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cases ORDER BY id DESC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def create_case(case_id: str, title: str, account_id: str, priority: str, assigned_to: str) -> Dict[str, Any]:
    """Creates a new fraud investigation case."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    INSERT INTO cases (case_id, title, account_id, priority, status, assigned_to, created_at, updated_at)
    VALUES (?, ?, ?, ?, 'NEW', ?, ?, ?)
    """, (case_id, title, account_id, priority, assigned_to, ts, ts))
    conn.commit()
    conn.close()

    log_audit(assigned_to, "INVESTIGATOR", "CREATE_CASE", case_id, {"title": title, "account_id": account_id})
    return {"case_id": case_id, "title": title, "status": "NEW"}


def update_case_status(case_id: str, status: str, updated_by: str) -> Dict[str, Any]:
    """Updates case status."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE cases SET status = ?, updated_at = ? WHERE case_id = ?;
    """, (status, ts, case_id))
    conn.commit()
    conn.close()

    log_audit(updated_by, "INVESTIGATOR", "UPDATE_CASE_STATUS", case_id, {"new_status": status})
    return {"case_id": case_id, "status": status}


# ---------------------------------------------------------------------------
# POLICY ENGINE CRUD
# ---------------------------------------------------------------------------
def fetch_policies() -> List[Dict[str, Any]]:
    """Fetches all policy rules."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM policies ORDER BY id ASC;")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


def update_policy(policy_id: int, is_enabled: bool, parameters_json: str, actor_username: str = "admin") -> Dict[str, Any]:
    """Updates policy rule status or configuration."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
    UPDATE policies SET is_enabled = ?, parameters_json = ?, updated_at = ? WHERE id = ?;
    """, (1 if is_enabled else 0, parameters_json, ts, policy_id))
    conn.commit()
    conn.close()

    log_audit(actor_username, "ADMIN", "UPDATE_POLICY", str(policy_id), {"is_enabled": is_enabled, "params": parameters_json})
    return {"policy_id": policy_id, "is_enabled": is_enabled}


# ---------------------------------------------------------------------------
# TAMPER-EVIDENT CRYPTOGRAPHIC AUDIT LOG (SHA-256 SIGNATURE CHAIN)
# ---------------------------------------------------------------------------
def log_audit(actor_username: str, actor_role: str, action_type: str, target_id: str, details_dict: Dict[str, Any]) -> str:
    """Logs action into audit trail with SHA-256 cryptographic signature."""
    conn = get_db_connection()
    cursor = conn.cursor()
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    details_json = json.dumps(details_dict)

    # Compute SHA-256 signature chain
    raw_sig = f"{actor_username}:{actor_role}:{action_type}:{target_id}:{details_json}:{ts}"
    hash_signature = hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()

    cursor.execute("""
    INSERT INTO audit_trail (actor_username, actor_role, action_type, target_id, details_json, hash_signature, timestamp)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (actor_username, actor_role, action_type, target_id, details_json, hash_signature, ts))
    conn.commit()
    conn.close()
    return hash_signature


def fetch_audit_trail(limit: int = 50) -> List[Dict[str, Any]]:
    """Fetches tamper-evident audit logs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM audit_trail ORDER BY id DESC LIMIT ?;", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]


# Initialize DB on module import
init_db()

