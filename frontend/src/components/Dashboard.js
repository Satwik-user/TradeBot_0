// frontend/src/components/Dashboard.js
import React from 'react';
import TradingViewChart from './TradingViewChart';
import MarketSummary from './MarketSummary';
import TradeForm from './TradeForm';
import VoiceAssistant from './VoiceRecognition';
import TradeHistory from './TradeHistory';
import { useAppContext } from '../context/AppContext';
import '../styles/components/Dashboard.css';

const Dashboard = () => {
  const { state } = useAppContext();
  const { trades, loading } = state;

  return (
    <div className="dashboard-container">
      <div className="row">
        <div className="col-md-8">
          <div className="card chart-section">
            <div className="card-header d-flex justify-content-between align-items-center">
              <h3>Market Chart</h3>
              {loading && (
                <div
                  className="spinner-border spinner-border-sm text-primary"
                  role="status"
                ></div>
              )}
            </div>
            <div
              className="card-body"
              style={{ height: '600px', padding: '0' }}
            >
              <TradingViewChart />
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

export default Dashboard;
