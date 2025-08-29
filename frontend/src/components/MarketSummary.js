import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';

const MarketSummary = () => {
  const { marketData, loading } = useContext(AppContext);

  // Format percentage with color based on value
  const formatChange = (change) => {
    const isPositive = change >= 0;
    const color = isPositive ? 'text-success' : 'text-danger';
    const sign = isPositive ? '+' : '';
    return <span className={color}>{sign}{change}%</span>;
  };

  return (
    <div className="card market-summary">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h4>Market Summary</h4>
        {loading && <div className="spinner-border spinner-border-sm text-primary" role="status"></div>}
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
              {marketData && Object.entries(marketData).length > 0 ? (
                Object.entries(marketData).map(([symbol, data]) => (
                  <tr key={symbol}>
                    <td>{symbol.replace('USDT', '')}</td>
                    <td>${data?.price?.toLocaleString() || 'N/A'}</td>
                    <td>{data?.change_24h !== undefined ? formatChange(data.change_24h) : 'N/A'}</td>
                    <td>{data?.volume ? `$${(data.volume / 1000000).toFixed(2)}M` : 'N/A'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="4" className="text-center">
                    {loading ? 'Loading market data...' : 'No market data available'}
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