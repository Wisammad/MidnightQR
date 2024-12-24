import axios from 'axios';
import { OrderItem } from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://192.168.1.168:5001';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const login = async (username: string, password: string) => {
  const response = await api.post('/auth/login', { username, password });
  return response.data;
};

export const getMenu = async () => {
  const response = await api.get('/menu');
  return response.data;
};

export const createOrder = async (items: OrderItem[]) => {
  const response = await api.post('/orders', { 
    items: items.map(item => ({
      id: item.id,
      quantity: item.quantity
    }))
  });
  return response.data;
};

export const getOrders = async () => {
  try {
    const response = await api.get('/orders');
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
    throw error;
  }
};

export const updateOrderStatus = async (
  orderId: number, 
  status: string, 
  staffId?: number
) => {
  const response = await fetch(`${API_URL}/orders/${orderId}/status`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${localStorage.getItem('token')}`
    },
    body: JSON.stringify({ status, staff_id: staffId })
  });
  
  if (!response.ok) {
    throw new Error('Failed to update order status');
  }
  
  return response.json();
};

export const processPayment = async (orderId: number, amount: number) => {
  const response = await api.post('/payments', { order_id: orderId, amount });
  return response.data;
};

export const authenticateViaQR = async (tableNumber: string, token: string) => {
  try {
    const response = await api.post('/auth/qr', { tableNumber, token });
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      return response.data;
    }
    throw new Error('Authentication failed');
  } catch (error) {
    throw error;
  }
}; 