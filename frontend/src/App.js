// src/App.js
import React, { useState } from 'react';
import './App.css';
import TestCaseApp from './components/testcases';
import PerformanceTestManager from './components/performance';
import AutomationTestManager from './components/automation';
import UnifiedDashboard from './components/dashboard';
import FolderManager from './components/dashboard/FolderManager';
import Settings from './components/settings/Settings';
import UserProfile from './components/auth/UserProfile';
import { ErrorBoundary } from './components/utils';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';

function AppContent() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const { user, logout } = useAuth();

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return (
          <ErrorBoundary>
            <UnifiedDashboard setActiveTab={setActiveTab} />
          </ErrorBoundary>
        );
      case 'testcases':
        return (
          <ErrorBoundary>
            <TestCaseApp />
          </ErrorBoundary>
        );
      case 'automation':
        return (
          <ErrorBoundary>
            <AutomationTestManager />
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
      case 'settings':
        return (
          <ErrorBoundary>
            <Settings />
          </ErrorBoundary>
        );
      case 'profile':
        return (
          <ErrorBoundary>
            <UserProfile />
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

  const handleLogout = () => {
    logout();
    setActiveTab('dashboard');
  };

  // 권한별 메뉴 표시 조건
  const canAccessSettings = () => {
    return user && (user.role === 'admin' || user.role === 'user');
  };

  const canAccessAutomation = () => {
    // 게스트도 자동화 테스트 조회 가능
    return user;
  };

  const canAccessPerformance = () => {
    // 게스트도 성능 테스트 조회 가능
    return user;
  };

  const canAccessFolders = () => {
    // 게스트도 폴더 조회 가능
    return user;
  };

  return (
    <ErrorBoundary>
      <div className="App">
        <nav className="navbar">
          <div className="nav-brand">
            <h1>Integrated Test Platform</h1>
            {user && (
              <div className="user-info">
                <span>👤 {user.username}</span>
                {user.role === 'admin' && <span className="admin-badge">관리자</span>}
                {user.role === 'user' && <span className="user-badge">사용자</span>}
                {user.role === 'guest' && <span className="guest-badge">게스트</span>}
              </div>
            )}
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
            {canAccessAutomation() && (
              <button 
                className={`nav-link ${activeTab === 'automation' ? 'active' : ''}`}
                onClick={() => setActiveTab('automation')}
              >
                🤖 자동화 테스트
              </button>
            )}
            {canAccessPerformance() && (
              <button 
                className={`nav-link ${activeTab === 'performance' ? 'active' : ''}`}
                onClick={() => setActiveTab('performance')}
              >
                ⚡ 성능 테스트
              </button>
            )}
            {canAccessFolders() && (
              <button 
                className={`nav-link ${activeTab === 'folders' ? 'active' : ''}`}
                onClick={() => setActiveTab('folders')}
              >
                📁 폴더 관리
              </button>
            )}
            {canAccessSettings() && (
              <button 
                className={`nav-link ${activeTab === 'settings' ? 'active' : ''}`}
                onClick={() => setActiveTab('settings')}
              >
                ⚙️ 설정
              </button>
            )}
            {user && (
              <button 
                className={`nav-link ${activeTab === 'profile' ? 'active' : ''}`}
                onClick={() => setActiveTab('profile')}
              >
                👤 프로필
              </button>
            )}
            <button 
              className="nav-link nav-logout"
              onClick={handleLogout}
              title="로그아웃"
            >
              🚪
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

function App() {
  return (
    <AuthProvider>
      <ProtectedRoute>
        <AppContent />
      </ProtectedRoute>
    </AuthProvider>
  );
}

export default App;
