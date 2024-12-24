import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, CssBaseline } from '@mui/material';
import { AuthProvider } from './contexts/AuthContext.tsx';
import theme from './theme.ts';
import ProtectedRoute from './components/ProtectedRoute.tsx';

// Pages
import Login from './pages/Login.tsx';
import TableView from './pages/TableView.tsx';
import StaffDashboard from './pages/StaffDashboard.tsx';
import AdminDashboard from './pages/AdminDashboard.tsx';
import AdminOrders from './components/AdminOrders.tsx';
import QRAuthPage from './pages/QRAuthPage.tsx';

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route 
              path="/table/:tableNumber" 
              element={
                <ProtectedRoute allowedRoles={['table']}>
                  <TableView />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/staff" 
              element={
                <ProtectedRoute allowedRoles={['staff']}>
                  <StaffDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminDashboard />
                </ProtectedRoute>
              } 
            />
            <Route 
              path="/admin/orders" 
              element={
                <ProtectedRoute allowedRoles={['admin']}>
                  <AdminOrders />
                </ProtectedRoute>
              } 
            />
            <Route path="/qr-auth/:tableNumber/:token" element={<QRAuthPage />} />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
