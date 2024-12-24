import React, { useState, useEffect } from 'react';
import { Box, Container, Grid, Typography } from '@mui/material';
import QRCodeGenerator from '../components/QRCodeGenerator.tsx';
import { useAuth } from '../contexts/AuthContext.tsx';
import { Navigate } from 'react-router-dom';
import NavBar from '../components/NavBar.tsx';

const AdminDashboard: React.FC = () => {
  const { role } = useAuth();
  const [tables, setTables] = useState<number[]>([1, 2, 3, 4, 5]); // Default tables
  const baseUrl = process.env.REACT_APP_API_URL?.replace(':5001', ':3000') || 'http://192.168.1.168:3000';

  if (role !== 'admin') {
    return <Navigate to="/login" replace />;
  }

  return (
    <>
      <NavBar />
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Table QR Codes
        </Typography>
        <Grid container spacing={3}>
          {tables.map((tableNumber) => (
            <Grid item xs={12} sm={6} md={4} key={tableNumber}>
              <QRCodeGenerator
                tableNumber={tableNumber}
                baseUrl={baseUrl}
              />
            </Grid>
          ))}
        </Grid>
      </Container>
    </>
  );
};

export default AdminDashboard; 