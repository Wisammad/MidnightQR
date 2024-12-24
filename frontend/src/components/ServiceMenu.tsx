import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Button,
  Grid,
  Box
} from '@mui/material';

interface ServiceMenuProps {
  onRequestService: (serviceType: string) => void;
}

const services = [
  {
    id: 'empty-glasses',
    name: 'Empty Glasses',
    description: 'Request clean empty glasses for your table',
    icon: '🥃'
  },
  {
    id: 'waiter-service',
    name: 'Call Waiter',
    description: 'Request waiter assistance at your table',
    icon: '👋'
  },
  {
    id: 'bottle-show',
    name: 'Bottle Show Service',
    description: 'Request a special bottle presentation service',
    icon: '🍾'
  }
];

const ServiceMenu: React.FC<ServiceMenuProps> = ({ onRequestService }) => {
  return (
    <Grid container spacing={2}>
      {services.map((service) => (
        <Grid item xs={12} sm={6} md={4} key={service.id}>
          <Card>
            <CardContent>
              <Box display="flex" flexDirection="column" alignItems="center">
                <Typography variant="h1" component="div" sx={{ fontSize: '3rem', mb: 2 }}>
                  {service.icon}
                </Typography>
                <Typography variant="h6" component="div" gutterBottom>
                  {service.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                  {service.description}
                </Typography>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => onRequestService(service.id)}
                >
                  Request Service
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
};

export default ServiceMenu; 