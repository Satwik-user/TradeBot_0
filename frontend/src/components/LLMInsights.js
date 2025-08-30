// frontend/src/components/LLMInsights.js
import React, { useEffect, useState } from "react";
import { getLLMAnalysis } from "../services/apiService";
import "../styles/components/LLMInsights.css";

const LLMInsights = ({ symbol = "AAPL", timeframe = "1h" }) => {
  const [insight, setInsight] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        setLoading(true);
        const data = await getLLMAnalysis(symbol, timeframe);
        setInsight(data);
      } catch (err) {
        setError("Failed to load LLM insights");
      } finally {
        setLoading(false);
      }
    };
    fetchInsights();
  }, [symbol, timeframe]);

  if (loading) return <div className="llm-insights">Loading AI insights...</div>;
  if (error) return <div className="llm-insights error">{error}</div>;
  if (!insight) return null;

  return (
    <div className="llm-insights">
      <h2>🤖 AI Market Insights</h2>
      <div className="insight-box">
        <p>{insight.insight || "No insights available."}</p>
      </div>
      <div className="insight-meta">
        <span>Symbol: {symbol}</span> | <span>Timeframe: {timeframe}</span>
      </div>
    </div>
  );
};

export default LLMInsights;
