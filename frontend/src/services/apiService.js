// frontend/src/services/apiService.js
import axios from "axios";

const API_BASE = "http://localhost:8000"; // ⚡ adjust if backend runs elsewhere

// =============================
// 📊 Technical Analysis Services
// =============================
export const getTechnicalIndicators = async (symbol, timeframe) => {
  const res = await axios.get(
    `${API_BASE}/api/technical/indicators/${symbol}?timeframe=${timeframe}`
  );
  return res.data;
};

export const getPatternDetection = async (symbol, timeframe) => {
  const res = await axios.get(
    `${API_BASE}/api/technical/patterns/${symbol}?timeframe=${timeframe}`
  );
  return res.data;
};

export const getTechnicalAnalysis = async (symbol, timeframe) => {
  const res = await axios.get(
    `${API_BASE}/api/technical/analysis/${symbol}?timeframe=${timeframe}`
  );
  return res.data;
};

// =============================
// 🤖 LLM-Powered Insights
// =============================
export const getLLMAnalysis = async (symbol, timeframe) => {
  const res = await axios.get(
    `${API_BASE}/api/llm/analysis/${symbol}?timeframe=${timeframe}`
  );
  return res.data;
};


// =============================
// 💹 Trading APIs
// =============================
export const executeTrade = async (tradeData) => {
  const res = await axios.post(`${API_BASE}/api/trades/execute`, tradeData);
  return res.data;
};

export const getUserTrades = async () => {
  const res = await axios.get(`${API_BASE}/api/trades/history`);
  return res.data;
};

// =============================
// 🗣️ Voice Assistant
// =============================
export const processVoiceCommand = async (command) => {
  const res = await axios.post(`${API_BASE}/api/voice/process`, { command });
  return res.data;
};

// =============================
// 📈 Market Data
// =============================
export const getMarketData = async (symbol) => {
  const res = await axios.get(`${API_BASE}/api/market/${symbol}`);
  return res.data;
};
