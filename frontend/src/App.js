// src/App.js
import React from 'react';
import './App.css';

function App() {
  return (
    <div style={{ padding: '20px', textAlign: 'center', fontFamily: 'Arial, sans-serif' }}>
      <h1>Test Platform - Debug Mode</h1>
      <p>API URL: {process.env.REACT_APP_API_URL || 'Not set'}</p>
      <p>Environment: {process.env.NODE_ENV}</p>
      <p>Build Time: {new Date().toLocaleString()}</p>
      
      <button 
        onClick={() => alert('Button works!')}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px', 
          backgroundColor: '#007bff', 
          color: 'white', 
          border: 'none', 
          borderRadius: '5px',
          cursor: 'pointer'
        }}
      >
        Test Button
      </button>
      
      <div style={{ marginTop: '20px' }}>
        <h3>Debug Info:</h3>
        <ul style={{ textAlign: 'left', maxWidth: '500px', margin: '0 auto' }}>
          <li>React Version: {React.version}</li>
          <li>User Agent: {navigator.userAgent}</li>
          <li>Screen Size: {window.innerWidth} x {window.innerHeight}</li>
          <li>Location: {window.location.href}</li>
        </ul>
      </div>
    </div>
  );
}

export default App;
