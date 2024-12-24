import React, { useState, useEffect } from 'react';
import {
  Container,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
} from '@mui/material';
import { getOrders, getMenu } from '../services/api.ts';
import { Order, MenuItem } from '../types';
import { useAuth } from '../contexts/AuthContext.tsx';
import { Navigate } from 'react-router-dom';
import NavBar from '../components/NavBar.tsx';

const AdminOrders: React.FC = () => {
  const { role } = useAuth();
  const [orders, setOrders] = useState<Order[]>([]);
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);

  useEffect(() => {
    loadOrders();
    loadMenu();
    const interval = setInterval(() => {
      loadOrders();
      loadMenu();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadOrders = async () => {
    try {
      const data = await getOrders();
      setOrders(data);
    } catch (err) {
      console.error('Failed to load orders:', err);
    }
  };

  const loadMenu = async () => {
    try {
      const data = await getMenu();
      setMenuItems(data);
    } catch (err) {
      console.error('Failed to load menu:', err);
    }
  };

  if (role !== 'admin') {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <NavBar />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Stock Levels
        </Typography>
        <TableContainer component={Paper} sx={{ mb: 4 }}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Item Name</TableCell>
                <TableCell>Current Stock</TableCell>
                <TableCell>Category</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {menuItems
                .filter(item => item.track_stock)
                .map((item) => (
                  <TableRow key={item.id}>
                    <TableCell>{item.name}</TableCell>
                    <TableCell>
                      <Chip 
                        label={item.stock ?? 0}
                        color={(item.stock ?? 0) < 10 ? 'error' : 'success'}
                      />
                    </TableCell>
                    <TableCell>{item.category}</TableCell>
                  </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        <Typography variant="h4" gutterBottom>
          All Orders
        </Typography>
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Order ID</TableCell>
                <TableCell>Table Number</TableCell>
                <TableCell>Items</TableCell>
                <TableCell>Total</TableCell>
                <TableCell>Status</TableCell>
                <TableCell>Assigned Staff</TableCell>
                <TableCell>Assignment Time</TableCell>
                <TableCell>Date</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {orders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>{order.id}</TableCell>
                  <TableCell>{order.table_number}</TableCell>
                  <TableCell>
                    {order.items.map(item => 
                      `${item.name} (x${item.quantity})`
                    ).join(', ')}
                  </TableCell>
                  <TableCell>${order.total_price.toFixed(2)}</TableCell>
                  <TableCell>{order.status}</TableCell>
                  <TableCell>{order.staff_name || 'Unassigned'}</TableCell>
                  <TableCell>
                    {new Date(order.created_at).toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Container>
    </>
  );
};

export default AdminOrders; 