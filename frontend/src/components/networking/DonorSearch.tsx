import React, { useState } from 'react';
import { Search, ExternalLink, Building, Globe, Mail } from 'lucide-react';
import api from '../../services/api';

interface DonorMatch {
  name: string;
  type: string;
  match_reason: string;
  website: string;
  contact_info: string;
}

const DonorSearch: React.FC = () => {
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState<DonorMatch[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!description.trim()) return;
    
    setLoading(true);
    setSearched(true);
    setMatches([]); // Clear previous results
    
    try {
      const response = await api.post('/donors/search', { project_description: description });
      setMatches(Array.isArray(response.data?.matches) ? response.data.matches : []);
    } catch (error) {
      console.error('Error:', error);
      setMatches([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Search Section */}
      <div className="card" style={{ padding: '2rem' }}>
        <div className="text-center" style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Find Funding for Your Impact</h2>
          <p className="text-muted">Describe your project idea, and our AI will match you with real-world donors, grants, and foundations.</p>
        </div>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <textarea
            className="form-control"
            rows={4}
            placeholder="e.g., I want to build a low-cost water filtration system using locally sourced materials for rural communities in Southeast Asia..."
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            style={{ fontSize: '1.1rem', padding: '1rem' }}
          />
          <button 
            className="btn btn-primary" 
            onClick={handleSearch}
            disabled={loading || !description.trim()}
            style={{ alignSelf: 'center', padding: '0.75rem 2rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {loading ? (
              <>Searching...</>
            ) : (
              <>
                <Search size={20} />
                Find Donors
              </>
            )}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {searched && (
        <div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>
            {loading ? 'Analyzing your project...' : matches.length > 0 ? `Found ${matches.length} Potential Donors` : 'No matches found. Try a more detailed description.'}
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
            {matches.map((donor, index) => (
              <div key={index} className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
                <div className="card-header" style={{ borderBottom: '1px solid var(--color-border)', paddingBottom: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h4 style={{ fontSize: '1.2rem', fontWeight: 600, margin: 0 }}>{donor.name}</h4>
                      <span className="badge" style={{ marginTop: '0.5rem', backgroundColor: 'var(--color-surface)' }}>{donor.type}</span>
                    </div>
                    <Building size={24} className="text-muted" />
                  </div>
                </div>
                
                <div style={{ padding: '1.5rem', flex: 1 }}>
                  <h5 style={{ fontSize: '0.9rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>Why it's a match</h5>
                  <p style={{ fontSize: '0.95rem', lineHeight: 1.6 }}>{donor.match_reason}</p>
                </div>
                
                <div style={{ padding: '1rem 1.5rem', backgroundColor: 'var(--color-surface)', borderTop: '1px solid var(--color-border)', display: 'flex', flexDirection: 'column', gap: '0.5rem', borderBottomLeftRadius: 'var(--radius-md)', borderBottomRightRadius: 'var(--radius-md)' }}>
                  <a href={donor.website} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-primary)', textDecoration: 'none', fontSize: '0.9rem' }}>
                    <Globe size={16} />
                    Visit Website <ExternalLink size={12} />
                  </a>
                  {donor.contact_info && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text-muted)', fontSize: '0.9rem' }}>
                      <Mail size={16} />
                      {donor.contact_info}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DonorSearch;
