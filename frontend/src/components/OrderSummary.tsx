import React from 'react';
import {
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Button,
  Box
} from '@mui/material';
import RemoveIcon from '@mui/icons-material/Remove';
import { OrderItem } from '../types';

interface OrderSummaryProps {
  items: OrderItem[];
  onRemoveItem: (itemId: number) => void;
  onPlaceOrder: () => void;
  total: number;
}

const OrderSummary: React.FC<OrderSummaryProps> = ({
  items,
  onRemoveItem,
  onPlaceOrder,
  total
}) => {
  return (
    <Paper elevation={2}>
      <Box p={2}>
        <Typography variant="h6" gutterBottom>
          Order Summary
        </Typography>
        <List>
          {items.map((item) => (
            <ListItem key={item.id}>
              <ListItemText
                primary={item.name}
                secondary={`$${item.price.toFixed(2)} x ${item.quantity}`}
              />
              <ListItemSecondaryAction>
                <IconButton edge="end" onClick={() => onRemoveItem(item.id)}>
                  <RemoveIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
        <Box mt={2}>
          <Typography variant="h6">
            Total: ${total.toFixed(2)}
          </Typography>
          <Button
            variant="contained"
            color="primary"
            fullWidth
            onClick={onPlaceOrder}
            disabled={items.length === 0}
            sx={{ mt: 2 }}
          >
            Place Order
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

export default OrderSummary; 