import React, { createContext, useState, useEffect } from 'react';
import { getMarketData } from '../services/apiService';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  // Initialize user from localStorage (only on first render)
  const [user, setUser] = useState(() => {
    const storedUser = localStorage.getItem('demoUser');
    return storedUser ? JSON.parse(storedUser) : null;
  });

  const [marketData, setMarketData] = useState({});
  const [isListening, setIsListening] = useState(false);
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trades, setTrades] = useState([]);

  // Keep user state in sync with localStorage
  useEffect(() => {
    const storedUser = localStorage.getItem('demoUser');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Fetch initial market data and update every 30 seconds
  useEffect(() => {
    const fetchMarketData = async () => {
      try {
        setLoading(true);
        const symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT'];
        const data = {};

        for (const symbol of symbols) {
          const response = await getMarketData(symbol);
          data[symbol] = response;
        }

        setMarketData(data);
        setLoading(false);
      } catch (err) {
        setError('Failed to fetch market data');
        setLoading(false);
        console.error(err);
      }
    };

    fetchMarketData();

    const interval = setInterval(fetchMarketData, 30000);
    return () => clearInterval(interval);
  }, []);

  // Add a trade to the history
  const addTrade = (trade) => {
    setTrades((prevTrades) => [trade, ...prevTrades]);
  };

  return (
    <AppContext.Provider value={{
      user,
      setUser,
      marketData,
      setMarketData,
      isListening,
      setIsListening,
      command,
      setCommand,
      response,
      setResponse,
      loading,
      setLoading,
      error,
      setError,
      trades,
      addTrade
    }}>
      {children}
      </AppContext.Provider>
  );
};