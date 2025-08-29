// frontend/src/services/authService.js
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('tradebot_token');
    if (token && token !== 'demo_token') {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tradebot_token');
      window.location.reload();
    }
    return Promise.reject(error);
  }
);

export const login = async (username, password) => {
  try {
    // Use form data for login as per FastAPI OAuth2 standard
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await api.post('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    
    const { access_token, user } = response.data;
    
    const userData = {
      id: user.id,
      username: user.username,
      email: user.email,
      name: user.username,
      balance: user.balance
    };

    // Store token
    localStorage.setItem('tradebot_token', access_token);
    
    return {
      success: true,
      token: access_token,
      user: userData
    };
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Login failed'
    };
  }
};

export const register = async (username, email, password) => {
  try {
    const response = await api.post('/auth/register', {
      username,
      email,
      password
    });
    
    return {
      success: true,
      message: 'Registration successful! Please sign in.',
      user: response.data
    };
  } catch (error) {
    console.error('Register error:', error);
    return {
      success: false,
      error: error.response?.data?.detail || error.message || 'Registration failed'
    };
  }
};

export const getCurrentUser = async () => {
  try {
    const token = localStorage.getItem('tradebot_token');
    if (!token || token === 'demo_token') {
      throw new Error('No valid token');
    }

    const response = await api.get('/auth/me');
    return response.data;
  } catch (error) {
    console.error('Get current user error:', error);
    throw error;
  }
};

export const logout = () => {
  localStorage.removeItem('tradebot_token');
  localStorage.removeItem('demoUser');
  window.location.reload();
};

export const isAuthenticated = () => {
  return !!localStorage.getItem('tradebot_token') || !!localStorage.getItem('demoUser');
};

export const getAuthHeaders = () => {
  const token = localStorage.getItem('tradebot_token');
  if (token && token !== 'demo_token') {
    return { 'Authorization': `Bearer ${token}` };
  }
  return {};
};

// Demo user login
export const loginDemo = () => {
  const demoUser = {
    id: 1,
    name: 'Demo User',
    username: 'demo_user',
    email: 'demo@tradebot.com',
    balance: 10000,
  };
  
  localStorage.setItem('demoUser', JSON.stringify(demoUser));
  return {
    success: true,
    user: demoUser,
    token: 'demo_token'
  };
};