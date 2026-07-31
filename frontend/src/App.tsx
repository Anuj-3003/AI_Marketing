import { Route, Routes } from 'react-router-dom'
import { Home } from './pages/Home'
import { CompetitorAds } from './pages/CompetitorAds'
import { GeneratedAds } from './pages/GeneratedAds'
import { Analytics } from './pages/Analytics'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/competitors/:id/ads" element={<CompetitorAds />} />
      <Route path="/ads/generate" element={<GeneratedAds />} />
      <Route path="/campaigns/:id/analytics" element={<Analytics />} />
    </Routes>
  )
}

export default App
