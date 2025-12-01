import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import DeanView from './pages/DeanView'
import DonorView from './pages/DonorView'
import StudentView from './pages/StudentView'
import ImpactCardDetail from './pages/ImpactCardDetail'
import Networking from './pages/Networking'
import Layout from './components/Layout'

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/dean" element={<DeanView />} />
        <Route path="/donor" element={<DonorView />} />
        <Route path="/student" element={<StudentView />} />
        <Route path="/impact-card/:cardId" element={<ImpactCardDetail />} />
        <Route path="/networking" element={<Networking />} />
      </Routes>
    </Layout>
  )
}

export default App
