// src/App.js
import React from 'react';
import './App.css';
import TestCaseApp from './TestCaseApp';
import PerformanceTestManager from './PerformanceTestManager';
import UnifiedDashboard from './UnifiedDashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Test Platform - Auto Deploy Test v1.0.1</h1>
        <p>GitHub Actions CI/CD 테스트 중...</p>
      </header>
      <main>
        <TestCaseApp />
        <PerformanceTestManager />
        <UnifiedDashboard />
      </main>
    </div>
  );
}

export default App;
