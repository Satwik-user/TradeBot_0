// frontend/src/components/TradingViewChart.js
import React, { useEffect, useRef, useState, memo } from 'react';
import '../styles/components/TradingViewChart.css';

let tvScriptLoadingPromise;

const TradingViewChart = memo(({ 
  symbol: initialSymbol = 'BTCUSDT', 
  timeframe: initialTimeframe = '60', 
  indicators = null,
  patterns = [],
  height = '500px' 
}) => {
  const containerRef = useRef();
  const widgetRef = useRef();
  const [symbol, setSymbol] = useState(`BINANCE:${initialSymbol}`);
  const [interval, setInterval] = useState(initialTimeframe);

  // Load TradingView script
  useEffect(() => {
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

    tvScriptLoadingPromise.then(() => createWidget());

    return () => {
      if (widgetRef.current) {
        try {
          widgetRef.current.remove();
        } catch (e) {
          console.error('Error removing TradingView widget:', e);
        }
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [symbol, interval]);

  const createWidget = () => {
    if (!containerRef.current || !window.TradingView) return;

    // Clear previous widget
    containerRef.current.innerHTML = '';

    widgetRef.current = new window.TradingView.widget({
      width: '100%',
      height: height,
      symbol: symbol,
      interval: interval,
      timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
      theme: 'dark',
      style: '1',
      locale: 'en',
      toolbar_bg: '#1e222d',
      enable_publishing: false,
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      container_id: containerRef.current.id,
      studies: [
        'RSI@tv-basicstudies',
        'MACD@tv-basicstudies',
        'BB@tv-basicstudies',
        'EMA@tv-basicstudies'
      ],
      overrides: {
        "paneProperties.background": "#1e222d",
        "paneProperties.vertGridProperties.color": "#2a2e39",
        "paneProperties.horzGridProperties.color": "#2a2e39",
        "symbolWatermarkProperties.transparency": 90,
        "scalesProperties.textColor": "#AAA",
        "mainSeriesProperties.candleStyle.upColor": "#26a69a",
        "mainSeriesProperties.candleStyle.downColor": "#ef5350",
        "mainSeriesProperties.candleStyle.drawWick": true,
        "mainSeriesProperties.candleStyle.drawBorder": true,
        "mainSeriesProperties.candleStyle.borderColor": "#378658",
        "mainSeriesProperties.candleStyle.borderUpColor": "#26a69a",
        "mainSeriesProperties.candleStyle.borderDownColor": "#ef5350",
        "mainSeriesProperties.candleStyle.wickUpColor": "#26a69a",
        "mainSeriesProperties.candleStyle.wickDownColor": "#ef5350"
      },
      studies_overrides: {
        "RSI.plot.color": "#9C27B0",
        "RSI.upper band.color": "#FF5722",
        "RSI.lower band.color": "#4CAF50",
        "MACD.macd.color": "#2196F3",
        "MACD.signal.color": "#FF9800",
        "BB.upper.color": "#FF6B6B",
        "BB.lower.color": "#4ECDC4",
        "BB.median.color": "#45B7D1"
      },
      loading_screen: {
        backgroundColor: "#1e222d",
        foregroundColor: "#2962ff"
      },
      enabled_features: [
        "study_templates",
        "header_symbol_search",
        "header_resolutions",
        "header_chart_type",
        "header_settings",
        "header_indicators",
        "header_compare",
        "header_undo_redo",
        "header_screenshot",
        "header_fullscreen_button"
      ],
      disabled_features: [
        "use_localstorage_for_settings",
        "volume_force_overlay",
        "header_saveload"
      ]
    });

    if (indicators) addCustomIndicatorOverlays(widgetRef.current, indicators);
    if (patterns && patterns.length > 0) addPatternOverlays(widgetRef.current, patterns);
  };

  const addCustomIndicatorOverlays = (widget, indicators) => {
    console.log('Adding indicator overlays:', indicators);
  };

  const addPatternOverlays = (widget, patterns) => {
    console.log('Adding pattern overlays:', patterns);
  };

  const handleSymbolChange = (e) => {
    setSymbol(e.target.value);
  };

  const handleIntervalChange = (e) => {
    setInterval(e.target.value);
  };

  const chartId = `tradingview-chart-${symbol}-${interval}`;

  return (
    <div className="tradingview-chart-container">
      {/* Controls */}
      <div className="chart-controls mb-3">
        <div className="row">
          <div className="col-md-6">
            <select className="form-select" value={symbol} onChange={handleSymbolChange}>
              <option value="BINANCE:BTCUSDT">Bitcoin (BTC/USDT)</option>
              <option value="BINANCE:ETHUSDT">Ethereum (ETH/USDT)</option>
              <option value="BINANCE:DOGEUSDT">Dogecoin (DOGE/USDT)</option>
              <option value="BINANCE:ADAUSDT">Cardano (ADA/USDT)</option>
              <option value="BINANCE:SOLUSDT">Solana (SOL/USDT)</option>
            </select>
          </div>
          <div className="col-md-6">
            <select className="form-select" value={interval} onChange={handleIntervalChange}>
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

      {/* Chart container */}
      <div ref={containerRef} id={chartId} style={{ height: height }} className="tradingview-widget-container" />

      {/* Loading overlay */}
      {!widgetRef.current && (
        <div className="chart-loading-overlay d-flex justify-content-center align-items-center">
          <div className="text-center">
            <div className="spinner-border text-primary mb-2" role="status"></div>
            <div>Loading chart...</div>
          </div>
        </div>
      )}

      {/* Chart info overlay */}
      <div className="chart-info-overlay">
        <div className="chart-symbol">{symbol}</div>
        <div className="chart-timeframe">{interval}</div>
        {indicators && (
          <div className="chart-indicators-badge">
            <i className="fas fa-chart-line me-1"></i>
            {Object.keys(indicators).length} indicators
          </div>
        )}
      </div>
    </div>
  );
});

TradingViewChart.displayName = 'TradingViewChart';

export default TradingViewChart;
