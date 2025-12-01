import React, { useState } from 'react';
import { Search, User, GraduationCap, Mail, ArrowRight } from 'lucide-react';

interface ProjectMatch {
  name: string;
  type: string;
  title: string;
  description: string;
  match_reason: string;
  email?: string;
}

const DonorPortal: React.FC = () => {
  const [interest, setInterest] = useState('');
  const [loading, setLoading] = useState(false);
  const [matches, setMatches] = useState<ProjectMatch[]>([]);
  const [searched, setSearched] = useState(false);

  const handleSearch = async () => {
    if (!interest.trim()) return;
    
    setLoading(true);
    setSearched(true);
    setMatches([]); 
    
    try {
      const response = await fetch('http://localhost:8000/api/v1/donors/find-projects', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ donor_interest: interest }),
      });
      
      if (response.ok) {
        const data = await response.json();
        setMatches(data.matches);
      } else {
        console.error('Failed to fetch projects');
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem', maxWidth: '1200px', margin: '0 auto' }}>
      {/* Search Section */}
      <div className="card" style={{ padding: '3rem', textAlign: 'center', background: 'linear-gradient(135deg, var(--color-surface) 0%, var(--color-background) 100%)' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '1rem' }}>Invest in Impact</h2>
        <p className="text-muted" style={{ fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto 2rem' }}>
          Tell us what kind of change you want to fund, and we'll match you with the professors and student teams making it happen.
        </p>
        
        <div style={{ display: 'flex', gap: '1rem', maxWidth: '700px', margin: '0 auto' }}>
          <input
            type="text"
            className="form-control"
            placeholder="e.g., Renewable Energy, AI for Health, Sustainable Agriculture..."
            value={interest}
            onChange={(e) => setInterest(e.target.value)}
            style={{ fontSize: '1.1rem', padding: '1rem', flex: 1 }}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button 
            className="btn btn-primary" 
            onClick={handleSearch}
            disabled={loading || !interest.trim()}
            style={{ padding: '0 2rem', fontSize: '1.1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
          >
            {loading ? 'Searching...' : <><Search size={20} /> Search</>}
          </button>
        </div>
      </div>

      {/* Results Section */}
      {searched && (
        <div>
          <h3 style={{ fontSize: '1.5rem', fontWeight: 600, marginBottom: '1.5rem' }}>
            {loading ? 'Analyzing our network...' : matches.length > 0 ? `Found ${matches.length} Matching Opportunities` : 'No matches found yet. Try a broader term.'}
          </h3>
          
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
            {matches.map((match, index) => (
              <div key={index} className="card" style={{ display: 'flex', flexDirection: 'column', height: '100%', borderTop: `4px solid ${match.type === 'Faculty' ? 'var(--color-primary)' : 'var(--color-secondary)'}` }}>
                <div style={{ padding: '1.5rem', flex: 1 }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                    <span className="badge" style={{ backgroundColor: match.type === 'Faculty' ? 'rgba(var(--color-primary-rgb), 0.1)' : 'rgba(var(--color-secondary-rgb), 0.1)', color: match.type === 'Faculty' ? 'var(--color-primary)' : 'var(--color-secondary)' }}>
                      {match.type === 'Faculty' ? <><User size={14} style={{ marginRight: 4 }} /> Faculty</> : <><GraduationCap size={14} style={{ marginRight: 4 }} /> Student Project</>}
                    </span>
                  </div>
                  
                  <h4 style={{ fontSize: '1.25rem', fontWeight: 700, marginBottom: '0.5rem' }}>{match.name}</h4>
                  <p style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)', marginBottom: '1rem', fontStyle: 'italic' }}>{match.title}</p>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <h5 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>Current Focus</h5>
                    <p style={{ fontSize: '0.95rem' }}>{match.description}</p>
                  </div>
                  
                  <div>
                    <h5 style={{ fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '0.05em', color: 'var(--color-text-muted)' }}>Why it's a match</h5>
                    <p style={{ fontSize: '0.95rem', color: 'var(--color-success)' }}>{match.match_reason}</p>
                  </div>
                </div>
                
                <div style={{ padding: '1rem 1.5rem', backgroundColor: 'var(--color-surface)', borderTop: '1px solid var(--color-border)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  {match.email ? (
                    <a href={`mailto:${match.email}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--color-text)', textDecoration: 'none', fontSize: '0.9rem', fontWeight: 500 }}>
                      <Mail size={16} /> Contact
                    </a>
                  ) : (
                    <span style={{ fontSize: '0.9rem', color: 'var(--color-text-muted)' }}>Contact via Department</span>
                  )}
                  <button className="btn btn-outline" style={{ padding: '0.4rem 0.8rem', fontSize: '0.85rem' }}>
                    View Profile <ArrowRight size={14} style={{ marginLeft: 4 }} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DonorPortal;
