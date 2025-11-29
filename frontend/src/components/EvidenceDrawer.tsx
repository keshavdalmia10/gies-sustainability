import { useState } from 'react';
import { ChevronDown, ChevronUp, ExternalLink, FileText, Award, Lightbulb } from 'lucide-react';
import ConfidenceBadge from './ConfidenceBadge';

interface Publication {
  id: string;
  title: string;
  journal?: string;
  year?: number;
  confidence: number;
  url?: string;
}

interface Grant {
  id: string;
  title: string;
  funder: string;
  amount?: number;
  confidence: number;
}

interface Patent {
  id: string;
  title: string;
  number: string;
  confidence: number;
}

interface EvidenceDrawerProps {
  publications: Publication[];
  grants: Grant[];
  patents: Patent[];
}

export default function EvidenceDrawer({ publications, grants, patents }: EvidenceDrawerProps) {
  const [isOpen, setIsOpen] = useState(false);

  const totalItems = publications.length + grants.length + patents.length;

  return (
    <div className="card" style={{ marginTop: 'var(--spacing-lg)', padding: '0' }}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        style={{
          width: '100%',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: 'var(--spacing-lg)',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          textAlign: 'left'
        }}
      >
        <div>
          <h3 className="card-title" style={{ fontSize: 'var(--font-size-lg)', marginBottom: '0' }}>
            Evidence Drawer
          </h3>
          <p className="card-subtitle" style={{ marginBottom: '0' }}>
            {totalItems} verified sources backing this impact
          </p>
        </div>
        {isOpen ? <ChevronUp size={24} /> : <ChevronDown size={24} />}
      </button>

      {isOpen && (
        <div style={{ padding: '0 var(--spacing-lg) var(--spacing-lg)' }}>
          <div style={{ borderTop: '1px solid var(--color-border)', paddingTop: 'var(--spacing-md)' }}>
            
            {/* Publications */}
            {publications.length > 0 && (
              <div className="mb-3">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: 'var(--font-size-md)' }}>
                  <FileText size={18} /> Publications
                </h4>
                <div className="grid" style={{ gap: 'var(--spacing-md)' }}>
                  {publications.map(pub => (
                    <div key={pub.id} style={{ 
                      padding: 'var(--spacing-md)', 
                      backgroundColor: 'var(--color-surface)', 
                      borderRadius: 'var(--radius-md)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600 }}>{pub.title}</span>
                        <ConfidenceBadge score={pub.confidence} size="sm" />
                      </div>
                      <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', display: 'flex', justifyContent: 'space-between' }}>
                        <span>{pub.journal} ({pub.year})</span>
                        {pub.url && (
                          <a href={pub.url} target="_blank" rel="noopener noreferrer" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            View <ExternalLink size={12} />
                          </a>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Grants */}
            {grants.length > 0 && (
              <div className="mb-3">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: 'var(--font-size-md)' }}>
                  <Award size={18} /> Grants & Funding
                </h4>
                <div className="grid" style={{ gap: 'var(--spacing-md)' }}>
                  {grants.map(grant => (
                    <div key={grant.id} style={{ 
                      padding: 'var(--spacing-md)', 
                      backgroundColor: 'var(--color-surface)', 
                      borderRadius: 'var(--radius-md)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600 }}>{grant.title}</span>
                        <ConfidenceBadge score={grant.confidence} size="sm" />
                      </div>
                      <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)' }}>
                        {grant.funder} • {grant.amount ? `$${grant.amount.toLocaleString()}` : 'Amount N/A'}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Patents */}
            {patents.length > 0 && (
              <div className="mb-3">
                <h4 style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: 'var(--font-size-md)' }}>
                  <Lightbulb size={18} /> Patents
                </h4>
                <div className="grid" style={{ gap: 'var(--spacing-md)' }}>
                  {patents.map(patent => (
                    <div key={patent.id} style={{ 
                      padding: 'var(--spacing-md)', 
                      backgroundColor: 'var(--color-surface)', 
                      borderRadius: 'var(--radius-md)'
                    }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '4px' }}>
                        <span style={{ fontWeight: 600 }}>{patent.title}</span>
                        <ConfidenceBadge score={patent.confidence} size="sm" />
                      </div>
                      <div style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)' }}>
                        Patent #{patent.number}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

          </div>
        </div>
      )}
    </div>
  );
}
