import React from 'react';
import { Bell, UserCheck, ShieldCheck, Activity } from 'lucide-react';

export default function Header({ user, onRunPipeline }) {
  return (
    <header style={{
      height: '70px',
      padding: '0 32px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      borderBottom: '1px solid rgba(255, 255, 255, 0.08)',
      background: 'rgba(11, 15, 25, 0.60)',
      backdropFilter: 'blur(16px)',
      position: 'sticky',
      top: 0,
      zIndex: 40
    }}>
      {/* Greeting & Title */}
      <div>
        <h2 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC' }}>
          Good Morning, <span style={{ color: '#60A5FA' }}>{user?.username || 'Investigator'}</span>
        </h2>
        <p style={{ fontSize: '12px', color: '#94A3B8' }}>
          Fraud Intelligence Center &middot; {user?.bank_name || 'JPMorgan Chase'}
        </p>
      </div>

      {/* Status & Actions */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        {/* Upload CSV File Button */}
        <label
          style={{
            padding: '8px 16px',
            borderRadius: '10px',
            background: 'rgba(255, 255, 255, 0.08)',
            border: '1px solid rgba(255, 255, 255, 0.15)',
            color: '#F8FAFC',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'all 0.2s ease'
          }}
        >
          <span>📤 Upload CSV Dataset</span>
          <input
            type="file"
            accept=".csv"
            style={{ display: 'none' }}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                const file = e.target.files[0];
                const formData = new FormData();
                formData.append('file', file);
                fetch('http://localhost:8000/api/pipeline/upload', {
                  method: 'POST',
                  body: formData
                })
                .then(res => res.json())
                .then(data => {
                  alert(`✅ CSV Uploaded! Processed ${data.txn_count} transactions. Graph updated!`);
                  window.location.reload();
                })
                .catch(err => alert('Error processing CSV file'));
              }
            }}
          />
        </label>

        {/* Run Pipeline Button */}
        <button
          onClick={onRunPipeline}
          style={{
            padding: '8px 16px',
            borderRadius: '10px',
            background: 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)',
            color: '#FFFFFF',
            border: 'none',
            fontSize: '13px',
            fontWeight: 600,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            boxShadow: '0 4px 14px rgba(59, 130, 246, 0.35)',
            transition: 'all 0.2s ease'
          }}
        >
          <Activity size={16} />
          <span>⚡ Run Agent Pipeline</span>
        </button>

        {/* System Online Badge */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          borderRadius: '20px',
          background: 'rgba(16, 185, 129, 0.12)',
          border: '1px solid rgba(16, 185, 129, 0.30)',
          color: '#10B981',
          fontSize: '12px',
          fontWeight: 600
        }}>
          <Bell size={14} className="pulse-badge" />
          <span>System Online</span>
        </div>

        {/* User Profile */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '6px 12px',
          borderRadius: '12px',
          background: 'rgba(255, 255, 255, 0.05)',
          border: '1px solid rgba(255, 255, 255, 0.08)'
        }}>
          <div style={{
            width: '28px',
            height: '28px',
            borderRadius: '50%',
            background: '#8B5CF6',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF',
            fontWeight: 700,
            fontSize: '12px'
          }}>
            👤
          </div>
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontSize: '12px', fontWeight: 600, color: '#F8FAFC' }}>
              {user?.username || 'admin'}
            </div>
            <div style={{ fontSize: '10px', color: '#A78BFA' }}>
              {user?.role || 'ADMIN'}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
