// frontend/src/components/TradeForm.js
import React, { useState } from 'react';
import { useAppContext } from '../context/AppContext';
import { executeTrade } from '../services/apiService';

const TradeForm = () => {
  const { state, actions } = useAppContext();
  const { marketData } = state;
  
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    order_type: 'buy',
    order_subtype: 'market',
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
    if (name === 'order_subtype' && value === 'market') {
      setFormData(prev => ({ ...prev, price: '' }));
    }
    
    // Clear messages when user types
    if (success) setSuccess('');
    if (error) setError('');
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      // Validate form
      if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
        throw new Error('Please enter a valid quantity greater than 0');
      }
      
      if (formData.order_subtype === 'limit' && (!formData.price || parseFloat(formData.price) <= 0)) {
        throw new Error('Please enter a valid price for limit orders');
      }
      
      // ✅ FIXED: Use camelCase field names that backend expects
      const tradeData = {
        symbol: formData.symbol,
        orderType: formData.order_type,      // ✅ CHANGED: order_type → orderType
        orderSubtype: formData.order_subtype, // ✅ CHANGED: order_subtype → orderSubtype
        quantity: parseFloat(formData.quantity),
      };
      
      // Add price for limit orders, or current market price for market orders
      if (formData.order_subtype === 'limit') {
        tradeData.price = parseFloat(formData.price);
      } else {
        // For market orders, include current market price
        const currentPrice = getCurrentPrice();
        if (currentPrice > 0) {
          tradeData.price = currentPrice;
        }
      }
      
      console.log('🚀 Submitting complete trade data:', tradeData);
      
      // Execute trade
      const result = await executeTrade(tradeData);
      
      console.log('✅ Trade result:', result);
      
      // Create trade object for history
      const newTrade = {
        id: result.order_id || `trade-${Date.now()}`,
        order_type: result.order_type || tradeData.orderType, // ✅ ADDED: fallback to sent data
        symbol: result.symbol,
        quantity: result.quantity,
        price: result.price,
        total_value: result.total_value,
        fee: result.fee || 0,
        status: result.status || 'simulated',
        created_at: new Date().toISOString(),
        pair: { symbol: result.symbol }
      };
      
      // Add to trade history using actions
      actions.addTrade(newTrade);
      
      // Update voice response
      const coinName = formData.symbol.replace('USDT', '');
      const successMessage = `${tradeData.orderType.toUpperCase()} order placed successfully! ${formData.quantity} ${coinName} at $${result.price?.toLocaleString()} = $${result.total_value?.toLocaleString()}`;
      
      actions.setResponse(successMessage);
      setSuccess(successMessage);
      
      // Reset form
      setFormData({
        symbol: 'BTCUSDT',
        order_type: 'buy',
        order_subtype: 'market',
        quantity: '',
        price: '',
      });
      
    } catch (err) {
      console.error('❌ Trade execution failed:', err);
      
      // Enhanced error handling for debugging
      let errorMessage = 'Failed to place order';
      
      if (err.response?.data) {
        console.log('🔍 Full error response:', err.response.data);
        
        // Handle different error response formats
        if (typeof err.response.data === 'string') {
          errorMessage = err.response.data;
        } else if (err.response.data.detail) {
          // Handle FastAPI validation errors
          if (Array.isArray(err.response.data.detail)) {
            const fieldErrors = err.response.data.detail.map(e => {
              if (e.loc && e.msg) {
                return `${e.loc.join('.')}: ${e.msg}`;
              }
              return e.msg || e;
            });
            errorMessage = `Validation errors: ${fieldErrors.join(', ')}`;
          } else {
            errorMessage = err.response.data.detail;
          }
        } else if (err.response.data.message) {
          errorMessage = err.response.data.message;
        }
      } else if (err.message) {
        errorMessage = err.message;
      }
      
      setError(errorMessage);
      actions.setResponse(`Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };
  
  // Helper functions
  const getCurrentPrice = () => {
    const data = marketData[formData.symbol];
    return data?.price || 0;
  };

  const estimateTotal = () => {
    if (!formData.quantity) return '0.00';
    const price = formData.order_subtype === 'limit' && formData.price 
      ? parseFloat(formData.price)
      : getCurrentPrice();
    const total = price * parseFloat(formData.quantity || 0);
    return total.toFixed(2);
  };
  
  return (
    <div className="card trade-form">
      <div className="card-header">
        <h4>Place Order</h4>
      </div>
      <div className="card-body">
        <form onSubmit={handleSubmit}>
          {/* Symbol Selection */}
          <div className="mb-3">
            <label htmlFor="symbol" className="form-label">Symbol</label>
            <select 
              id="symbol"
              name="symbol"
              className="form-select"
              value={formData.symbol}
              onChange={handleInputChange}
              disabled={loading}
              required
            >
              <option value="BTCUSDT">Bitcoin (BTC)</option>
              <option value="ETHUSDT">Ethereum (ETH)</option>
              <option value="DOGEUSDT">Dogecoin (DOGE)</option>
            </select>
            {getCurrentPrice() > 0 && (
              <small className="text-muted">
                Current price: ${getCurrentPrice().toLocaleString()}
              </small>
            )}
          </div>
          
          {/* Order Type */}
          <div className="mb-3">
            <label className="form-label">Order Type</label>
            <div className="d-flex">
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="order_type"
                  id="orderTypeBuy"
                  value="buy"
                  checked={formData.order_type === 'buy'}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                <label className="form-check-label" htmlFor="orderTypeBuy">
                  Buy
                </label>
              </div>
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="order_type"
                  id="orderTypeSell"
                  value="sell"
                  checked={formData.order_type === 'sell'}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                <label className="form-check-label" htmlFor="orderTypeSell">
                  Sell
                </label>
              </div>
            </div>
          </div>
          
          {/* Order Subtype */}
          <div className="mb-3">
            <label className="form-label">Order Subtype</label>
            <div className="d-flex">
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="order_subtype"
                  id="orderSubtypeMarket"
                  value="market"
                  checked={formData.order_subtype === 'market'}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                <label className="form-check-label" htmlFor="orderSubtypeMarket">
                  Market
                </label>
              </div>
              <div className="form-check form-check-inline flex-grow-1">
                <input
                  className="form-check-input"
                  type="radio"
                  name="order_subtype"
                  id="orderSubtypeLimit"
                  value="limit"
                  checked={formData.order_subtype === 'limit'}
                  onChange={handleInputChange}
                  disabled={loading}
                />
                <label className="form-check-label" htmlFor="orderSubtypeLimit">
                  Limit
                </label>
              </div>
            </div>
          </div>
          
          {/* Quantity */}
          <div className="mb-3">
            <label htmlFor="quantity" className="form-label">Quantity</label>
            <input
              type="number"
              className="form-control"
              id="quantity"
              name="quantity"
              value={formData.quantity}
              onChange={handleInputChange}
              step="0.000001"
              min="0.000001"
              placeholder="0.001"
              disabled={loading}
              required
            />
            {formData.quantity && (
              <small className="text-muted">
                Estimated total: ~${estimateTotal()}
              </small>
            )}
          </div>
          
          {/* Limit Price (only show for limit orders) */}
          {formData.order_subtype === 'limit' && (
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
                placeholder={getCurrentPrice().toFixed(2)}
                disabled={loading}
                required
              />
              <small className="text-muted">
                Market price: ${getCurrentPrice().toLocaleString()}
              </small>
            </div>
          )}
          
          {/* Error and Success Messages */}
          {error && (
            <div className="alert alert-danger">
              <i className="fas fa-exclamation-triangle me-2"></i>
              {String(error)}
            </div>
          )}
          
          {success && (
            <div className="alert alert-success">
              <i className="fas fa-check-circle me-2"></i>
              {String(success)}
            </div>
          )}
          
          {/* Submit Button */}
          <button 
            type="submit" 
            className={`btn w-100 ${formData.order_type === 'buy' ? 'btn-success' : 'btn-danger'}`}
            disabled={loading || !formData.quantity || parseFloat(formData.quantity) <= 0}
          >
            {loading ? (
              <>
                <div className="spinner-border spinner-border-sm me-2" role="status"></div>
                Processing...
              </>
            ) : (
              `Place ${formData.order_type.toUpperCase()} Order`
            )}
          </button>
          
          {/* Quick Amount Buttons */}
          <div className="mt-2 d-flex gap-1">
            <button 
              type="button" 
              className="btn btn-sm btn-outline-secondary"
              onClick={() => setFormData(prev => ({ ...prev, quantity: '0.001' }))}
              disabled={loading}
            >
              0.001
            </button>
            <button 
              type="button" 
              className="btn btn-sm btn-outline-secondary"
              onClick={() => setFormData(prev => ({ ...prev, quantity: '0.01' }))}
              disabled={loading}
            >
              0.01
            </button>
            <button 
              type="button" 
              className="btn btn-sm btn-outline-secondary"
              onClick={() => setFormData(prev => ({ ...prev, quantity: '0.1' }))}
              disabled={loading}
            >
              0.1
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default TradeForm;