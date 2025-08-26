import React, { useContext } from 'react';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import Footer from './components/Footer';
import { AppContext } from './context/AppContext';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/main.css';

function App() {
  const { user } = useContext(AppContext);

  return (
    <div className="app-container">
      <Header />
      
      <main className="app-content container-fluid">
        {user ? (
          <Dashboard />
        ) : (
          <div className="welcome-container text-center">
            <h2>Welcome to TradeBot</h2>
            <p>Your voice-powered trading assistant</p>
            <button className="btn btn-primary" onClick={() => {
              // For demo purposes, simulate login
              localStorage.setItem('demoUser', JSON.stringify({
                id: 1,
                name: 'Demo User',
                balance: 10000,
              }));
              window.location.reload();
            }}>
              Enter Demo Mode
            </button>
          </div>
        )}
      </main>
      
      <Footer />
    </div>
  );
}

export default App;