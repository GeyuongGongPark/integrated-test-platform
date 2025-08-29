import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './UnifiedDashboard.css';
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js';
import { Doughnut } from 'react-chartjs-2';

// Chart.js 등록
ChartJS.register(ArcElement, Tooltip, Legend);

// GitHub Secrets 설정 완료 후 배포 테스트

// axios 기본 URL 설정
axios.defaults.baseURL = config.apiUrl;
axios.defaults.withCredentials = false;  // CORS 문제 해결을 위해 false로 설정

// axios 인터셉터 설정 - CORS 및 인증 문제 해결
axios.interceptors.request.use(
  (config) => {
            // 요청 헤더에 CORS 관련 설정 추가
        config.headers['Content-Type'] = 'application/json';
        config.headers['X-Requested-With'] = 'XMLHttpRequest';
        config.headers['Accept'] = 'application/json';
    
    // Vercel 환경에서 추가 설정
    if (process.env.NODE_ENV === 'production') {
      config.timeout = 15000; // 15초 타임아웃으로 증가
    }
    
    // API Request 로그는 출력하지 않음
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 응답 인터셉터 설정
axios.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // 오류는 조용히 처리
    return Promise.reject(error);
  }
);



const UnifiedDashboard = ({ setActiveTab }) => {
  const [testCases, setTestCases] = useState([]);
  const [performanceTests, setPerformanceTests] = useState([]);
  const [testExecutions, setTestExecutions] = useState([]);
  const [dashboardSummaries, setDashboardSummaries] = useState([]);
  const [testcaseSummaries, setTestcaseSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dbInitializing, setDbInitializing] = useState(false);
  
  // 페이징 상태 추가
  const [testCasesPage, setTestCasesPage] = useState(1);
  const [performanceTestsPage, setPerformanceTestsPage] = useState(1);
  const [testExecutionsPage, setTestExecutionsPage] = useState(1);
  const [testCasesPagination, setTestCasesPagination] = useState(null);
  const [performanceTestsPagination, setPerformanceTestsPagination] = useState(null);
  const [testExecutionsPagination, setTestExecutionsPagination] = useState(null);
  const itemsPerPage = 5;

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const initializeDatabase = async () => {
    try {
      setDbInitializing(true);
      
      const response = await axios.post('/init-db');
      
      // 초기화 후 데이터 다시 로드 (skipInit=true로 호출하여 무한 루프 방지)
      await fetchDashboardData(true);
      
      return true;
    } catch (err) {
      return false;
    } finally {
      setDbInitializing(false);
    }
  };

  const fetchDashboardData = async (skipInit = false) => {
    try {
      setLoading(true);
      setError(null);
      
      // 헬스체크 요청
      try {
        const healthRes = await axios.get('/health');
        
        // 데이터베이스 상태 확인 (skipInit이 false일 때만)
        if (!skipInit && healthRes.data.database && !healthRes.data.database.tables_exist) {
          const initSuccess = await initializeDatabase();
          if (!initSuccess) {
            throw new Error('데이터베이스 초기화에 실패했습니다.');
          }
        }
      } catch (healthErr) {
        // 헬스체크 오류는 조용히 처리
      }
      
      const [testCasesRes, performanceTestsRes, testExecutionsRes, summariesRes, testcaseSummariesRes] = await Promise.all([
        axios.get(`/testcases?page=1&per_page=${itemsPerPage}`),
        axios.get(`/performance-tests?page=1&per_page=${itemsPerPage}`),
        axios.get(`/test-executions?page=1&per_page=${itemsPerPage}`),
        axios.get('/dashboard-summaries'),
        axios.get('/testcases/summary/all')
      ]);

      setTestCases(testCasesRes.data.items || testCasesRes.data);
      setPerformanceTests(performanceTestsRes.data.items || performanceTestsRes.data);
      setTestExecutions(testExecutionsRes.data.items || testExecutionsRes.data);
      setDashboardSummaries(summariesRes.data);
      setTestcaseSummaries(testcaseSummariesRes.data);
      
      // 페이징 정보 설정
      if (testCasesRes.data.pagination) {
        setTestCasesPagination(testCasesRes.data.pagination);
      }
      if (performanceTestsRes.data.pagination) {
        setPerformanceTestsPagination(performanceTestsRes.data.pagination);
      }
      if (testExecutionsRes.data.pagination) {
        setTestExecutionsPagination(testExecutionsRes.data.pagination);
      }
      
    } catch (err) {
      // 오류는 조용히 처리 (개발 환경에서만 로그 출력)
      if (process.env.NODE_ENV === 'development') {
        console.error('Dashboard 데이터 로드 오류:', err);
      }
      
      // 데이터베이스 오류인 경우 초기화 시도 (skipInit이 false일 때만)
      if (!skipInit && err.response?.status === 500 && err.response?.data?.error?.includes('no such table')) {
        setError('데이터베이스 테이블이 없습니다. 초기화를 시도합니다...');
        
        const initSuccess = await initializeDatabase();
        if (initSuccess) {
          setError(null);
          return; // 성공하면 함수 종료
        }
      }
      
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 페이징 데이터 로드 함수들
  const loadMoreTestCases = async () => {
    try {
      const nextPage = testCasesPage + 1;
      const response = await axios.get(`/testcases?page=${nextPage}&per_page=${itemsPerPage}`);
      
      if (response.data.items) {
        setTestCases(prev => [...prev, ...response.data.items]);
        setTestCasesPage(nextPage);
        setTestCasesPagination(response.data.pagination);
      }
    } catch (err) {
      console.error('테스트 케이스 추가 로드 실패:', err);
    }
  };

  const loadMorePerformanceTests = async () => {
    try {
      const nextPage = performanceTestsPage + 1;
      const response = await axios.get(`/performance-tests?page=${nextPage}&per_page=${itemsPerPage}`);
      
      if (response.data.items) {
        setPerformanceTests(prev => [...prev, ...response.data.items]);
        setPerformanceTestsPage(nextPage);
        setPerformanceTestsPagination(response.data.pagination);
      }
    } catch (err) {
      console.error('성능 테스트 추가 로드 실패:', err);
    }
  };

  const loadMoreTestExecutions = async () => {
    try {
      const nextPage = testExecutionsPage + 1;
      const response = await axios.get(`/test-executions?page=${nextPage}&per_page=${itemsPerPage}`);
      
      if (response.data.items) {
        setTestExecutions(prev => [...prev, ...response.data.items]);
        setTestExecutionsPage(nextPage);
        setTestExecutionsPagination(response.data.pagination);
      }
    } catch (err) {
      console.error('테스트 실행 추가 로드 실패:', err);
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

  const getTestcaseEnvironmentSummary = (environment) => {
    const summary = testcaseSummaries.find(s => s.environment === environment);
    return summary || {
      total_testcases: 0,
      passed: 0,
      failed: 0,
      nt: 0,
      na: 0,
      blocked: 0
    };
  };

  // 페이징 관련 함수들
  const resetTestCasesPaging = () => {
    setTestCasesPage(1);
  };

  const resetPerformanceTestsPaging = () => {
    setPerformanceTestsPage(1);
  };

  const resetTestExecutionsPaging = () => {
    setTestExecutionsPage(1);
  };

  const getStatusColor = (passRate) => {
    if (passRate >= 90) return '#4CAF50'; // Green
    if (passRate >= 70) return '#FF9800'; // Orange
    return '#F44336'; // Red
  };

  const createChartData = (environment) => {
    const summary = getEnvironmentSummary(environment);
    const passed = summary.passed_tests;
    const failed = summary.failed_tests;
    const skipped = summary.skipped_tests;
    
    return {
      labels: ['성공', '실패', '건너뜀'],
      datasets: [
        {
          data: [passed, failed, skipped],
          backgroundColor: [
            '#28a745', // 성공 - 녹색
            '#dc3545', // 실패 - 빨간색
            '#ffc107'  // 건너뜀 - 노란색
          ],
          borderColor: [
            '#1e7e34',
            '#c82333',
            '#e0a800'
          ],
          borderWidth: 2,
        },
      ],
    };
  };

  const createTestcaseChartData = (environment) => {
    const summary = getTestcaseEnvironmentSummary(environment);
    const passed = summary.passed;
    const failed = summary.failed;
    const nt = summary.nt;
    const na = summary.na;
    const blocked = summary.blocked;

    return {
      labels: ['Pass', 'Fail', 'N/T', 'N/A', 'Block'],
      datasets: [
        {
          data: [passed, failed, nt, na, blocked],
          backgroundColor: [
            '#28a745', // Pass - 초록색
            '#dc3545', // Fail - 빨간색
            '#d3d3d3', // N/T - 연한 회색
            '#6c757d', // N/A - 진한 회색
            '#000000'  // Block - 검은색
          ],
          borderColor: [
            '#1e7e34',
            '#c82333',
            '#b8b8b8',
            '#545b62',
            '#333333'
          ],
          borderWidth: 2,
        },
      ],
    };
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'bottom',
        labels: {
          padding: 20,
          usePointStyle: true,
          font: {
            size: 12
          }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed;
            const total = context.dataset.data.reduce((a, b) => a + b, 0);
            const percentage = ((value / total) * 100).toFixed(1);
            return `${label}: ${value} (${percentage}%)`;
          }
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner">
          <div className="spinner"></div>
        </div>
        <p>대시보드 데이터를 불러오는 중...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <div className="error-icon">⚠️</div>
        <h3>오류가 발생했습니다</h3>
        <p>{error}</p>
        <div className="error-actions">
          <button 
            className="btn-retry"
            onClick={fetchDashboardData}
            disabled={loading}
          >
            다시 시도
          </button>
          <button 
            className="btn-init-db"
            onClick={initializeDatabase}
            disabled={dbInitializing}
          >
            {dbInitializing ? '초기화 중...' : '데이터베이스 초기화'}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="unified-dashboard">
      <h1>통합 테스트 플랫폼 대시보드</h1>
      
      {/* 데이터베이스 초기화 버튼 */}
      <div className="db-init-section">
        <button 
          className={`db-init-button ${dbInitializing ? 'initializing' : ''}`}
          onClick={initializeDatabase}
          disabled={dbInitializing}
        >
          {dbInitializing ? '데이터베이스 초기화 중...' : '데이터베이스 초기화'}
        </button>
        {error && (
          <div className="error-message">
            {error}
            <button 
              className="retry-button"
              onClick={initializeDatabase}
              disabled={dbInitializing}
            >
              다시 시도
            </button>
          </div>
        )}
      </div>
      
      {/* 환경별 테스트 케이스 상태 요약 */}
      <div className="environment-summary-section">
        <h2>환경별 테스트 케이스 상태 요약</h2>
        <div className="environment-cards">
          {['dev', 'alpha', 'production'].map(env => {
            const summary = getTestcaseEnvironmentSummary(env);
            const total = summary.total_testcases;
            const passed = summary.passed;
            const failed = summary.failed;
            const nt = summary.nt;
            const na = summary.na;
            const blocked = summary.blocked;
            
            // 성공률: Pass / 전체 테스트 케이스 * 100
            const successRate = total > 0 ? (passed / total * 100) : 0;
            
            // 수행률: (전체 테스트 케이스 - N/T) / 전체 테스트 케이스 * 100
            const executionRate = total > 0 ? ((total - nt) / total * 100) : 0;
            
            return (
              <div key={env} className="environment-card">
                <h3>{env.toUpperCase()} 환경</h3>
                <div className="chart-container">
                  <div className="chart-wrapper">
                    <Doughnut 
                      data={createTestcaseChartData(env)} 
                      options={chartOptions}
                      height={200}
                    />
                  </div>
                  <div className="summary-table-container">
                    <table className="summary-table">
                      <thead>
                        <tr>
                          <th>Total</th>
                          <th>Pass</th>
                          <th>Fail</th>
                          <th>N/T</th>
                          <th>N/A</th>
                          <th>Block</th>
                          <th>성공률</th>
                          <th>수행률</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr>
                          <td>{total}</td>
                          <td className="status-pass">{passed}</td>
                          <td className="status-fail">{failed}</td>
                          <td className="status-nt">{nt}</td>
                          <td className="status-na">{na}</td>
                          <td className="status-block">{blocked}</td>
                          <td className="success-rate">{successRate.toFixed(1)}%</td>
                          <td className="execution-rate">{executionRate.toFixed(1)}%</td>
                        </tr>
                      </tbody>
                    </table>
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
          <div className="card-header">
            <h3>테스트 케이스 ({testCases.length})</h3>
            <button 
              className="btn-move-to-tab"
              onClick={() => setActiveTab('testcases')}
              title="테스트 케이스 상세 보기"
            >
              이동 &gt;
            </button>
          </div>
          <div className="card-content">
            {testCases.slice(0, testCasesPage * itemsPerPage).map(testCase => (
              <div key={testCase.id} className="test-item">
                <span className="test-name">{testCase.name || '이름 없음'}</span>
                <span className={`test-status ${(testCase.result_status || 'N/A').toLowerCase().replace('/', '-')}`}>
                  {testCase.result_status || 'N/A'}
                </span>
              </div>
            ))}
            {testCasesPagination?.has_next && (
              <div 
                className="more-items clickable"
                onClick={loadMoreTestCases}
              >
                + {testCasesPagination.total - testCases.length} more
              </div>
            )}
            {testCasesPage > 1 && (
              <div 
                className="reset-paging clickable"
                onClick={resetTestCasesPaging}
              >
                처음부터 보기
              </div>
            )}
            {testCasesPagination && (
              <div className="pagination-info">
                <div className="pagination-stats">
                  <span>총 {testCasesPagination.total}개</span>
                  <span>페이지 {testCasesPagination.page}/{testCasesPagination.pages}</span>
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>성능 테스트 ({performanceTests.length})</h3>
            <button 
              className="btn-move-to-tab"
              onClick={() => setActiveTab('performance')}
              title="성능 테스트 상세 보기"
            >
              이동 &gt;
            </button>
          </div>
          <div className="card-content">
            {performanceTests.slice(0, performanceTestsPage * itemsPerPage).map(test => (
              <div key={test.id} className="test-item">
                <span className="test-name">{test.name}</span>
                <span className="test-environment">{test.environment}</span>
              </div>
            ))}
            {performanceTestsPagination?.total_pages > 1 && (
              <div 
                className="more-items clickable"
                onClick={loadMorePerformanceTests}
              >
                + {performanceTestsPagination.total_items - (performanceTestsPage * itemsPerPage)} more
              </div>
            )}
            {performanceTestsPage > 1 && (
              <div 
                className="reset-paging clickable"
                onClick={resetPerformanceTestsPaging}
              >
                처음부터 보기
              </div>
            )}
          </div>
        </div>

        <div className="dashboard-card">
          <div className="card-header">
            <h3>최근 테스트 실행 ({testExecutions.length})</h3>
            <button 
              className="btn-move-to-tab"
              onClick={() => setActiveTab('testcases')}
              title="테스트 실행 상세 보기"
            >
              이동 &gt;
            </button>
          </div>
          <div className="card-content">
            {testExecutions.slice(0, testExecutionsPage * itemsPerPage).map(execution => (
              <div key={execution.id} className="test-item">
                <span className="test-name">Test #{execution.id}</span>
                <span className={`test-status ${(execution.status || 'N/A').toLowerCase().replace('/', '-')}`}>
                  {execution.status || 'N/A'}
                </span>
              </div>
            ))}
            {testExecutionsPagination?.has_next && (
              <div 
                className="more-items clickable"
                onClick={loadMoreTestExecutions}
              >
                + {testExecutionsPagination.total - testExecutions.length} more
              </div>
            )}
            {testExecutionsPage > 1 && (
              <div 
                className="reset-paging clickable"
                onClick={resetTestExecutionsPaging}
              >
                처음부터 보기
              </div>
            )}
            {testExecutionsPagination && (
              <div className="pagination-info">
                <div className="pagination-stats">
                  <span>총 {testExecutionsPagination.total}개</span>
                  <span>페이지 {testExecutionsPagination.page}/{testExecutionsPagination.pages}</span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedDashboard; 