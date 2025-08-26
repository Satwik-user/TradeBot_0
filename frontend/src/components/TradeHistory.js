import React from 'react';

const TradeHistory = ({ trades }) => {
  return (
    <div className="card trade-history">
      <div className="card-header">
        <h4>Trade History</h4>
      </div>
      <div className="card-body">
        {trades.length > 0 ? (
          <div className="table-responsive">
            <table className="table table-sm">
              <thead>
                <tr>
                  <th>Asset</th>
                  <th>Type</th>
                  <th>Qty</th>
                  <th>Price</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade, index) => (
                  <tr key={index}>
                    <td>{trade.symbol.replace('USDT', '')}</td>
                    <td className={trade.order_type === 'buy' ? 'text-success' : 'text-danger'}>
                      {trade.order_type.toUpperCase()}
                    </td>
                    <td>{trade.quantity}</td>
                    <td>${trade.price}</td>
                    <td>
                      <span className="badge bg-secondary">{trade.status}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-muted text-center">No trades yet</p>
        )}
      </div>
    </div>
  );
};

export default TradeHistory;