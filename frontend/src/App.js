// src/App.js
import React, { useState } from 'react';
import TestCaseApp from './TestCaseAPP';
import PerformanceTestManager from './PerformanceTestManager';
import UnifiedDashboard from './UnifiedDashboard';
import './App.css';

const App = () => {
    const [currentView, setCurrentView] = useState('dashboard');

    const renderContent = () => {
        switch (currentView) {
            case 'test-cases':
                return <TestCaseApp />;
            case 'performance-tests':
                return <PerformanceTestManager />;
            case 'dashboard':
            default:
                return <UnifiedDashboard />;
        }
    };

    return (
        <div className="App">
            <nav className="navbar">
                <div className="nav-brand">
                    <h1>통합 테스트 관리 플랫폼</h1>
                </div>
                <div className="nav-links">
                    <button 
                        className={`nav-link ${currentView === 'dashboard' ? 'active' : ''}`}
                        onClick={() => setCurrentView('dashboard')}
                    >
                        대시보드
                    </button>
                    <button 
                        className={`nav-link ${currentView === 'test-cases' ? 'active' : ''}`}
                        onClick={() => setCurrentView('test-cases')}
                    >
                        테스트 케이스
                    </button>
                    <button 
                        className={`nav-link ${currentView === 'performance-tests' ? 'active' : ''}`}
                        onClick={() => setCurrentView('performance-tests')}
                    >
                        성능 테스트
                    </button>
                </div>
            </nav>
            <main className="main-content">
                {renderContent()}
            </main>
        </div>
    );
};

export default App;
