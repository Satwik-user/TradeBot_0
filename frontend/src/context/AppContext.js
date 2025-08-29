// frontend/src/context/AppContext.js
import React, { createContext, useReducer, useEffect } from 'react';
import { getMarketData, getUserTrades, getUserBalances } from '../services/apiService';

export const AppContext = createContext();

// Initial state
const initialState = {
  // Authentication state
  user: null,
  isAuthenticated: false,
  token: localStorage.getItem('tradebot_token'),
  
  // App state
  marketData: {},
  isListening: false,
  command: '',
  response: '',
  loading: false,
  error: null,
  trades: [],
  
  // Portfolio state
  portfolio: { balances: {}, total_value: 0, assets: [] }
};

// Action types
const actionTypes = {
  // Auth actions
  LOGIN_SUCCESS: 'LOGIN_SUCCESS',
  LOGIN_FAILURE: 'LOGIN_FAILURE',
  LOGOUT: 'LOGOUT',
  SET_USER: 'SET_USER',
  
  // App actions
  SET_MARKET_DATA: 'SET_MARKET_DATA',
  UPDATE_MARKET_DATA: 'UPDATE_MARKET_DATA',
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_VOICE_STATE: 'SET_VOICE_STATE',
  SET_COMMAND: 'SET_COMMAND',
  SET_RESPONSE: 'SET_RESPONSE',
  ADD_TRADE: 'ADD_TRADE',
  SET_TRADES: 'SET_TRADES',
  SET_PORTFOLIO: 'SET_PORTFOLIO',
  CLEAR_ERROR: 'CLEAR_ERROR'
};

// Reducer function
const appReducer = (state, action) => {
  switch (action.type) {
    case actionTypes.LOGIN_SUCCESS:
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        error: null,
        loading: false
      };

    case actionTypes.LOGIN_FAILURE:
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        error: action.payload,
        loading: false
      };

    case actionTypes.LOGOUT:
      return {
        ...initialState,
        token: null,
        isAuthenticated: false,
        loading: false
      };

    case actionTypes.SET_USER:
      return {
        ...state,
        user: action.payload
      };

    case actionTypes.SET_MARKET_DATA:
      return {
        ...state,
        marketData: action.payload
      };

    case actionTypes.UPDATE_MARKET_DATA:
      return {
        ...state,
        marketData: { ...state.marketData, ...action.payload }
      };

    case actionTypes.SET_LOADING:
      return {
        ...state,
        loading: action.payload
      };

    case actionTypes.SET_ERROR:
      return {
        ...state,
        error: action.payload
      };

    case actionTypes.CLEAR_ERROR:
      return {
        ...state,
        error: null
      };

    case actionTypes.SET_VOICE_STATE:
      return {
        ...state,
        isListening: action.payload.isListening,
        command: action.payload.command !== undefined ? action.payload.command : state.command,
        response: action.payload.response !== undefined ? action.payload.response : state.response
      };

    case actionTypes.SET_COMMAND:
      return {
        ...state,
        command: action.payload
      };

    case actionTypes.SET_RESPONSE:
      return {
        ...state,
        response: action.payload
      };

    case actionTypes.ADD_TRADE:
      return {
        ...state,
        trades: [action.payload, ...state.trades]
      };

    case actionTypes.SET_TRADES:
      return {
        ...state,
        trades: action.payload
      };

    case actionTypes.SET_PORTFOLIO:
      return {
        ...state,
        portfolio: action.payload
      };

    default:
      return state;
  }
};

export const AppProvider = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Check authentication on app load
  useEffect(() => {
    const checkAuth = async () => {
      dispatch({ type: actionTypes.SET_LOADING, payload: true });
      
      const token = localStorage.getItem('tradebot_token');
      const demoUser = localStorage.getItem('demoUser');
      
      if (demoUser) {
        // Handle demo user
        const user = JSON.parse(demoUser);
        dispatch({
          type: actionTypes.LOGIN_SUCCESS,
          payload: { user, token: 'demo_token' }
        });
      } else if (token && token !== 'demo_token') {
        // Handle real user authentication
        try {
          const response = await fetch('http://localhost:8000/api/auth/me', {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json'
            }
          });
          
          if (response.ok) {
            const userData = await response.json();
            dispatch({
              type: actionTypes.LOGIN_SUCCESS,
              payload: { 
                user: {
                  id: userData.id,
                  username: userData.username,
                  email: userData.email,
                  name: userData.username,
                  balance: userData.balance
                }, 
                token 
              }
            });
          } else {
            localStorage.removeItem('tradebot_token');
            dispatch({ type: actionTypes.LOGOUT });
          }
        } catch (error) {
          console.error('Auth check failed:', error);
          localStorage.removeItem('tradebot_token');
          dispatch({ type: actionTypes.LOGOUT });
        }
      } else {
        dispatch({ type: actionTypes.SET_LOADING, payload: false });
      }
    };

    checkAuth();
  }, []);

  // Fetch market data when authenticated
  useEffect(() => {
    if (state.isAuthenticated) {
      const fetchMarketData = async () => {
        try {
          const symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT'];
          const data = {};

          for (const symbol of symbols) {
            try {
              const response = await getMarketData(symbol);
              data[symbol] = response;
            } catch (error) {
              console.error(`Failed to fetch ${symbol}:`, error);
            }
          }

          dispatch({ type: actionTypes.SET_MARKET_DATA, payload: data });
        } catch (err) {
          dispatch({ type: actionTypes.SET_ERROR, payload: 'Failed to fetch market data' });
          console.error(err);
        }
      };

      // Initial fetch
      fetchMarketData();
      
      // Set up interval for real-time updates
      const interval = setInterval(fetchMarketData, 30000);
      return () => clearInterval(interval);
    }
  }, [state.isAuthenticated]);

  // Fetch user trades when authenticated
  useEffect(() => {
    if (state.isAuthenticated && state.user && !localStorage.getItem('demoUser')) {
      const fetchTrades = async () => {
        try {
          const trades = await getUserTrades();
          dispatch({ type: actionTypes.SET_TRADES, payload: trades });
        } catch (error) {
          console.error('Failed to fetch trades:', error);
        }
      };
      
      fetchTrades();
    }
  }, [state.isAuthenticated, state.user]);

  // Action creators
  const actions = {
    login: (user, token) => {
      localStorage.setItem('tradebot_token', token);
      dispatch({ type: actionTypes.LOGIN_SUCCESS, payload: { user, token } });
    },

    loginDemo: (user) => {
      localStorage.setItem('demoUser', JSON.stringify(user));
      dispatch({ type: actionTypes.LOGIN_SUCCESS, payload: { user, token: 'demo_token' } });
    },

    logout: () => {
      localStorage.removeItem('tradebot_token');
      localStorage.removeItem('demoUser');
      dispatch({ type: actionTypes.LOGOUT });
    },

    addTrade: (trade) => {
      dispatch({ type: actionTypes.ADD_TRADE, payload: trade });
    },

    setTrades: (trades) => {
      dispatch({ type: actionTypes.SET_TRADES, payload: trades });
    },

    setVoiceState: (voiceState) => {
      dispatch({ type: actionTypes.SET_VOICE_STATE, payload: voiceState });
    },

    setCommand: (command) => {
      dispatch({ type: actionTypes.SET_COMMAND, payload: command });
    },

    setResponse: (response) => {
      dispatch({ type: actionTypes.SET_RESPONSE, payload: response });
    },

    updateMarketData: (data) => {
      dispatch({ type: actionTypes.UPDATE_MARKET_DATA, payload: data });
    },

    setPortfolio: (portfolio) => {
      dispatch({ type: actionTypes.SET_PORTFOLIO, payload: portfolio });
    },

    setError: (error) => {
      dispatch({ type: actionTypes.SET_ERROR, payload: error });
    },

    clearError: () => {
      dispatch({ type: actionTypes.CLEAR_ERROR });
    },

    setLoading: (loading) => {
      dispatch({ type: actionTypes.SET_LOADING, payload: loading });
    }
  };

  return (
    <AppContext.Provider value={{ state, actions, dispatch, actionTypes }}>
      {children}
    </AppContext.Provider>
  );
};

// Custom hook to use the context
export const useAppContext = () => {
  const context = React.useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

export { actionTypes };