import axios from "axios";

const api = axios.create({
  baseURL: "http://localhost:8000", // adjust if backend runs elsewhere
});

// 🔹 Run analysis + AI insight
export const analyzeSymbol = async (symbol, timeframe = "1h") => {
  try {
    const response = await api.post(`/analysis/${symbol}?timeframe=${timeframe}`);
    return response.data.result;
  } catch (error) {
    console.error("Error analyzing symbol:", error);
    throw error;
  }
};

// 🔹 Execute trade
export const executeTrade = async (tradeData) => {
  try {
    const response = await api.post("/trades/execute", tradeData);
    return response.data;
  } catch (error) {
    console.error("Error executing trade:", error);
    throw error;
  }
};

// 🔹 Fetch user trade history
export const getUserTrades = async (userId) => {
  try {
    const response = await api.get(`/trades/${userId}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching user trades:", error);
    throw error;
  }
};

// 🔹 Process voice command
export const processVoiceCommand = async (command) => {
  try {
    const response = await api.post("/voice/command", { command });
    return response.data;
  } catch (error) {
    console.error("Error processing voice command:", error);
    throw error;
  }
};

// 🔹 Fetch live market data
export const getMarketData = async (symbol) => {
  try {
    const response = await api.get(`/market/${symbol}`);
    return response.data;
  } catch (error) {
    console.error("Error fetching market data:", error);
    throw error;
  }
};

export default api;
