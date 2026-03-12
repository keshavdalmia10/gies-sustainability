import { useState } from 'react'
import { ChevronDown, ChevronUp, ExternalLink, FileText, Award, Lightbulb } from 'lucide-react'
import ConfidenceBadge from './ConfidenceBadge'
import './EvidenceDrawer.css'

interface Publication {
  id: string
  title: string
  journal?: string
  year?: number
  confidence: number
  url?: string
}

interface Grant {
  id: string
  title: string
  funder: string
  amount?: number
  confidence: number
}

interface Patent {
  id: string
  title: string
  number: string
  confidence: number
}

interface EvidenceDrawerProps {
  publications: Publication[]
  grants: Grant[]
  patents: Patent[]
}

export default function EvidenceDrawer({ publications, grants, patents }: EvidenceDrawerProps) {
  const [isOpen, setIsOpen] = useState(false)
  const totalItems = publications.length + grants.length + patents.length

  return (
    <div className="evidence-drawer card">
      <button
        className="evidence-toggle"
        onClick={() => setIsOpen((prev) => !prev)}
        aria-expanded={isOpen}
        aria-controls="evidence-content"
      >
        <div>
          <h3 className="card-title">Evidence Drawer</h3>
          <p className="card-subtitle mb-0">{totalItems} sources backing this impact card</p>
        </div>
        {isOpen ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
      </button>

      {isOpen && (
        <div id="evidence-content" className="evidence-content">
          {publications.length > 0 && (
            <section className="evidence-section">
              <h4>
                <FileText size={16} /> Publications
              </h4>
              <div className="evidence-grid">
                {publications.map((publication) => (
                  <article key={publication.id} className="evidence-item">
                    <div className="evidence-item-top">
                      <strong>{publication.title}</strong>
                      <ConfidenceBadge score={publication.confidence} size="sm" />
                    </div>
                    <div className="evidence-item-meta">
                      <span>
                        {publication.journal} {publication.year ? `(${publication.year})` : ''}
                      </span>
                      {publication.url && (
                        <a href={publication.url} target="_blank" rel="noopener noreferrer">
                          View <ExternalLink size={12} />
                        </a>
                      )}
                    </div>
                  </article>
                ))}
              </div>
            </section>
          )}

          {grants.length > 0 && (
            <section className="evidence-section">
              <h4>
                <Award size={16} /> Grants and Funding
              </h4>
              <div className="evidence-grid">
                {grants.map((grant) => (
                  <article key={grant.id} className="evidence-item">
                    <div className="evidence-item-top">
                      <strong>{grant.title}</strong>
                      <ConfidenceBadge score={grant.confidence} size="sm" />
                    </div>
                    <p className="evidence-item-meta mb-0">
                      {grant.funder} {grant.amount ? `• $${grant.amount.toLocaleString()}` : ''}
                    </p>
                  </article>
                ))}
              </div>
            </section>
          )}

          {patents.length > 0 && (
            <section className="evidence-section">
              <h4>
                <Lightbulb size={16} /> Patents
              </h4>
              <div className="evidence-grid">
                {patents.map((patent) => (
                  <article key={patent.id} className="evidence-item">
                    <div className="evidence-item-top">
                      <strong>{patent.title}</strong>
                      <ConfidenceBadge score={patent.confidence} size="sm" />
                    </div>
                    <p className="evidence-item-meta mb-0">Patent #{patent.number}</p>
                  </article>
                ))}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  )
}
