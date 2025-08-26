import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const processVoiceCommand = async (command) => {
  try {
    const response = await api.post('/voice/process', { command });
    return response.data;
  } catch (error) {
    console.error('Error processing voice command:', error);
    throw error;
  }
};

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

export const getUserTrades = async (userId) => {
  try {
    const response = await api.get(`/trades/history/${userId}`);
    return response.data;
  } catch (error) {
    console.error('Error getting user trades:', error);
    throw error;
  }
};

export const getUserBalances = async (userId) => {
  try {
    const response = await api.get(`/users/${userId}/balances`);
    return response.data;
  } catch (error) {
    console.error('Error getting user balances:', error);
    throw error;
  }
};