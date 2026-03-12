import { useState } from 'react'
import { Sparkles, Network, Search, UserCircle2, Coins, UserRound, type LucideIcon } from 'lucide-react'
import ProfileUpload from '../components/networking/ProfileUpload'
import NetworkChatbot from '../components/networking/NetworkChatbot'
import NetworkGraph from '../components/networking/NetworkGraph'
import Leaderboard from '../components/networking/Leaderboard'
import DonorSearch from '../components/networking/DonorSearch'
import DonorPortal from '../components/networking/DonorPortal'
import FacultyUpdate from '../components/networking/FacultyUpdate'
import './Networking.css'

type NetworkingTab = 'profile' | 'graph' | 'funding' | 'donors' | 'faculty'

const TAB_CONFIG: { id: NetworkingTab; label: string; icon: LucideIcon }[] = [
  { id: 'profile', label: 'Create Profile', icon: UserCircle2 },
  { id: 'graph', label: 'Network Analysis', icon: Network },
  { id: 'funding', label: 'Find Funding', icon: Search },
  { id: 'donors', label: 'For Donors', icon: Coins },
  { id: 'faculty', label: 'Faculty Updates', icon: UserRound },
]

export default function Networking() {
  const [activeTab, setActiveTab] = useState<NetworkingTab>('profile')
  const [graphData, setGraphData] = useState<any>(null)

  const handleGraphUpdate = (data: any) => {
    const safeGraphData =
      data && Array.isArray(data.nodes) && Array.isArray(data.edges)
        ? data
        : null
    setGraphData(safeGraphData)
    if (activeTab !== 'graph') {
      setActiveTab('graph')
    }
  }

  return (
    <div className="container networking-view page-shell">
      <header className="page-header networking-header">
        <span className="eyebrow">
          <Sparkles size={12} /> Collaboration Hub
        </span>
        <h1>Networking and Opportunity Matching</h1>
        <p className="page-subtitle">
          Build profiles, discover collaborators, and connect donors to active projects through one network layer.
        </p>
      </header>

      <div className="networking-tabs" role="tablist" aria-label="Networking modules">
        {TAB_CONFIG.map((tab) => {
          const Icon = tab.icon
          const selected = activeTab === tab.id
          return (
            <button
              key={tab.id}
              className={selected ? 'networking-tab active' : 'networking-tab'}
              onClick={() => setActiveTab(tab.id)}
              role="tab"
              aria-selected={selected}
            >
              <Icon size={15} />
              <span>{tab.label}</span>
            </button>
          )
        })}
      </div>

      {activeTab === 'funding' ? (
        <section className="networking-full-width">
          <DonorSearch />
        </section>
      ) : activeTab === 'donors' ? (
        <section className="networking-full-width">
          <DonorPortal />
        </section>
      ) : activeTab === 'faculty' ? (
        <section className="networking-full-width">
          <FacultyUpdate />
        </section>
      ) : (
        <section className="networking-main-grid">
          <div className="networking-primary-column">
            {activeTab === 'profile' ? (
              <ProfileUpload />
            ) : (
              <div className="network-graph-panel card">
                <h3 className="card-title">Collaboration Graph</h3>
                <p className="card-subtitle mb-3">
                  Explore relationship pathways between students, faculty, and domain skills.
                </p>
                <div className="network-graph-canvas">
                  <NetworkGraph data={graphData} />
                </div>
              </div>
            )}
          </div>

          <aside className="networking-side-column">
            <Leaderboard />
            <div className="networking-chat-shell">
              <NetworkChatbot onGraphUpdate={handleGraphUpdate} />
            </div>
          </aside>
        </section>
      )}
    </div>
  )
}
