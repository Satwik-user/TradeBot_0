// frontend/src/components/PatternDetection.js
import React, { useState } from 'react';

const PatternDetection = ({ patterns = [], loading }) => {
  const [expandedPattern, setExpandedPattern] = useState(null);
  
  if (loading) {
    return (
      <div className="card">
        <div className="card-body text-center">
          <div className="spinner-border text-primary mb-2" role="status"></div>
          <div>Detecting patterns...</div>
        </div>
      </div>
    );
  }
  
  const getPatternIcon = (patternType) => {
    const icons = {
      'head_and_shoulders': 'fas fa-mountain',
      'double_top': 'fas fa-arrows-alt-v',
      'double_bottom': 'fas fa-arrows-alt-v',
      'triangle': 'fas fa-play',
      'support_resistance': 'fas fa-minus',
      'trend_line': 'fas fa-chart-line'
    };
    return icons[patternType] || 'fas fa-chart-area';
  };
  
  const getPatternColor = (patternType, confidence) => {
    if (confidence >= 0.8) return 'success';
    if (confidence >= 0.6) return 'warning';
    return 'info';
  };
  
  const getPatternSentiment = (patternType) => {
    const bearishPatterns = ['head_and_shoulders', 'double_top', 'descending_triangle'];
    const bullishPatterns = ['double_bottom', 'ascending_triangle'];
    
    if (bearishPatterns.includes(patternType)) return { text: 'Bearish', class: 'text-danger' };
    if (bullishPatterns.includes(patternType)) return { text: 'Bullish', class: 'text-success' };
    return { text: 'Neutral', class: 'text-muted' };
  };
  
  const formatPatternType = (type) => {
    return type.split('_').map(word => 
      word.charAt(0).toUpperCase() + word.slice(1)
    ).join(' ');
  };
  
  const togglePattern = (index) => {
    setExpandedPattern(expandedPattern === index ? null : index);
  };
  
  return (
    <div className="card">
      <div className="card-header d-flex justify-content-between align-items-center">
        <h6 className="mb-0">
          <i className="fas fa-search me-2"></i>
          Pattern Detection
        </h6>
        <span className="badge bg-primary">{patterns.length}</span>
      </div>
      
      <div className="card-body">
        {patterns.length === 0 ? (
          <div className="text-center text-muted py-3">
            <i className="fas fa-chart-area fa-2x mb-2"></i>
            <div>No patterns detected</div>
            <small>Patterns will appear as they are identified</small>
          </div>
        ) : (
          <div className="pattern-list">
            {patterns.map((pattern, index) => {
              const sentiment = getPatternSentiment(pattern.pattern_type);
              const isExpanded = expandedPattern === index;
              
              return (
                <div key={index} className={`pattern-item mb-3 ${isExpanded ? 'expanded' : ''}`}>
                  <div 
                    className="pattern-header d-flex justify-content-between align-items-center cursor-pointer"
                    onClick={() => togglePattern(index)}
                  >
                    <div className="d-flex align-items-center">
                      <i className={`${getPatternIcon(pattern.pattern_type)} me-2`}></i>
                      <div>
                        <strong>{formatPatternType(pattern.pattern_type)}</strong>
                        <div className="d-flex align-items-center mt-1">
                          <span className={`badge bg-${getPatternColor(pattern.pattern_type, pattern.confidence)} me-2`}>
                            {(pattern.confidence * 100).toFixed(0)}%
                          </span>
                          <small className={sentiment.class}>
                            {sentiment.text}
                          </small>
                        </div>
                      </div>
                    </div>
                    
                    <div className="d-flex align-items-center">
                      <small className="text-muted me-2">
                        {new Date(pattern.detected_at).toLocaleDateString()}
                      </small>
                      <i className={`fas fa-chevron-${isExpanded ? 'up' : 'down'}`}></i>
                    </div>
                  </div>
                  
                  {isExpanded && (
                    <div className="pattern-details mt-3 p-3 bg-light rounded">
                      <div className="row">
                        <div className="col-md-8">
                          <h6>Description</h6>
                          <p className="mb-2">{pattern.description}</p>
                          
                          <h6>Confidence Level</h6>
                          <div className="progress mb-2" style={{ height: '6px' }}>
                            <div 
                              className={`progress-bar bg-${getPatternColor(pattern.pattern_type, pattern.confidence)}`}
                              style={{ width: `${pattern.confidence * 100}%` }}
                            ></div>
                          </div>
                          <small className="text-muted">
                            {pattern.confidence >= 0.8 ? 'High' : pattern.confidence >= 0.6 ? 'Medium' : 'Low'} confidence
                          </small>
                        </div>
                        
                        <div className="col-md-4">
                          <h6>Pattern Data</h6>
                          {pattern.pattern_data && (
                            <div className="pattern-data">
                              {Object.entries(pattern.pattern_data).map(([key, value]) => (
                                <div key={key} className="d-flex justify-content-between mb-1">
                                  <small className="text-muted">{key.replace('_', ' ')}:</small>
                                  <small>
                                    {typeof value === 'object' && value.price 
                                      ? `$${value.price.toFixed(2)}`
                                      : JSON.stringify(value)
                                    }
                                  </small>
                                </div>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      
                      <div className="mt-3 p-2 border-left border-primary bg-primary bg-opacity-10">
                        <small>
                          <i className="fas fa-lightbulb text-primary me-1"></i>
                          <strong>Trading Insight:</strong> {getPatternTradingInsight(pattern.pattern_type)}
                        </small>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};

const getPatternTradingInsight = (patternType) => {
  const insights = {
    'head_and_shoulders': 'Strong bearish reversal pattern. Consider taking profits on long positions and watch for breakdown below neckline.',
    'double_top': 'Bearish reversal pattern suggesting uptrend exhaustion. Wait for confirmation below support.',
    'double_bottom': 'Bullish reversal pattern indicating potential upward movement. Look for breakout above resistance.',
    'triangle': 'Consolidation pattern. Breakout direction often continues the prior trend.',
    'ascending_triangle': 'Generally bullish pattern. Watch for upward breakout with volume confirmation.',
    'descending_trianglee': 'Generally bearish pattern. Expect downward breakout with increased volume.',
    'support_resistance': 'Key levels for entry/exit decisions. Watch for bounces or breaks.',
    'trend_line': 'Trend continuation or reversal signal depending on break direction.'
  };
  
  return insights[patternType] || 'Monitor price action for potential trading opportunities.';
};

export default PatternDetection;