import React from 'react';
import { Bot, CheckCircle2, Loader2, Clock, Sparkles } from 'lucide-react';

export default function AgentNetworkPanel({ progress = 82 }) {
  const agents = [
    { name: 'Fraud Detection Agent', status: 'Complete', icon: CheckCircle2, color: '#10B981' },
    { name: 'Entity Linking Agent', status: 'Complete', icon: CheckCircle2, color: '#10B981' },
    { name: 'Graph Analysis Agent', status: 'Running', icon: Loader2, color: '#3B82F6', spin: true },
    { name: 'Risk Assessment Agent', status: 'Waiting', icon: Clock, color: '#64748B' },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 1fr', gap: '20px', marginBottom: '28px' }}>
      {/* Agent Network Box */}
      <div className="glass-card" style={{ padding: '22px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '18px' }}>
          <Bot size={20} color="#8B5CF6" />
          <h3 style={{ fontSize: '16px', fontWeight: 700, color: '#F8FAFC' }}>
            ● Agent Network Execution State
          </h3>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {agents.map((ag, idx) => {
            const Icon = ag.icon;
            return (
              <div
                key={idx}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  padding: '10px 14px',
                  borderRadius: '10px',
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.05)'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: ag.color }} />
                  <span style={{ fontSize: '14px', color: '#F8FAFC', fontWeight: 500 }}>{ag.name}</span>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: ag.color, fontSize: '13px', fontWeight: 600 }}>
                  <Icon size={16} className={ag.spin ? 'pulse-badge' : ''} />
                  <span>{ag.status}</span>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Current Investigation Progress */}
      <div className="glass-card" style={{ padding: '22px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
            <span style={{ fontSize: '14px', fontWeight: 700, color: '#F8FAFC' }}>Current Investigation</span>
            <span style={{ fontSize: '12px', color: '#A78BFA', fontWeight: 600 }}>Live Feed</span>
          </div>

          <p style={{ fontSize: '13px', color: '#94A3B8', marginBottom: '16px' }}>
            Analyzing <strong style={{ color: '#F8FAFC' }}>1,284 transactions</strong> across PaySim stream...
          </p>

          {/* Progress Bar */}
          <div style={{ marginBottom: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', color: '#94A3B8', marginBottom: '6px' }}>
              <span>Pipeline Stage 3/4</span>
              <span style={{ color: '#3B82F6', fontWeight: 700 }}>{progress}%</span>
            </div>
            <div style={{ height: '10px', borderRadius: '6px', background: 'rgba(255, 255, 255, 0.1)', overflow: 'hidden' }}>
              <div style={{
                height: '100%',
                width: `${progress}%`,
                background: 'linear-gradient(90deg, #3B82F6 0%, #8B5CF6 100%)',
                borderRadius: '6px',
                transition: 'width 0.4s ease'
              }} />
            </div>
          </div>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '10px 12px',
          borderRadius: '10px',
          background: 'rgba(239, 68, 68, 0.10)',
          border: '1px solid rgba(239, 68, 68, 0.25)',
          color: '#EF4444',
          fontSize: '13px',
          fontWeight: 600
        }}>
          <Sparkles size={16} />
          <span>12 suspicious relationships identified in Ring #1</span>
        </div>
      </div>
    </div>
  );
}
