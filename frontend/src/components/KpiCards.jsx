import React from 'react';
import { ShieldAlert, AlertTriangle, IndianRupee, Cpu } from 'lucide-react';

export default function KpiCards({ stats }) {
  const cards = [
    {
      title: 'Active Cases',
      value: stats?.active_cases_count || '24',
      change: '↑ 12%',
      sub: 'Open SOC Queue',
      icon: ShieldAlert,
      color: '#3B82F6',
      badgeClass: 'badge-blue'
    },
    {
      title: 'Fraud Rings',
      value: String(stats?.flagged_rings_count || 8).padStart(2, '0'),
      change: '↑ 3 detected',
      sub: 'Colluding Mule Rings',
      icon: AlertTriangle,
      color: '#EF4444',
      badgeClass: 'badge-red'
    },
    {
      title: 'Amount at Risk',
      value: stats?.amount_scammed_formatted || '₹18.4 Cr',
      change: 'This month',
      sub: 'Flagged Ring Volume',
      icon: IndianRupee,
      color: '#F59E0B',
      badgeClass: 'badge-amber'
    },
    {
      title: 'AI Confidence',
      value: `${stats?.ai_confidence_score || 94.2}%`,
      change: '+2.4%',
      sub: 'Composite Graph ML',
      icon: Cpu,
      color: '#8B5CF6',
      badgeClass: 'badge-violet'
    }
  ];

  return (
    <div style={{
      display: 'grid',
      gridTemplateColumns: 'repeat(4, 1fr)',
      gap: '20px',
      marginBottom: '28px'
    }}>
      {cards.map((card, idx) => {
        const Icon = card.icon;
        return (
          <div key={idx} className="glass-card" style={{ padding: '20px' }}>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
              <span style={{ fontSize: '13px', fontWeight: 600, color: '#94A3B8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                {card.title}
              </span>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '10px',
                background: `${card.color}15`,
                border: `1px solid ${card.color}30`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}>
                <Icon size={18} color={card.color} />
              </div>
            </div>

            <div style={{ fontSize: '28px', fontWeight: 800, color: '#F8FAFC', marginBottom: '8px', fontFamily: 'Inter, sans-serif' }}>
              {card.value}
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '12px' }}>
              <span style={{
                color: card.color,
                fontWeight: 700,
                background: `${card.color}15`,
                padding: '2px 8px',
                borderRadius: '6px'
              }}>
                {card.change}
              </span>
              <span style={{ color: '#64748B' }}>{card.sub}</span>
            </div>
          </div>
        );
      })}
    </div>
  );
}
