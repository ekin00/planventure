const BASE_URL = 'http://localhost:5000';

const getAuthHeaders = () => {
  const stored = localStorage.getItem('user');
  let userId = '';
  if (stored) {
    try {
      userId = JSON.parse(stored).id ?? '';
    } catch {
      localStorage.removeItem('user');
    }
  }
  return {
    'Content-Type': 'application/json',
    'X-User-Id': userId,
  };
};

const handleResponse = async (response) => {
  if (response.status === 401) {
    localStorage.removeItem('user');
    window.location.href = '/welcome';
    throw new Error('Unknown user. Please join again.');
  }

  if (response.status === 404) {
    throw new Error('Trip not found');
  }

  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || data.message || 'Request failed');
  }

  console.log('API Response:', data); // Debug log
  return data;
};

export const api = {
  get: async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
  
  post: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  put: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PUT',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  patch: async (endpoint, data) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  delete: async (endpoint) => {
    const response = await fetch(`${BASE_URL}${endpoint}`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  auth: {
    join: async (data) => {
      return api.post('/auth/join', data);
    }
  }
};

export default api;