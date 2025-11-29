import { User, TrendingUp } from 'lucide-react';
import EvidenceDrawer from './EvidenceDrawer';

interface ImpactCardProps {
  faculty: {
    name: string;
    department: string;
    imageUrl?: string;
  };
  sdg: {
    number: number;
    title: string;
    color?: string;
  };
  narrative: string;
  keyOutcomes: string[];
  metrics: {
    totalFunding: number;
    communitiesReached: number;
    fundingGap: number;
  };
  evidence: {
    publications: any[];
    grants: any[];
    patents: any[];
  };
}

export default function ImpactCard({ faculty, sdg, narrative, keyOutcomes, metrics, evidence }: ImpactCardProps) {
  const sdgColor = sdg.color || `var(--sdg-${sdg.number}, #0066cc)`;

  return (
    <div className="card" style={{ maxWidth: '800px', margin: '0 auto', borderTop: `6px solid ${sdgColor}` }}>
      
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 'var(--spacing-lg)' }}>
        <div style={{ display: 'flex', gap: 'var(--spacing-md)' }}>
          <div style={{ 
            width: '64px', 
            height: '64px', 
            borderRadius: '50%', 
            backgroundColor: 'var(--color-surface)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            overflow: 'hidden'
          }}>
            {faculty.imageUrl ? (
              <img src={faculty.imageUrl} alt={faculty.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
            ) : (
              <User size={32} color="var(--color-text-light)" />
            )}
          </div>
          <div>
            <h2 style={{ fontSize: 'var(--font-size-xl)', marginBottom: '4px' }}>{faculty.name}</h2>
            <p className="text-muted" style={{ margin: 0 }}>{faculty.department}</p>
          </div>
        </div>
        <div className="badge" style={{ backgroundColor: sdgColor, color: '#fff', fontSize: 'var(--font-size-sm)' }}>
          SDG {sdg.number}: {sdg.title}
        </div>
      </div>

      {/* Narrative */}
      <div className="mb-4">
        <h3 style={{ fontSize: 'var(--font-size-lg)', marginBottom: 'var(--spacing-sm)' }}>The Impact Story</h3>
        <p style={{ lineHeight: '1.7' }}>{narrative}</p>
      </div>

      {/* Key Outcomes */}
      <div className="mb-4" style={{ backgroundColor: 'var(--color-surface)', padding: 'var(--spacing-lg)', borderRadius: 'var(--radius-md)' }}>
        <h3 style={{ fontSize: 'var(--font-size-md)', marginBottom: 'var(--spacing-md)', display: 'flex', alignItems: 'center', gap: '8px' }}>
          <TrendingUp size={20} color="var(--color-primary)" /> Key Real-World Outcomes
        </h3>
        <ul style={{ paddingLeft: '20px', margin: 0 }}>
          {keyOutcomes.map((outcome, index) => (
            <li key={index} style={{ marginBottom: '8px' }}>{outcome}</li>
          ))}
        </ul>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-3 mb-4">
        <div className="text-center">
          <div style={{ color: 'var(--color-text-light)', fontSize: 'var(--font-size-sm)', marginBottom: '4px' }}>Total Funding</div>
          <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-primary)' }}>
            ${metrics.totalFunding.toLocaleString()}
          </div>
        </div>
        <div className="text-center">
          <div style={{ color: 'var(--color-text-light)', fontSize: 'var(--font-size-sm)', marginBottom: '4px' }}>Communities Reached</div>
          <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-success)' }}>
            {metrics.communitiesReached.toLocaleString()}
          </div>
        </div>
        <div className="text-center">
          <div style={{ color: 'var(--color-text-light)', fontSize: 'var(--font-size-sm)', marginBottom: '4px' }}>Funding Gap</div>
          <div style={{ fontSize: 'var(--font-size-xl)', fontWeight: 700, color: 'var(--color-warning)' }}>
            ${metrics.fundingGap.toLocaleString()}
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-xl)' }}>
        <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
          Fund This Impact
        </button>
        <button className="btn btn-outline" style={{ flex: 1, justifyContent: 'center' }}>
          Contact Researcher
        </button>
      </div>

      {/* Evidence Drawer */}
      <EvidenceDrawer 
        publications={evidence.publications}
        grants={evidence.grants}
        patents={evidence.patents}
      />

    </div>
  );
}
