import React, { useState, useEffect } from 'react';
import { Container, Grid, Typography, Box, Alert } from '@mui/material';
import MenuList from '../components/MenuList.tsx';
import OrderSummary from '../components/OrderSummary.tsx';
import { MenuItem, OrderItem, Order } from '../types';
import { getMenu, createOrder, getOrders } from '../services/api.ts';
import { useAuth } from '../contexts/AuthContext.tsx';
import { Navigate } from 'react-router-dom';
import NavBar from '../components/NavBar.tsx';
import TableOrders from '../components/TableOrders.tsx';
import ServiceMenu from '../components/ServiceMenu.tsx';
import PaymentWindow from '../components/PaymentWindow.tsx';

const TableView: React.FC = () => {
  const { role } = useAuth();
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [orderItems, setOrderItems] = useState<OrderItem[]>([]);
  const [orders, setOrders] = useState<Order[]>([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [paymentOrder, setPaymentOrder] = useState<Order | null>(null);

  useEffect(() => {
    loadMenu();
    loadOrders();
    const interval = setInterval(() => {
      loadOrders();
    }, 30000); // Refresh orders every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const loadMenu = async () => {
    try {
      const items = await getMenu();
      setMenuItems(items);
    } catch (err) {
      setError('Failed to load menu');
    }
  };

  const loadOrders = async () => {
    try {
      const orders = await getOrders();
      setOrders(orders);
    } catch (err) {
      setError('Failed to load orders');
    }
  };

  const handleAddItem = (itemId: number) => {
    const menuItem = menuItems.find(item => item.id === itemId);
    if (!menuItem) return;

    setOrderItems(prevItems => {
      const existingItem = prevItems.find(item => item.id === itemId);
      if (existingItem) {
        return prevItems.map(item =>
          item.id === itemId
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prevItems, { ...menuItem, quantity: 1 }];
    });
  };

  const handleRemoveItem = (itemId: number) => {
    setOrderItems(prevItems => {
      const existingItem = prevItems.find(item => item.id === itemId);
      if (existingItem && existingItem.quantity > 1) {
        return prevItems.map(item =>
          item.id === itemId
            ? { ...item, quantity: item.quantity - 1 }
            : item
        );
      }
      return prevItems.filter(item => item.id !== itemId);
    });
  };

  const handlePlaceOrder = async () => {
    try {
      const response = await createOrder(orderItems);
      setPaymentOrder(response);
      setOrderItems([]);
      loadOrders();
    } catch (err) {
      setError('Failed to place order');
      setTimeout(() => setError(''), 3000);
    }
  };

  const handleServiceRequest = async (serviceType: string) => {
    try {
      const serviceItems = {
        'empty-glasses': { 
          id: menuItems.find(item => item.name === 'Empty Glasses')?.id,
          name: 'Empty Glasses',
          price: 0,
          quantity: 1
        },
        'waiter-service': {
          id: menuItems.find(item => item.name === 'Waiter Service')?.id,
          name: 'Waiter Service',
          price: 0,
          quantity: 1
        },
        'bottle-show': {
          id: menuItems.find(item => item.name === 'Bottle Show Service')?.id,
          name: 'Bottle Show Service',
          price: 0,
          quantity: 1
        }
      };
      
      const service = serviceItems[serviceType];
      if (!service.id) {
        throw new Error('Service not found in menu');
      }
      await createOrder([service]);
      setSuccess(`${service.name} requested successfully!`);
      loadOrders();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to request service');
      setTimeout(() => setError(''), 3000);
    }
  };

  if (role !== 'table') {
    return <Navigate to="/login" replace />;
  }

  const total = orderItems.reduce(
    (sum, item) => sum + item.price * item.quantity,
    0
  );

  return (
    <>
      <NavBar />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
        
        <Typography variant="h4" gutterBottom>
          Place New Order
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Typography variant="h5" gutterBottom>
              Menu
            </Typography>
            <MenuList items={menuItems} onAddItem={handleAddItem} />
          </Grid>
          <Grid item xs={12} md={4}>
            <OrderSummary
              items={orderItems}
              onRemoveItem={handleRemoveItem}
              onPlaceOrder={handlePlaceOrder}
              total={total}
            />
          </Grid>
        </Grid>

        <Typography variant="h4" sx={{ mt: 4 }} gutterBottom>
          Your Orders
        </Typography>
        <TableOrders 
          orders={orders}
          onOrderUpdate={loadOrders}
          hideTimestamp={true}
        />

        <Typography variant="h4" sx={{ mt: 4 }} gutterBottom>
          Services
        </Typography>
        <ServiceMenu 
          onRequestService={handleServiceRequest}
        />

        <PaymentWindow
          order={paymentOrder}
          open={!!paymentOrder}
          onClose={() => setPaymentOrder(null)}
          onPaymentComplete={() => {
            setSuccess('Payment completed successfully!');
            loadOrders();
            setTimeout(() => setSuccess(''), 3000);
          }}
        />
      </Container>
    </>
  );
};

export default TableView; 