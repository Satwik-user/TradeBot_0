// frontend/src/components/TechnicalAnalysis.js
import React, { useState, useEffect } from 'react';
import { useAppContext } from '../context/AppContext';
import { getTechnicalIndicators, getPatternDetection, getTechnicalAnalysis } from '../services/apiService';
import TradingViewChart from './TradingViewChart';
import IndicatorPanel from './IndicatorPanel';
import PatternDetection from './PatternDetection';
import AnalysisPanel from './AnalysisPanel';

const TechnicalAnalysis = () => {
  const { state } = useAppContext();
  const { selectedSymbol = 'BTCUSDT' } = state;
  
  const [activeTimeframe, setActiveTimeframe] = useState('1h');
  const [indicators, setIndicators] = useState(null);
  const [patterns, setPatterns] = useState([]);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  
  const timeframes = [
    { value: '5m', label: '5m' },
    { value: '15m', label: '15m' },
    { value: '1h', label: '1H' },
    { value: '4h', label: '4H' },
    { value: '1d', label: '1D' }
  ];
  
  useEffect(() => {
    fetchTechnicalData();
    
    // Set up periodic refresh
    const interval = setInterval(fetchTechnicalData, 60000); // Every minute
    return () => clearInterval(interval);
  }, [selectedSymbol, activeTimeframe]);
  
  const fetchTechnicalData = async () => {
    if (!selectedSymbol) return;
    
    setLoading(true);
    setError('');
    
    try {
      const [indicatorsData, patternsData, analysisData] = await Promise.allSettled([
        getTechnicalIndicators(selectedSymbol, activeTimeframe),
        getPatternDetection(selectedSymbol, activeTimeframe),
        getTechnicalAnalysis(selectedSymbol, activeTimeframe)
      ]);
      
      if (indicatorsData.status === 'fulfilled') {
        setIndicators(indicatorsData.value);
      }
      
      if (patternsData.status === 'fulfilled') {
        setPatterns(patternsData.value);
      }
      
      if (analysisData.status === 'fulfilled') {
        setAnalysis(analysisData.value);
      }
      
    } catch (err) {
      console.error('Error fetching technical data:', err);
      setError('Failed to load technical analysis data');
    } finally {
      setLoading(false);
    }
  };
  
  const handleTimeframeChange = (timeframe) => {
    setActiveTimeframe(timeframe);
  };
  
  const renderTimeframeButtons = () => (
    <div className="btn-group" role="group">
      {timeframes.map(tf => (
        <button
          key={tf.value}
          type="button"
          className={`btn ${activeTimeframe === tf.value ? 'btn-primary' : 'btn-outline-primary'}`}
          onClick={() => handleTimeframeChange(tf.value)}
        >
          {tf.label}
        </button>
      ))}
    </div>
  );
  
  return (
    <div className="technical-analysis">
      {/* Header */}
      <div className="card mb-3">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-center">
            <h4 className="card-title mb-0">
              📈 Technical Analysis - {selectedSymbol}
            </h4>
            <div className="d-flex gap-3 align-items-center">
              {renderTimeframeButtons()}
              <button 
                className="btn btn-outline-secondary btn-sm"
                onClick={fetchTechnicalData}
                disabled={loading}
              >
                {loading ? (
                  <span className="spinner-border spinner-border-sm me-1" />
                ) : (
                  <i className="fas fa-sync-alt me-1" />
                )}
                Refresh
              </button>
            </div>
          </div>
          
          {error && (
            <div className="alert alert-warning mt-2 mb-0">
              <i className="fas fa-exclamation-triangle me-2" />
              {error}
            </div>
          )}
        </div>
      </div>
      
      {/* Main Content */}
      <div className="row">
        {/* Chart Section */}
        <div className="col-lg-8">
          <div className="card mb-3">
            <div className="card-body p-0">
              <TradingViewChart 
                symbol={selectedSymbol}
                timeframe={activeTimeframe}
                indicators={indicators}
                patterns={patterns}
                height="500px"
              />
            </div>
          </div>
          
          {/* Patterns Section */}
          <PatternDetection 
            patterns={patterns}
            loading={loading}
          />
        </div>
        
        {/* Indicators & Analysis Section */}
        <div className="col-lg-4">
          <IndicatorPanel 
            indicators={indicators}
            loading={loading}
          />
          
          <AnalysisPanel 
            analysis={analysis}
            loading={loading}
          />
        </div>
      </div>
    </div>
  );
};

export default TechnicalAnalysis;