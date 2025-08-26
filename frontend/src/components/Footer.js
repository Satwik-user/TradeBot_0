import React from 'react';

const Footer = () => {
  return (
    <footer className="app-footer text-center py-3">
      <div className="container">
        <p className="mb-0">
          TradeBot Voice Trading Assistant &copy; {new Date().getFullYear()} - 
          Hackathon Project by Prajukta, Satwik, and Srija
        </p>
      </div>
    </footer>
  );
};

export default Footer;