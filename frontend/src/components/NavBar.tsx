import React from 'react';
import { AppBar, Toolbar, Button, Box } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext.tsx';

const NavBar: React.FC = () => {
  const navigate = useNavigate();
  const { logout, role } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <AppBar position="static">
      <Toolbar>
        {role === 'admin' && (
          <Box sx={{ flexGrow: 1 }}>
            <Button color="inherit" onClick={() => navigate('/admin')}>QR Codes</Button>
            <Button color="inherit" onClick={() => navigate('/admin/orders')}>Orders</Button>
          </Box>
        )}
        <Button color="inherit" onClick={handleLogout}>
          Logout
        </Button>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar; 