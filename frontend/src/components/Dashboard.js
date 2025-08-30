// frontend/src/components/Dashboard.js
import React from 'react';
import TradingViewChart from './TradingViewChart';
import MarketSummary from './MarketSummary';
import TradeForm from './TradeForm';
import VoiceAssistant from './VoiceRecognition';
import CommandExamples from './CommandExamples';
import TradeHistory from './TradeHistory';
import { useAppContext } from '../context/AppContext';
import '../styles/components/Dashboard.css';

const Dashboard = () => {
  const { state } = useAppContext();
  const { command, response, trades, loading } = state;

  return (
    <div className="dashboard-container">
      <div className="row">
        <div className="col-md-8">
          <div className="card chart-section">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h3>Market Chart</h3>
              {loading && <div className="spinner-border spinner-border-sm text-primary" role="status"></div>}
            </div>
            <div className="card-body" style={{ height: '600px', padding: '0' }}>
              <TradingViewChart />
            </div>
          </div>
        </div>
        
        <div className="col-md-4">
          <VoiceAssistant />
          
          <div className="card command-section mt-3">
            <div className="card-header">
              <h4>Voice Command Center</h4>
            </div>
            <div className="card-body">
              {command && (
                <div className="command-display mb-3">
                  <div className="alert alert-info mb-2">
                    <strong>You said:</strong>
                    <div className="mt-1">"{command}"</div>
                  </div>
                  {response && (
                    <div className="alert alert-success mb-2">
                      <strong>TradeBot:</strong>
                      <div className="mt-1">{response}</div>
                    </div>
                  )}
                </div>
              )}
              
              <CommandExamples />
            </div>
          </div>
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

export default Dashboard;