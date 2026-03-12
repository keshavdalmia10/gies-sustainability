import type { CSSProperties } from 'react'
import { User, Mail, BookOpen, Award } from 'lucide-react'
import './MentorCard.css'

interface MentorCardProps {
  faculty: {
    name: string
    department: string
    imageUrl?: string
    email: string
  }
  sdg: {
    number: number
    title: string
    color?: string
  }
  activeProjects: string[]
  studentOpportunities: string[]
}

export default function MentorCard({ faculty, sdg, activeProjects, studentOpportunities }: MentorCardProps) {
  const sdgColor = sdg.color || `var(--sdg-${sdg.number}, #0f766e)`

  return (
    <article className="mentor-card card" style={{ '--mentor-color': sdgColor } as CSSProperties}>
      <header className="mentor-card-header">
        <div className="mentor-avatar">
          {faculty.imageUrl ? (
            <img src={faculty.imageUrl} alt={faculty.name} />
          ) : (
            <User size={24} color="var(--color-text-muted)" />
          )}
        </div>
        <div>
          <h3>{faculty.name}</h3>
          <p className="mb-0 text-muted">{faculty.department}</p>
        </div>
      </header>

      <div className="mentor-sdg">
        <span className="badge">SDG {sdg.number}</span>
        <p className="mb-0">{sdg.title}</p>
      </div>

      <div className="mentor-section">
        <h4>Active Projects</h4>
        <ul>
          {activeProjects.slice(0, 3).map((project) => (
            <li key={project}>{project}</li>
          ))}
        </ul>
      </div>

      <div className="mentor-section">
        <h4>Student Opportunities</h4>
        <div className="mentor-tags">
          {studentOpportunities.map((opportunity) => (
            <span key={opportunity} className="mentor-tag">
              {opportunity.includes('RA') ? <BookOpen size={12} /> : <Award size={12} />}
              {opportunity}
            </span>
          ))}
        </div>
      </div>

      <a
        href={`mailto:${faculty.email}?subject=Interest in SDG ${sdg.number} Research`}
        className="btn btn-outline mentor-action"
      >
        <Mail size={16} /> Contact for Mentorship
      </a>
    </article>
  )
}
