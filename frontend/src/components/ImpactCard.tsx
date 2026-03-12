import { useState, type CSSProperties } from 'react'
import { User, TrendingUp, Check, X, Shield } from 'lucide-react'
import EvidenceDrawer from './EvidenceDrawer'
import { useImpactDetective } from '../hooks/useImpactDetective'
import './ImpactCard.css'

interface ImpactCardProps {
  faculty: {
    name: string
    department: string
    imageUrl?: string
  }
  sdg: {
    number: number
    title: string
    color?: string
  }
  narrative: string
  keyOutcomes: string[]
  metrics: {
    totalFunding: number
    communitiesReached: number
    fundingGap: number
  }
  evidence: {
    publications: any[]
    grants: any[]
    patents: any[]
  }
}

export default function ImpactCard({
  faculty,
  sdg,
  narrative,
  keyOutcomes,
  metrics,
  evidence,
}: ImpactCardProps) {
  const sdgColor = sdg.color || `var(--sdg-${sdg.number}, #0f766e)`
  const { validateCard } = useImpactDetective()
  const [hasValidated, setHasValidated] = useState(false)

  const handleValidation = (status: 'approved' | 'rejected') => {
    if (hasValidated) return
    validateCard(status, '00000000-0000-0000-0000-000000000000')
    setHasValidated(true)
  }

  return (
    <article className="impact-card-shell card" style={{ '--sdg-color': sdgColor } as CSSProperties}>
      <header className="impact-card-header-row">
        <div className="impact-faculty">
          <div className="impact-faculty-avatar">
            {faculty.imageUrl ? <img src={faculty.imageUrl} alt={faculty.name} /> : <User size={30} />}
          </div>
          <div>
            <h2>{faculty.name}</h2>
            <p className="mb-0 text-muted">{faculty.department}</p>
          </div>
        </div>

        <span className="impact-sdg-badge">
          SDG {sdg.number}: {sdg.title}
        </span>
      </header>

      <section className="impact-story-block">
        <h3>The Impact Story</h3>
        <p className="mb-0">{narrative}</p>
      </section>

      <section className="impact-outcomes-block">
        <h3>
          <TrendingUp size={18} /> Key Real-World Outcomes
        </h3>
        <ul>
          {keyOutcomes.map((outcome) => (
            <li key={outcome}>{outcome}</li>
          ))}
        </ul>
      </section>

      <section className="impact-metrics-grid">
        <div className="impact-metric-item">
          <span>Total Funding</span>
          <strong>${metrics.totalFunding.toLocaleString()}</strong>
        </div>
        <div className="impact-metric-item">
          <span>Communities Reached</span>
          <strong>{metrics.communitiesReached.toLocaleString()}</strong>
        </div>
        <div className="impact-metric-item warning">
          <span>Funding Gap</span>
          <strong>${metrics.fundingGap.toLocaleString()}</strong>
        </div>
      </section>

      <div className="impact-cta-row">
        <button className="btn btn-secondary">Fund This Impact</button>
        <button className="btn btn-outline">Contact Researcher</button>
      </div>

      <EvidenceDrawer
        publications={evidence.publications}
        grants={evidence.grants}
        patents={evidence.patents}
      />

      <footer className="impact-validation-row">
        <div className="impact-validation-label">
          <Shield size={18} />
          <span>Impact Detective validation</span>
        </div>

        {!hasValidated ? (
          <div className="impact-validation-actions">
            <button
              onClick={() => handleValidation('rejected')}
              className="btn btn-outline impact-reject-btn"
            >
              <X size={15} /> Reject
            </button>
            <button
              onClick={() => handleValidation('approved')}
              className="btn impact-approve-btn"
            >
              <Check size={15} /> Approve
            </button>
          </div>
        ) : (
          <span className="impact-validated-pill">
            <Check size={15} /> Validated
          </span>
        )}
      </footer>
    </article>
  )
}
