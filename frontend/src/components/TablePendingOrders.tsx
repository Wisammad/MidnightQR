import React from 'react';
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
import { Order } from '../types';
import { updateOrderStatus } from '../services/api.ts';

interface TablePendingOrdersProps {
  orders: Order[];
  onOrderUpdate: () => void;
}

const TablePendingOrders: React.FC<TablePendingOrdersProps> = ({ orders, onOrderUpdate }) => {
  const handleRefund = async (orderId: number) => {
    try {
      await updateOrderStatus(orderId, 'Refunded');
      onOrderUpdate();
    } catch (error) {
      console.error('Failed to refund order:', error);
    }
  };

  return (
    <TableContainer component={Paper}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Order ID</TableCell>
            <TableCell>Items</TableCell>
            <TableCell>Total</TableCell>
            <TableCell>Status</TableCell>
            <TableCell>Time</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {orders.map((order) => (
            <TableRow key={order.id}>
              <TableCell>{order.id}</TableCell>
              <TableCell>
                {order.items.map(item => 
                  `${item.name} (x${item.quantity})`
                ).join(', ')}
              </TableCell>
              <TableCell>${order.total_price.toFixed(2)}</TableCell>
              <TableCell>
                <Chip 
                  label={order.status}
                  color={
                    order.status === 'Accepted' ? 'info' :
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
                    color="error"
                    onClick={() => handleRefund(order.id)}
                  >
                    {order.is_service ? 'Cancel Service' : 'Refund Order'}
                  </Button>
                )}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};

export default TablePendingOrders; 