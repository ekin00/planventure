import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Box,
  TextField,
  Button,
  Typography,
  Alert
} from '@mui/material';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';

const RESERVED_NAME_PATTERN = /^guest\d*$/i;
const RESERVED_NAME_MESSAGE =
  "😄 'GUEST' names are saved for our walk-in adventurers — pick another name!";

const WelcomeForm = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [name, setName] = useState('');
  const [warning, setWarning] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleChange = (e) => {
    setName(e.target.value);
    // Clear messages as soon as the user edits the field
    setWarning('');
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    const trimmedName = name.trim();

    // Client-side pre-check to save a round trip; the server enforces it too.
    if (trimmedName && RESERVED_NAME_PATTERN.test(trimmedName)) {
      setWarning(RESERVED_NAME_MESSAGE);
      return;
    }

    setIsLoading(true);
    setWarning('');
    setError('');

    try {
      const response = await api.auth.join(
        trimmedName ? { name: trimmedName } : {}
      );
      login(response);
      navigate('/dashboard', { replace: true });
    } catch (err) {
      console.error('Join error:', err);
      if ((err.message || '').toLowerCase().includes('reserved')) {
        setWarning(RESERVED_NAME_MESSAGE);
      } else {
        setError(err.message || 'Something went wrong. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Box
      component="form"
      onSubmit={handleSubmit}
      sx={{
        width: '100%',
        display: 'flex',
        flexDirection: 'column',
        gap: 2
      }}
    >
      <Typography variant="h5" component="h1" gutterBottom textAlign="center">
        Welcome to Planventure
      </Typography>

      <Typography variant="body2" textAlign="center" color="text.secondary">
        Enter your name to find your trips, or leave it blank and we&apos;ll
        set you up as a guest.
      </Typography>

      {warning && (
        <Alert severity="warning" sx={{ mb: 2 }}>
          {warning}
        </Alert>
      )}

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <TextField
        fullWidth
        label="Your name"
        name="name"
        value={name}
        onChange={handleChange}
        disabled={isLoading}
        inputProps={{ maxLength: 50 }}
        autoFocus
      />

      <Button
        type="submit"
        variant="contained"
        color="primary"
        size="large"
        disabled={isLoading}
        sx={{ mt: 2 }}
      >
        {isLoading ? 'Joining...' : 'Start Planning'}
      </Button>
    </Box>
  );
};

export default WelcomeForm;
