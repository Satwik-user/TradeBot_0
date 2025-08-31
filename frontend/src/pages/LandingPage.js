import React from 'react';
import { useNavigate } from 'react-router-dom';
import '../styles/pages/LandingPage.css';

// A simple helper for icons
const Icon = ({ children }) => <span className="icon">{children}</span>;

const LandingPage = () => {
  const navigate = useNavigate();

  // This function will redirect the user to the login page
  const handleTryNow = () => {
    navigate('/login');
  };

  return (
    <div className="landing-page">
      {/* Hero Section */}
      <header className="hero-section">
        <div className="hero-text">
          <h1>AI-Driven Trading Assistant</h1>
          <p>Voice-powered, intelligent, and seamless trading experience</p>
          <button onClick={handleTryNow} className="hero-button">
            Try it Now
          </button>
        </div>
        <div className="hero-image">
          <img src="/assets/images/robot-assistant.png" alt="AI Trading Robot" />
        </div>
      </header>

      <main className="landing-content">
        {/* Problem & Solution Section */}
        <section className="problem-solution-section">
          <div className="problem-column">
            <h2>The Problem</h2>
            <ul>
              <li><Icon>⚡</Icon> Complexity in analyzing trading charts and indicators.</li>
              <li><Icon>🎤</Icon> Lack of intuitive voice-based assistance in trading.</li>
              <li><Icon>🔗</Icon> Limited integration with popular trading platforms.</li>
            </ul>
          </div>
          <div className="solution-column">
            <h2>Our Solution</h2>
            <ul>
              <li><Icon>🎙️</Icon> Accepts voice commands to execute trades.</li>
              <li><Icon>📋</Icon> Explains trading indicators and market patterns.</li>
              <li><Icon>🤖</Icon> AI-powered trade recommendations and automation.</li>
            </ul>
          </div>
        </section>

        {/* Core Features Section */}
        <section className="features-section">
          <h2>Core Features</h2>
          <div className="features-grid">
            <div className="feature-card">
              <h3>Voice Modulation</h3>
              <p>Control trades with natural voice commands and get real-time feedback.</p>
            </div>
            <div className="feature-card">
              <h3>Graph Interpretation</h3>
              <p>Understand RSI, MACD, Bollinger Bands & more with AI-powered insights.</p>
            </div>
            <div className="feature-card">
              <h3>Automated Trades</h3>
              <p>Execute buy/sell orders with stop-loss, trailing stops, and OCO orders.</p>
            </div>
          </div>
        </section>

        {/* Future Scope Section */}
        <section className="future-scope-section">
          <h2>Future Scope</h2>
          <p><Icon>🚀</Icon> Enhance AI for smarter trade recommendations</p>
        </section>
      </main>
    </div>
  );
};

export default LandingPage;