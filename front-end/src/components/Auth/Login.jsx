import React, { useState } from 'react';
import axios from 'axios';
import './Login.css'; // Import your custom CSS for styling

const Login = ({ onLoginSuccess, onSwitchToRegister }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    console.log("Sending request:", formData);
    try {
      const response = await axios.post("http://localhost:8000/login/", formData);
      console.log("Response:", response.data);
      if ('token' in response.data) {
        console.log("Login successful");
        onLoginSuccess(response.data.token);
      }
    } catch (error) {
      console.error("Login failed:", error.response?.data);
      setError(error.response?.data?.message || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="login-container">
      <div className="login-form">
        <h2>Login</h2>
        {error && <p style={{ color: 'red', marginBottom: '10px' }}>{error}</p>}
        <form onSubmit={handleLogin}>
          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              required
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={(e) => setFormData({ ...formData, password: e.target.value })}
              required
            />
          </div>
          <button type="submit" className="login-button">Login</button>
        </form>
        <p style={{ marginTop: '15px', textAlign: 'center' }}>
          Don't have an account? 
          <button 
            onClick={onSwitchToRegister}
            style={{
              background: 'none',
              border: 'none',
              color: '#0066cc',
              cursor: 'pointer',
              textDecoration: 'underline',
              marginLeft: '5px'
            }}
          >
            Register here
          </button>
        </p>
      </div>
    </div>
  );
};

export default Login;
