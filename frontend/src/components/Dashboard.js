import React, { useState } from 'react';
import TradingViewChart from './TradingViewChart';
import TechnicalAnalysis from './TechnicalAnalysis';
import MarketSummary from './MarketSummary';
import TradeForm from './TradeForm';
import VoiceAssistant from './VoiceRecognition';
import TradeHistory from './TradeHistory';
import { useAppContext } from '../context/AppContext';
import '../styles/components/Dashboard.css';
import LLMInsights from './LLMInsights';

const Dashboard = () => {
  const { state } = useAppContext();
  const { trades, loading } = state;
  const [activeTab, setActiveTab] = useState('chart');

  const handleTabClick = (tabName) => {
    setActiveTab(tabName);
  };

  return (
    <div className="dashboard-container">
      <div className="row">
        <div className="col-md-8">
          <div className="card chart-section">
            <div className="card-header">
              <div className="d-flex justify-content-between align-items-center">
                <ul className="nav nav-tabs card-header-tabs mb-0">
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'chart' ? 'active' : ''}`}
                      onClick={() => handleTabClick('chart')}
                      type="button"
                    >
                      <i className="fas fa-chart-line me-2"></i>
                      Chart
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'analysis' ? 'active' : ''}`}
                      onClick={() => handleTabClick('analysis')}
                      type="button"
                    >
                      <i className="fas fa-chart-bar me-2"></i>
                      Technical Analysis
                    </button>
                  </li>
                  <li className="nav-item">
                    <button
                      className={`nav-link ${activeTab === 'llm' ? 'active' : ''}`}
                      onClick={() => handleTabClick('llm')}
                      type="button"
                    >
                      <i className="fas fa-robot me-2"></i>
                      AI Insights
                    </button>
                  </li>
                </ul>
                {loading && (
                  <div
                    className="spinner-border spinner-border-sm text-primary"
                    role="status"
                  >
                    <span className="visually-hidden">Loading...</span>
                  </div>
                )}
              </div>
            </div>
            
            <div className="card-body p-0" style={{ height: '600px' }}>
              <div className="tab-content h-100">
                {/* Chart Tab - Shows TradingView Chart */}
                <div
                  className={`tab-pane fade h-100 ${activeTab === 'chart' ? 'show active' : ''}`}
                  id="chart"
                  role="tabpanel"
                >
                  <TradingViewChart />
                </div>
                
                {/* Technical Analysis Tab - Shows only indicators, no chart */}
                <div
                  className={`tab-pane fade h-100 ${activeTab === 'analysis' ? 'show active' : ''}`}
                  id="analysis"
                  role="tabpanel"
                >
                  <div className="p-3 h-100 overflow-auto">
                    <TechnicalAnalysisNoChart />
                  </div>
                </div>
                
                {/* AI Insights Tab */}
                <div
                  className={`tab-pane fade h-100 ${activeTab === 'llm' ? 'show active' : ''}`}
                  id="llm"
                  role="tabpanel"
                >
                  <div className="p-3 h-100 overflow-auto">
                    <LLMInsights symbol="BTCUSDT" timeframe="1h" />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="col-md-4">
          <VoiceAssistant />
        </div>
      </div>

      <div className="row mt-4">
        <div className="col-md-4">
          <MarketSummary />
        </div>

        <div className="col-md-4">
          <TradeForm />
        </div>

        <div className="col-md-4">
          <TradeHistory trades={trades} />
        </div>
      </div>
    </div>
  );
};

// Component for Technical Analysis without chart
const TechnicalAnalysisNoChart = () => {
  const { state } = useAppContext();
  const { selectedSymbol = 'BTCUSDT' } = state;
  const [timeframe, setTimeframe] = useState('1h');
  const [indicators, setIndicators] = useState(null);
  const [patterns, setPatterns] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [llmAnalysis, setLlmAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    try {
      // Fetch technical analysis data
      // Add your API calls here
      console.log('Fetching technical analysis data...');
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="technical-analysis-no-chart">
      {/* Header with timeframe selector */}
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h5 className="mb-0">
          <i className="fas fa-chart-bar me-2"></i>
          Technical Analysis - {selectedSymbol}
        </h5>
        <div>
          <div className="btn-group me-2" role="group">
            {['5m', '15m', '1h', '4h', '1d'].map((tf) => (
              <button
                key={tf}
                type="button"
                className={`btn btn-sm ${timeframe === tf ? 'btn-primary' : 'btn-outline-primary'}`}
                onClick={() => setTimeframe(tf)}
              >
                {tf}
              </button>
            ))}
          </div>
          <button
            className="btn btn-sm btn-secondary"
            onClick={fetchData}
            disabled={loading}
          >
            {loading ? (
              <span className="spinner-border spinner-border-sm me-1"></span>
            ) : (
              <i className="fas fa-sync-alt me-1"></i>
            )}
            Refresh
          </button>
        </div>
      </div>

      {/* Technical Indicators Grid */}
      <div className="row mb-4">
        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="fas fa-chart-line me-2"></i>
                Technical Indicators
              </h6>
            </div>
            <div className="card-body">
              {loading ? (
                <div className="text-center">
                  <div className="spinner-border text-primary" role="status"></div>
                </div>
              ) : (
                <div className="row">
                  <div className="col-6">
                    <div className="text-center mb-3">
                      <small className="text-muted d-block">RSI (14)</small>
                      <span className="h5 text-warning">52.3</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="text-center mb-3">
                      <small className="text-muted d-block">MACD</small>
                      <span className="h5 text-success">+0.025</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="text-center mb-3">
                      <small className="text-muted d-block">SMA 20</small>
                      <span className="h5">$43,250</span>
                    </div>
                  </div>
                  <div className="col-6">
                    <div className="text-center mb-3">
                      <small className="text-muted d-block">EMA 50</small>
                      <span className="h5">$42,890</span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        <div className="col-md-6">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="fas fa-bullseye me-2"></i>
                Market Signals
              </h6>
            </div>
            <div className="card-body">
              {loading ? (
                <div className="text-center">
                  <div className="spinner-border text-primary" role="status"></div>
                </div>
              ) : (
                <div>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>Overall Trend</span>
                    <span className="badge bg-success">Bullish</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>Support Level</span>
                    <span className="text-success">$42,500</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center mb-2">
                    <span>Resistance Level</span>
                    <span className="text-danger">$44,200</span>
                  </div>
                  <div className="d-flex justify-content-between align-items-center">
                    <span>Risk Level</span>
                    <span className="badge bg-warning">Medium</span>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Pattern Detection */}
      <div className="row mb-4">
        <div className="col-md-12">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="fas fa-shapes me-2"></i>
                Pattern Detection
              </h6>
            </div>
            <div className="card-body">
              {loading ? (
                <div className="text-center">
                  <div className="spinner-border text-primary" role="status"></div>
                </div>
              ) : (
                <div className="row">
                  <div className="col-md-4">
                    <div className="text-center">
                      <div className="h6 text-primary">Ascending Triangle</div>
                      <small className="text-muted">Confidence: 85%</small>
                      <p className="small mt-2">Bullish pattern forming with higher lows and resistance at $44,200</p>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center">
                      <div className="h6 text-warning">Double Bottom</div>
                      <small className="text-muted">Confidence: 72%</small>
                      <p className="small mt-2">Potential reversal pattern detected near $42,000 level</p>
                    </div>
                  </div>
                  <div className="col-md-4">
                    <div className="text-center">
                      <div className="h6 text-info">Volume Breakout</div>
                      <small className="text-muted">Confidence: 91%</small>
                      <p className="small mt-2">Unusual volume spike indicates potential price movement</p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Analysis Summary */}
      <div className="row">
        <div className="col-md-12">
          <div className="card">
            <div className="card-header">
              <h6 className="mb-0">
                <i className="fas fa-brain me-2"></i>
                Analysis Summary
              </h6>
            </div>
            <div className="card-body">
              {loading ? (
                <div className="text-center">
                  <div className="spinner-border text-primary" role="status"></div>
                </div>
              ) : (
                <div>
                  <p className="mb-3">
                    <strong>Current Market Outlook:</strong> The technical analysis suggests a moderately bullish sentiment 
                    for {selectedSymbol} on the {timeframe} timeframe. Key indicators are showing mixed signals with 
                    RSI in neutral territory and MACD showing positive momentum.
                  </p>
                  <div className="row">
                    <div className="col-md-6">
                      <h6 className="text-success">Bullish Factors:</h6>
                      <ul className="small">
                        <li>MACD showing positive divergence</li>
                        <li>Volume confirmation on recent moves</li>
                        <li>Support holding at key levels</li>
                      </ul>
                    </div>
                    <div className="col-md-6">
                      <h6 className="text-danger">Bearish Factors:</h6>
                      <ul className="small">
                        <li>Resistance at $44,200 level</li>
                        <li>RSI approaching overbought territory</li>
                        <li>Market uncertainty in broader context</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;