// frontend/src/App.js
import React, { useState } from 'react';
import { useAppContext } from './context/AppContext';
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import Footer from './components/Footer';
import Login from './components/Login';
import Register from './components/Register';
import 'bootstrap/dist/css/bootstrap.min.css';
import './styles/main.css';

function App() {
  const { state } = useAppContext();
  const { user, isAuthenticated, loading } = state;
  const [showRegister, setShowRegister] = useState(false);

  // Show loading spinner while checking authentication
  if (loading) {
    return (
      <div className="app-container d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <div className="text-center">
          <div className="spinner-border text-primary mb-3" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p>Loading TradeBot...</p>
        </div>
      </div>
    );
  }

  // Show authentication pages if not logged in
  if (!isAuthenticated) {
    return (
      <div className="app-container">
        {showRegister ? (
          <Register onSwitchToLogin={() => setShowRegister(false)} />
        ) : (
          <Login onSwitchToRegister={() => setShowRegister(true)} />
        )}
      </div>
    );
  }

  // Show main dashboard if authenticated
  return (
    <div className="app-container">
      <Header />
      
      <main className="app-content container-fluid">
        <Dashboard user={user} />
      </main>
      
      <Footer />
    </div>
  );
}

export default App;