// frontend/src/components/MarketSummary.js
import React from 'react';
import { useAppContext } from '../context/AppContext';

const MarketSummary = () => {
  const { state, actions } = useAppContext();
  const { marketData, loading } = state;

  // Format percentage with color based on value
  const formatChange = (change) => {
    const isPositive = change >= 0;
    const color = isPositive ? 'text-success' : 'text-danger';
    const sign = isPositive ? '+' : '';
    return <span className={color}>{sign}{change?.toFixed(2)}%</span>;
  };

  const formatPrice = (price) => {
    if (!price) return 'N/A';
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: price < 1 ? 6 : 2
    }).format(price);
  };

  const formatVolume = (volume) => {
    if (!volume) return 'N/A';
    if (volume >= 1e9) return `$${(volume / 1e9).toFixed(1)}B`;
    if (volume >= 1e6) return `$${(volume / 1e6).toFixed(1)}M`;
    if (volume >= 1e3) return `$${(volume / 1e3).toFixed(1)}K`;
    return `$${volume.toFixed(0)}`;
  };

  const getCoinName = (symbol) => {
    const coinNames = {
      'BTCUSDT': 'Bitcoin (BTC)',
      'ETHUSDT': 'Ethereum (ETH)', 
      'DOGEUSDT': 'Dogecoin (DOGE)'
    };
    return coinNames[symbol] || symbol.replace('USDT', '');
  };

  const refreshMarketData = async () => {
    try {
      const symbols = ['BTCUSDT', 'ETHUSDT', 'DOGEUSDT'];
      const { getMarketData } = await import('../services/apiService');
      
      const newData = {};
      for (const symbol of symbols) {
        try {
          const data = await getMarketData(symbol);
          newData[symbol] = data;
        } catch (error) {
          console.error(`Failed to fetch ${symbol}:`, error);
          // Fallback to simulated data
          const basePrice = symbol === 'BTCUSDT' ? 58000 : symbol === 'ETHUSDT' ? 3200 : 0.12;
          newData[symbol] = {
            symbol,
            price: basePrice + (Math.random() - 0.5) * basePrice * 0.1,
            change_24h: (Math.random() - 0.5) * 10,
            volume: Math.random() * 1000000000,
            timestamp: Date.now()
          };
        }
      }
      
      actions.updateMarketData(newData);
    } catch (error) {
      console.error('Failed to refresh market data:', error);
    }
  };

  return (
    <div className="card market-summary">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h4>Market Summary</h4>
        <button 
          className="btn btn-sm btn-outline-primary" 
          onClick={refreshMarketData}
          disabled={loading}
        >
          {loading ? (
            <>
              <div className="spinner-border spinner-border-sm me-1" role="status"></div>
              Loading...
            </>
          ) : (
            <>
              <i className="fas fa-sync-alt me-1"></i>
              Refresh
            </>
          )}
        </button>
      </div>
      <div className="card-body">
        <div className="table-responsive">
          <table className="table table-striped">
            <thead>
              <tr>
                <th>Asset</th>
                <th>Price</th>
                <th>Change (24h)</th>
                <th>Volume</th>
              </tr>
            </thead>
            <tbody>
              {marketData && Object.keys(marketData).length > 0 ? (
                Object.entries(marketData).map(([symbol, data]) => (
                  <tr key={symbol}>
                    <td>
                      <strong>{getCoinName(symbol)}</strong>
                    </td>
                    <td className="fw-bold">
                      {formatPrice(data?.price)}
                    </td>
                    <td>
                      {data?.change_24h !== undefined ? formatChange(data.change_24h) : 'N/A'}
                    </td>
                    <td className="text-muted small">
                      {formatVolume(data?.volume)}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center text-muted">
                    {loading ? (
                      <>
                        <div className="spinner-border spinner-border-sm me-2" role="status"></div>
                        Loading market data...
                      </>
                    ) : (
                      <>
                        No market data available
                        <br />
                        <button 
                          className="btn btn-sm btn-primary mt-2" 
                          onClick={refreshMarketData}
                        >
                          Load Market Data
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      <div className="card-footer text-muted">
        Last updated: {new Date().toLocaleTimeString()}
      </div>
    </div>
  );
};

export default MarketSummary;