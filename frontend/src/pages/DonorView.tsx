import { useEffect, useMemo, useState } from 'react'
import { Heart, TrendingUp, DollarSign, MapPin, Sparkles, Target } from 'lucide-react'
import { Link } from 'react-router-dom'
import api from '../services/api'
import './DonorView.css'

interface ImpactCard {
  card_id: string
  title: string
  summary: string
  narrative: string
  key_outcomes: string[]
  total_funding: number
  funding_gap: number
  sdg: number
  geography: string
  faculty_name?: string
  department?: string
}

const SDG_COLORS: Record<number, string> = {
  7: '#FCC30B',
  13: '#3F7E44',
  11: '#FD9D24',
}

export default function DonorView() {
  const [impactCards, setImpactCards] = useState<ImpactCard[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedSDG, setSelectedSDG] = useState<number | null>(null)

  useEffect(() => {
    fetchImpactCards()
  }, [selectedSDG])

  const fetchImpactCards = async () => {
    try {
      setLoading(true)
      const params = selectedSDG ? { sdg: selectedSDG, status: 'published' } : { status: 'published' }
      const response = await api.get('/impact-cards', { params })
      setImpactCards(response.data)
    } catch (error) {
      console.error('Error fetching impact cards:', error)
      setImpactCards([])
    } finally {
      setLoading(false)
    }
  }

  const portfolioTotals = useMemo(
    () => ({
      fundingGap: impactCards.reduce((sum, card) => sum + card.funding_gap, 0),
      invested: impactCards.reduce((sum, card) => sum + card.total_funding, 0),
    }),
    [impactCards],
  )

  return (
    <div className="donor-view container page-shell">
      <header className="page-header donor-header">
        <span className="eyebrow">
          <Sparkles size={12} /> Donor Lens
        </span>
        <h1>Impact Investment Opportunities</h1>
        <p className="page-subtitle">
          Discover verified research stories with transparent evidence, current funding, and clear support gaps.
        </p>
        <div className="donor-header-pills">
          <span className="pill">
            <Target size={14} /> Evidence-backed impact cards
          </span>
          <span className="pill">
            <Heart size={14} /> Human-validated confidence loop
          </span>
        </div>
      </header>

      <section className="filters card">
        <h3>Filter by SDG focus</h3>
        <p className="text-muted mb-2">Narrow to a theme to compare funding opportunities side by side.</p>
        <div className="sdg-filters" role="tablist" aria-label="SDG filters">
          <button
            className={!selectedSDG ? 'btn btn-primary' : 'btn btn-outline'}
            onClick={() => setSelectedSDG(null)}
          >
            All SDGs
          </button>
          <button
            className={selectedSDG === 7 ? 'btn btn-primary' : 'btn btn-outline'}
            onClick={() => setSelectedSDG(7)}
          >
            SDG 7: Clean Energy
          </button>
          <button
            className={selectedSDG === 13 ? 'btn btn-primary' : 'btn btn-outline'}
            onClick={() => setSelectedSDG(13)}
          >
            SDG 13: Climate Action
          </button>
        </div>
      </section>

      {loading ? (
        <div className="loading-state" aria-live="polite">
          <div className="skeleton" style={{ height: '220px', marginBottom: '1rem' }} />
          <div className="skeleton" style={{ height: '220px', marginBottom: '1rem' }} />
          <div className="skeleton" style={{ height: '220px' }} />
        </div>
      ) : impactCards.length === 0 ? (
        <div className="empty-state card">
          <h3>No published impact cards found</h3>
          <p className="mb-2">Generate or publish cards in the backend to unlock donor opportunities here.</p>
          <code>python scripts/generate_sdg7_cards.py --limit 10</code>
        </div>
      ) : (
        <section className="impact-cards-grid">
          {impactCards.map((card) => (
            <article key={card.card_id} className="impact-card card">
              <div className="card-header">
                <div className="sdg-badge" style={{ backgroundColor: SDG_COLORS[card.sdg] || '#0066cc' }}>
                  SDG {card.sdg}
                </div>
                <h3 className="card-title">{card.title}</h3>
              </div>

              <p className="card-summary">{card.summary}</p>

              <div className="outcomes">
                <h4>Key outcomes</h4>
                <ul className="outcomes-list">
                  {card.key_outcomes.slice(0, 4).map((outcome, idx) => (
                    <li key={idx}>
                      <TrendingUp size={16} />
                      {outcome}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="metrics">
                <div className="metric">
                  <DollarSign size={20} />
                  <div>
                    <div className="metric-label">Current Funding</div>
                    <div className="metric-value">${card.total_funding.toLocaleString()}</div>
                  </div>
                </div>
                <div className="metric">
                  <Heart size={20} />
                  <div>
                    <div className="metric-label">Open Funding Gap</div>
                    <div className="metric-value highlight">${card.funding_gap.toLocaleString()}</div>
                  </div>
                </div>
              </div>

              {card.geography && (
                <div className="geography">
                  <MapPin size={16} />
                  <span>{card.geography}</span>
                </div>
              )}

              <div className="card-actions">
                <Link to={`/impact-card/${card.card_id}`} className="btn btn-outline">
                  View Evidence
                </Link>
                <button className="btn btn-secondary">Fund This Project</button>
              </div>
            </article>
          ))}
        </section>
      )}

      {impactCards.length > 0 && (
        <section className="summary-stats card">
          <h3>Portfolio Summary</h3>
          <div className="stats-grid">
            <div className="stat">
              <div className="stat-value">{impactCards.length}</div>
              <div className="stat-label">Impact Opportunities</div>
            </div>
            <div className="stat">
              <div className="stat-value">${portfolioTotals.fundingGap.toLocaleString()}</div>
              <div className="stat-label">Total Funding Needed</div>
            </div>
            <div className="stat">
              <div className="stat-value">${portfolioTotals.invested.toLocaleString()}</div>
              <div className="stat-label">Current Investment</div>
            </div>
          </div>
        </section>
      )}
    </div>
  )
}
