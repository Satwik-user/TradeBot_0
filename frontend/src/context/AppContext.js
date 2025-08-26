import React, { createContext, useState, useEffect } from 'react';
import { getMarketData } from '../services/apiService';

export const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [marketData, setMarketData] = useState({});
  const [isListening, setIsListening] = useState(false);
  const [command, setCommand] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [trades, setTrades] = useState([]);

  // Load user from localStorage on initial render
  useEffect(() => {
    const storedUser = localStorage.getItem('demoUser');
    if (storedUser) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  // Fetch initial market data
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

    // Update market data every 30 seconds
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