// frontend/src/components/AnalysisPanel.js
import React, { useState } from 'react';

const AnalysisPanel = ({ analysis, llmAnalysis, loading }) => {
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
  
  if (!analysis && !llmAnalysis) {
    return (
      <div className="card">
        <div className="card-body text-center text-muted">
          <i className="fas fa-robot fa-2x mb-2"></i>
          <div>No analysis available</div>
        </div>
      </div>
    );
  }

  const formatAnalysisText = (text) => {
    if (!text) return '';
    return text.split('\n').map((line, i) => (
      <div key={i} className="mb-1">{line}</div>
    ));
  };
  
  return (
    <div className="card">
      <div className="card-header">
        <i className="fas fa-robot me-2"></i> AI Analysis
      </div>
      <div className="card-body">
        {/* Original Technical Analysis */}
        {analysis && (
          <>
            <h6 className="fw-bold mb-2">📊 Technical Summary</h6>
            <div className={`analysis-text ${showFullAnalysis ? '' : 'text-truncate-5'}`}>
              {formatAnalysisText(analysis.analysis_text)}
            </div>
            <button 
              className="btn btn-sm btn-outline-primary mt-2"
              onClick={() => setShowFullAnalysis(!showFullAnalysis)}
            >
              {showFullAnalysis ? 'Show Less' : 'Show More'}
            </button>
          </>
        )}

        {/* 🔹 LLM Insight Section */}
        {llmAnalysis && (
          <div className="mt-4">
            <h6 className="fw-bold mb-2">🤖 AI Simplified Insight</h6>
            <p className="bg-blue-50 p-3 rounded">{llmAnalysis.llm_summary}</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisPanel;
