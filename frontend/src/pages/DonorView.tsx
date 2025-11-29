import { useState, useEffect } from 'react'
import { Heart, TrendingUp, DollarSign, MapPin } from 'lucide-react'
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

  const SDGColors: Record<number, string> = {
    7: '#FCC30B',
    13: '#3F7E44',
    11: '#FD9D24',
  }

  return (
    <div className="donor-view container">
      <div className="page-header">
        <h1>Impact Investment Opportunities</h1>
        <p className="page-subtitle">
          Discover high-impact research projects that transform communities and advance sustainability
        </p>
      </div>

      {/* Filters */}
      <div className="filters card">
        <h3>Filter by SDG</h3>
        <div className="sdg-filters">
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
      </div>

      {/* Impact Cards Grid */}
      {loading ? (
        <div className="loading-state">
          <div className="skeleton" style={{ height: '200px', marginBottom: '1rem' }}></div>
          <div className="skeleton" style={{ height: '200px', marginBottom: '1rem' }}></div>
          <div className="skeleton" style={{ height: '200px' }}></div>
        </div>
      ) : impactCards.length === 0 ? (
        <div className="empty-state card">
          <p>No impact cards available yet. Generate some using the backend!</p>
          <code>python scripts/generate_sdg7_cards.py --limit 10</code>
        </div>
      ) : (
        <div className="impact-cards-grid">
          {impactCards.map((card) => (
            <div key={card.card_id} className="impact-card card">
              <div className="card-header">
                <div className="sdg-badge" style={{ backgroundColor: SDGColors[card.sdg] || '#0066cc' }}>
                  SDG {card.sdg}
                </div>
                <h3 className="card-title">{card.title}</h3>
              </div>

              <p className="card-summary">{card.summary}</p>

              <div className="outcomes">
                <h4>Key Outcomes</h4>
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
                    <div className="metric-label">Total Funding</div>
                    <div className="metric-value">${card.total_funding.toLocaleString()}</div>
                  </div>
                </div>
                <div className="metric">
                  <Heart size={20} />
                  <div>
                    <div className="metric-label">Funding Gap</div>
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
                <a href={`/impact-card/${card.card_id}`} className="btn btn-outline">
                  View Details →
                </a>
                <button className="btn btn-secondary">
                  Fund This Project
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {impactCards.length > 0 && (
        <div className="summary-stats card">
          <h3>Portfolio Summary</h3>
          <div className="stats-grid">
            <div className="stat">
              <div className="stat-value">{impactCards.length}</div>
              <div className="stat-label">Impact Opportunities</div>
            </div>
            <div className="stat">
              <div className="stat-value">
                ${impactCards.reduce((sum, card) => sum + card.funding_gap, 0).toLocaleString()}
              </div>
              <div className="stat-label">Total Funding Needed</div>
            </div>
            <div className="stat">
              <div className="stat-value">
                ${impactCards.reduce((sum, card) => sum + card.total_funding, 0).toLocaleString()}
              </div>
              <div className="stat-label">Current Investment</div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
