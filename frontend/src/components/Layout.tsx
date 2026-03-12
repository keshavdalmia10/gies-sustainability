import { ReactNode } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  Building2,
  CheckCircle2,
  GraduationCap,
  HeartHandshake,
  Home,
  Network,
  ShieldCheck,
  XCircle,
} from 'lucide-react'
import { useImpactDetective } from '../hooks/useImpactDetective'
import './Layout.css'

interface LayoutProps {
  children: ReactNode
}

const NAV_ITEMS = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/dean', label: 'Dean View', icon: Building2 },
  { to: '/donor', label: 'Donor View', icon: HeartHandshake },
  { to: '/student', label: 'Student View', icon: GraduationCap },
  { to: '/networking', label: 'Networking', icon: Network },
]

export default function Layout({ children }: LayoutProps) {
  const location = useLocation()
  const { validationCount, showToast, lastAction } = useImpactDetective()

  const isActive = (path: string) =>
    path === '/' ? location.pathname === '/' : location.pathname.startsWith(path)

  return (
    <div className="app-layout">
      <header className="site-header">
        <div className="container site-header-inner">
          <Link to="/" className="brand" aria-label="Go to dashboard home">
            <div className="brand-mark" aria-hidden="true">
              <span>G</span>
            </div>
            <div className="brand-copy">
              <span className="brand-title">Gies Sustainability Impact</span>
              <span className="brand-subtitle">From data to decisions</span>
            </div>
          </Link>

          <div className="header-chip" aria-live="polite">
            <ShieldCheck size={16} />
            <span>{validationCount} validations logged</span>
          </div>
        </div>

        <div className="container">
          <nav className="layout-nav" aria-label="Primary">
            {NAV_ITEMS.map((item) => {
              const Icon = item.icon
              return (
                <Link
                  key={item.to}
                  to={item.to}
                  className={isActive(item.to) ? 'layout-nav-link active' : 'layout-nav-link'}
                >
                  <Icon size={15} />
                  <span>{item.label}</span>
                </Link>
              )
            })}
          </nav>
        </div>
      </header>

      <main className="main-content">{children}</main>

      {showToast && (
        <div
          className={
            lastAction === 'approved'
              ? 'impact-toast impact-toast-approved'
              : 'impact-toast impact-toast-rejected'
          }
          role="status"
          aria-live="polite"
        >
          {lastAction === 'approved' ? <CheckCircle2 size={20} /> : <XCircle size={20} />}
          <div>
            <p className="impact-toast-title">
              {lastAction === 'approved' ? 'Impact evidence approved' : 'Feedback submitted'}
            </p>
            <p className="impact-toast-copy">Community trust increased to {validationCount} reviews.</p>
          </div>
        </div>
      )}

      <footer className="site-footer">
        <div className="container site-footer-content">
          <p className="mb-0">
            &copy; {new Date().getFullYear()} Gies College of Business, University of Illinois
          </p>
          <p className="text-small text-muted mb-0">
            Sustainability Impact Dashboard: Pillar 2, transparent impact intelligence.
          </p>
        </div>
      </footer>
    </div>
  )
}
