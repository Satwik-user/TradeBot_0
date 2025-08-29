// frontend/src/components/Header.js
import React from 'react';
import { useAppContext } from '../context/AppContext';
import { logout } from '../services/authService';

const Header = () => {
  const { state } = useAppContext();
  const { user, isAuthenticated } = state;

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  const isDemoMode = user?.id === 1 || localStorage.getItem('demoUser');

  return (
    <header className="app-header">
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container">
          <a className="navbar-brand" href="/">
            <i className="fas fa-robot me-2"></i>
            TradeBot
          </a>
          
          {isAuthenticated && user && (
            <div className="d-flex ms-auto align-items-center">
              <div className="user-info me-3 text-light">
                <span>Welcome, <strong>{user.name || user.username}</strong></span>
                {isDemoMode && (
                  <span className="ms-2 badge bg-warning text-dark">Demo Mode</span>
                )}
                <span className="ms-3 badge bg-success">
                  Balance: ${user.balance?.toFixed(2) || '10,000.00'}
                </span>
              </div>
              
              <button 
                className="btn btn-outline-light btn-sm" 
                onClick={handleLogout}
                title="Logout"
              >
                <i className="fas fa-sign-out-alt me-1"></i>
                Logout
              </button>
            </div>
          )}
        </div>
      </nav>
    </header>
  );
};

export default Header;