import React, { useState } from 'react';
import { ShieldAlert, AlertTriangle, Cpu, ArrowRight, Lock, CheckCircle } from 'lucide-react';

export default function AccountDetailsInspector({ accountId = 'ACC-20481', accountData, onRequestRestriction }) {
  const [restricted, setRestricted] = useState(false);

  const acc = accountData || {
    account_id: accountId,
    risk_score: 94,
    risk_tier: 'CRITICAL',
    connections: {
      accounts_count: 8,
      devices_count: 3,
      ip_addresses_count: 4,
      transactions_count: 127
    },
    total_amount_lakhs: 12.8,
    ai_insight: 'Account shares a device and beneficiary relationship with 7 other suspicious accounts.'
  };

  const handleRestriction = () => {
    setRestricted(true);
    if (onRequestRestriction) {
      onRequestRestriction(acc.account_id);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px', borderBottom: '1px solid rgba(255, 255, 255, 0.08)', paddingBottom: '12px' }}>
        <div>
          <div style={{ fontSize: '11px', color: '#64748B', fontWeight: 700, letterSpacing: '1px' }}>
            ACCOUNT DETAILS
          </div>
          <h3 style={{ fontSize: '20px', fontWeight: 800, color: '#F8FAFC', fontFamily: 'monospace' }}>
            {acc.account_id}
          </h3>
        </div>
        <span style={{
          padding: '4px 10px',
          borderRadius: '8px',
          background: '#EF4444',
          color: '#FFFFFF',
          fontSize: '11px',
          fontWeight: 800,
          letterSpacing: '0.5px'
        }}>
          {acc.risk_tier}
        </span>
      </div>

      {/* Risk Score */}
      <div style={{
        padding: '16px',
        borderRadius: '12px',
        background: 'rgba(239, 68, 68, 0.10)',
        border: '1px solid rgba(239, 68, 68, 0.25)',
        marginBottom: '20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between'
      }}>
        <div>
          <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 600 }}>Risk Score</div>
          <div style={{ fontSize: '32px', fontWeight: 900, color: '#EF4444' }}>
            {acc.risk_score} <span style={{ fontSize: '16px', color: '#64748B', fontWeight: 500 }}>/ 100</span>
          </div>
        </div>
        <ShieldAlert size={36} color="#EF4444" />
      </div>

      {/* Connections List */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '12px', color: '#94A3B8', fontWeight: 700, marginBottom: '10px', uppercase: true }}>
          Connections
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '11px', color: '#64748B' }}>Accounts</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#F8FAFC' }}>
              {String(acc.connections.accounts_count).padStart(2, '0')} Accounts
            </div>
          </div>
          <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '11px', color: '#64748B' }}>Devices</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#F8FAFC' }}>
              {String(acc.connections.devices_count).padStart(2, '0')} Devices
            </div>
          </div>
          <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '11px', color: '#64748B' }}>IP Addresses</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#F8FAFC' }}>
              {String(acc.connections.ip_addresses_count).padStart(2, '0')} IPs
            </div>
          </div>
          <div style={{ padding: '10px', borderRadius: '10px', background: 'rgba(255, 255, 255, 0.03)', border: '1px solid rgba(255, 255, 255, 0.05)' }}>
            <div style={{ fontSize: '11px', color: '#64748B' }}>Transactions</div>
            <div style={{ fontSize: '16px', fontWeight: 700, color: '#F8FAFC' }}>
              {acc.connections.transactions_count}
            </div>
          </div>
        </div>
      </div>

      {/* Amount Flagged */}
      <div style={{ marginBottom: '20px', padding: '12px 14px', borderRadius: '10px', background: 'rgba(245, 158, 11, 0.10)', border: '1px solid rgba(245, 158, 11, 0.25)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: '13px', color: '#94A3B8' }}>Flagged Volume</span>
        <span style={{ fontSize: '18px', fontWeight: 800, color: '#F59E0B' }}>
          ₹{acc.total_amount_lakhs} Lakhs
        </span>
      </div>

      {/* AI Insight */}
      <div style={{
        padding: '14px',
        borderRadius: '12px',
        background: 'rgba(139, 92, 246, 0.10)',
        border: '1px solid rgba(139, 92, 246, 0.25)',
        marginBottom: '24px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
          <Cpu size={16} color="#A78BFA" />
          <span style={{ fontSize: '12px', fontWeight: 700, color: '#A78BFA' }}>AI INSIGHT</span>
        </div>
        <p style={{ fontSize: '13px', color: '#F8FAFC', fontStyle: 'italic', lineHeight: '1.4' }}>
          &ldquo;{acc.ai_insight}&rdquo;
        </p>
      </div>

      {/* Actions */}
      <div style={{ display: 'flex', gap: '10px', marginTop: 'auto' }}>
        <button style={{
          flex: 1,
          padding: '10px',
          borderRadius: '10px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          color: '#F8FAFC',
          fontSize: '12px',
          fontWeight: 600,
          cursor: 'pointer'
        }}>
          [ View Investigation ]
        </button>

        <button
          onClick={handleRestriction}
          disabled={restricted}
          style={{
            flex: 1.2,
            padding: '10px',
            borderRadius: '10px',
            background: restricted ? 'linear-gradient(135deg, #10B981 0%, #059669 100%)' : 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)',
            border: 'none',
            color: '#FFFFFF',
            fontSize: '12px',
            fontWeight: 700,
            cursor: restricted ? 'default' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            boxShadow: restricted ? '0 4px 14px rgba(16, 185, 129, 0.3)' : '0 4px 14px rgba(239, 68, 68, 0.35)'
          }}
        >
          {restricted ? <CheckCircle size={14} /> : <Lock size={14} />}
          <span>{restricted ? 'ACCOUNT FROZEN' : '[ Request Restriction ]'}</span>
        </button>
      </div>
    </div>
  );
}
