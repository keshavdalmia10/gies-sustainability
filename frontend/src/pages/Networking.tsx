import React, { useState } from 'react';
import ProfileUpload from '../components/networking/ProfileUpload';
import NetworkChatbot from '../components/networking/NetworkChatbot';
import NetworkGraph from '../components/networking/NetworkGraph';

const Networking: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'profile' | 'graph'>('profile');
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
      
      <div className="card mb-4" style={{ padding: 'var(--spacing-sm)', display: 'inline-flex', gap: 'var(--spacing-sm)', backgroundColor: 'var(--color-surface)' }}>
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
      </div>

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
        
        <div style={{ gridColumn: '2 / 3', height: '600px' }}>
          <NetworkChatbot onGraphUpdate={handleGraphUpdate} />
        </div>
      </div>
    </div>
  );
};

export default Networking;
