import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Typography,
  CircularProgress,
  Box
} from '@mui/material';
import { Order } from '../types';

interface PaymentWindowProps {
  order: Order | null;
  open: boolean;
  onClose: () => void;
  onPaymentComplete: () => void;
}

const PaymentWindow: React.FC<PaymentWindowProps> = ({
  order,
  open,
  onClose,
  onPaymentComplete
}) => {
  const [timeLeft, setTimeLeft] = useState<number>(300); // 5 minutes in seconds
  const [cardNumber, setCardNumber] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [cvv, setCvv] = useState('');

  useEffect(() => {
    if (open && order) {
      setTimeLeft(300);
      const timer = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearInterval(timer);
            onClose();
            return 0;
          }
          return prev - 1;
        });
      }, 1000);

      return () => clearInterval(timer);
    }
  }, [open, order]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleSubmit = () => {
    // Simulate payment processing
    onPaymentComplete();
    onClose();
  };

  if (!order || !open) return null;

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Complete Your Payment</DialogTitle>
      <DialogContent>
        <Box sx={{ mb: 2 }}>
          <Typography color="error">
            Time remaining: {formatTime(timeLeft)}
          </Typography>
          <Typography variant="h6" gutterBottom>
            Total Amount: ${order.total_price?.toFixed(2) || '0.00'}
          </Typography>
        </Box>

        <TextField
          fullWidth
          label="Card Number"
          value={cardNumber}
          onChange={(e) => setCardNumber(e.target.value)}
          margin="normal"
        />
        <TextField
          fullWidth
          label="Expiry Date (MM/YY)"
          value={expiryDate}
          onChange={(e) => setExpiryDate(e.target.value)}
          margin="normal"
        />
        <TextField
          fullWidth
          label="CVV"
          value={cvv}
          onChange={(e) => setCvv(e.target.value)}
          margin="normal"
          type="password"
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose} color="error">
          Cancel
        </Button>
        <Button 
          onClick={handleSubmit} 
          color="primary" 
          variant="contained"
          disabled={!cardNumber || !expiryDate || !cvv}
        >
          Pay Now
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default PaymentWindow; 