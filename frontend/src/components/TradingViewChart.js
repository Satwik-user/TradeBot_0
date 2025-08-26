import React, { useEffect, useRef, useState } from 'react';
import '../styles/components/TradingViewChart.css';

let tvScriptLoadingPromise;

const TradingViewChart = () => {
  const onLoadScriptRef = useRef();
  const [symbol, setSymbol] = useState('BINANCE:BTCUSDT');
  const [interval, setInterval] = useState('60');
  
  useEffect(() => {
    onLoadScriptRef.current = createWidget;

    if (!tvScriptLoadingPromise) {
      tvScriptLoadingPromise = new Promise((resolve) => {
        const script = document.createElement('script');
        script.id = 'tradingview-widget-loading-script';
        script.src = 'https://s3.tradingview.com/tv.js';
        script.type = 'text/javascript';
        script.onload = resolve;
        
        document.head.appendChild(script);
      });
    }

    tvScriptLoadingPromise.then(() => onLoadScriptRef.current && onLoadScriptRef.current());

    return () => {
      onLoadScriptRef.current = null;
    };
  }, [symbol, interval]);

  function createWidget() {
    if (document.getElementById('tradingview_chart') && window.TradingView) {
      new window.TradingView.widget({
        autosize: true,
        symbol: symbol,
        interval: interval,
        timezone: "Etc/UTC",
        theme: "dark",
        style: "1",
        locale: "en",
        toolbar_bg: "#f1f3f6",
        enable_publishing: false,
        withdateranges: true,
        allow_symbol_change: true,
        studies: [
          "RSI@tv-basicstudies",
          "MACD@tv-basicstudies",
          "BollingerBands@tv-basicstudies"
        ],
        container_id: "tradingview_chart"
      });
    }
  }
  
  const handleSymbolChange = (e) => {
    setSymbol(e.target.value);
  };
  
  const handleIntervalChange = (e) => {
    setInterval(e.target.value);
  };

  return (
    <div className="tradingview-chart-container">
      <div className="chart-controls mb-3">
        <div className="row">
          <div className="col-md-6">
            <select 
              className="form-select" 
              value={symbol} 
              onChange={handleSymbolChange}
            >
              <option value="BINANCE:BTCUSDT">Bitcoin (BTC/USDT)</option>
              <option value="BINANCE:ETHUSDT">Ethereum (ETH/USDT)</option>
              <option value="BINANCE:DOGEUSDT">Dogecoin (DOGE/USDT)</option>
              <option value="BINANCE:ADAUSDT">Cardano (ADA/USDT)</option>
              <option value="BINANCE:SOLUSDT">Solana (SOL/USDT)</option>
            </select>
          </div>
          <div className="col-md-6">
            <select 
              className="form-select" 
              value={interval} 
              onChange={handleIntervalChange}
            >
              <option value="1">1 Minute</option>
              <option value="5">5 Minutes</option>
              <option value="15">15 Minutes</option>
              <option value="30">30 Minutes</option>
              <option value="60">1 Hour</option>
              <option value="240">4 Hours</option>
              <option value="D">1 Day</option>
              <option value="W">1 Week</option>
            </select>
          </div>
        </div>
      </div>
      
      <div id="tradingview_chart" className="chart-container" />
    </div>
  );
};

export default TradingViewChart;