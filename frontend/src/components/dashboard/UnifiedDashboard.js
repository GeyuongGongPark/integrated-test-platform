import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './UnifiedDashboard.css';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

// Chart.js 등록
ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement);

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
  const [jiraStats, setJiraStats] = useState({
    totalIssues: 0,
    issuesByStatus: {},
    issuesByPriority: {},
    issuesByType: {},
    issuesByLabels: {},
    recentIssues: []
  });
  const [jiraEnvironmentStats, setJiraEnvironmentStats] = useState({});
  const [jiraRecentIssues, setJiraRecentIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // 대시보드 카드 설정 상태
  const [showCardSettings, setShowCardSettings] = useState(false);
  const [cardSettings, setCardSettings] = useState(() => {
    // localStorage에서 설정을 불러오되, 새로운 환경별 카드 설정으로 초기화
    const savedSettings = localStorage.getItem('dashboardCardSettings');
    if (savedSettings) {
      try {
        const parsed = JSON.parse(savedSettings);
        // 기존 environmentSummary와 jiraStats가 있으면 제거하고 새로운 카드들로 교체
        const { environmentSummary, jiraStats, jiraSummary, ...otherSettings } = parsed;
        return {
          environmentDev: { enabled: true, order: 1, size: 'medium' },
          environmentAlpha: { enabled: true, order: 2, size: 'medium' },
          environmentProduction: { enabled: true, order: 3, size: 'medium' },
          jiraStatus: { enabled: true, order: 4, size: 'medium' },
          jiraPriority: { enabled: true, order: 5, size: 'medium' },
          jiraType: { enabled: true, order: 6, size: 'medium' },
          jiraEnvironment: { enabled: true, order: 7, size: 'medium' },
          jiraLabels: { enabled: true, order: 8, size: 'medium' },
          jiraRecentIssues: { enabled: true, order: 9, size: 'medium' },
          ...otherSettings
        };
      } catch (e) {
        console.error('설정 파싱 오류:', e);
      }
    }
    return {
      environmentDev: { enabled: true, order: 1, size: 'medium' },
      environmentAlpha: { enabled: true, order: 2, size: 'medium' },
      environmentProduction: { enabled: true, order: 3, size: 'medium' },
      jiraStatus: { enabled: true, order: 4, size: 'medium' },
      jiraPriority: { enabled: true, order: 5, size: 'medium' },
      jiraType: { enabled: true, order: 6, size: 'medium' },
      jiraEnvironment: { enabled: true, order: 7, size: 'medium' },
      jiraLabels: { enabled: true, order: 8, size: 'medium' },
      jiraRecentIssues: { enabled: true, order: 9, size: 'medium' },
      testCases: { enabled: true, order: 10, size: 'medium' },
      performanceTests: { enabled: true, order: 11, size: 'medium' },
      testExecutions: { enabled: true, order: 12, size: 'medium' },
      screenshots: { enabled: true, order: 13, size: 'small' }
    };
  });
  
  // 드래그 앤 드롭 상태
  const [draggedCard, setDraggedCard] = useState(null);
  const [dragOverCard, setDragOverCard] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  
  // 페이징 상태 추가
  const [testCasesPage, setTestCasesPage] = useState(1);
  const [performanceTestsPage, setPerformanceTestsPage] = useState(1);
  const [testExecutionsPage, setTestExecutionsPage] = useState(1);
  const [jiraRecentIssuesPage, setJiraRecentIssuesPage] = useState(1);
  const [testCasesPagination, setTestCasesPagination] = useState(null);
  const [performanceTestsPagination, setPerformanceTestsPagination] = useState(null);
  const [testExecutionsPagination, setTestExecutionsPagination] = useState(null);
  const [jiraRecentIssuesPagination, setJiraRecentIssuesPagination] = useState(null);
  const itemsPerPage = 5;

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // 카드 설정이 변경될 때 localStorage에 저장
  useEffect(() => {
    localStorage.setItem('dashboardCardSettings', JSON.stringify(cardSettings));
  }, [cardSettings]);

  // 카드 설정 저장
  const saveCardSettings = (newSettings) => {
    setCardSettings(newSettings);
    localStorage.setItem('dashboardCardSettings', JSON.stringify(newSettings));
  };

  // 카드 활성화/비활성화 토글
  const toggleCard = (cardKey) => {
    const newSettings = {
      ...cardSettings,
      [cardKey]: {
        ...cardSettings[cardKey],
        enabled: !cardSettings[cardKey].enabled
      }
    };
    saveCardSettings(newSettings);
  };

  // 카드 순서 변경
  const moveCard = (cardKey, direction) => {
    const newSettings = { ...cardSettings };
    const currentOrder = newSettings[cardKey].order;
    const newOrder = direction === 'up' ? currentOrder - 1 : currentOrder + 1;
    
    // 다른 카드와 순서 교환
    const otherCard = Object.keys(newSettings).find(key => 
      newSettings[key].order === newOrder
    );
    
    if (otherCard) {
      newSettings[cardKey].order = newOrder;
      newSettings[otherCard].order = currentOrder;
      saveCardSettings(newSettings);
    }
  };

  // 카드 크기 변경
  const changeCardSize = (cardKey, size) => {
    const newSettings = {
      ...cardSettings,
      [cardKey]: {
        ...cardSettings[cardKey],
        size: size
      }
    };
    saveCardSettings(newSettings);
  };

  // 드래그 시작
  const handleDragStart = (e, cardKey) => {
    setDraggedCard(cardKey);
    setIsDragging(true);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/html', cardKey);
    
    // body에 드래그 클래스 추가
    document.body.classList.add('dragging');
    
    // 드래그 이미지 설정
    const dragImage = e.target.cloneNode(true);
    dragImage.style.opacity = '0.5';
    dragImage.style.transform = 'rotate(5deg)';
    dragImage.style.width = '300px'; // 고정 너비 설정
    dragImage.style.height = '200px'; // 고정 높이 설정
    dragImage.style.overflow = 'hidden';
    document.body.appendChild(dragImage);
    e.dataTransfer.setDragImage(dragImage, 150, 100); // 중앙에서 드래그
    
    // 드래그 이미지 제거
    setTimeout(() => {
      if (document.body.contains(dragImage)) {
        document.body.removeChild(dragImage);
      }
    }, 0);
  };

  // 드래그 오버
  const handleDragOver = (e, cardKey) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    setDragOverCard(cardKey);
  };

  // 드래그 리브
  const handleDragLeave = (e) => {
    // 자식 요소로 이동하는 경우는 무시
    if (!e.currentTarget.contains(e.relatedTarget)) {
      setDragOverCard(null);
    }
  };

  // 드롭
  const handleDrop = (e, targetCardKey) => {
    e.preventDefault();
    
    if (draggedCard && draggedCard !== targetCardKey) {
      const newSettings = { ...cardSettings };
      const draggedOrder = newSettings[draggedCard].order;
      const targetOrder = newSettings[targetCardKey].order;
      
      // 순서 교환
      newSettings[draggedCard].order = targetOrder;
      newSettings[targetCardKey].order = draggedOrder;
      
      saveCardSettings(newSettings);
    }
    
    setDraggedCard(null);
    setDragOverCard(null);
    setIsDragging(false);
    document.body.classList.remove('dragging');
  };

  // 드래그 종료
  const handleDragEnd = () => {
    setDraggedCard(null);
    setDragOverCard(null);
    setIsDragging(false);
    document.body.classList.remove('dragging');
  };

  // 활성화된 카드들을 순서대로 정렬
  const getEnabledCards = () => {
    return Object.entries(cardSettings)
      .filter(([key, config]) => config.enabled)
      .sort((a, b) => a[1].order - b[1].order);
  };

  // 카드 표시 이름 반환
  const getCardDisplayName = (cardKey) => {
    const names = {
      environmentDev: 'DEV 환경 테스트 케이스',
      environmentAlpha: 'ALPHA 환경 테스트 케이스',
      environmentProduction: 'PRODUCTION 환경 테스트 케이스',
      jiraStatus: '상태',
      jiraPriority: '우선순위',
      jiraType: '타입',
      jiraEnvironment: '환경별 이슈',
      jiraLabels: '🏷️ 이슈 레이블 통계',
      jiraRecentIssues: '최근 이슈',
      testCases: '테스트 케이스',
      performanceTests: '성능 테스트',
      testExecutions: '테스트 실행 결과',
      screenshots: '스크린샷'
    };
    return names[cardKey] || cardKey;
  };

  // 최근 이슈 가져오기
  const fetchJiraRecentIssues = async (page = 1) => {
    try {
      const response = await axios.get(`/api/jira/issues?page=${page}&per_page=${itemsPerPage}`);
      if (response.data.success) {
        setJiraRecentIssuesPagination(response.data.data.pagination);
        return response.data.data.issues || [];
      } else {
        console.error('최근 이슈 조회 실패:', response.data.error);
        return [];
      }
    } catch (error) {
      console.error('최근 이슈 조회 오류:', error);
      return [];
    }
  };

  // 환경별 카드 렌더링 함수
  const renderEnvironmentCard = (env) => {
    try {
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
        <>
          <div className="card-header">
            <h3>{env.toUpperCase()} 환경 테스트 케이스</h3>
            <button 
              className="btn-move-to-tab"
              onClick={() => setActiveTab('testcases')}
              title="테스트 케이스 상세 보기"
            >
              이동 &gt;
            </button>
          </div>
          <div className="card-content">
            <div className="environment-card">
              <div className="chart-container">
                <div className="chart-wrapper">
                  <Doughnut 
                    data={createTestcaseChartData(env)} 
                    options={chartOptions}
                    height={150}
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
          </div>
        </>
      );
    } catch (error) {
      console.error(`환경별 카드 렌더링 오류 (${env}):`, error);
      return (
        <div className="card-header">
          <h3>{env.toUpperCase()} 환경 테스트 케이스</h3>
          <div className="card-content">
            <p>데이터를 불러오는 중 오류가 발생했습니다.</p>
          </div>
        </div>
      );
    }
  };



  const fetchDashboardData = async (skipInit = false) => {
    try {
      setLoading(true);
      setError(null);
      
      // 최적화: 불필요한 헬스체크 요청 제거, 병렬 요청만 유지
      const [testCasesRes, performanceTestsRes, testExecutionsRes, summariesRes, testcaseSummariesRes, jiraStatsRes, jiraEnvironmentStatsRes, jiraRecentIssuesRes] = await Promise.all([
        axios.get(`/testcases?page=1&per_page=${itemsPerPage}`),
        axios.get(`/performance-tests?page=1&per_page=${itemsPerPage}`),
        axios.get(`/test-executions?page=1&per_page=${itemsPerPage}`),
        axios.get('/dashboard-summaries'),
        axios.get('/testcases/summary/all'),
        axios.get('/api/jira/stats'),
        axios.get('/api/jira/stats/environment'),
        axios.get(`/api/jira/issues?page=1&per_page=${itemsPerPage}`)
      ]);

      setTestCases(testCasesRes.data.items || testCasesRes.data);
      setPerformanceTests(performanceTestsRes.data.items || performanceTestsRes.data);
      setTestExecutions(testExecutionsRes.data.items || testExecutionsRes.data);
      setDashboardSummaries(summariesRes.data);
      setTestcaseSummaries(testcaseSummariesRes.data);
      
      // JIRA 통계 처리
      console.log('📊 JIRA 통계 응답:', jiraStatsRes.data);
      if (jiraStatsRes.data && jiraStatsRes.data.success) {
        const stats = jiraStatsRes.data.data;
        console.log('📊 JIRA 통계 데이터:', stats);
        setJiraStats({
          totalIssues: stats.total_issues || 0,
          issuesByStatus: stats.issues_by_status || {},
          issuesByPriority: stats.issues_by_priority || {},
          issuesByType: stats.issues_by_type || {},
          issuesByLabels: stats.issues_by_labels || {},
          recentIssues: stats.recent_issues || []
        });
        console.log('📊 JIRA 통계 상태 설정 완료');
      } else {
        console.log('❌ JIRA 통계 응답 실패:', jiraStatsRes.data);
      }
      
      // 환경별 JIRA 통계 처리
      console.log('🌍 환경별 JIRA 통계 응답:', jiraEnvironmentStatsRes.data);
      if (jiraEnvironmentStatsRes.data && jiraEnvironmentStatsRes.data.success) {
        const envStats = jiraEnvironmentStatsRes.data.data || {};
        console.log('🌍 환경별 JIRA 통계 데이터:', envStats);
        
        // 백엔드 필드명(normalized: totalIssues, issuesByStatus)을 프론트 사용 필드명으로 정규화
        const normalizedEnvStats = {};
        Object.entries(envStats).forEach(([env, data]) => {
          const total = data?.totalIssues ?? data?.total_issues ?? 0;
          const statusBreakdown = data?.issuesByStatus ?? data?.status_breakdown ?? {};
          const doneCount = statusBreakdown?.Done ?? 0;
          const resolutionRate = total > 0 ? Math.round((doneCount / total) * 100) : 0;
          
          normalizedEnvStats[env] = {
            total_issues: total,
            status_breakdown: statusBreakdown,
            resolution_rate: resolutionRate,
          };
        });

        setJiraEnvironmentStats(normalizedEnvStats);
        console.log('🌍 환경별 JIRA 통계 상태 설정 완료');
      } else {
        console.log('❌ 환경별 JIRA 통계 응답 실패:', jiraEnvironmentStatsRes.data);
      }
      
      // 최근 이슈 처리
      if (jiraRecentIssuesRes.data && jiraRecentIssuesRes.data.success) {
        setJiraRecentIssues(jiraRecentIssuesRes.data.data.issues || []);
        setJiraRecentIssuesPagination(jiraRecentIssuesRes.data.data.pagination);
      } else {
        console.error('최근 이슈 조회 실패:', jiraRecentIssuesRes.data?.error);
        setJiraRecentIssues([]);
        setJiraRecentIssuesPagination(null);
      }
      
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

  const createLabelsChartData = () => {
    const labels = Object.keys(jiraStats.issuesByLabels);
    const counts = Object.values(jiraStats.issuesByLabels);
    
    // 레이블을 길이순으로 정렬 (긴 레이블이 많을 수 있으므로)
    const sortedData = labels.map((label, index) => ({
      label,
      count: counts[index]
    })).sort((a, b) => b.count - a.count);

    const sortedLabels = sortedData.map(item => item.label);
    const sortedCounts = sortedData.map(item => item.count);

    // 색상 배열 생성 (다양한 색상)
    const colors = [
      '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
      '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d',
      '#343a40', '#f8f9fa', '#e9ecef', '#dee2e6', '#ced4da'
    ];

    return {
      labels: sortedLabels,
      datasets: [
        {
          label: '이슈 수',
          data: sortedCounts,
          backgroundColor: sortedLabels.map((_, index) => 
            colors[index % colors.length]
          ),
          borderColor: sortedLabels.map((_, index) => 
            colors[index % colors.length]
          ),
          borderWidth: 1,
        },
      ],
    };
  };

  const createDoughnutFromObject = (obj, datasetLabel = '값') => {
    const labels = Object.keys(obj || {});
    const values = Object.values(obj || {});
    const palette = [
      '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
      '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d',
      '#343a40', '#4dabf7', '#69db7c', '#ffa8a8', '#ffd43b'
    ];
    return {
      labels,
      datasets: [
        {
          label: datasetLabel,
          data: values,
          backgroundColor: labels.map((_, i) => palette[i % palette.length]),
          borderColor: '#ffffff',
          borderWidth: 2,
        }
      ]
    };
  };

  const createEnvironmentIssuesChartData = () => {
    // 환경 순서 정의 (우선순위 지정 후, 없는 환경은 제거)
    const environmentOrder = ['alpha', 'prod'];
    const environments = environmentOrder.filter(env => jiraEnvironmentStats.hasOwnProperty(env));
    const totalIssues = environments.map(env => jiraEnvironmentStats[env]?.total_issues || 0);
    
    const palette = [
      '#007bff', '#28a745', '#dc3545', '#ffc107', '#17a2b8',
      '#6f42c1', '#e83e8c', '#fd7e14', '#20c997', '#6c757d'
    ];

    return {
      labels: environments.map(env => env.toUpperCase()),
      datasets: [
        {
          label: '이슈 수',
          data: totalIssues,
          backgroundColor: environments.map((_, i) => palette[i % palette.length]),
          borderColor: '#ffffff',
          borderWidth: 2,
        }
      ]
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

  const barChartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            const label = context.label || '';
            const value = context.parsed.y;
            return `${label}: ${value}개 이슈`;
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: {
          stepSize: 1
        }
      },
      x: {
        ticks: {
          maxRotation: 45,
          minRotation: 0
        }
      }
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="dashboard-loading-spinner">
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
        </div>
      </div>
    );
  }

  return (
    <div className="unified-dashboard">
      <div className="dashboard-header">
        <div className="dashboard-title-section">
      <h1>통합 테스트 플랫폼 대시보드</h1>
      
        </div>
        <button 
          className="btn-card-settings"
          onClick={() => setShowCardSettings(!showCardSettings)}
          title="카드 설정"
        >
          ⚙️  
        </button>
      </div>

      {/* 카드 설정 모달 */}
      {showCardSettings && (
        <div className="card-settings-modal">
          <div className="card-settings-content">
            <div className="card-settings-header">
              <h3>대시보드 카드 설정</h3>
              <button 
                className="btn-close"
                onClick={() => setShowCardSettings(false)}
              >
                ✕
              </button>
            </div>
            <div className="card-settings-body">
              {Object.entries(cardSettings).map(([cardKey, config]) => (
                <div key={cardKey} className="card-setting-item">
                  <div className="card-setting-info">
                    <div className="card-setting-header">
                      <label className="card-toggle">
                        <input
                          type="checkbox"
                          checked={config.enabled}
                          onChange={() => toggleCard(cardKey)}
                        />
                        <span className="card-name">
                          {getCardDisplayName(cardKey)}
                        </span>
                      </label>
                    </div>
                    {config.enabled && (
                        <div className="card-setting-controls">
                          <div className="card-order-controls">
                            <button
                              className="btn-move"
                              onClick={() => moveCard(cardKey, 'up')}
                              disabled={config.order === 1}
                              title="위로 이동"
                            >
                              ↑
                            </button>
                            <span className="order-number">{config.order}</span>
                            <button
                              className="btn-move"
                              onClick={() => moveCard(cardKey, 'down')}
                              disabled={config.order === Object.keys(cardSettings).length}
                              title="아래로 이동"
                            >
                              ↓
                            </button>
                          </div>
                          <div className="card-size-controls">
                            <label>크기:</label>
                            <select
                              value={config.size}
                              onChange={(e) => changeCardSize(cardKey, e.target.value)}
                            >
                              <option value="small">작게 (3열 그리드)</option>
                              <option value="medium">보통 (3열 그리드)</option>
                              <option value="large">크게 (전체 너비)</option>
                            </select>
                          </div>
                        </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            <div className="card-settings-footer">
              <button 
                className="btn-reset"
                onClick={() => {
                  const defaultSettings = {
                    environmentDev: { enabled: true, order: 1, size: 'medium' },
                    environmentAlpha: { enabled: true, order: 2, size: 'medium' },
                    environmentProduction: { enabled: true, order: 3, size: 'medium' },
                    jiraStatus: { enabled: true, order: 4, size: 'medium' },
                    jiraPriority: { enabled: true, order: 5, size: 'medium' },
                    jiraType: { enabled: true, order: 6, size: 'medium' },
                    jiraEnvironment: { enabled: true, order: 7, size: 'medium' },
                    jiraLabels: { enabled: true, order: 8, size: 'medium' },
                    jiraRecentIssues: { enabled: true, order: 9, size: 'medium' },
                    testCases: { enabled: true, order: 10, size: 'medium' },
                    performanceTests: { enabled: true, order: 11, size: 'medium' },
                    testExecutions: { enabled: true, order: 12, size: 'medium' },
                    screenshots: { enabled: true, order: 13, size: 'small' }
                  };
                  saveCardSettings(defaultSettings);
                }}
              >
                기본값으로 재설정
              </button>
              <button 
                className="btn-close-modal"
                onClick={() => setShowCardSettings(false)}
              >
                완료
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* 동적으로 렌더링되는 카드들 */}
      <div className="dynamic-cards-container">
        {getEnabledCards().map(([cardKey, config]) => {
        const isDragging = draggedCard === cardKey;
        const isDragOver = dragOverCard === cardKey;
        
        return (
          <div key={cardKey}>
            {cardKey === 'environmentDev' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                
                <div className="card-content">
                  {renderEnvironmentCard('dev')}
                </div>
              </div>
            )}
            
            {cardKey === 'environmentAlpha' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                
                <div className="card-content">
                  {renderEnvironmentCard('alpha')}
                </div>
              </div>
            )}
            
            {cardKey === 'environmentProduction' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-content">
                  
                  {renderEnvironmentCard('production')}
                </div>
              </div>
            )}
            
            {cardKey === 'jiraStatus' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-header">
                  <h3>상태</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('jira')}
                    title="이슈 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="chart-wrapper">
                    <Doughnut data={createDoughnutFromObject(jiraStats.issuesByStatus, '이슈 수')} options={chartOptions} />
                  </div>
                </div>
              </div>
            )}

            {cardKey === 'jiraPriority' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-header">
                  <h3>우선순위</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('jira')}
                    title="이슈 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="chart-wrapper">
                    <Doughnut data={createDoughnutFromObject(jiraStats.issuesByPriority, '이슈 수')} options={chartOptions} />
                  </div>
                </div>
              </div>
            )}

            {cardKey === 'jiraType' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-header">
                  <h3>타입</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('jira')}
                    title="이슈 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="chart-wrapper">
                    <Doughnut data={createDoughnutFromObject(jiraStats.issuesByType, '이슈 수')} options={chartOptions} />
                  </div>
                </div>
              </div>
            )}

            {cardKey === 'jiraEnvironment' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-header">
                  <h3>환경별 이슈</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('jira')}
                    title="이슈 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="environment-issues-container">
                    {/* 환경별 이슈 차트 */}
                    {Object.keys(jiraEnvironmentStats).length > 0 && (
                      <div className="chart-wrapper">
                        <Bar data={createEnvironmentIssuesChartData()} options={barChartOptions} />
                      </div>
                    )}
                    
                    {/* 환경별 이슈 요약 */}
                    <div className="environment-summary">
                      {Object.keys(jiraEnvironmentStats).length > 0 ? (
                        ['alpha', 'prod'].filter(env => jiraEnvironmentStats.hasOwnProperty(env)).map(env => {
                          const data = jiraEnvironmentStats[env];
                          return (
                          <div key={env} className="environment-issue-item">
                            <div className="environment-name">{env.toUpperCase()}</div>
                            <div className="environment-stats">
                              <div className="stat-item">
                                <span className="stat-label">총 이슈:</span>
                                <span className="stat-value">{data.total_issues}</span>
                              </div>
                              <div className="stat-item">
                                <span className="stat-label">해결률:</span>
                                <span className="stat-value resolution-rate">{data.resolution_rate}%</span>
                              </div>
                              <div className="stat-item">
                                <span className="stat-label">완료:</span>
                                <span className="stat-value done-count">{data.status_breakdown?.Done || 0}</span>
                              </div>
                            </div>
                          </div>
                          );
                        })
                      ) : (
                        <p className="no-environment-data">환경별 이슈 데이터가 없습니다.</p>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}

            {cardKey === 'jiraLabels' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
              >
                <div className="card-header">
                  <h3>🏷️ 이슈 레이블 통계</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('jira')}
                    title="이슈 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="chart-container">
                    {/* 전체 레이블 통계 */}
                    <div className="labels-summary">
                      <div className="labels-total">
                        <span className="labels-total-number">{Object.keys(jiraStats.issuesByLabels).length}</span>
                        <span className="labels-total-label">개 레이블</span>
                      </div>
                    </div>
                    
                    {/* 레이블별 막대 그래프 */}
                    <div className="chart-wrapper">
                      <Bar 
                        data={createLabelsChartData()} 
                        options={barChartOptions}
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {cardKey === 'jiraRecentIssues' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-header">
                  <h3>최근 이슈</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('jira')}
                    title="이슈 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="recent-issues-section">
                    <div className="recent-issues-list">
                      {jiraRecentIssues.length > 0 ? (
                        jiraRecentIssues.map(issue => (
                          <div key={issue.id} className="recent-issue-item">
                            <div className="issue-info">
                              <span className="issue-key">{issue.issue_key}</span>
                              <span className="issue-summary">{issue.summary}</span>
                            </div>
                            <div className="issue-meta">
                              <span className={`issue-status status-${issue.status.toLowerCase().replace(' ', '-')}`}>
                                {issue.status}
                              </span>
                              <span className={`issue-priority priority-${issue.priority.toLowerCase()}`}>
                                {issue.priority}
                              </span>
                            </div>
                          </div>
                        ))
                      ) : (
                        <p className="no-recent-issues">최근 이슈가 없습니다.</p>
                      )}
                    </div>
                    
                    {/* 페이지네이션 */}
                    {jiraRecentIssuesPagination && jiraRecentIssuesPagination.total_pages > 1 && (
                      <div className="pagination-controls">
                        <button
                          className="pagination-btn"
                          onClick={() => {
                            const newPage = jiraRecentIssuesPage - 1;
                            if (newPage >= 1) {
                              setJiraRecentIssuesPage(newPage);
                              fetchJiraRecentIssues(newPage).then(issues => {
                                setJiraRecentIssues(issues);
                              });
                            }
                          }}
                          disabled={jiraRecentIssuesPage <= 1}
                        >
                          &lt;
                        </button>
                        
                        <span className="pagination-info">
                          {jiraRecentIssuesPage} / {jiraRecentIssuesPagination.total_pages}
                        </span>
                        
                        <button
                          className="pagination-btn"
                          onClick={() => {
                            const newPage = jiraRecentIssuesPage + 1;
                            if (newPage <= jiraRecentIssuesPagination.total_pages) {
                              setJiraRecentIssuesPage(newPage);
                              fetchJiraRecentIssues(newPage).then(issues => {
                                setJiraRecentIssues(issues);
                              });
                            }
                          }}
                          disabled={jiraRecentIssuesPage >= jiraRecentIssuesPagination.total_pages}
                        >
                          &gt;
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
            
            {cardKey === 'testCases' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
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
                  <span>페이지 {testCasesPagination.page}/{testCasesPagination.pages || 1}</span>
                </div>
              </div>
            )}
          </div>
        </div>
            )}
            
            {cardKey === 'performanceTests' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
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
            {performanceTestsPagination && (
              <div className="pagination-info">
                <div className="pagination-stats">
                  <span>총 {performanceTestsPagination.total_items}개</span>
                  <span>페이지 {performanceTestsPagination.page}/{performanceTestsPagination.total_pages || 1}</span>
                </div>
              </div>
            )}
          </div>
        </div>
            )}
            
            {cardKey === 'testExecutions' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
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
                  <span>페이지 {testExecutionsPagination.page}/{testExecutionsPagination.pages || 1}</span>
                </div>
              </div>
            )}
          </div>
        </div>
            )}
            
            {cardKey === 'screenshots' && (
              <div 
                className={`dashboard-card card-size-${config.size} draggable-card ${isDragging ? 'dragging' : ''} ${isDragOver ? 'drag-over' : ''}`}
                draggable={true}
                onDragStart={(e) => handleDragStart(e, cardKey)}
                onDragOver={(e) => handleDragOver(e, cardKey)}
                onDragLeave={handleDragLeave}
                onDrop={(e) => handleDrop(e, cardKey)}
                onDragEnd={handleDragEnd}
              >
                <div className="card-header">
                  <h3>스크린샷</h3>
                  <button 
                    className="btn-move-to-tab"
                    onClick={() => setActiveTab('testcases')}
                    title="스크린샷 상세 보기"
                  >
                    이동 &gt;
                  </button>
                </div>
                <div className="card-content">
                  <div className="screenshots-grid">
                    <div className="screenshot-item">
                      <div className="screenshot-placeholder">
                        <span>📸</span>
                        <p>스크린샷이 없습니다</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
      </div>
        );
      })}
      </div>

      {/* 기존 대시보드 내용은 동적 렌더링으로 이동됨 */}
    </div>
  );
};

export default UnifiedDashboard; 