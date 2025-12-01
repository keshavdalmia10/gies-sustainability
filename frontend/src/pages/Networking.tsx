import React, { useState } from 'react';
import ProfileUpload from '../components/networking/ProfileUpload';
import NetworkChatbot from '../components/networking/NetworkChatbot';
import NetworkGraph from '../components/networking/NetworkGraph';
import Leaderboard from '../components/networking/Leaderboard';
import DonorSearch from '../components/networking/DonorSearch';
import DonorPortal from '../components/networking/DonorPortal';
import FacultyUpdate from '../components/networking/FacultyUpdate';

const Networking: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'graph' | 'funding' | 'donors' | 'faculty'>('profile');
  const [graphData, setGraphData] = useState<any>(null);

  const handleGraphUpdate = (data: any) => {
    setGraphData(data);
    // Switch to graph tab if not already
    if (activeTab !== 'graph') {
      setActiveTab('graph');
    }
  };

  return (
    <div className="container" style={{ paddingBottom: 'var(--spacing-2xl)' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--spacing-xl)' }}>
        <h1 className="mb-0">Networking & Collaboration</h1>
      </div>
      
      <div className="card mb-4" style={{ padding: 'var(--spacing-sm)', display: 'inline-flex', gap: 'var(--spacing-sm)', backgroundColor: 'var(--color-surface)', flexWrap: 'wrap' }}>
        <button
          className={`btn ${activeTab === 'profile' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('profile')}
          style={{ border: 'none' }}
        >
          Create Profile
        </button>
        <button
          className={`btn ${activeTab === 'graph' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('graph')}
          style={{ border: 'none' }}
        >
          Network Analysis
        </button>
        <button
          className={`btn ${activeTab === 'funding' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('funding')}
          style={{ border: 'none' }}
        >
          Find Funding
        </button>
        <button
          className={`btn ${activeTab === 'donors' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('donors')}
          style={{ border: 'none' }}
        >
          For Donors
        </button>
        <button
          className={`btn ${activeTab === 'faculty' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => setActiveTab('faculty')}
          style={{ border: 'none' }}
        >
          Faculty Updates
        </button>
      </div>

      {activeTab === 'funding' ? (
        <DonorSearch />
      ) : activeTab === 'donors' ? (
        <DonorPortal />
      ) : activeTab === 'faculty' ? (
        <FacultyUpdate />
      ) : (
        <div className="grid grid-3" style={{ gridTemplateColumns: '2fr 1fr', gap: 'var(--spacing-xl)' }}>
          {activeTab === 'profile' && (
            <div style={{ gridColumn: '1 / 2' }}>
              <ProfileUpload />
            </div>
          )}
          
          {activeTab === 'graph' && (
            <div style={{ gridColumn: '1 / 2', minHeight: '500px' }}>
              <NetworkGraph data={graphData} />
            </div>
          )}
          
          <div style={{ gridColumn: '2 / 3', display: 'flex', flexDirection: 'column', gap: 'var(--spacing-xl)' }}>
            <Leaderboard />
            <div style={{ height: '500px' }}>
              <NetworkChatbot onGraphUpdate={handleGraphUpdate} />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Networking;
