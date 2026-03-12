import { Link } from 'react-router-dom'
import {
  ArrowRight,
  CheckCircle2,
  Database,
  DollarSign,
  GraduationCap,
  ShieldCheck,
  Sparkles,
  Users,
} from 'lucide-react'
import NewsFeed from '../components/news/NewsFeed'
import './HomePage.css'

const HERO_STATS = [
  { value: '6', label: 'Integrated Research Sources', note: 'Google Scholar, Scopus, WoS, NIH, NSF, USPTO' },
  { value: '1,500+', label: 'Publications Indexed', note: 'Unified in one queryable model' },
  { value: '85+', label: 'Faculty Profiles', note: 'Cross-linked to grants, patents, outcomes' },
  { value: '98%', label: 'Community Confidence', note: 'Human-in-the-loop validation feedback' },
]

const PERSONA_CARDS = [
  {
    to: '/dean',
    icon: Users,
    title: 'Dean / Provost',
    summary: 'Prioritize hiring, funding, and strategy with SDG momentum, gaps, and confidence context.',
    points: ['Portfolio shape by SDG', 'Department-level gaps', 'Action-ready recommendations'],
    cta: 'Open strategic dashboard',
    tone: 'dean',
  },
  {
    to: '/donor',
    icon: DollarSign,
    title: 'Donor / Funder',
    summary: 'Explore evidence-backed impact cards with funding gaps and clear next actions.',
    points: ['Story + evidence in one card', 'Funding need transparency', 'Real-world outcomes and geography'],
    cta: 'Discover funding opportunities',
    tone: 'donor',
  },
  {
    to: '/student',
    icon: GraduationCap,
    title: 'Student',
    summary: 'Find faculty mentors by SDG focus, active projects, and opportunities to contribute.',
    points: ['SDG-filtered mentor discovery', 'Project and lab visibility', 'Direct contact pathways'],
    cta: 'Find your mentor match',
    tone: 'student',
  },
]

export default function HomePage() {
  return (
    <div className="home-page page-shell">
      <section className="hero-block">
        <div className="container hero-grid">
          <div className="hero-copy">
            <span className="eyebrow">
              <Sparkles size={12} /> From Papers to Proof
            </span>
            <h1 className="hero-title">Sustainability impact intelligence for leaders, donors, and students.</h1>
            <p className="hero-subtitle">
              The dashboard links publications to verified outcomes, confidence signals, and funding actions so
              research decisions are faster and more defensible.
            </p>

            <div className="hero-actions">
              <Link to="/dean" className="btn btn-primary">
                Start with Dean View <ArrowRight size={16} />
              </Link>
              <Link to="/donor" className="btn btn-outline">
                View Impact Portfolio
              </Link>
            </div>
          </div>

          <div className="hero-panel card fade-in">
            <h2 className="hero-panel-title">Where trust comes from</h2>
            <ul className="hero-panel-list" aria-label="Trust architecture">
              <li>
                <Database size={16} />
                <div>
                  <strong>Source transparency</strong>
                  <span>Every metric maps to its data origin and update cadence.</span>
                </div>
              </li>
              <li>
                <ShieldCheck size={16} />
                <div>
                  <strong>Human verification loop</strong>
                  <span>Faculty and admins can flag, review, and approve corrections.</span>
                </div>
              </li>
              <li>
                <CheckCircle2 size={16} />
                <div>
                  <strong>Explainable confidence</strong>
                  <span>Impact scores include factor-level rationale for each linkage.</span>
                </div>
              </li>
            </ul>
          </div>
        </div>
      </section>

      <section className="container">
        <div className="hero-stats-grid">
          {HERO_STATS.map((stat, index) => (
            <article key={stat.label} className="hero-stat-card card" style={{ animationDelay: `${index * 70}ms` }}>
              <p className="hero-stat-value">{stat.value}</p>
              <p className="hero-stat-label">{stat.label}</p>
              <p className="hero-stat-note">{stat.note}</p>
            </article>
          ))}
        </div>
      </section>

      <section className="container">
        <div className="section-head">
          <h2>Choose Your Decision Lens</h2>
          <p className="lead">
            Each view surfaces role-specific decisions while sharing one common data and verification backbone.
          </p>
        </div>

        <div className="persona-grid">
          {PERSONA_CARDS.map((persona) => {
            const Icon = persona.icon
            return (
              <Link key={persona.to} to={persona.to} className={`persona-card card persona-${persona.tone}`}>
                <div className="persona-icon-wrap">
                  <Icon size={22} />
                </div>
                <h3 className="persona-title">{persona.title}</h3>
                <p className="persona-description">{persona.summary}</p>
                <ul className="persona-list" aria-label={`${persona.title} features`}>
                  {persona.points.map((item) => (
                    <li key={item}>
                      <CheckCircle2 size={14} /> {item}
                    </li>
                  ))}
                </ul>
                <span className="persona-cta">
                  {persona.cta}
                  <ArrowRight size={15} />
                </span>
              </Link>
            )
          })}
        </div>
      </section>

      <section className="container">
        <div className="status-quo card">
          <h2>Before vs After</h2>
          <p className="lead mb-4">
            The platform moves stakeholders from fragmented manual research to transparent, decision-ready insight.
          </p>
          <div className="status-grid">
            <div className="status-column status-before">
              <h3>Before</h3>
              <ul>
                <li>Research data scattered across disconnected sources.</li>
                <li>Impact claims difficult to verify and compare.</li>
                <li>Strategic funding conversations rely on anecdotal evidence.</li>
              </ul>
            </div>
            <div className="status-column status-after">
              <h3>After</h3>
              <ul>
                <li>Unified ingestion from major academic and funding databases.</li>
                <li>Evidence drawers + confidence context on every impact narrative.</li>
                <li>Role-specific workflows for allocation, donor matching, and mentorship.</li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="container news-section">
        <div className="section-head">
          <h2>Global SDG Signal Feed</h2>
          <p className="lead mb-0">Recent SDG developments and AI-curated opportunities to inform strategy.</p>
        </div>
        <NewsFeed />
      </section>
    </div>
  )
}
