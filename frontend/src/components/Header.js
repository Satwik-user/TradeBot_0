import React, { useContext } from 'react';
import { AppContext } from '../context/AppContext';

const Header = () => {
  const { user, setUser } = useContext(AppContext);

  const handleLogout = () => {
    localStorage.removeItem('demoUser');
    setUser(null);
  };

  return (
    <header className="app-header">
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark">
        <div className="container">
          <a className="navbar-brand" href="/">
            <i className="fas fa-robot me-2"></i>
            TradeBot
          </a>
          
          {user && (
            <div className="d-flex ms-auto">
              <div className="user-info me-3 text-light">
                <span>Welcome, {user.name}</span>
                <span className="ms-3 badge bg-success">
                  ${user.balance.toFixed(2)}
                </span>
              </div>
              
              <button className="btn btn-outline-light btn-sm" onClick={handleLogout}>
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