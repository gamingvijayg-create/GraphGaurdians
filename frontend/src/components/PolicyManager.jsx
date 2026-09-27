import React, { useState } from 'react';
import { Sliders, ToggleLeft, ToggleRight, Check, AlertCircle } from 'lucide-react';

export default function PolicyManager({ policies = [], onUpdatePolicy }) {
  const [ruleList, setRuleList] = useState(policies.length > 0 ? policies : [
    { id: 1, rule_name: 'VelocityRule', category: 'TRANSACTION', description: 'Flags accounts with over 10 txns within 5 mins across shared IP', is_enabled: 1, parameters_json: '{"max_txns": 10, "window_minutes": 5}' },
    { id: 2, rule_name: 'SharedDeviceRule', category: 'HARDWARE', description: 'Flags hardware fingerprints shared across 3 or more accounts', is_enabled: 1, parameters_json: '{"max_accounts_per_device": 3}' },
    { id: 3, rule_name: 'HighRiskOutflowRule', category: 'AMOUNT', description: 'Triggers critical alert on outbound transfers exceeding threshold within 1 hour', is_enabled: 1, parameters_json: '{"max_amount": 1000000, "window_hours": 1}' },
    { id: 4, rule_name: 'CompositeRiskThresholdRule', category: 'ML_SCORE', description: 'Auto-routes account to restriction pending queue if risk score > cutoff', is_enabled: 1, parameters_json: '{"cutoff_score": 0.85}' },
  ]);

  const toggleRule = (ruleId) => {
    setRuleList(prev => prev.map(r => r.id === ruleId ? { ...r, is_enabled: r.is_enabled ? 0 : 1 } : r));
    if (onUpdatePolicy) {
      const target = ruleList.find(r => r.id === ruleId);
      onUpdatePolicy(ruleId, !target.is_enabled, target.parameters_json);
    }
  };

  return (
    <div className="glass-card" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '20px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Sliders size={20} color="#8B5CF6" />
            <span>⚖ Dynamic Policy &amp; Rules Configurator Engine</span>
          </h3>
          <p style={{ fontSize: '12px', color: '#94A3B8' }}>
            Configure real-time automated fraud triggers and ML decision parameters
          </p>
        </div>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {ruleList.map(rule => (
          <div key={rule.id} style={{
            padding: '18px',
            borderRadius: '12px',
            background: 'rgba(255, 255, 255, 0.03)',
            border: `1px solid ${rule.is_enabled ? 'rgba(59, 130, 246, 0.30)' : 'rgba(255, 255, 255, 0.06)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                <span style={{ fontSize: '16px', fontWeight: 800, color: '#F8FAFC', fontFamily: 'monospace' }}>
                  {rule.rule_name}
                </span>
                <span style={{
                  fontSize: '10px',
                  fontWeight: 800,
                  padding: '2px 8px',
                  borderRadius: '6px',
                  background: rule.category === 'ML_SCORE' ? 'rgba(139, 92, 246, 0.2)' : 'rgba(59, 130, 246, 0.2)',
                  color: rule.category === 'ML_SCORE' ? '#A78BFA' : '#60A5FA'
                }}>
                  {rule.category}
                </span>
              </div>
              <p style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '8px' }}>
                {rule.description}
              </p>
              <div style={{ fontSize: '11px', color: '#64748B', fontFamily: 'monospace' }}>
                PARAMETERS: {rule.parameters_json}
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
              <span style={{ fontSize: '12px', fontWeight: 700, color: rule.is_enabled ? '#10B981' : '#64748B' }}>
                {rule.is_enabled ? 'ENABLED' : 'DISABLED'}
              </span>
              <button
                onClick={() => toggleRule(rule.id)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: rule.is_enabled ? '#3B82F6' : '#64748B' }}
              >
                {rule.is_enabled ? <ToggleRight size={32} /> : <ToggleLeft size={32} />}
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
