import React from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { Paper, Box, Typography } from '@mui/material';
import { generateSecureToken } from '../utils/security.ts';

interface QRCodeGeneratorProps {
  tableNumber: number;
  baseUrl: string;
}

const QRCodeGenerator: React.FC<QRCodeGeneratorProps> = ({ tableNumber, baseUrl }) => {
  const token = generateSecureToken(tableNumber);
  const qrValue = `${baseUrl}/qr-auth/${tableNumber}/${token}`;

  return (
    <Paper elevation={3}>
      <Box p={3} display="flex" flexDirection="column" alignItems="center">
        <Typography variant="h6" gutterBottom>
          Table {tableNumber} QR Code
        </Typography>
        <QRCodeSVG
          value={qrValue}
          size={256}
          level="H"
          includeMargin={true}
        />
        <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
          Scan to access table menu
        </Typography>
      </Box>
    </Paper>
  );
};

export default QRCodeGenerator; 