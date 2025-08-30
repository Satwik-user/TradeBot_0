// frontend/src/components/IndicatorPanel.js
import React from 'react';

const IndicatorPanel = ({ indicators, loading }) => {
  if (loading) {
    return (
      <div className="card mb-3">
        <div className="card-body text-center">
          <div className="spinner-border text-primary mb-2" role="status"></div>
          <div>Loading indicators...</div>
        </div>
      </div>
    );
  }
  
  if (!indicators) {
    return (
      <div className="card mb-3">
        <div className="card-body text-center text-muted">
          <i className="fas fa-chart-line fa-2x mb-2"></i>
          <div>No indicator data available</div>
        </div>
      </div>
    );
  }
  
  const getIndicatorColor = (value, type) => {
    switch (type) {
      case 'rsi':
        if (value < 30) return 'text-success'; // Oversold - potential buy
        if (value > 70) return 'text-danger';  // Overbought - potential sell
        return 'text-warning'; // Neutral
      case 'macd':
        return value > 0 ? 'text-success' : 'text-danger';
      default:
        return 'text-info';
    }
  };
  
  const formatValue = (value, decimals = 2) => {
    if (value === null || value === undefined) return 'N/A';
    return typeof value === 'number' ? value.toFixed(decimals) : value;
  };
  
  const getRSIStatus = (rsi) => {
    if (rsi < 30) return { text: 'Oversold', class: 'badge-success' };
    if (rsi > 70) return { text: 'Overbought', class: 'badge-danger' };
    return { text: 'Neutral', class: 'badge-secondary' };
  };
  
  const getMACDStatus = (macd, signal) => {
    if (macd > signal) return { text: 'Bullish', class: 'badge-success' };
    return { text: 'Bearish', class: 'badge-danger' };
  };
  
  return (
    <div className="card mb-3">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h6 className="mb-0">
          <i className="fas fa-chart-line me-2"></i>
          Technical Indicators
        </h6>
        <small className="text-muted">
          {indicators.timestamp && new Date(indicators.timestamp).toLocaleTimeString()}
        </small>
      </div>
      
      <div className="card-body">
        {/* RSI Section */}
        <div className="indicator-section mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>RSI (14)</strong>
            {indicators.rsi && (
              <span className={`badge ${getRSIStatus(indicators.rsi).class}`}>
                {getRSIStatus(indicators.rsi).text}
              </span>
            )}
          </div>
          <div className="d-flex justify-content-between">
            <span className={getIndicatorColor(indicators.rsi, 'rsi')}>
              <strong>{formatValue(indicators.rsi)}</strong>
            </span>
            <div className="rsi-levels text-small text-muted">
              <span className="me-2">30</span>
              <span>70</span>
            </div>
          </div>
          {indicators.rsi && (
            <div className="progress mt-1" style={{ height: '4px' }}>
              <div 
                className="progress-bar bg-primary"
                style={{ width: `${indicators.rsi}%` }}
              ></div>
            </div>
          )}
        </div>
        
        {/* MACD Section */}
        <div className="indicator-section mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>MACD</strong>
            {indicators.macd && (
              <span className={`badge ${getMACDStatus(indicators.macd.macd, indicators.macd.signal).class}`}>
                {getMACDStatus(indicators.macd.macd, indicators.macd.signal).text}
              </span>
            )}
          </div>
          <div className="row">
            <div className="col-6">
              <small className="text-muted">MACD</small>
              <div className={getIndicatorColor(indicators.macd?.macd, 'macd')}>
                <strong>{formatValue(indicators.macd?.macd, 4)}</strong>
              </div>
            </div>
            <div className="col-6">
              <small className="text-muted">Signal</small>
              <div className={getIndicatorColor(indicators.macd?.signal, 'macd')}>
                <strong>{formatValue(indicators.macd?.signal, 4)}</strong>
              </div>
            </div>
          </div>
          <div className="mt-1">
            <small className="text-muted">Histogram</small>
            <div className={indicators.macd?.histogram > 0 ? 'text-success' : 'text-danger'}>
              <strong>{formatValue(indicators.macd?.histogram, 4)}</strong>
            </div>
          </div>
        </div>
        
        {/* Bollinger Bands Section */}
        <div className="indicator-section mb-3">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>Bollinger Bands</strong>
          </div>
          <div className="row">
            <div className="col-4">
              <small className="text-muted">Upper</small>
              <div className="text-danger">
                <strong>{formatValue(indicators.bollinger_bands?.upper)}</strong>
              </div>
            </div>
            <div className="col-4">
              <small className="text-muted">Middle</small>
              <div className="text-warning">
                <strong>{formatValue(indicators.bollinger_bands?.middle)}</strong>
              </div>
            </div>
            <div className="col-4">
              <small className="text-muted">Lower</small>
              <div className="text-success">
                <strong>{formatValue(indicators.bollinger_bands?.lower)}</strong>
              </div>
            </div>
          </div>
        </div>
        
        {/* Moving Averages Section */}
        <div className="indicator-section">
          <div className="d-flex justify-content-between align-items-center mb-2">
            <strong>Moving Averages</strong>
          </div>
          <div className="row">
            <div className="col-6">
              <small className="text-muted">EMA 20</small>
              <div className="text-info">
                <strong>{formatValue(indicators.moving_averages?.ema_20)}</strong>
              </div>
              <small className="text-muted">EMA 50</small>
              <div className="text-info">
                <strong>{formatValue(indicators.moving_averages?.ema_50)}</strong>
              </div>
            </div>
            <div className="col-6">
              <small className="text-muted">SMA 20</small>
              <div className="text-secondary">
                <strong>{formatValue(indicators.moving_averages?.sma_20)}</strong>
              </div>
              <small className="text-muted">SMA 50</small>
              <div className="text-secondary">
                <strong>{formatValue(indicators.moving_averages?.sma_50)}</strong>
              </div>
            </div>
          </div>
        </div>
        
        {/* Volume SMA */}
        <div className="indicator-section mt-3">
          <div className="d-flex justify-content-between">
            <small className="text-muted">Volume SMA</small>
            <strong>{formatValue(indicators.volume_sma, 0)}</strong>
          </div>
        </div>
      </div>
    </div>
  );
};

export default IndicatorPanel;