import { ShieldCheck } from 'lucide-react'
import ImpactCard from '../components/ImpactCard'
import './ImpactCardDetail.css'

export default function ImpactCardDetail() {
  const mockCardData = {
    faculty: {
      name: 'Prof. Jane Doe',
      department: 'Department of Finance',
      imageUrl: 'https://i.pravatar.cc/150?u=jane',
    },
    sdg: {
      number: 7,
      title: 'Affordable and Clean Energy',
      color: '#fcc30b',
    },
    narrative:
      "Professor Jane Doe's research addresses the critical barrier of financing for small-scale solar installations. By developing novel risk-assessment models for rural cooperatives, her work has unlocked capital for over 200 rooftop systems in Illinois. This financial innovation directly translates to cleaner energy access and local job creation, bridging the gap between high-level economic theory and tangible community impact.",
    keyOutcomes: [
      '200 rooftop solar systems financed',
      '200+ local jobs created in installation and maintenance',
      '15 Illinois communities served',
      'Adoption of new lending guidelines by IL EPA',
    ],
    metrics: {
      totalFunding: 2100000,
      communitiesReached: 15,
      fundingGap: 500000,
    },
    evidence: {
      publications: [
        {
          id: 'p1',
          title: 'Risk Models for Distributed Solar Finance',
          journal: 'Journal of Sustainable Finance',
          year: 2023,
          confidence: 0.95,
          url: '#',
        },
        {
          id: 'p2',
          title: 'Community Solar: Economic Viability Analysis',
          journal: 'Energy Policy Review',
          year: 2022,
          confidence: 0.88,
          url: '#',
        },
        {
          id: 'p3',
          title: 'Rural Cooperative Lending Frameworks',
          journal: 'Agri-Economics Quarterly',
          year: 2021,
          confidence: 0.92,
          url: '#',
        },
      ],
      grants: [
        {
          id: 'g1',
          title: 'Solar Financing for Rural Co-ops',
          funder: 'DOE SunShot Initiative',
          amount: 1500000,
          confidence: 0.98,
        },
        {
          id: 'g2',
          title: 'Economic Impact of Community Solar',
          funder: 'Illinois EPA',
          amount: 600000,
          confidence: 0.9,
        },
      ],
      patents: [
        {
          id: 'pt1',
          title: 'Algorithmic Risk Assessment for Micro-Utilities',
          number: 'US-2023-998877',
          confidence: 0.99,
        },
        {
          id: 'pt2',
          title: 'Distributed Ledger for Solar Credits',
          number: 'US-2022-112233',
          confidence: 0.85,
        },
      ],
    },
  }

  return (
    <div className="container impact-detail page-shell">
      <header className="page-header impact-detail-header">
        <span className="eyebrow">
          <ShieldCheck size={12} /> Evidence Story View
        </span>
        <h1>Impact Card Preview</h1>
        <p className="page-subtitle">Visualizing the link between research output and real-world change.</p>
      </header>

      <ImpactCard {...mockCardData} />

      <p className="impact-detail-footnote">
        This preview uses mock data to demonstrate the impact-linkage card design and evidence workflow. In
        production this view should fetch <code>/api/impact-cards/:id</code>.
      </p>
    </div>
  )
}
