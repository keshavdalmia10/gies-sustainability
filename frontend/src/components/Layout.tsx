import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  
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
          </nav>
        </div>
      </header>
      
      <main className="main-content">
        {children}
      </main>
      
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
