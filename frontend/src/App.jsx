import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from './contexts/AuthContext'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Verification from './pages/Verification'
import Dashboard from './pages/Dashboard'
import Projects from './pages/Projects'
import ProjectDetail from './pages/ProjectDetail'
import AvailableProjects from './pages/AvailableProjects'
import Scraping from './pages/Scraping'
import Outreach from './pages/Outreach'
import Settings from './pages/Settings'
import Plans from './pages/Plans'
import PlanPurchase from './pages/PlanPurchase'
import PublicProjects from './pages/PublicProjects'
import PublicProjectDetail from './pages/PublicProjectDetail'
import Layout from './components/Layout'

function PrivateRoute({ children }) {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  return user ? children : <Navigate to="/login" />
}

function RootRoute() {
  const { user, loading } = useAuth()
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }
  
  // If user is authenticated, redirect to dashboard
  if (user) {
    return <Navigate to="/dashboard" replace />
  }
  
  // If not authenticated, show public projects
  return <PublicProjects />
}

function AppRoutes() {
  return (
    <Routes>
      {/* Root route - shows public projects or dashboard based on auth */}
      <Route path="/" element={<RootRoute />} />
      
      {/* Public routes (no authentication required) */}
      <Route path="/public" element={<PublicProjects />} />
      <Route path="/public/projects/:id" element={<PublicProjectDetail />} />
      
      {/* Auth routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Signup />} />
      <Route
        path="/verify"
        element={
          <PrivateRoute>
            <Verification />
          </PrivateRoute>
        }
      />
      
      {/* Private routes (authentication required) */}
      <Route
        path="/dashboard"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="projects" element={<Projects />} />
        <Route path="projects/available" element={<AvailableProjects />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="scraping" element={<Scraping />} />
        <Route path="outreach" element={<Outreach />} />
        <Route path="settings" element={<Settings />} />
        <Route path="plans" element={<Plans />} />
        <Route path="plans/purchase/:planId" element={<PlanPurchase />} />
      </Route>
      
      {/* Legacy routes - redirect to dashboard for authenticated users */}
      <Route
        path="/app/*"
        element={
          <PrivateRoute>
            <Layout />
          </PrivateRoute>
        }
      >
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="projects" element={<Projects />} />
        <Route path="projects/available" element={<AvailableProjects />} />
        <Route path="projects/:id" element={<ProjectDetail />} />
        <Route path="scraping" element={<Scraping />} />
        <Route path="outreach" element={<Outreach />} />
        <Route path="settings" element={<Settings />} />
        <Route path="plans" element={<Plans />} />
        <Route path="plans/purchase/:planId" element={<PlanPurchase />} />
      </Route>
    </Routes>
  )
}

function App() {
  return (
    <Router>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </Router>
  )
}

export default App
