import { useState } from 'react';
import { Search, Filter } from 'lucide-react';
import MentorCard from '../components/MentorCard';

// Mock Data
const MOCK_MENTORS = [
  {
    id: 1,
    faculty: {
      name: "Prof. Jane Doe",
      department: "Finance",
      email: "jane.doe@example.edu",
      imageUrl: "https://i.pravatar.cc/150?u=jane"
    },
    sdg: { number: 7, title: "Affordable and Clean Energy", color: "#fcc30b" },
    activeProjects: ["Solar Financing Risk Models", "Rural Cooperative Lending"],
    studentOpportunities: ["RA Position (Paid)", "Independent Study"]
  },
  {
    id: 2,
    faculty: {
      name: "Prof. John Smith",
      department: "Business Administration",
      email: "john.smith@example.edu",
      imageUrl: "https://i.pravatar.cc/150?u=john"
    },
    sdg: { number: 13, title: "Climate Action", color: "#3f7e44" },
    activeProjects: ["Corporate Carbon Disclosure", "Supply Chain Resilience"],
    studentOpportunities: ["Case Competition Mentor", "Thesis Advisor"]
  },
  {
    id: 3,
    faculty: {
      name: "Prof. Emily Chen",
      department: "Accountancy",
      email: "emily.chen@example.edu",
      imageUrl: "https://i.pravatar.cc/150?u=emily"
    },
    sdg: { number: 12, title: "Responsible Consumption", color: "#cf8d2a" },
    activeProjects: ["Circular Economy Audits", "Waste Reduction Metrics"],
    studentOpportunities: ["RA Position (Credit)", "Capstone Project"]
  },
  {
    id: 4,
    faculty: {
      name: "Prof. Michael Brown",
      department: "Economics",
      email: "michael.brown@example.edu"
    },
    sdg: { number: 8, title: "Decent Work and Economic Growth", color: "#a21942" },
    activeProjects: ["Labor Market Analysis", "Gig Economy Policy"],
    studentOpportunities: ["Data Analysis RA", "Seminar Course"]
  }
];

const SDG_OPTIONS = [
  { number: 0, title: "All SDGs" },
  { number: 7, title: "SDG 7: Clean Energy" },
  { number: 8, title: "SDG 8: Decent Work" },
  { number: 12, title: "SDG 12: Responsible Consumption" },
  { number: 13, title: "SDG 13: Climate Action" },
];

export default function StudentView() {
  const [selectedSDG, setSelectedSDG] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");

  const filteredMentors = MOCK_MENTORS.filter(mentor => {
    const matchesSDG = selectedSDG === 0 || mentor.sdg.number === selectedSDG;
    const matchesSearch = mentor.faculty.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          mentor.activeProjects.some(p => p.toLowerCase().includes(searchQuery.toLowerCase()));
    return matchesSDG && matchesSearch;
  });

  return (
    <div className="container" style={{ paddingBottom: 'var(--spacing-2xl)' }}>
      
      {/* Hero Section */}
      <div style={{ textAlign: 'center', marginBottom: 'var(--spacing-xl)', padding: 'var(--spacing-xl) 0' }}>
        <h1 style={{ marginBottom: 'var(--spacing-sm)' }}>Find Your Mentor</h1>
        <p className="text-muted" style={{ fontSize: 'var(--font-size-lg)', maxWidth: '600px', margin: '0 auto' }}>
          Connect with faculty working on the sustainability challenges you care about.
          Find research opportunities, thesis advisors, and project mentors.
        </p>
      </div>

      {/* Search & Filter */}
      <div className="card" style={{ padding: 'var(--spacing-lg)', marginBottom: 'var(--spacing-xl)' }}>
        <div style={{ display: 'flex', gap: 'var(--spacing-md)', flexWrap: 'wrap' }}>
          
          <div style={{ flex: 1, minWidth: '200px', position: 'relative' }}>
            <Search size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-light)' }} />
            <input 
              type="text" 
              placeholder="Search by name or topic..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              style={{ 
                width: '100%', 
                padding: '10px 10px 10px 40px', 
                borderRadius: 'var(--radius-md)', 
                border: '1px solid var(--color-border)',
                fontSize: 'var(--font-size-md)'
              }}
            />
          </div>

          <div style={{ minWidth: '200px', position: 'relative' }}>
            <Filter size={20} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-light)' }} />
            <select 
              value={selectedSDG}
              onChange={(e) => setSelectedSDG(Number(e.target.value))}
              style={{ 
                width: '100%', 
                padding: '10px 10px 10px 40px', 
                borderRadius: 'var(--radius-md)', 
                border: '1px solid var(--color-border)',
                fontSize: 'var(--font-size-md)',
                appearance: 'none',
                backgroundColor: 'white'
              }}
            >
              {SDG_OPTIONS.map(opt => (
                <option key={opt.number} value={opt.number}>{opt.title}</option>
              ))}
            </select>
          </div>

        </div>
      </div>

      {/* Results Grid */}
      {filteredMentors.length > 0 ? (
        <div className="grid grid-3">
          {filteredMentors.map(mentor => (
            <MentorCard key={mentor.id} {...mentor} />
          ))}
        </div>
      ) : (
        <div style={{ textAlign: 'center', padding: 'var(--spacing-2xl)', color: 'var(--color-text-light)' }}>
          <p style={{ fontSize: 'var(--font-size-lg)' }}>No mentors found matching your criteria.</p>
          <button 
            className="btn btn-outline mt-2"
            onClick={() => { setSelectedSDG(0); setSearchQuery(""); }}
          >
            Clear Filters
          </button>
        </div>
      )}

    </div>
  );
}
