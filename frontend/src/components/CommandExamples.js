import React from 'react';

const CommandExamples = () => {
  const examples = [
    "TradeBot, buy 0.5 Bitcoin when it drops to $57,000",
    "TradeBot, what is the RSI indicator showing?",
    "TradeBot, set a stop loss at 2% below entry",
    "TradeBot, show me the current price of Ethereum",
    "TradeBot, what is MACD showing for Bitcoin?"
  ];

  return (
    <div className="command-examples mt-3">
      <h5>Try saying:</h5>
      <ul className="list-group">
        {examples.map((example, index) => (
          <li key={index} className="list-group-item">
            <i className="fa fa-microphone me-2 text-primary"></i>
            {example}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default CommandExamples;