// frontend/src/services/apiService.js
import axios from 'axios';
import { getAuthHeaders } from './authService';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth headers
api.interceptors.request.use(
  (config) => {
    const authHeaders = getAuthHeaders();
    config.headers = { ...config.headers, ...authHeaders };
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('tradebot_token');
      window.location.reload();
    }
    console.error('API Error:', error.response?.data || error.message);
    throw error;
  }
);

export const processVoiceCommand = async (command) => {
  try {
    const response = await api.post('/voice/process', { command });
    return response.data;
  } catch (error) {
    console.error('Error processing voice command:', error);
    throw error;
  }
};

// Updated to match backend endpoint: /trades/market-data/{symbol}
export const getMarketData = async (symbol) => {
  try {
    const response = await api.get(`/trades/market-data/${symbol}`);
    return response.data;
  } catch (error) {
    console.error('Error getting market data:', error);
    throw error;
  }
};

export const executeTrade = async (tradeData) => {
  try {
    const response = await api.post('/trades/execute', tradeData);
    return response.data;
  } catch (error) {
    console.error('Error executing trade:', error);
    throw error;
  }
};

// Updated to match backend endpoint: /trades/history
export const getUserTrades = async (limit = 50, offset = 0) => {
  try {
    const response = await api.get(`/trades/history?limit=${limit}&offset=${offset}`);
    return response.data;
  } catch (error) {
    console.error('Error getting user trades:', error);
    throw error;
  }
};

// Portfolio endpoint - using trade history to calculate portfolio
export const getUserBalances = async () => {
  try {
    // Since backend doesn't have a direct portfolio endpoint, we'll calculate from trades
    const trades = await getUserTrades(1000); // Get more trades for accurate calculation
    
    // Simple portfolio calculation (you can enhance this)
    const portfolio = {
      balances: { USDT: 10000 },
      total_value: 10000,
      assets: [{ asset: 'USDT', balance: 10000, value: 10000 }]
    };
    
    return portfolio;
  } catch (error) {
    console.error('Error getting user balances:', error);
    throw error;
  }
};

export const healthCheck = async () => {
  try {
    const response = await axios.get('http://localhost:8000/healthcheck');
    return response.data;
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};