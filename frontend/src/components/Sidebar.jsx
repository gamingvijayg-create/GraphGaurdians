import React from 'react';
import { 
  LayoutDashboard, 
  Search, 
  Network, 
  Bot, 
  Sliders, 
  FileText, 
  Settings, 
  ShieldAlert,
  ShieldCheck
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, userRole }) {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: LayoutDashboard, symbol: '⌂' },
    { id: 'investigations', label: 'Investigations', icon: Search, symbol: '◎' },
    { id: 'fraud_rings', label: 'Fraud Rings', icon: ShieldAlert, symbol: '◉' },
    { id: 'network_3d', label: '3D Network', icon: Network, symbol: '⬡' },
    { id: 'ai_agents', label: 'AI Agents', icon: Bot, symbol: '⚡' },
    { id: 'policy_engine', label: 'Policy Engine', icon: Sliders, symbol: '⚖' },
    { id: 'reports_audit', label: 'Reports & Audit', icon: FileText, symbol: '▣' },
    { id: 'settings', label: 'Settings', icon: Settings, symbol: '⚙' },
  ];

  return (
    <aside style={{
      width: '260px',
      height: '100vh',
      position: 'fixed',
      left: 0,
      top: 0,
      background: 'rgba(11, 15, 25, 0.85)',
      backdropFilter: 'blur(20px)',
      borderRight: '1px solid rgba(255, 255, 255, 0.08)',
      display: 'flex',
      flexDirection: 'column',
      padding: '24px 16px',
      zIndex: 50
    }}>
      {/* Brand Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '0 8px 28px 8px' }}>
        <div style={{
          width: '36px',
          height: '36px',
          borderRadius: '10px',
          background: 'linear-gradient(135deg, #3B82F6 0%, #8B5CF6 100%)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          boxShadow: '0 0 15px rgba(59, 130, 246, 0.4)'
        }}>
          <ShieldCheck size={22} color="#FFFFFF" />
        </div>
        <div>
          <h1 style={{ fontSize: '20px', fontWeight: 800, letterSpacing: '1px', color: '#F8FAFC' }}>
            FRAUD<span style={{ color: '#3B82F6' }}>X</span>
          </h1>
          <span style={{ fontSize: '11px', color: '#64748B', fontWeight: 500, letterSpacing: '0.5px' }}>
            FINANCIAL INTELLIGENCE
          </span>
        </div>
      </div>

      {/* Navigation Items */}
      <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px', flex: 1 }}>
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <div
              key={item.id}
              className={`sidebar-item ${isActive ? 'active' : ''}`}
              onClick={() => setActiveTab(item.id)}
            >
              <span style={{ fontSize: '16px', width: '20px', textAlign: 'center', opacity: 0.9 }}>
                {item.symbol}
              </span>
              <span style={{ flex: 1 }}>{item.label}</span>
              {isActive && (
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: '#3B82F6',
                  boxShadow: '0 0 8px #3B82F6'
                }} />
              )}
            </div>
          );
        })}
      </nav>

      {/* User RBAC Badge */}
      <div style={{
        marginTop: 'auto',
        padding: '12px 14px',
        borderRadius: '12px',
        background: 'rgba(255, 255, 255, 0.03)',
        border: '1px solid rgba(255, 255, 255, 0.06)',
        display: 'flex',
        alignItems: 'center',
        gap: '10px'
      }}>
        <div style={{
          width: '10px', height: '10px', borderRadius: '50%', background: '#10B981', boxShadow: '0 0 8px #10B981'
        }} />
        <div>
          <div style={{ fontSize: '12px', color: '#F8FAFC', fontWeight: 600 }}>JPMorgan SOC</div>
          <div style={{ fontSize: '11px', color: '#8B5CF6', fontWeight: 600, fontFamily: 'monospace' }}>
            ROLE: {userRole || 'ADMIN'}
          </div>
        </div>
      </div>
    </aside>
  );
}
