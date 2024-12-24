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
  Chip,
  Typography,
  Box,
  Tabs,
  Tab
} from '@mui/material';
import { Order } from '../types';
import { updateOrderStatus } from '../services/api.ts';

interface TableOrdersProps {
  orders: Order[];
  onOrderUpdate: () => void;
  hideTimestamp?: boolean;
}

const TableOrders: React.FC<TableOrdersProps> = ({ orders, onOrderUpdate, hideTimestamp = false }) => {
  const [tabValue, setTabValue] = React.useState(0);

  const handleRefund = async (orderId: number) => {
    try {
      await updateOrderStatus(orderId, 'Refunded');
      onOrderUpdate();
    } catch (error) {
      console.error('Failed to refund order:', error);
    }
  };

  const pendingOrders = orders.filter(order => order.status === 'Pending');
  const acceptedOrders = orders.filter(order => order.status === 'Accepted');

  const orderTableColumns = [
    { id: 'orderId', label: 'Order ID' },
    { id: 'items', label: 'Items' },
    { id: 'total', label: 'Total' },
    { id: 'status', label: 'Status' },
    { id: 'actions', label: 'Actions' }
  ];

  return (
    <Box sx={{ width: '100%' }}>
      <Tabs value={tabValue} onChange={(_, newValue) => setTabValue(newValue)}>
        <Tab label="Pending Orders" />
        <Tab label="In Progress Orders" />
      </Tabs>

      {tabValue === 0 && (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                {orderTableColumns.map((column) => (
                  <TableCell key={column.id}>{column.label}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {pendingOrders.map((order) => (
                <TableRow key={order.id}>
                  <TableCell>{order.id}</TableCell>
                  <TableCell>
                    {order.items.map(item => 
                      `${item.name} (x${item.quantity})`
                    ).join(', ')}
                  </TableCell>
                  <TableCell>${order.total_price.toFixed(2)}</TableCell>
                  <TableCell>{order.status}</TableCell>
                  <TableCell>
                    <Button
                      variant="contained"
                      color="error"
                      onClick={() => handleRefund(order.id)}
                    >
                      {order.is_service ? 'Cancel Service' : 'Refund Order'}
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      {tabValue === 1 && (
        <TableContainer component={Paper} sx={{ mt: 2 }}>
          <Table>
            <TableHead>
              <TableRow>
                {orderTableColumns.map((column) => (
                  <TableCell key={column.id}>{column.label}</TableCell>
                ))}
              </TableRow>
            </TableHead>
            <TableBody>
              {acceptedOrders.map((order) => (
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
                      color="info"
                    />
                  </TableCell>
                  <TableCell>-</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      )}
    </Box>
  );
};

export default TableOrders; 