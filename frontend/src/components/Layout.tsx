import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Award, CheckCircle } from 'lucide-react'
import { useImpactDetective } from '../hooks/useImpactDetective'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { validationCount, showToast, lastAction } = useImpactDetective()
  
  const isActive = (path: string) => location.pathname === path
  
  return (
    <div className="app-layout">
      <header className="header">
        <div className="container header-content">
          <Link to="/" className="logo">
            <span className="logo-icon">🌱</span>
            <span className="logo-text">Gies Sustainability Impact</span>
          </Link>
          
          <nav className="nav">
            <Link to="/" className={isActive('/') ? 'nav-link active' : 'nav-link'}>
              Home
            </Link>
            <Link to="/dean" className={isActive('/dean') ? 'nav-link active' : 'nav-link'}>
              Dean View
            </Link>
            <Link to="/donor" className={isActive('/donor') ? 'nav-link active' : 'nav-link'}>
              Donor View
            </Link>
            <Link to="/student" className={isActive('/student') ? 'nav-link active' : 'nav-link'}>
              Student View
            </Link>
            
            {/* Impact Detective Badge */}
            <div className="nav-link" style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--color-primary)', fontWeight: 600, cursor: 'default' }}>
              <Award size={18} />
              <span>{validationCount}</span>
            </div>
          </nav>
        </div>
      </header>
      
      <main className="main-content">
        {children}
      </main>
      
      {/* Toast Notification */}
      {showToast && (
        <div style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          backgroundColor: '#fff',
          padding: '16px 24px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          zIndex: 1000,
          animation: 'slideUp 0.3s ease-out',
          borderLeft: '4px solid var(--color-success)'
        }}>
          <CheckCircle size={24} color="var(--color-success)" />
          <div>
            <div style={{ fontWeight: 600, fontSize: '14px' }}>
              {lastAction === 'approved' ? 'Impact Verified!' : 'Feedback Recorded'}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--color-text-light)' }}>
              You just strengthened our impact story! ({validationCount} total)
            </div>
          </div>
        </div>
      )}
      
      <footer className="footer">
        <div className="container footer-content">
          <p>&copy; 2024 Gies College of Business, University of Illinois</p>
          <p className="text-small text-muted">
            Sustainability Impact Dashboard - Pillar 2: From Data to Decisions
          </p>
        </div>
      </footer>
    </div>
  )
}
