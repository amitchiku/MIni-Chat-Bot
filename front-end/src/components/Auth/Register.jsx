import React, { useState } from "react";
import axios from "axios";
import { toast } from 'react-toastify';
import "./Register.css"; // Import your custom CSS for styling

const Register = ({ onRegisterSuccess, onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    password: "",
  });
  const [error, setError] = useState('');

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    console.log(formData)
    try {
      const response = await axios.post(
        "http://localhost:8000/register/",
        formData
      );
      if (response.data.message === "User registered successfully") {
        console.log("Registration successful");
        toast.success('Registration successful! Please log in with your credentials.');
        onRegisterSuccess();
      }
    } catch (error) {
      console.error("Registration failed", error.response?.data);
      setError(error.response?.data?.message || 'Registration failed. Please try again.');
    }
  };

  return (
    <div className="register-container">
      <div className="register-form">
        <h2>Register</h2>
        {error && <p style={{ color: 'red', marginBottom: '10px' }}>{error}</p>}
        <form onSubmit={handleRegister}>
          <div className="input-group">
            <label>Username</label>
            <input
              type="text"
              placeholder="Enter your username"
              value={formData.username}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
            />
          </div>
          <div className="input-group">
            <label>Email</label>
            <input
              type="email"
              placeholder="Enter your email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
            />
          </div>
          <div className="input-group">
            <label>Password</label>
            <input
              type="password"
              placeholder="Enter your password"
              value={formData.password}
              onChange={(e) =>
                setFormData({ ...formData, password: e.target.value })
              }
            />
          </div>
          {/* <div className="input-group">
            <label>Mobile no.</label>
            <input
              type="text"
              placeholder="Enter your mobile no."
              value={formData.phone}
              onChange={(e) =>
                setFormData({ ...formData, phone: e.target.value })
              }
            />
          </div>
          <div className="input-group">
            <label>Address</label>
            <input
              type="text"
              placeholder="Enter your address."
              value={formData.address}
              onChange={(e) =>
                setFormData({ ...formData, address: e.target.value })
              }
            />
          </div> */}
          <button type="submit" className="register-button">
            Register
          </button>
        </form>        <p style={{ marginTop: '15px', textAlign: 'center' }}>
          Already have an account? 
          <button 
            onClick={onSwitchToLogin}
            style={{
              background: 'none',
              border: 'none',
              color: '#0066cc',
              cursor: 'pointer',
              textDecoration: 'underline',
              marginLeft: '5px'
            }}
          >
            Login here
          </button>
        </p>      </div>
    </div>
  );
};

export default Register;
