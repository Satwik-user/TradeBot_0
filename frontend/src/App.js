import React from 'react';
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';

// Import Pages and Components
import LandingPage from './pages/LandingPage';
import Login from './pages/Login'; // Use Login.js instead of LoginPage.js
import Dashboard from './components/Dashboard';
import Header from './components/Header';
import Footer from './components/Footer';

// Import main stylesheet
import './styles/main.css';

const AppLayout = () => {
  const location = useLocation();
  const noLayoutPages = ['/', '/login'];
  const isNoLayoutPage = noLayoutPages.includes(location.pathname);

  return (
    <div className="app-container">
      {!isNoLayoutPage && <Header />}
      <main className={`app-content ${isNoLayoutPage ? 'full-width' : 'container-fluid'}`}>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Login />} /> {/* This now correctly points to your Login component */}
          <Route path="/dashboard" element={<Dashboard />} />
        </Routes>
      </main>
      {!isNoLayoutPage && <Footer />}
    </div>
  );
};

function App() {
  return (
    <Router>
      <AppLayout />
    </Router>
  );
}

export default App;