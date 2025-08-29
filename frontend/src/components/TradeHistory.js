// frontend/src/components/TradeHistory.js
import React, { useEffect, useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { getUserTrades } from '../services/apiService';

const TradeHistory = () => {
  const { state, actions } = useAppContext();
  const { trades, user } = state;
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Only fetch if user is authenticated and not in demo mode
    if (user && !localStorage.getItem('demoUser')) {
      fetchTrades();
    }
  }, [user]);

  const fetchTrades = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedTrades = await getUserTrades(50, 0);
      actions.setTrades(fetchedTrades);
    } catch (err) {
      console.error('Error fetching trades:', err);
      setError('Failed to load trade history');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  const formatCurrency = (amount) => {
    return `$${parseFloat(amount).toFixed(2)}`;
  };

  const getStatusBadge = (status) => {
    const statusClasses = {
      simulated: 'bg-info',
      filled: 'bg-success',
      pending: 'bg-warning',
      cancelled: 'bg-danger'
    };

    return `badge ${statusClasses[status] || 'bg-secondary'}`;
  };

  if (loading) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p>Loading trade history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h5 className="mb-0">📈 Trade History</h5>
        <button 
          className="btn btn-outline-primary btn-sm"
          onClick={fetchTrades}
          disabled={loading}
        >
          <i className="fas fa-sync-alt me-1"></i>
          Refresh
        </button>
      </div>
      
      <div className="card-body">
        {error && (
          <div className="alert alert-danger">
            {error}
          </div>
        )}

        {trades.length === 0 ? (
          <div className="text-center text-muted">
            <i className="fas fa-chart-line fa-3x mb-3"></i>
            <p>No trades yet.</p>
            <p>Use voice commands or manual trading to get started!</p>
          </div>
        ) : (
          <div className="table-responsive">
            <table className="table table-hover">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Symbol</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Total</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade, index) => (
                  <tr key={trade.id || index}>
                    <td className="small">
                      {formatDate(trade.created_at)}
                    </td>
                    <td>
                      <span className={`badge ${
                        trade.order_type === 'buy' ? 'bg-success' : 'bg-danger'
                      }`}>
                        {trade.order_type?.toUpperCase()}
                      </span>
                    </td>
                    <td>
                      <strong>{trade.symbol || trade.pair?.symbol}</strong>
                    </td>
                    <td>{parseFloat(trade.quantity).toFixed(6)}</td>
                    <td>{formatCurrency(trade.price)}</td>
                    <td>{formatCurrency(trade.total_value)}</td>
                    <td>
                      <span className={getStatusBadge(trade.status)}>
                        {trade.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default TradeHistory;