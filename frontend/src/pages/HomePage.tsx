import { Link } from 'react-router-dom'
import { Users, DollarSign, GraduationCap } from 'lucide-react'
import './HomePage.css'
import NewsFeed from '../components/news/NewsFeed'

export default function HomePage() {
  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <h1 className="hero-title fade-in">
            Gies Sustainability Impact Dashboard
          </h1>
          <p className="hero-subtitle fade-in">
            From Data to Decisions: Transforming research into measurable impact for UN SDG goals
          </p>
          
          <div className="hero-stats grid grid-3 fade-in">
            <div className="stat-card card">
              <div className="stat-number">85+</div>
              <div className="stat-label">Faculty Researchers</div>
            </div>
            <div className="stat-card card">
              <div className="stat-number">1,500+</div>
              <div className="stat-label">Publications</div>
            </div>
            <div className="stat-card card">
              <div className="stat-number">$15M+</div>
              <div className="stat-label">Research Funding</div>
            </div>
          </div>
        </div>
      </section>

      {/* Persona Selection */}
      <section className="personas container">
        <h2 className="text-center mb-4">Choose Your View</h2>
        
        <div className="persona-grid">
          <Link to="/dean" className="persona-card card">
            <div className="persona-icon">
              <Users size={48} />
            </div>
            <h3 className="persona-title">Dean / Provost</h3>
            <p className="persona-description">
              Strategic gaps analysis, SDG momentum tracking, and resource allocation insights
            </p>
            <div className="persona-features">
              <div className="feature-item">✓ SDG × Department Matrix</div>
              <div className="feature-item">✓ Momentum Indicators</div>
              <div className="feature-item">✓ Gap Analysis</div>
            </div>
            <button className="btn btn-primary">View Dashboard →</button>
          </Link>

          <Link to="/donor" className="persona-card card">
            <div className="persona-icon donor">
              <DollarSign size={48} />
            </div>
            <h3 className="persona-title">Donor / Funder</h3>
            <p className="persona-description">
              Impact cards showcasing research outcomes, funding opportunities, and community reach
            </p>
            <div className="persona-features">
              <div className="feature-item">✓ Impact Stories</div>
              <div className="feature-item">✓ Funding Gaps</div>
              <div className="feature-item">✓ Real-World Outcomes</div>
            </div>
            <button className="btn btn-secondary">Explore Opportunities →</button>
          </Link>

          <Link to="/student" className="persona-card card">
            <div className="persona-icon student">
              <GraduationCap size={48} />
            </div>
            <h3 className="persona-title">Student</h3>
            <p className="persona-description">
              Find faculty mentors working on sustainability challenges aligned with your interests
            </p>
            <div className="persona-features">
              <div className="feature-item">✓ Faculty Search</div>
              <div className="feature-item">✓ Research Profiles</div>
              <div className="feature-item">✓ Connect with Mentors</div>
            </div>
            <button className="btn btn-outline">Find Mentors →</button>
          </Link>
        </div>
      </section>

      {/* Mission Statement */}
      <section className="mission container">
        <div className="card mission-card">
          <h2>Our Mission</h2>
          <p>
            The Gies Sustainability Impact Dashboard transforms research data into actionable insights
            for decision-makers. By linking faculty publications to real-world impacts—grants, patents,
            policies, and community outcomes—we demonstrate how Gies College research advances the
            UN Sustainable Development Goals.
          </p>
          <p>
            <strong>Pillar 2: From Data to Decisions</strong> - This dashboard empowers deans to allocate
            resources strategically, enables donors to fund high-impact research, and helps students
            find mentors working on sustainability challenges that matter.
          </p>
        </div>
      </section>

      {/* News Section */}
      <section className="news-section container mt-12 mb-12">
        <NewsFeed />
      </section>
    </div>
  )
}
