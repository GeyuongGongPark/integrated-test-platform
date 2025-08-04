// src/App.js
import React, { useState } from 'react';
import './App.css';
import TestCaseApp from './components/testcases';
import PerformanceTestManager from './components/performance';
import UnifiedDashboard from './components/dashboard';
import FolderManager from './components/dashboard/FolderManager';
import { ErrorBoundary } from './components/utils';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <ErrorBoundary>
            <UnifiedDashboard />
          </ErrorBoundary>
        );
      case 'testcases':
        return (
          <ErrorBoundary>
            <TestCaseApp />
          </ErrorBoundary>
        );
      case 'performance':
        return (
          <ErrorBoundary>
            <PerformanceTestManager />
          </ErrorBoundary>
        );
      case 'folders':
        return (
          <ErrorBoundary>
            <FolderManager />
          </ErrorBoundary>
        );
      default:
        return (
          <ErrorBoundary>
            <UnifiedDashboard />
          </ErrorBoundary>
        );
    }
  };

  return (
    <ErrorBoundary>
      <div className="App">
        {/* <header className="App-header">
          <h1>Test Platform - Production Ready v1.0.3</h1>
          <p>✅ 백엔드 배포 성공 | ✅ 프론트엔드 배포 성공</p>
          <p>🚀 완전한 CI/CD 파이프라인 구축 완료!</p>
        </header> */}
        
        <nav className="navbar">
          <div className="nav-brand">
            <h1>Integrated Test Platform</h1>
          </div>
          <div className="nav-links">
            <button 
              className={`nav-link ${activeTab === 'dashboard' ? 'active' : ''}`}
              onClick={() => setActiveTab('dashboard')}
            >
              📊 대시보드
            </button>
            <button 
              className={`nav-link ${activeTab === 'testcases' ? 'active' : ''}`}
              onClick={() => setActiveTab('testcases')}
            >
              🧪 테스트 케이스
            </button>
            <button 
              className={`nav-link ${activeTab === 'performance' ? 'active' : ''}`}
              onClick={() => setActiveTab('performance')}
            >
              ⚡ 성능 테스트
            </button>
            <button 
              className={`nav-link ${activeTab === 'folders' ? 'active' : ''}`}
              onClick={() => setActiveTab('folders')}
            >
              📁 폴더 관리
            </button>
          </div>
        </nav>

        <main className="main-content">
          {renderContent()}
        </main>
      </div>
    </ErrorBoundary>
  );
}

export default App;
