import React, { useState } from 'react';
import { LayoutDashboard, Target, TrendingUp, Users } from 'lucide-react';
import DeanOverviewTab from '../components/dean/DeanOverviewTab';
import DeanSDGTab from '../components/dean/DeanSDGTab';
import DeanTrendsTab from '../components/dean/DeanTrendsTab';
import DeanFacultyTab from '../components/dean/DeanFacultyTab';

export default function DeanView() {
  const [activeTab, setActiveTab] = useState('overview');

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview': return <DeanOverviewTab />;
      case 'sdgs': return <DeanSDGTab />;
      case 'trends': return <DeanTrendsTab />;
      case 'faculty': return <DeanFacultyTab />;
      default: return <DeanOverviewTab />;
    }
  };

  return (
    <div className="container" style={{ paddingBottom: 'var(--spacing-2xl)' }}>
      
      {/* Header */}
      <div style={{ marginBottom: 'var(--spacing-lg)', padding: 'var(--spacing-xl) 0' }}>
        <h1 style={{ marginBottom: 'var(--spacing-sm)' }}>Strategic Gaps & Bets</h1>
        <p className="text-muted" style={{ fontSize: 'var(--font-size-lg)' }}>
          Data-driven insights to guide faculty hiring, research investment, and donor engagement.
        </p>
      </div>

      {/* Tab Navigation */}
      <div style={{ 
        display: 'flex', 
        borderBottom: '1px solid var(--color-border)', 
        marginBottom: 'var(--spacing-lg)',
        gap: '24px'
      }}>
        <button 
          className={activeTab === 'overview' ? 'active-tab' : ''}
          onClick={() => setActiveTab('overview')}
          style={{ 
            padding: '12px 4px', 
            background: 'none', 
            border: 'none', 
            borderBottom: activeTab === 'overview' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'overview' ? 'var(--color-primary)' : 'var(--color-text-light)',
            fontWeight: activeTab === 'overview' ? 600 : 400,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '16px'
          }}
        >
          <LayoutDashboard size={18} /> Overview
        </button>
        <button 
          className={activeTab === 'sdgs' ? 'active-tab' : ''}
          onClick={() => setActiveTab('sdgs')}
          style={{ 
            padding: '12px 4px', 
            background: 'none', 
            border: 'none', 
            borderBottom: activeTab === 'sdgs' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'sdgs' ? 'var(--color-primary)' : 'var(--color-text-light)',
            fontWeight: activeTab === 'sdgs' ? 600 : 400,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '16px'
          }}
        >
          <Target size={18} /> SDG Performance
        </button>
        <button 
          className={activeTab === 'trends' ? 'active-tab' : ''}
          onClick={() => setActiveTab('trends')}
          style={{ 
            padding: '12px 4px', 
            background: 'none', 
            border: 'none', 
            borderBottom: activeTab === 'trends' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'trends' ? 'var(--color-primary)' : 'var(--color-text-light)',
            fontWeight: activeTab === 'trends' ? 600 : 400,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '16px'
          }}
        >
          <TrendingUp size={18} /> Trends
        </button>
        <button 
          className={activeTab === 'faculty' ? 'active-tab' : ''}
          onClick={() => setActiveTab('faculty')}
          style={{ 
            padding: '12px 4px', 
            background: 'none', 
            border: 'none', 
            borderBottom: activeTab === 'faculty' ? '2px solid var(--color-primary)' : '2px solid transparent',
            color: activeTab === 'faculty' ? 'var(--color-primary)' : 'var(--color-text-light)',
            fontWeight: activeTab === 'faculty' ? 600 : 400,
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            fontSize: '16px'
          }}
        >
          <Users size={18} /> Faculty Insights
        </button>
      </div>

      {/* Tab Content */}
      <div className="tab-content">
        {renderTabContent()}
      </div>

    </div>
  );
}
