import React from 'react';
import { 
  List, 
  ListItem, 
  ListItemText, 
  ListItemSecondaryAction,
  IconButton,
  Typography,
  Paper
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import { MenuItem } from '../types';

interface MenuListProps {
  items: MenuItem[];
  onAddItem: (itemId: number) => void;
}

const MenuList: React.FC<MenuListProps> = ({ items, onAddItem }) => {
  return (
    <Paper elevation={2}>
      <List>
        {items.map((item) => (
          <ListItem key={item.id}>
            <ListItemText
              primary={item.name}
              secondary={`$${item.price.toFixed(2)}`}
            />
            <ListItemSecondaryAction>
              <IconButton 
                edge="end" 
                onClick={() => onAddItem(item.id)}
                disabled={!item.stock}
              >
                <AddIcon />
              </IconButton>
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default MenuList; 