import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './UnifiedDashboard.css';

// axios 기본 URL 설정
axios.defaults.baseURL = config.apiUrl;

const UnifiedDashboard = () => {
  const [testCases, setTestCases] = useState([]);
  const [performanceTests, setPerformanceTests] = useState([]);
  const [testExecutions, setTestExecutions] = useState([]);
  const [dashboardSummaries, setDashboardSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [testCasesRes, performanceTestsRes, testExecutionsRes, summariesRes] = await Promise.all([
        axios.get('/testcases'),
        axios.get('/performance-tests'),
        axios.get('/test-executions'),
        axios.get('/dashboard-summaries')
      ]);

      setTestCases(testCasesRes.data);
      setPerformanceTests(performanceTestsRes.data);
      setTestExecutions(testExecutionsRes.data);
      setDashboardSummaries(summariesRes.data);
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
      console.error('Dashboard data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getEnvironmentSummary = (environment) => {
    const summary = dashboardSummaries.find(s => s.environment === environment);
    return summary || {
      total_tests: 0,
      passed_tests: 0,
      failed_tests: 0,
      skipped_tests: 0,
      pass_rate: 0
    };
  };

  const getStatusColor = (passRate) => {
    if (passRate >= 90) return '#4CAF50'; // Green
    if (passRate >= 70) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  if (loading) {
    return <div className="dashboard-loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="dashboard-error">{error}</div>;
  }

  return (
    <div className="unified-dashboard">
      <h1>통합 테스트 플랫폼 대시보드</h1>
      
      {/* 환경별 테스트 결과 요약 */}
      <div className="environment-summary-section">
        <h2>환경별 테스트 결과 요약</h2>
        <div className="environment-cards">
          {['dev', 'alpha', 'production'].map(env => {
            const summary = getEnvironmentSummary(env);
            return (
              <div key={env} className="environment-card">
                <h3>{env.toUpperCase()} 환경</h3>
                <div className="summary-stats">
                  <div className="stat-item">
                    <span className="stat-label">전체 테스트:</span>
                    <span className="stat-value">{summary.total_tests}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">성공:</span>
                    <span className="stat-value success">{summary.passed_tests}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">실패:</span>
                    <span className="stat-value failed">{summary.failed_tests}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">건너뜀:</span>
                    <span className="stat-value skipped">{summary.skipped_tests}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">성공률:</span>
                    <span 
                      className="stat-value pass-rate"
                      style={{ color: getStatusColor(summary.pass_rate) }}
                    >
                      {summary.pass_rate}%
                    </span>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* 기존 대시보드 내용 */}
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h3>테스트 케이스 ({testCases.length})</h3>
          <div className="card-content">
            {testCases.slice(0, 5).map(testCase => (
              <div key={testCase.id} className="test-item">
                <span className="test-name">{testCase.description}</span>
                <span className={`test-status ${testCase.result_status.toLowerCase().replace('/', '-')}`}>
                  {testCase.result_status}
                </span>
              </div>
            ))}
            {testCases.length > 5 && (
              <div className="more-items">+ {testCases.length - 5} more</div>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>성능 테스트 ({performanceTests.length})</h3>
          <div className="card-content">
            {performanceTests.slice(0, 5).map(test => (
              <div key={test.id} className="test-item">
                <span className="test-name">{test.name}</span>
                <span className="test-environment">{test.environment}</span>
              </div>
            ))}
            {performanceTests.length > 5 && (
              <div className="more-items">+ {performanceTests.length - 5} more</div>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <h3>최근 테스트 실행 ({testExecutions.length})</h3>
          <div className="card-content">
            {testExecutions.slice(0, 5).map(execution => (
              <div key={execution.id} className="test-item">
                <span className="test-name">Test #{execution.id}</span>
                <span className={`test-status ${execution.status.toLowerCase().replace('/', '-')}`}>
                  {execution.status}
                </span>
              </div>
            ))}
            {testExecutions.length > 5 && (
              <div className="more-items">+ {testExecutions.length - 5} more</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedDashboard; 