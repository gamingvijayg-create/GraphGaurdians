import React, { useState } from 'react';
import { Search, Plus, UserCheck, ShieldAlert, CheckCircle2, Clock } from 'lucide-react';

export default function CaseManager({ cases = [], onUpdateStatus }) {
  const [activeCases, setActiveCases] = useState(cases.length > 0 ? cases : [
    { case_id: 'CASE-20481', title: 'Suspicious Mule Ring Collusion', account_id: 'ACC-20481', priority: 'CRITICAL', status: 'UNDER_INVESTIGATION', assigned_to: 'lead_investigator' },
    { case_id: 'CASE-10932', title: 'Rapid Device Swap & Outflow', account_id: 'ACC-10932', priority: 'HIGH', status: 'RESTRICTION_PENDING', assigned_to: 'soc_analyst' },
    { case_id: 'CASE-30491', title: 'High Velocity Micro-Transfers', account_id: 'ACC-30491', priority: 'MEDIUM', status: 'NEW', assigned_to: 'Unassigned' },
  ]);

  const columns = [
    { id: 'NEW', label: 'New Alerts', color: '#3B82F6' },
    { id: 'UNDER_INVESTIGATION', label: 'Under Investigation', color: '#F59E0B' },
    { id: 'RESTRICTION_PENDING', label: 'Restriction Pending', color: '#EF4444' },
    { id: 'CLOSED', label: 'Closed / Resolved', color: '#10B981' },
  ];

  const moveStatus = (caseId, newStatus) => {
    setActiveCases(prev => prev.map(c => c.case_id === caseId ? { ...c, status: newStatus } : c));
    if (onUpdateStatus) {
      onUpdateStatus(caseId, newStatus);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC' }}>
            ◎ Case Management Lifecycle Board
          </h3>
          <p style={{ fontSize: '12px', color: '#94A3B8' }}>
            Role-Based Access Control &middot; Active Investigation Queue
          </p>
        </div>

        <button style={{
          padding: '8px 16px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
          border: 'none',
          color: '#FFFFFF',
          fontSize: '13px',
          fontWeight: 600,
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          gap: '6px'
        }}>
          <Plus size={16} />
          <span>New Case</span>
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        {columns.map(col => {
          const colCases = activeCases.filter(c => c.status === col.id);
          return (
            <div key={col.id} style={{
              background: 'rgba(15, 23, 42, 0.60)',
              borderRadius: '12px',
              padding: '16px',
              border: '1px solid rgba(255, 255, 255, 0.05)',
              display: 'flex',
              flexDirection: 'column',
              minHeight: '340px'
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '14px', borderBottom: `2px solid ${col.color}`, paddingBottom: '8px' }}>
                <span style={{ fontSize: '13px', fontWeight: 700, color: col.color }}>{col.label}</span>
                <span style={{ fontSize: '11px', fontWeight: 800, background: 'rgba(255, 255, 255, 0.1)', padding: '2px 6px', borderRadius: '6px', color: '#F8FAFC' }}>
                  {colCases.length}
                </span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', flex: 1 }}>
                {colCases.map(item => (
                  <div key={item.case_id} style={{
                    padding: '14px',
                    borderRadius: '10px',
                    background: 'rgba(255, 255, 255, 0.03)',
                    border: '1px solid rgba(255, 255, 255, 0.08)',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '8px'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontSize: '11px', fontWeight: 700, fontFamily: 'monospace', color: '#A78BFA' }}>
                        {item.case_id}
                      </span>
                      <span style={{
                        fontSize: '10px',
                        fontWeight: 800,
                        padding: '2px 6px',
                        borderRadius: '4px',
                        background: item.priority === 'CRITICAL' ? '#EF4444' : item.priority === 'HIGH' ? '#F59E0B' : '#3B82F6',
                        color: '#FFFFFF'
                      }}>
                        {item.priority}
                      </span>
                    </div>

                    <div style={{ fontSize: '13px', fontWeight: 600, color: '#F8FAFC' }}>
                      {item.title}
                    </div>

                    <div style={{ fontSize: '11px', color: '#64748B' }}>
                      Account: {item.account_id}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '4px' }}>
                      <span style={{ fontSize: '10px', color: '#94A3B8' }}>👤 {item.assigned_to}</span>

                      {col.id === 'NEW' && (
                        <button onClick={() => moveStatus(item.case_id, 'UNDER_INVESTIGATION')} style={{ fontSize: '10px', background: '#3B82F6', border: 'none', color: '#FFF', padding: '2px 6px', borderRadius: '4px', cursor: 'pointer' }}>
                          Investigate &rarr;
                        </button>
                      )}
                      {col.id === 'UNDER_INVESTIGATION' && (
                        <button onClick={() => moveStatus(item.case_id, 'RESTRICTION_PENDING')} style={{ fontSize: '10px', background: '#EF4444', border: 'none', color: '#FFF', padding: '2px 6px', borderRadius: '4px', cursor: 'pointer' }}>
                          Restrict &rarr;
                        </button>
                      )}
                      {col.id === 'RESTRICTION_PENDING' && (
                        <button onClick={() => moveStatus(item.case_id, 'CLOSED')} style={{ fontSize: '10px', background: '#10B981', border: 'none', color: '#FFF', padding: '2px 6px', borderRadius: '4px', cursor: 'pointer' }}>
                          Close &rarr;
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
