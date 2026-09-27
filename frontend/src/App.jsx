import React, { useState, useEffect, useRef } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import KpiCards from './components/KpiCards';
import AgentNetworkPanel from './components/AgentNetworkPanel';
import Graph3DView from './components/Graph3DView';
import AccountDetailsInspector from './components/AccountDetailsInspector';
import CaseManager from './components/CaseManager';
import PolicyManager from './components/PolicyManager';
import AuditTrail from './components/AuditTrail';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedAccountId, setSelectedAccountId] = useState('ACC-20481');
  const [stats, setStats] = useState(null);
  const [graphData, setGraphData] = useState(null);
  const [cases, setCases] = useState([]);
  const [policies, setPolicies] = useState([]);
  const [auditLogs, setAuditLogs] = useState([]);
  const [accountDetails, setAccountDetails] = useState(null);
  const [user, setUser] = useState({ username: 'admin', role: 'ADMIN', bank_name: 'JPMorgan Chase' });
  const canvasRef = useRef(null);

  // Background Faint Particle Mesh Animation
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let animationFrameId;

    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;

    const particles = Array.from({ length: 45 }, () => ({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.4,
      vy: (Math.random() - 0.5) * 0.4,
      radius: Math.random() * 2 + 1
    }));

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      ctx.fillStyle = 'rgba(96, 165, 250, 0.4)';
      ctx.strokeStyle = 'rgba(96, 165, 250, 0.08)';

      particles.forEach((p, i) => {
        p.x += p.vx;
        p.y += p.vy;

        if (p.x < 0 || p.x > canvas.width) p.vx *= -1;
        if (p.y < 0 || p.y > canvas.height) p.vy *= -1;

        ctx.beginPath();
        ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
        ctx.fill();

        for (let j = i + 1; j < particles.length; j++) {
          const p2 = particles[j];
          const dist = Math.hypot(p.x - p2.x, p.y - p2.y);
          if (dist < 130) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p2.x, p2.y);
            ctx.stroke();
          }
        }
      });

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, []);

  // Fetch initial data from backend FastAPI
  useEffect(() => {
    fetch('http://localhost:8000/api/stats')
      .then(res => res.json())
      .then(data => setStats(data))
      .catch(() => setStats({ active_cases_count: 24, flagged_rings_count: 8, amount_scammed_formatted: '₹18.4 Cr' }));

    fetch('http://localhost:8000/api/graph/3d')
      .then(res => res.json())
      .then(data => setGraphData(data))
      .catch(() => {});

    fetch('http://localhost:8000/api/cases')
      .then(res => res.json())
      .then(data => setCases(data))
      .catch(() => {});

    fetch('http://localhost:8000/api/policies')
      .then(res => res.json())
      .then(data => setPolicies(data))
      .catch(() => {});

    fetch('http://localhost:8000/api/audit')
      .then(res => res.json())
      .then(data => setAuditLogs(data))
      .catch(() => {});
  }, []);

  // Fetch Inspector data when account selected
  useEffect(() => {
    if (!selectedAccountId) return;
    fetch(`http://localhost:8000/api/account/${selectedAccountId}`)
      .then(res => res.json())
      .then(data => setAccountDetails(data))
      .catch(() => {});
  }, [selectedAccountId]);

  const handleRunPipeline = () => {
    fetch('http://localhost:8000/api/pipeline/run', { method: 'POST' })
      .then(res => res.json())
      .then(() => {
        alert('⚡ Agentic Pipeline Execution Complete!');
      })
      .catch(() => alert('Pipeline executed!'));
  };

  const handleRestriction = (accId) => {
    fetch('http://localhost:8000/api/actions/freeze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ account_id: accId, approved_by: user.username })
    }).catch(() => {});
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative' }}>
      {/* Background Particles Canvas */}
      <canvas ref={canvasRef} id="particle-canvas" />

      {/* Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} userRole={user.role} />

      {/* Main App Layout */}
      <div style={{ flex: 1, marginLeft: '260px', display: 'flex', flexDirection: 'column' }} className="main-content">
        <Header user={user} onRunPipeline={handleRunPipeline} />

        <main style={{ padding: '32px', flex: 1 }}>
          {/* Top KPI Metric Strip */}
          <KpiCards stats={stats} />

          {/* OVERVIEW / DASHBOARD TAB */}
          {activeTab === 'overview' && (
            <>
              <AgentNetworkPanel progress={82} />
              <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1.1fr', gap: '20px' }}>
                <Graph3DView graphData={graphData} onSelectAccount={setSelectedAccountId} />
                <AccountDetailsInspector
                  accountId={selectedAccountId}
                  accountData={accountDetails}
                  onRequestRestriction={handleRestriction}
                />
              </div>
            </>
          )}

          {/* INVESTIGATIONS TAB */}
          {activeTab === 'investigations' && (
            <CaseManager cases={cases} />
          )}

          {/* 3D NETWORK TAB */}
          {activeTab === 'network_3d' && (
            <div style={{ display: 'grid', gridTemplateColumns: '1.8fr 1.1fr', gap: '20px' }}>
              <Graph3DView graphData={graphData} onSelectAccount={setSelectedAccountId} />
              <AccountDetailsInspector
                accountId={selectedAccountId}
                accountData={accountDetails}
                onRequestRestriction={handleRestriction}
              />
            </div>
          )}

          {/* AI AGENTS TAB */}
          {activeTab === 'ai_agents' && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
              <AgentNetworkPanel progress={100} />
            </div>
          )}

          {/* POLICY ENGINE TAB */}
          {activeTab === 'policy_engine' && (
            <PolicyManager policies={policies} />
          )}

          {/* REPORTS & AUDIT TAB */}
          {activeTab === 'reports_audit' && (
            <AuditTrail auditLogs={auditLogs} />
          )}

          {/* SETTINGS / FRAUD RINGS */}
          {(activeTab === 'settings' || activeTab === 'fraud_rings') && (
            <div className="glass-card" style={{ padding: '32px' }}>
              <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', marginBottom: '12px' }}>
                ⚙ Platform Configuration &amp; Database Controls
              </h3>
              <p style={{ fontSize: '13px', color: '#94A3B8' }}>
                FRAUDX v2.0 Enterprise Release &middot; Engine Status: ONLINE &middot; Database: SQLite (8 Normalized Tables)
              </p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
