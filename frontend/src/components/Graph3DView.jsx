import React, { useState, useEffect, useRef } from 'react';
import { Search, Maximize2, Filter, Layers, RefreshCw } from 'lucide-react';

export default function Graph3DView({ graphData, onSelectAccount }) {
  const [filterType, setFilterType] = useState('ALL');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedNode, setSelectedNode] = useState('ACC-20481');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const containerRef = useRef(null);

  const filterPills = [
    { id: 'ALL', label: 'All' },
    { id: 'ACCOUNTS', label: 'Accounts' },
    { id: 'DEVICES', label: 'Devices' },
    { id: 'IPS', label: 'IPs' },
    { id: 'TRANSACTIONS', label: 'Transactions' },
  ];

  // Dummy 3D Canvas visual node layout
  const nodes = graphData?.nodes || [
    { id: 'ACC-20481', label: 'ACC-20481', type: 'ACCOUNT', risk: 94, is_fraud: true, x: 50, y: 30 },
    { id: 'DEV-9812A', label: 'Device DEV-9812A', type: 'DEVICE', risk: 85, is_fraud: true, x: 25, y: 60 },
    { id: 'IP-192.168.1.45', label: 'IP 192.168.1.45', type: 'IP', risk: 88, is_fraud: true, x: 75, y: 60 },
    { id: 'ACC-10932', label: 'ACC-10932', type: 'ACCOUNT', risk: 78, is_fraud: true, x: 50, y: 85 },
    { id: 'ACC-30491', label: 'ACC-30491', type: 'ACCOUNT', risk: 42, is_fraud: false, x: 15, y: 25 },
    { id: 'ACC-50912', label: 'ACC-50912', type: 'ACCOUNT', risk: 12, is_fraud: false, x: 85, y: 25 },
  ];

  const handleNodeClick = (nodeId) => {
    setSelectedNode(nodeId);
    if (onSelectAccount) {
      onSelectAccount(nodeId);
    }
  };

  const filteredNodes = nodes.filter(n => {
    if (filterType === 'ACCOUNTS') return n.type === 'ACCOUNT';
    if (filterType === 'DEVICES') return n.type === 'DEVICE';
    if (filterType === 'IPS') return n.type === 'IP';
    if (searchTerm) return n.id.toLowerCase().includes(searchTerm.toLowerCase());
    return true;
  });

  return (
    <div className="glass-card" style={{ padding: '24px', position: 'relative', overflow: 'hidden' }}>
      {/* Header Bar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '18px', flexWrap: 'wrap', gap: '12px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 700, color: '#F8FAFC', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span>⬡ 3D Network Fraud Topology</span>
          </h3>
          <p style={{ fontSize: '12px', color: '#94A3B8' }}>
            glowing 3D wire connections &amp; multi-tier account linkage graph
          </p>
        </div>

        {/* Filter Pills */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', background: 'rgba(0, 0, 0, 0.4)', padding: '4px', borderRadius: '12px', border: '1px solid rgba(255, 255, 255, 0.08)' }}>
          {filterPills.map(pill => (
            <button
              key={pill.id}
              onClick={() => setFilterType(pill.id)}
              style={{
                padding: '6px 14px',
                borderRadius: '8px',
                border: 'none',
                background: filterType === pill.id ? '#3B82F6' : 'transparent',
                color: filterType === pill.id ? '#FFFFFF' : '#94A3B8',
                fontSize: '12px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              [ {pill.label} ]
            </button>
          ))}
        </div>

        {/* Search & Fullscreen */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} color="#94A3B8" style={{ position: 'absolute', left: '10px', top: '9px' }} />
            <input
              type="text"
              placeholder="🔎 Search Account / IP..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              style={{
                padding: '6px 12px 6px 30px',
                borderRadius: '8px',
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#F8FAFC',
                fontSize: '12px',
                outline: 'none',
                width: '180px'
              }}
            />
          </div>

          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            style={{
              padding: '6px 10px',
              borderRadius: '8px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid rgba(255, 255, 255, 0.1)',
              color: '#94A3B8',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              fontSize: '12px'
            }}
          >
            <Maximize2 size={14} />
            <span>⛶ Fullscreen</span>
          </button>
        </div>
      </div>

      {/* 3D Wire Network Canvas Representation */}
      <div
        ref={containerRef}
        style={{
          width: '100%',
          height: isFullscreen ? '75vh' : '440px',
          background: 'radial-gradient(circle at center, #0F172A 0%, #070A12 100%)',
          borderRadius: '12px',
          border: '1px solid rgba(59, 130, 246, 0.20)',
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden'
        }}
      >
        {/* SVG Wire Lines */}
        <svg style={{ position: 'absolute', width: '100%', height: '100%', pointerEvents: 'none' }}>
          <line x1="50%" y1="30%" x2="25%" y2="60%" stroke="#EF4444" strokeWidth="2.5" strokeDasharray="4" />
          <line x1="50%" y1="30%" x2="75%" y2="60%" stroke="#EF4444" strokeWidth="2.5" strokeDasharray="4" />
          <line x1="25%" y1="60%" x2="75%" y2="60%" stroke="#F59E0B" strokeWidth="2" />
          <line x1="25%" y1="60%" x2="50%" y2="85%" stroke="#EF4444" strokeWidth="2.5" />
          <line x1="75%" y1="60%" x2="50%" y2="85%" stroke="#EF4444" strokeWidth="2.5" />
          <line x1="50%" y1="30%" x2="15%" y2="25%" stroke="#3B82F6" strokeWidth="1.5" opacity="0.4" />
          <line x1="50%" y1="30%" x2="85%" y2="25%" stroke="#3B82F6" strokeWidth="1.5" opacity="0.4" />
        </svg>

        {/* Nodes */}
        {filteredNodes.map((node) => {
          const isSelected = selectedNode === node.id;
          const isFraud = node.is_fraud;
          return (
            <div
              key={node.id}
              onClick={() => handleNodeClick(node.id)}
              style={{
                position: 'absolute',
                left: `${node.x}%`,
                top: `${node.y}%`,
                transform: 'translate(-50%, -50%)',
                cursor: 'pointer',
                textAlign: 'center',
                zIndex: 10
              }}
            >
              {/* Glowing Node Marker */}
              <div style={{
                width: isSelected ? '32px' : '24px',
                height: isSelected ? '32px' : '24px',
                borderRadius: node.type === 'DEVICE' ? '4px' : '50%',
                background: isFraud ? 'linear-gradient(135deg, #EF4444 0%, #DC2626 100%)' : '#3B82F6',
                border: isSelected ? '3px solid #FFFFFF' : '2px solid rgba(255, 255, 255, 0.4)',
                boxShadow: isFraud ? '0 0 20px #EF4444' : '0 0 15px #3B82F6',
                margin: '0 auto 6px auto',
                transition: 'all 0.25s ease'
              }} />

              {/* Node Label */}
              <div style={{
                fontSize: '11px',
                fontWeight: 700,
                color: '#F8FAFC',
                background: 'rgba(15, 23, 42, 0.85)',
                padding: '2px 8px',
                borderRadius: '6px',
                border: `1px solid ${isFraud ? '#EF4444' : '#3B82F6'}`,
                whiteSpace: 'nowrap'
              }}>
                {node.label}
              </div>
            </div>
          );
        })}

        {/* Bottom Diagram Legend */}
        <div style={{
          position: 'absolute',
          bottom: '12px',
          left: '16px',
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          background: 'rgba(11, 15, 25, 0.85)',
          padding: '6px 14px',
          borderRadius: '8px',
          border: '1px solid rgba(255, 255, 255, 0.08)',
          fontSize: '11px',
          color: '#94A3B8'
        }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#EF4444' }} /> Flagged Fraud Account
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '4px', background: '#F59E0B' }} /> Shared Device Fingerprint
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: '#3B82F6' }} /> Normal Account
          </span>
        </div>
      </div>
    </div>
  );
}
