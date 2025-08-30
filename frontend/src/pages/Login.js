import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppContext } from '../context/AppContext';
import { login, loginDemo } from '../services/authService'; // Fixed import path

const Login = ({ onSwitchToRegister }) => {
  const navigate = useNavigate();
  const { actions } = useAppContext();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!formData.username || !formData.password) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    try {
      const result = await login(formData.username, formData.password);
      
      if (result.success) {
        // Store token in localStorage
        localStorage.setItem('tradebot_token', result.token);
        
        // Update app context
        actions.login(result.user, result.token);
        
        // Navigate to dashboard
        navigate('/dashboard');
        
        // Show success message (optional)
        console.log('Login successful, redirecting to dashboard...');
      } else {
        setError(result.error || 'Login failed');
      }
    } catch (error) {
      console.error('Login error:', error);
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDemoLogin = () => {
    try {
      const result = loginDemo();
      if (result.success) {
        // Store demo flag in localStorage
        localStorage.setItem('tradebot_demo', 'true');
        localStorage.setItem('tradebot_token', 'demo_token');
        
        // Update app context
        actions.loginDemo(result.user);
        
        // Navigate to dashboard
        navigate('/dashboard');
        
        console.log('Demo login successful, redirecting to dashboard...');
      }
    } catch (error) {
      console.error('Demo login error:', error);
      setError('Demo login failed. Please try again.');
    }
  };

  const handleRegisterClick = () => {
    if (onSwitchToRegister) {
      onSwitchToRegister();
    } else {
      // If no onSwitchToRegister prop, navigate to register route
      navigate('/register');
    }
  };

  return (
    <div className="container-fluid vh-100 d-flex align-items-center justify-content-center bg-primary">
      <div className="card shadow-lg" style={{ maxWidth: '400px', width: '100%' }}>
        <div className="card-body p-4">
          <div className="text-center mb-4">
            <i className="fas fa-robot fa-3x text-primary mb-2"></i>
            <h3>Welcome to TradeBot</h3>
            <p className="text-muted">Voice-powered trading assistant</p>
          </div>

          <form onSubmit={handleSubmit}>
            <div className="mb-3">
              <label htmlFor="username" className="form-label">Username</label>
              <input
                type="text"
                className="form-control"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Enter your username"
                disabled={isLoading}
                required
                autoComplete="username"
              />
            </div>

            <div className="mb-3">
              <label htmlFor="password" className="form-label">Password</label>
              <input
                type="password"
                className="form-control"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter your password"
                disabled={isLoading}
                required
                autoComplete="current-password"
              />
            </div>

            {error && (
              <div className="alert alert-danger" role="alert">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
              </div>
            )}

            <button 
              type="submit" 
              className="btn btn-primary w-100 mb-3"
              disabled={isLoading}
            >
              {isLoading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" role="status"></span>
                  Signing In...
                </>
              ) : (
                <>
                  <i className="fas fa-sign-in-alt me-2"></i>
                  Sign In
                </>
              )}
            </button>
          </form>

          <div className="text-center mb-3">
            <span className="text-muted">or</span>
          </div>

          <button 
            type="button"
            onClick={handleDemoLogin}
            className="btn btn-success w-100 mb-3"
            disabled={isLoading}
          >
            <i className="fas fa-gamepad me-2"></i>
            Enter Demo Mode
          </button>

          <div className="text-center">
            <span className="text-muted">Don't have an account? </span>
            <button 
              type="button"
              onClick={handleRegisterClick}
              className="btn btn-link p-0 text-decoration-none"
              disabled={isLoading}
            >
              Sign Up
            </button>
          </div>

          {/* Optional: Add forgot password link */}
          <div className="text-center mt-2">
            <button 
              type="button"
              className="btn btn-link btn-sm text-muted"
              onClick={() => console.log('Forgot password clicked')}
              disabled={isLoading}
            >
              Forgot Password?
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;