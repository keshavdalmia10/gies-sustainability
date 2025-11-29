import { User, Mail, BookOpen, Award } from 'lucide-react';

interface MentorCardProps {
  faculty: {
    name: string;
    department: string;
    imageUrl?: string;
    email: string;
  };
  sdg: {
    number: number;
    title: string;
    color?: string;
  };
  activeProjects: string[];
  studentOpportunities: string[];
}

export default function MentorCard({ faculty, sdg, activeProjects, studentOpportunities }: MentorCardProps) {
  const sdgColor = sdg.color || `var(--sdg-${sdg.number}, #0066cc)`;

  return (
    <div className="card" style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      borderTop: `4px solid ${sdgColor}`,
      transition: 'transform 0.2s ease, box-shadow 0.2s ease'
    }}>
      
      {/* Header */}
      <div style={{ display: 'flex', gap: 'var(--spacing-md)', marginBottom: 'var(--spacing-md)' }}>
        <div style={{ 
          width: '56px', 
          height: '56px', 
          borderRadius: '50%', 
          backgroundColor: 'var(--color-surface)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          overflow: 'hidden',
          flexShrink: 0
        }}>
          {faculty.imageUrl ? (
            <img src={faculty.imageUrl} alt={faculty.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          ) : (
            <User size={28} color="var(--color-text-light)" />
          )}
        </div>
        <div>
          <h3 style={{ fontSize: 'var(--font-size-lg)', marginBottom: '2px' }}>{faculty.name}</h3>
          <p className="text-muted" style={{ fontSize: 'var(--font-size-sm)', margin: 0 }}>{faculty.department}</p>
        </div>
      </div>

      {/* SDG Badge */}
      <div style={{ marginBottom: 'var(--spacing-md)' }}>
         <span className="badge" style={{ backgroundColor: 'var(--color-surface)', color: 'var(--color-text)', border: `1px solid ${sdgColor}` }}>
            SDG {sdg.number}: {sdg.title}
         </span>
      </div>

      {/* Active Projects */}
      <div style={{ marginBottom: 'var(--spacing-md)', flex: 1 }}>
        <h4 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
          Active Projects
        </h4>
        <ul style={{ paddingLeft: '20px', margin: 0, fontSize: 'var(--font-size-sm)' }}>
          {activeProjects.slice(0, 2).map((project, idx) => (
            <li key={idx} style={{ marginBottom: '4px' }}>{project}</li>
          ))}
        </ul>
      </div>

      {/* Opportunities */}
      <div style={{ marginBottom: 'var(--spacing-lg)' }}>
         <h4 style={{ fontSize: 'var(--font-size-sm)', color: 'var(--color-text-light)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '8px' }}>
          Student Opportunities
        </h4>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
          {studentOpportunities.map((opp, idx) => (
            <span key={idx} className="badge" style={{ backgroundColor: 'rgba(0, 102, 204, 0.1)', color: 'var(--color-primary)' }}>
              {opp.includes('RA') ? <BookOpen size={12} style={{ marginRight: '4px' }} /> : <Award size={12} style={{ marginRight: '4px' }} />}
              {opp}
            </span>
          ))}
        </div>
      </div>

      {/* Action */}
      <a 
        href={`mailto:${faculty.email}?subject=Interest in SDG ${sdg.number} Research`}
        className="btn btn-outline" 
        style={{ width: '100%', justifyContent: 'center', marginTop: 'auto' }}
      >
        <Mail size={16} /> Contact for Mentorship
      </a>

    </div>
  );
}
