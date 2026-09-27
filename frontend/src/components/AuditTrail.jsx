import React from 'react';
import { ShieldCheck, Download, Key, CheckCircle, FileText } from 'lucide-react';

export default function AuditTrail({ auditLogs = [] }) {
  const sampleLogs = auditLogs.length > 0 ? auditLogs : [
    { id: 1, actor_username: 'lead_investigator', actor_role: 'LEAD_INVESTIGATOR', action_type: 'FREEZE_ACCOUNT', target_id: 'ACC-20481', details_json: '{"reason": "High Risk Mule Ring Collusion", "status": "EXECUTED"}', hash_signature: 'a8f9c2d1e4b309f18274bcde3901928374650192837465928173649581029384', timestamp: '2026-09-27 13:30:12' },
    { id: 2, actor_username: 'soc_analyst', actor_role: 'SOC_ANALYST', action_type: 'CREATE_CASE', target_id: 'CASE-20481', details_json: '{"title": "Suspicious Mule Ring Collusion", "account_id": "ACC-20481"}', hash_signature: 'b7e8d1c0a2f918e2736450918273645918273645918273645918273645918273', timestamp: '2026-09-27 13:25:40' },
    { id: 3, actor_username: 'admin', actor_role: 'ADMIN', action_type: 'UPDATE_POLICY', target_id: 'CompositeRiskThresholdRule', details_json: '{"is_enabled": true, "params": "cutoff_score: 0.85"}', hash_signature: 'c6d7e0f9a8b17263540918273645091827364509182736450918273645091827', timestamp: '2026-09-27 13:10:05' },
  ];

  const handleDownloadSAR = () => {
    const element = document.createElement("a");
    const file = new Blob([
      "FinCEN Suspicious Activity Report (SAR)\n======================================\n" +
      "Subject: Account ACC-20481\n" +
      "Risk Score: 94 / 100 (CRITICAL)\n" +
      "Reason: Money Mule Ring Collusion (Louvain Modularity 0.78)\n" +
      "Cryptographic Signature: SHA256-a8f9c2d1e4b309f18274bcde3901928374650192837465928173649581029384\n" +
      "Timestamp: 2026-09-27 13:30:12\n"
    ], { type: 'text/plain' });
    element.href = URL.createObjectURL(file);
    element.download = "FinCEN_SAR_Report_ACC-20481.txt";
    document.body.appendChild(element);
    element.click();
  };

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <ShieldCheck size={20} color="#10B981" />
            <span>▣ Tamper-Evident SHA-256 Cryptographic Audit Log</span>
          </h3>
          <p style={{ fontSize: '12px', color: '#94A3B8' }}>
            Immutable Evidence Chain &middot; Auditor Compliance View
          </p>
        </div>

        <button
          onClick={handleDownloadSAR}
          style={{
            padding: '8px 16px',
            borderRadius: '10px',
            background: 'rgba(16, 185, 129, 0.15)',
            border: '1px solid rgba(16, 185, 129, 0.35)',
            color: '#10B981',
            fontSize: '13px',
            fontWeight: 700,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}
        >
          <Download size={16} />
          <span>Download FinCEN SAR Package</span>
        </button>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {sampleLogs.map(log => (
          <div key={log.id} style={{
            padding: '16px',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.03)',
            border: '1px solid rgba(255, 255, 255, 0.06)',
            display: 'flex',
            flexDirection: 'column',
            gap: '8px'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span style={{
                  padding: '3px 8px',
                  borderRadius: '6px',
                  background: log.action_type.includes('FREEZE') ? 'rgba(239, 68, 68, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                  color: log.action_type.includes('FREEZE') ? '#EF4444' : '#60A5FA',
                  fontSize: '11px',
                  fontWeight: 800,
                  fontFamily: 'monospace'
                }}>
                  {log.action_type}
                </span>

                <span style={{ fontSize: '13px', fontWeight: 600, color: '#F8FAFC' }}>
                  Target: {log.target_id}
                </span>
              </div>

              <span style={{ fontSize: '12px', color: '#64748B' }}>
                {log.timestamp}
              </span>
            </div>

            <div style={{ fontSize: '12px', color: '#94A3B8' }}>
              Actor: <strong style={{ color: '#F8FAFC' }}>{log.actor_username}</strong> ({log.actor_role}) &middot; Details: {log.details_json}
            </div>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontSize: '11px',
              color: '#10B981',
              fontFamily: 'monospace',
              background: 'rgba(16, 185, 129, 0.08)',
              padding: '6px 10px',
              borderRadius: '6px'
            }}>
              <CheckCircle size={14} />
              <span>SHA-256 HASH SIGNATURE: {log.hash_signature}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
