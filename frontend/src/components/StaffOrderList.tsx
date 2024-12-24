import React, { useEffect, useState } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Chip
} from '@mui/material';
import { MenuItem, Order } from '../types';
import { updateOrderStatus } from '../services/api.ts';
import { getMenu } from '../services/api.ts';
import { useAuth } from '../contexts/AuthContext.tsx';

interface StaffOrderListProps {
  orders: Order[];
  onOrderUpdate: () => void;
}

const StaffOrderList: React.FC<StaffOrderListProps> = ({ orders, onOrderUpdate }) => {
  const { user } = useAuth();
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);

  useEffect(() => {
    loadMenu();
    const interval = setInterval(loadMenu, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadMenu = async () => {
    try {
      const data = await getMenu();
      setMenuItems(data);
    } catch (err) {
      console.error('Failed to load menu:', err);
    }
  };

  const handleStatusUpdate = async (orderId: number, newStatus: string) => {
    try {
      await updateOrderStatus(orderId, newStatus, user?.id);
      onOrderUpdate();
    } catch (error) {
      console.error('Failed to update order status:', error);
    }
  };

  return (
    <>
      <TableContainer component={Paper} sx={{ mb: 4 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Item</TableCell>
              <TableCell>Available Stock</TableCell>
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
                      size="small"
                    />
                  </TableCell>
                </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Order ID</TableCell>
              <TableCell>Table</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Items</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Time</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {orders.map((order) => (
              <TableRow 
                key={order.id}
                sx={{ 
                  backgroundColor: order.is_service ? 'rgba(25, 118, 210, 0.08)' : 'inherit'
                }}
              >
                <TableCell>{order.id}</TableCell>
                <TableCell>{order.table_number}</TableCell>
                <TableCell>
                  <Chip 
                    label={order.is_service ? 'Service Request' : 'Order'}
                    color={order.is_service ? 'info' : 'default'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  {order.items.map(item => 
                    `${item.name} (x${item.quantity})`
                  ).join(', ')}
                </TableCell>
                <TableCell>
                  <Chip 
                    label={order.status}
                    color={
                      order.status === 'Completed' ? 'success' :
                      order.status === 'Pending' ? 'warning' :
                      'default'
                    }
                  />
                </TableCell>
                <TableCell>
                  {new Date(order.created_at).toLocaleString()}
                </TableCell>
                <TableCell>
                  {order.status === 'Pending' && (
                    <Button
                      variant="contained"
                      color="primary"
                      onClick={() => handleStatusUpdate(order.id, 'Accepted')}
                    >
                      {order.is_service ? 'Accept Request' : 'Accept Order'}
                    </Button>
                  )}
                  {order.status === 'Accepted' && (
                    <Button
                      variant="contained"
                      color="success"
                      onClick={() => handleStatusUpdate(order.id, 'Completed')}
                    >
                      {order.is_service ? 'Complete Request' : 'Mark Completed'}
                    </Button>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
    </>
  );
};

export default StaffOrderList; 