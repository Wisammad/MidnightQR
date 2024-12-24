import React, { useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { authenticateViaQR } from '../services/api.ts';
import { useAuth } from '../contexts/AuthContext.tsx';
import { CircularProgress, Container, Typography } from '@mui/material';

const QRAuthPage: React.FC = () => {
  const { tableNumber, token } = useParams();
  const navigate = useNavigate();
  const { login: authLogin } = useAuth();

  useEffect(() => {
    const authenticate = async () => {
      try {
        const data = await authenticateViaQR(tableNumber!, token!);
        authLogin(data.access_token, data.role);
        navigate(`/table/${tableNumber}`);
      } catch (error) {
        console.error('Authentication error:', error);
        navigate('/login');
      }
    };

    if (tableNumber && token) {
      authenticate();
    }
  }, [tableNumber, token, navigate, authLogin]);

  return (
    <Container sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', mt: 4 }}>
      <CircularProgress />
      <Typography sx={{ mt: 2 }}>Authenticating...</Typography>
    </Container>
  );
};

export default QRAuthPage; 