import React, { useState, useEffect } from 'react';
import './App.css';
import ChatUI from './components/Display/ChatUI';
import Login from './components/Auth/Login';
import Register from './components/Auth/Register';
import Profile from './components/Auth/Profile';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authView, setAuthView] = useState('login'); // 'login', 'register', 'chat'

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setIsAuthenticated(true);
      setAuthView('chat');
    }
  }, []);

  const handleLoginSuccess = (token) => {
    localStorage.setItem('token', JSON.stringify(token));
    setIsAuthenticated(true);
    setAuthView('chat');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('selectedPdfId');
    localStorage.removeItem('documentTitle');
    setIsAuthenticated(false);
    setAuthView('login');
  };

  if (!isAuthenticated) {
    return (
      <div className="app-shell">
        {authView === 'login' && (
          <Login 
            onLoginSuccess={handleLoginSuccess}
            onSwitchToRegister={() => setAuthView('register')}
          />
        )}
        {authView === 'register' && (
          <Register 
            onRegisterSuccess={() => setAuthView('login')}
            onSwitchToLogin={() => setAuthView('login')}
          />
        )}
      </div>
    );
  }

  return (
    <div className="app-shell">
      <ChatUI onLogout={handleLogout} />
    </div>
  );
}

export default App;
