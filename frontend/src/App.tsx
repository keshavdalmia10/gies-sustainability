import { Suspense, lazy } from 'react'
import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import Layout from './components/Layout'
import RouteErrorBoundary from './components/RouteErrorBoundary'

const DeanView = lazy(() => import('./pages/DeanView'))
const DonorView = lazy(() => import('./pages/DonorView'))
const StudentView = lazy(() => import('./pages/StudentView'))
const ImpactCardDetail = lazy(() => import('./pages/ImpactCardDetail'))
const Networking = lazy(() => import('./pages/Networking'))

function App() {
  return (
    <Layout>
      <RouteErrorBoundary>
        <Suspense fallback={<div className="container page-shell">Loading view...</div>}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/dean" element={<DeanView />} />
            <Route path="/donor" element={<DonorView />} />
            <Route path="/student" element={<StudentView />} />
            <Route path="/impact-card/:cardId" element={<ImpactCardDetail />} />
            <Route path="/networking" element={<Networking />} />
          </Routes>
        </Suspense>
      </RouteErrorBoundary>
    </Layout>
  )
}

export default App
