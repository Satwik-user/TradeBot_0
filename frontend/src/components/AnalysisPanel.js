// frontend/src/components/AnalysisPanel.js
import React, { useState } from 'react';

const AnalysisPanel = ({ analysis, loading }) => {
  const [showFullAnalysis, setShowFullAnalysis] = useState(false);
  
  if (loading) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <div className="spinner-border text-primary mb-2" role="status"></div>
          <div>Generating analysis...</div>
        </div>
      </div>
    );
  }
  
  if (!analysis) {
    return (
      <div className="card">
        <div className="card-body text-center text-muted">
          <i className="fas fa-robot fa-2x mb-2"></i>
          <div>No analysis available</div>
        </div>
      </div>
    );
  }
  
  const getTrendIcon = (trend) => {
    const icons = {
      'bullish': 'fas fa-arrow-up text-success',
      'bearish': 'fas fa-arrow-down text-danger',
      'sideways': 'fas fa-arrows-alt-h text-warning'
    };
    return icons[trend] || 'fas fa-minus text-muted';
  };
  
  const getRiskColor = (risk) => {
    const colors = {
      'low': 'success',
      'medium': 'warning',
      'high': 'danger'
    };
    return colors[risk] || 'secondary';
  };
  
  const getSignalIcon = (signalType) => {
    const icons = {
      'buy': 'fas fa-arrow-up text-success',
      'sell': 'fas fa-arrow-down text-danger',
      'hold': 'fas fa-hand-paper text-warning'
    };
    return icons[signalType] || 'fas fa-circle text-muted';
  };
  
  const getSignalStrengthColor = (strength) => {
    const colors = {
      'strong': 'primary',
      'medium': 'info',
      'weak': 'secondary'
    };
    return colors[strength] || 'secondary';
  };
  
  const groupSignalsByType = (signals) => {
    return signals.reduce((acc, signal) => {
      if (!acc[signal.type]) {
        acc[signal.type] = [];
      }
      acc[signal.type].push(signal);
      return acc;
    }, {});
  };
  
  const formatAnalysisText = (text) => {
    if (!text) return '';
    
    // Split by lines and format
    return text.split('\n').map((line, index) => {
      if (line.trim() === '') return null;
      
      // Handle headers (lines starting with emojis or **text**)
      if (line.includes('**') || /^[📈📊🔍🎯]/.test(line)) {
        return (
          <div key={index} className="fw-bold mb-2 text-primary">
            {line.replace(/\*\*/g, '')}
          </div>
        );
      }
      
      // Handle bullet points
      if (line.trim().startsWith('•') || line.trim().startsWith('-')) {
        return (
          <div key={index} className="ms-3 mb-1">
            <i className="fas fa-circle fa-xs text-muted me-2"></i>
            {line.replace(/^[•-]\s*/, '')}
          </div>
        );
      }
      
      return (
        <div key={index} className="mb-1">
          {line}
        </div>
      );
    }).filter(Boolean);
  };
  
  const signalGroups = groupSignalsByType(analysis.signals || []);
  const totalSignals = analysis.signals?.length || 0;
  
  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h6 className="mb-0">
          <i className="fas fa-robot me-2"></i>
          AI Analysis
        </h6>
        <small className="text-muted">
          {analysis.created_at && new Date(analysis.created_at).toLocaleTimeString()}
        </small>
      </div>
      
      <div className="card-body">
        {/* Overall Summary */}
        <div className="analysis-summary mb-4">
          <div className="row">
            <div className="col-6">
              <div className="stat-item text-center">
                <i className={getTrendIcon(analysis.trend_direction)}></i>
                <div className="mt-1">
                  <small className="text-muted">Trend</small>
                  <div className="fw-bold text-capitalize">
                    {analysis.trend_direction}
                  </div>
                </div>
              </div>
            </div>
            <div className="col-6">
              <div className="stat-item text-center">
                <span className={`badge bg-${getRiskColor(analysis.risk_level)}`}>
                  {analysis.risk_level?.toUpperCase()}
                </span>
                <div className="mt-1">
                  <small className="text-muted">Risk Level</small>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Trading Signals */}
        <div className="trading-signals mb-4">
          <h6 className="mb-3">
            Trading Signals 
            <span className="badge bg-info ms-2">{totalSignals}</span>
          </h6>
          
          {totalSignals === 0 ? (
            <div className="text-center text-muted py-2">
              <i className="fas fa-clock me-1"></i>
              No active signals
            </div>
          ) : (
            <div className="signals-grid">
              {Object.entries(signalGroups).map(([type, signals]) => (
                <div key={type} className="signal-group mb-3">
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <div className="d-flex align-items-center">
                      <i className={getSignalIcon(type)}></i>
                      <strong className="ms-2 text-capitalize">{type} Signals</strong>
                    </div>
                    <span className="badge bg-secondary">{signals.length}</span>
                  </div>
                  
                  {signals.map((signal, index) => (
                    <div key={index} className="signal-item p-2 mb-2 bg-light rounded">
                      <div className="d-flex justify-content-between align-items-start">
                        <div className="flex-grow-1">
                          <div className="signal-reason">{signal.reason}</div>
                        </div>
                        <span className={`badge bg-${getSignalStrengthColor(signal.strength)} ms-2`}>
                          {signal.strength}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          )}
        </div>
        
        {/* Key Levels */}
        {analysis.key_levels && (
          <div className="key-levels mb-4">
            <h6 className="mb-3">Key Levels</h6>
            
            <div className="row">
              {analysis.key_levels.support_levels && (
                <div className="col-6">
                  <div className="level-group">
                    <small className="text-muted">Support</small>
                    {analysis.key_levels.support_levels.map((level, index) => (
                      <div key={index} className="level-item d-flex justify-content-between">
                        <span>S{index + 1}</span>
                        <strong className="text-success">${level.toFixed(2)}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {analysis.key_levels.resistance_levels && (
                <div className="col-6">
                  <div className="level-group">
                    <small className="text-muted">Resistance</small>
                    {analysis.key_levels.resistance_levels.map((level, index) => (
                      <div key={index} className="level-item d-flex justify-content-between">
                        <span>R{index + 1}</span>
                        <strong className="text-danger">${level.toFixed(2)}</strong>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
            
            {analysis.key_levels.pivot_point && (
              <div className="pivot-point mt-2 p-2 bg-warning bg-opacity-10 rounded">
                <div className="d-flex justify-content-between">
                  <small>Pivot Point</small>
                  <strong>${analysis.key_levels.pivot_point.toFixed(2)}</strong>
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Detailed Analysis */}
        <div className="detailed-analysis">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h6 className="mb-0">Detailed Analysis</h6>
            <button 
              className="btn btn-sm btn-outline-primary"
              onClick={() => setShowFullAnalysis(!showFullAnalysis)}
            >
              {showFullAnalysis ? 'Show Less' : 'Show More'}
            </button>
          </div>
          
          <div className={`analysis-text ${showFullAnalysis ? '' : 'text-truncate-5'}`}>
            {formatAnalysisText(analysis.analysis_text)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPanel;