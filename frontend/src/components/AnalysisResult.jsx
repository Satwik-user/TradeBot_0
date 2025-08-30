import React from "react";

const AnalysisResult = ({ analysis }) => {
  if (!analysis) return null;

  return (
    <div className="p-4 bg-white shadow-lg rounded-2xl">
      <h2 className="text-xl font-bold mb-2">📊 Technical Analysis</h2>
      <pre className="bg-gray-100 p-2 rounded whitespace-pre-wrap">
        {analysis.analysis.analysis_text}
      </pre>

      <h2 className="text-xl font-bold mt-4">🤖 AI Simplified Insight</h2>
      <p className="bg-blue-50 p-3 rounded">{analysis.llm_insight}</p>
    </div>
  );
};

export default AnalysisResult;
