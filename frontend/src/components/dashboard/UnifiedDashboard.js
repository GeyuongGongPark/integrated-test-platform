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
    
    // 개발 환경에서만 로깅
    if (process.env.NODE_ENV === 'development') {
      console.log('🌐 API Request:', config.method?.toUpperCase(), config.url);
    }
    
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
    console.error('🚨 API Error:', error.response?.status, error.response?.data || error.message);
    
    // CORS 오류 처리
    if (error.code === 'ERR_NETWORK' || error.message === 'Network Error') {
      console.error('🌐 CORS 또는 네트워크 오류 발생');
    }
    
    // 401 오류 처리
    if (error.response?.status === 401) {
      console.error('🔐 인증 오류 발생');
    }
    
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

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const initializeDatabase = async () => {
    try {
      setDbInitializing(true);
      console.log('🔄 데이터베이스 초기화 시작...');
      
      const response = await axios.post('/init-db');
      console.log('✅ 데이터베이스 초기화 성공:', response.data);
      
      // 초기화 후 데이터 다시 로드
      await fetchDashboardData();
      
      return true;
    } catch (err) {
      console.error('❌ 데이터베이스 초기화 실패:', err);
      return false;
    } finally {
      setDbInitializing(false);
    }
  };

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // API URL 로깅
      console.log('🔗 Current API URL:', config.apiUrl);
      console.log('🌐 Current Origin:', window.location.origin);
      
      // 먼저 간단한 테스트 요청
      try {
        const testRes = await axios.get('/test');
        console.log('✅ Test endpoint successful:', testRes.data);
      } catch (testErr) {
        console.error('❌ Test endpoint failed:', testErr);
      }
      
      // CORS 전용 테스트 요청
      try {
        const corsTestRes = await axios.get('/cors-test');
        console.log('✅ CORS test successful:', corsTestRes.data);
      } catch (corsTestErr) {
        console.error('❌ CORS test failed:', corsTestErr);
      }
      
      // 헬스체크 요청
      try {
        const healthRes = await axios.get('/health');
        console.log('✅ Health check successful:', healthRes.data);
        
        // 데이터베이스 상태 확인
        if (healthRes.data.database && !healthRes.data.database.tables_exist) {
          console.log('⚠️ 데이터베이스 테이블이 존재하지 않습니다. 초기화를 시도합니다...');
          const initSuccess = await initializeDatabase();
          if (!initSuccess) {
            throw new Error('데이터베이스 초기화에 실패했습니다.');
          }
        }
      } catch (healthErr) {
        console.error('❌ Health check failed:', healthErr);
      }
      
      const [testCasesRes, performanceTestsRes, testExecutionsRes, summariesRes, testcaseSummariesRes] = await Promise.all([
        axios.get('/testcases'),
        axios.get('/performance-tests'),
        axios.get('/test-executions'),
        axios.get('/dashboard-summaries'),
        axios.get('/testcases/summary/all')
      ]);

      setTestCases(testCasesRes.data);
      setPerformanceTests(performanceTestsRes.data);
      setTestExecutions(testExecutionsRes.data);
      setDashboardSummaries(summariesRes.data);
      setTestcaseSummaries(testcaseSummariesRes.data);
      
      // 테스트 케이스 요약 데이터 디버깅
      console.log('📊 Testcase summaries loaded:', testcaseSummariesRes.data);
      console.log('📊 Testcases loaded:', testCasesRes.data);
      
      console.log('✅ Dashboard data loaded successfully');
    } catch (err) {
      console.error('Dashboard data fetch error:', err);
      console.error('Error details:', {
        message: err.message,
        code: err.code,
        response: err.response,
        request: err.request
      });
      
      // 데이터베이스 오류인 경우 초기화 시도
      if (err.response?.status === 500 && err.response?.data?.error?.includes('no such table')) {
        console.log('🔄 데이터베이스 테이블 오류 감지. 초기화를 시도합니다...');
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
      blocked: 0,
      pass_rate: 0
    };
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
    return <div className="dashboard-loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="dashboard-error">{error}</div>;
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
              <div 
                className="more-items clickable"
                onClick={() => setActiveTab('testcases')}
              >
                + {testCases.length - 5} more
              </div>
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
              <div 
                className="more-items clickable"
                onClick={() => setActiveTab('performance')}
              >
                + {performanceTests.length - 5} more
              </div>
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
              <div 
                className="more-items clickable"
                onClick={() => setActiveTab('testcases')}
              >
                + {testExecutions.length - 5} more
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default UnifiedDashboard; 