import React, { useState, useEffect } from 'react';
import { Container, Typography, Alert } from '@mui/material';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';
import { getOrders } from '../services/api.ts';
import StaffOrderList from '../components/StaffOrderList.tsx';
import NavBar from '../components/NavBar.tsx';
import { Order } from '../types';

const StaffDashboard: React.FC = () => {
  const { role } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState<string>('');

  useEffect(() => {
    loadOrders();
    const interval = setInterval(loadOrders, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadOrders = async () => {
    try {
      const data = await getOrders();
      setOrders(data);
    } catch (err) {
      setError('Failed to load orders');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (role !== 'staff') {
    return <Navigate to="/login" replace />;
  }

  const activeOrders = orders.filter(order => ['Pending', 'Preparing'].includes(order.status));
  const completedOrders = orders.filter(order => order.status === 'Completed');

  return (
    <>
      <NavBar />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        
        <Typography variant="h4" gutterBottom>
          Active Orders
        </Typography>
        <StaffOrderList 
          orders={activeOrders}
          onOrderUpdate={loadOrders}
        />

        <Typography variant="h4" sx={{ mt: 4 }} gutterBottom>
          Completed Orders
        </Typography>
        <StaffOrderList 
          orders={completedOrders}
          onOrderUpdate={loadOrders}
        />
      </Container>
    </>
  );
};

export default StaffDashboard; 