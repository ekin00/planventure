import { AppBar, Toolbar, Typography, Button, Stack } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';

const Navbar = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, logout } = useAuth();

  const handleSwitchUser = () => {
    logout();
    navigate('/welcome');
  };

  return (
    <AppBar position="fixed">
      <Toolbar>
        <Typography 
          variant="h6" 
          component="div" 
          sx={{ flexGrow: 1, cursor: 'pointer', textAlign: 'left' }}
          onClick={() => navigate('/')}
        >
          Planventure
        </Typography>
        <Stack direction="row" spacing={2} alignItems="center">
          {isAuthenticated ? (
            <>
              <Typography variant="body1">
                Welcome, {user?.name}
              </Typography>
              <Button 
                color="inherit" 
                onClick={() => navigate('/trips')}
              >
                My Trips
              </Button>
              <Button 
                color="inherit" 
                variant="outlined" 
                onClick={handleSwitchUser}
                sx={{ borderColor: 'inherit' }}
              >
                Switch User
              </Button>
            </>
          ) : (
            <Button 
              color="inherit" 
              onClick={() => navigate('/welcome')}
            >
              Get Started
            </Button>
          )}
        </Stack>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;