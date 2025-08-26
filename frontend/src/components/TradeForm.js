import React, { useState, useContext } from 'react';
import { AppContext } from '../context/AppContext';
import { executeTrade } from '../services/apiService';

const TradeForm = () => {
  const { addTrade } = useContext(AppContext);
  
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    orderType: 'buy',
    orderSubtype: 'market',
    quantity: '',
    price: '',
  });
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    // Clear price if market order is selected
    if (name === 'orderSubtype' && value === 'market') {
      setFormData(prev => ({ ...prev, price: '' }));
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Validate form
      if (!formData.quantity) {
        throw new Error('Please enter a quantity');
      }
      
      if (formData.orderSubtype === 'limit' && !formData.price) {
        throw new Error('Please enter a price for limit orders');
      }
      
      // Execute trade
      const tradeData = {
        ...formData,
        quantity: parseFloat(formData.quantity),
        price: formData.price ? parseFloat(formData.price) : null,
      };
      
      const result = await executeTrade(tradeData);
      
      // Add to trade history
      addTrade(result);
      
      // Show success message
      setSuccess(`${formData.orderType.toUpperCase()} order placed successfully!`);
      
      // Reset form
      setFormData({
        symbol: 'BTCUSDT',
        orderType: 'buy',
        orderSubtype: 'market',
        quantity: '',
        price: '',
      });
    } catch (err) {
      setError(err.message || 'Failed to place order');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="card trade-form">
      <div className="card-header">
        <h4>Place Order</h4>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          <div className="mb-3">
            <label htmlFor="symbol" className="form-label">Symbol</label>
            <select 
              id="symbol"
              name="symbol"
              className="form-select"
              value={formData.symbol}
              onChange={handleInputChange}
              required
            >
              <option value="BTCUSDT">Bitcoin (BTC)</option>
              <option value="ETHUSDT">Ethereum (ETH)</option>
              <option value="DOGEUSDT">Dogecoin (DOGE)</option>
            </select>
          </div>
          
          <div className="mb-3">
            <label className="form-label">Order Type</label>
            <div className="d-flex">
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="orderType"
                  id="orderTypeBuy"
                  value="buy"
                  checked={formData.orderType === 'buy'}
                  onChange={handleInputChange}
                />
                <label className="form-check-label" htmlFor="orderTypeBuy">
                  Buy
                </label>
              </div>
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="orderType"
                  id="orderTypeSell"
                  value="sell"
                  checked={formData.orderType === 'sell'}
                  onChange={handleInputChange}
                />
                <label className="form-check-label" htmlFor="orderTypeSell">
                  Sell
                </label>
              </div>
            </div>
          </div>
          
          <div className="mb-3">
            <label className="form-label">Order Subtype</label>
            <div className="d-flex">
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="orderSubtype"
                  id="orderSubtypeMarket"
                  value="market"
                  checked={formData.orderSubtype === 'market'}
                  onChange={handleInputChange}
                />
                <label className="form-check-label" htmlFor="orderSubtypeMarket">
                  Market
                </label>
              </div>
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="orderSubtype"
                  id="orderSubtypeLimit"
                  value="limit"
                  checked={formData.orderSubtype === 'limit'}
                  onChange={handleInputChange}
                />
                <label className="form-check-label" htmlFor="orderSubtypeLimit">
                  Limit
                </label>
              </div>
            </div>
          </div>
          
          <div className="mb-3">
            <label htmlFor="quantity" className="form-label">Quantity</label>
            <input
              type="number"
              className="form-control"
              id="quantity"
              name="quantity"
              value={formData.quantity}
              onChange={handleInputChange}
              step="0.0001"
              min="0.0001"
              required
            />
          </div>
          
          {formData.orderSubtype === 'limit' && (
            <div className="mb-3">
              <label htmlFor="price" className="form-label">Limit Price ($)</label>
              <input
                type="number"
                className="form-control"
                id="price"
                name="price"
                value={formData.price}
                onChange={handleInputChange}
                step="0.01"
                min="0.01"
                required={formData.orderSubtype === 'limit'}
              />
            </div>
          )}
          
          {error && <div className="alert alert-danger">{error}</div>}
          {success && <div className="alert alert-success">{success}</div>}
          
          <button 
            type="submit" 
            className="btn btn-primary w-100" 
            disabled={loading}
          >
            {loading ? (
              <span>
                <span className="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                <span className="ms-2">Processing...</span>
              </span>
            ) : (
              `Place ${formData.orderType.toUpperCase()} Order`
            )}
          </button>
        </form>
      </div>
    </div>
  );
};

export default TradeForm;