// frontend/src/components/Register.js
import React, { useState } from 'react';
import { register } from '../services/authService';

const Register = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    if (error) setError('');
    if (success) setSuccess('');
  };

  const validateForm = () => {
    if (!formData.username || !formData.email || !formData.password || !formData.confirmPassword) {
      setError('Please fill in all fields');
      return false;
    }

    if (formData.username.length < 3) {
      setError('Username must be at least 3 characters');
      return false;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters');
      return false;
    }

    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return false;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Please enter a valid email address');
      return false;
    }

    return true;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const result = await register(formData.username, formData.email, formData.password);
      
      if (result.success) {
        setSuccess('Registration successful! Please sign in.');
        setFormData({
          username: '',
          email: '',
          password: '',
          confirmPassword: ''
        });
        setTimeout(() => onSwitchToLogin(), 2000);
      } else {
        setError(result.error || 'Registration failed');
      }
    } catch (error) {
      setError('Network error. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container-fluid vh-100 d-flex align-items-center justify-content-center bg-primary">
      <div className="card shadow-lg" style={{ maxWidth: '400px', width: '100%' }}>
        <div className="card-body p-4">
          <div className="text-center mb-4">
            <i className="fas fa-user-plus fa-3x text-primary mb-2"></i>
            <h3>Create Account</h3>
            <p className="text-muted">Join TradeBot today</p>
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
                placeholder="Choose a username"
                disabled={isLoading}
                required
              />
            </div>

            <div className="mb-3">
              <label htmlFor="email" className="form-label">Email</label>
              <input
                type="email"
                className="form-control"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="Enter your email"
                disabled={isLoading}
                required
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
                placeholder="Create a password (min 6 characters)"
                disabled={isLoading}
                required
              />
            </div>

            <div className="mb-3">
              <label htmlFor="confirmPassword" className="form-label">Confirm Password</label>
              <input
                type="password"
                className="form-control"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleInputChange}
                placeholder="Confirm your password"
                disabled={isLoading}
                required
              />
            </div>

            {error && (
              <div className="alert alert-danger" role="alert">
                {error}
              </div>
            )}

            {success && (
              <div className="alert alert-success" role="alert">
                {success}
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
                  Creating Account...
                </>
              ) : (
                'Create Account'
              )}
            </button>
          </form>

          <div className="text-center">
            <span className="text-muted">Already have an account? </span>
            <button 
              type="button"
              onClick={onSwitchToLogin}
              className="btn btn-link p-0"
            >
              Sign In
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;