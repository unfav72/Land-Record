import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import Upload from './pages/Upload';
import Records from './pages/Records';
import Verification from './pages/Verification';
import Users from './pages/Users';
import ManualEntry from './pages/ManualEntry';
import ErrorBoundary from './components/ErrorBoundary';



function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      
      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/upload" element={<ErrorBoundary><Upload /></ErrorBoundary>} />
          <Route path="/manual-entry" element={<ErrorBoundary><ManualEntry /></ErrorBoundary>} />
          {/* Note: The 'Records' list also serves as search/filter base in this UI design */}
          <Route path="/records" element={<Records />} />
          <Route path="/search" element={<Navigate to="/records" replace />} /> 
          
          <Route path="/verify/:id" element={<Verification />} />
          
          <Route element={<ProtectedRoute requiredRole="admin" />}>
            <Route path="/users" element={<Users />} />
          </Route>
        </Route>
      </Route>
      
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
