// src/App.js
import React from 'react';
import './App.css';
import TestCaseApp from './TestCaseAPP';
import PerformanceTestManager from './PerformanceTestManager';
import UnifiedDashboard from './UnifiedDashboard';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Test Platform - Production Ready v1.0.3</h1>
        <p>✅ 백엔드 배포 성공 | ✅ 프론트엔드 배포 성공</p>
        <p>🚀 완전한 CI/CD 파이프라인 구축 완료!</p>
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
