import { useMemo, useState } from 'react'
import { Search, Filter, Sparkles } from 'lucide-react'
import MentorCard from '../components/MentorCard'
import './StudentView.css'

const MOCK_MENTORS = [
  {
    id: 1,
    faculty: {
      name: 'Prof. Jane Doe',
      department: 'Finance',
      email: 'jane.doe@example.edu',
      imageUrl: 'https://i.pravatar.cc/150?u=jane',
    },
    sdg: { number: 7, title: 'Affordable and Clean Energy', color: '#fcc30b' },
    activeProjects: ['Solar Financing Risk Models', 'Rural Cooperative Lending'],
    studentOpportunities: ['RA Position (Paid)', 'Independent Study'],
  },
  {
    id: 2,
    faculty: {
      name: 'Prof. John Smith',
      department: 'Business Administration',
      email: 'john.smith@example.edu',
      imageUrl: 'https://i.pravatar.cc/150?u=john',
    },
    sdg: { number: 13, title: 'Climate Action', color: '#3f7e44' },
    activeProjects: ['Corporate Carbon Disclosure', 'Supply Chain Resilience'],
    studentOpportunities: ['Case Competition Mentor', 'Thesis Advisor'],
  },
  {
    id: 3,
    faculty: {
      name: 'Prof. Emily Chen',
      department: 'Accountancy',
      email: 'emily.chen@example.edu',
      imageUrl: 'https://i.pravatar.cc/150?u=emily',
    },
    sdg: { number: 12, title: 'Responsible Consumption', color: '#cf8d2a' },
    activeProjects: ['Circular Economy Audits', 'Waste Reduction Metrics'],
    studentOpportunities: ['RA Position (Credit)', 'Capstone Project'],
  },
  {
    id: 4,
    faculty: {
      name: 'Prof. Michael Brown',
      department: 'Economics',
      email: 'michael.brown@example.edu',
    },
    sdg: { number: 8, title: 'Decent Work and Economic Growth', color: '#a21942' },
    activeProjects: ['Labor Market Analysis', 'Gig Economy Policy'],
    studentOpportunities: ['Data Analysis RA', 'Seminar Course'],
  },
]

const SDG_OPTIONS = [
  { number: 0, title: 'All SDGs' },
  { number: 7, title: 'SDG 7: Clean Energy' },
  { number: 8, title: 'SDG 8: Decent Work' },
  { number: 12, title: 'SDG 12: Responsible Consumption' },
  { number: 13, title: 'SDG 13: Climate Action' },
]

export default function StudentView() {
  const [selectedSDG, setSelectedSDG] = useState(0)
  const [searchQuery, setSearchQuery] = useState('')

  const filteredMentors = useMemo(
    () =>
      MOCK_MENTORS.filter((mentor) => {
        const matchesSDG = selectedSDG === 0 || mentor.sdg.number === selectedSDG
        const q = searchQuery.toLowerCase()
        const matchesSearch =
          mentor.faculty.name.toLowerCase().includes(q) ||
          mentor.activeProjects.some((project) => project.toLowerCase().includes(q))
        return matchesSDG && matchesSearch
      }),
    [searchQuery, selectedSDG],
  )

  return (
    <div className="container student-view page-shell">
      <header className="page-header student-header">
        <span className="eyebrow">
          <Sparkles size={12} /> Student Lens
        </span>
        <h1>Find Your Mentor</h1>
        <p className="page-subtitle">
          Match with faculty by SDG focus, active projects, and current opportunities for research collaboration.
        </p>
      </header>

      <section className="student-filter-panel card">
        <div className="student-filter-grid">
          <label className="student-field" htmlFor="mentor-search">
            <span className="student-field-label">Search by faculty name or project</span>
            <div className="student-input-wrap">
              <Search size={17} />
              <input
                id="mentor-search"
                type="text"
                placeholder="Try: climate, finance, policy..."
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                className="form-control"
              />
            </div>
          </label>

          <label className="student-field" htmlFor="sdg-filter">
            <span className="student-field-label">Filter by SDG theme</span>
            <div className="student-input-wrap">
              <Filter size={17} />
              <select
                id="sdg-filter"
                value={selectedSDG}
                onChange={(event) => setSelectedSDG(Number(event.target.value))}
                className="form-control"
              >
                {SDG_OPTIONS.map((option) => (
                  <option key={option.number} value={option.number}>
                    {option.title}
                  </option>
                ))}
              </select>
            </div>
          </label>
        </div>

        <p className="student-result-meta mb-0">
          Showing <strong>{filteredMentors.length}</strong> mentor matches
          {selectedSDG !== 0 && (
            <>
              {' '}
              for <strong>{SDG_OPTIONS.find((option) => option.number === selectedSDG)?.title}</strong>
            </>
          )}
          .
        </p>
      </section>

      {filteredMentors.length > 0 ? (
        <section className="student-results-grid grid grid-3">
          {filteredMentors.map((mentor) => (
            <MentorCard key={mentor.id} {...mentor} />
          ))}
        </section>
      ) : (
        <section className="student-empty card">
          <h3>No mentors found</h3>
          <p>Try broadening the search text or selecting a different SDG filter.</p>
          <button
            className="btn btn-outline"
            onClick={() => {
              setSelectedSDG(0)
              setSearchQuery('')
            }}
          >
            Clear Filters
          </button>
        </section>
      )}
    </div>
  )
}
