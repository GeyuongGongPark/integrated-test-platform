// src/TestCaseApp.js
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import config from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import { formatUTCToKST } from '../../utils/dateUtils';
import './TestCaseAPP.css';

// axios 인터셉터 설정 - 인증 토큰 자동 추가
axios.interceptors.request.use(
  (config) => {
    // 로컬 스토리지에서 토큰 가져오기
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    
    // 요청 헤더에 CORS 관련 설정 추가
    config.headers['Content-Type'] = 'application/json';
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    config.headers['Accept'] = 'application/json';
    
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
    console.error('🚨 API Error:', error.response?.status, error.response?.data || error.message);
    
    // 401 오류 처리 (인증 실패)
    if (error.response?.status === 401) {
      console.error('🔐 인증 오류 발생 - 로그인이 필요합니다');
      // 로컬 스토리지에서 토큰 제거
      localStorage.removeItem('token');
      // 페이지 새로고침하여 로그인 페이지로 이동
      window.location.reload();
    }
    
    return Promise.reject(error);
  }
);

// 스크린샷 컴포넌트
const TestCaseScreenshots = ({ testCaseId }) => {
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchScreenshots = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get(`${config.apiUrl}/testcases/${testCaseId}/screenshots`);
      setScreenshots(response.data);
    } catch (err) {
      console.error('스크린샷 조회 오류:', err);
      setError('스크린샷을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  }, [testCaseId]);

  useEffect(() => {
    if (testCaseId) {
      fetchScreenshots();
    }
  }, [testCaseId, fetchScreenshots]);

  if (loading) {
    return <div className="screenshots-loading">스크린샷 로딩 중...</div>;
  }

  if (error) {
    return (
      <div className="screenshots-error">
        <p>❌ {error}</p>
        <button onClick={fetchScreenshots} className="retry-button">
          다시 시도
        </button>
      </div>
    );
  }

  if (screenshots.length === 0) {
    return <div className="no-screenshots">스크린샷이 없습니다.</div>;
  }

  return (
    <div className="screenshots-container">
      {/* 스크린샷 표시는 클라우드 전환 시 S3/CDN으로 대체 예정 */}
      <div className="screenshot-placeholder">
        <p>📸 스크린샷 {screenshots.length}개</p>
        <small>클라우드 전환 시 S3/CDN으로 이미지 표시 예정</small>
        <div className="screenshot-paths">
          {screenshots.map((screenshot, index) => (
            <div key={screenshot.id} className="screenshot-path-item">
              <span>• {screenshot.screenshot_path}</span>
                              <small>{screenshot.timestamp ? formatUTCToKST(screenshot.timestamp) : '시간 정보 없음'}</small>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// 실행 결과 컴포넌트
const TestCaseExecutionResults = ({ testCaseId }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchResults = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${config.apiUrl}/testresults/${testCaseId}`);
      setResults(response.data);
    } catch (err) {
      console.error('실행 결과 조회 오류:', err);
    } finally {
      setLoading(false);
    }
  }, [testCaseId]);

  useEffect(() => {
    if (testCaseId) {
      fetchResults();
    }
  }, [testCaseId, fetchResults]);

  if (loading) {
    return <div className="results-loading">실행 결과 로딩 중...</div>;
  }

  if (results.length === 0) {
    return <div className="no-results">실행 결과가 없습니다.</div>;
  }

  return (
    <div className="execution-results-container">
      {results.map((result, index) => (
        <div key={result.id} className={`result-item ${(result.result || 'N/A').toLowerCase()}`}>
          <div className="result-header">
            <span className={`result-status ${(result.result || 'N/A').toLowerCase()}`}>
              {result.result || 'N/A'}
            </span>
            <span className="result-timestamp">
                              {formatUTCToKST(result.executed_at)}
            </span>
          </div>
          {result.execution_duration && (
            <div className="result-duration">
              실행 시간: {result.execution_duration.toFixed(2)}초
            </div>
          )}
          {result.error_message && (
            <div className="result-error">
              <strong>오류:</strong> {result.error_message}
            </div>
          )}
          {result.screenshot && (
            <div className="result-screenshot">
              <img 
                src={`${config.apiUrl}/screenshots/${result.screenshot}`}
                alt="실행 결과 스크린샷"
                className="result-screenshot-image"
              />
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

// axios 기본 URL 설정
axios.defaults.baseURL = config.apiUrl;

const TestCaseAPP = () => {
  const { user } = useAuth();
  const [testCases, setTestCases] = useState([]);
  const [folderTree, setFolderTree] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTestCase, setEditingTestCase] = useState(null);
  const [newTestCase, setNewTestCase] = useState({
    name: '',
    main_category: '',
    sub_category: '',
    detail_category: '',
    pre_condition: '',
    expected_result: '',
    result_status: 'N/T',
    remark: '',
    folder_id: null,
    automation_code_path: '',
    automation_code_type: 'playwright',
    assignee_id: null
  });
  
  // 사용자 목록 관련 상태
  const [users, setUsers] = useState([]);
  
  // 폴더 이동 관련 상태
  const [selectedTestCases, setSelectedTestCases] = useState([]);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [targetFolderId, setTargetFolderId] = useState('');
  const [allFolders, setAllFolders] = useState([]);
  
  // 아코디언 관련 상태
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [expandedTestCases, setExpandedTestCases] = useState(new Set());
  
  // 검색 관련 상태
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [environmentFilter, setEnvironmentFilter] = useState('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [creatorFilter, setCreatorFilter] = useState('all');
  const [assigneeFilter, setAssigneeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const [testCasesRes, treeRes, foldersRes] = await Promise.all([
        axios.get(`${config.apiUrl}/testcases`),
        axios.get(`${config.apiUrl}/folders/tree`),
        axios.get(`${config.apiUrl}/folders`)
      ]);

      setTestCases(testCasesRes.data);
      setFolderTree(treeRes.data);
      setAllFolders(foldersRes.data);
      
      // 사용자 목록도 가져오기
      try {
        const usersRes = await axios.get(`${config.apiUrl}/users/list`);
        setUsers(usersRes.data);
      } catch (userErr) {
        setUsers([]);
      }
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
      // 오류는 조용히 처리
    } finally {
      setLoading(false);
    }
  };

  const handleFolderSelect = (folderId) => {
          const selectedFolderInfo = findFolderInTree(folderTree, folderId);
    setSelectedFolder(folderId);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      alert('파일을 선택해주세요.');
      return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await axios.post(`${config.apiUrl}/testcases/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        transformRequest: [function (data) {
          return data; // FormData를 그대로 전송
        }],
      });

      alert(response.data.message);
      setShowUploadModal(false);
      setSelectedFile(null);
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('파일 업로드 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleAddTestCase = async () => {
    if (!newTestCase.main_category || !newTestCase.sub_category || !newTestCase.detail_category) {
      alert('필수 항목을 입력해주세요.');
      return;
    }

    try {
      // 자동으로 테스트 케이스 이름 생성
      const autoName = `${newTestCase.main_category} - ${newTestCase.sub_category} - ${newTestCase.detail_category}`;
      const testCaseData = {
        ...newTestCase,
        name: autoName
      };

      // 토큰 확인
      const token = localStorage.getItem('token');
      if (!token) {
        alert('로그인이 필요합니다. 토큰이 없습니다.');
        return;
      }

      await axios.post(`${config.apiUrl}/testcases`, testCaseData);
      alert('테스트 케이스가 성공적으로 추가되었습니다.');
      setShowAddModal(false);
      setNewTestCase({
        name: '',
        main_category: '',
        sub_category: '',
        detail_category: '',
        pre_condition: '',
        expected_result: '',
        result_status: 'N/T',
        remark: '',
        folder_id: null,
        automation_code_path: '',
        automation_code_type: 'playwright',
        assignee_id: null
      });
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('테스트 케이스 추가 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message));
    }
  };

  const handleEditTestCase = async () => {
    if (!editingTestCase.main_category || !editingTestCase.sub_category || !editingTestCase.detail_category) {
      alert('필수 항목을 입력해주세요.');
      return;
    }

    try {
      await axios.put(`${config.apiUrl}/testcases/${editingTestCase.id}`, editingTestCase);
      alert('테스트 케이스가 성공적으로 수정되었습니다.');
      setShowEditModal(false);
      setEditingTestCase(null);
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('테스트 케이스 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleDeleteTestCase = async (testCaseId) => {
    if (!window.confirm('정말로 이 테스트 케이스를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await axios.delete(`${config.apiUrl}/testcases/${testCaseId}`);
      alert('테스트 케이스가 성공적으로 삭제되었습니다.');
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('테스트 케이스 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleStatusChange = async (testCaseId, newStatus) => {
    try {
      const response = await axios.put(`${config.apiUrl}/testcases/${testCaseId}/status`, { 
        status: newStatus 
      });
      
      alert('테스트 케이스 상태가 성공적으로 변경되었습니다.');
      fetchData(); // 데이터 새로고침
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || '알 수 없는 오류가 발생했습니다.';
      alert('테스트 케이스 상태 변경 중 오류가 발생했습니다: ' + errorMessage);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.get(`${config.apiUrl}/testcases/download`, {
        responseType: 'blob',
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `testcases_${new Date().toISOString().slice(0, 10)}.xlsx`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('파일 다운로드 중 오류가 발생했습니다: ' + err.message);
    }
  };

  const executeAutomationCode = async (testCaseId) => {
    try {
      const response = await axios.post(`/testcases/${testCaseId}/execute`);
      alert(`자동화 코드 실행 완료: ${response.data.result}`);
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('자동화 코드 실행 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  // 체크박스 관련 함수들
  const handleSelectTestCase = (testCaseId) => {
    setSelectedTestCases(prev => 
      prev.includes(testCaseId) 
        ? prev.filter(id => id !== testCaseId)
        : [...prev, testCaseId]
    );
  };

  const handleSelectAll = () => {
    if (selectedTestCases.length === testCases.length) {
      setSelectedTestCases([]);
    } else {
      setSelectedTestCases(testCases.map(tc => tc.id));
    }
  };

  const handleMoveToFolder = async () => {
    if (!targetFolderId) {
      alert('대상 폴더를 선택해주세요.');
      return;
    }

    if (selectedTestCases.length === 0) {
      alert('이동할 테스트 케이스를 선택해주세요.');
      return;
    }

    try {
      console.log('🔄 폴더 이동 시도:', { selectedTestCases, targetFolderId });
      
      // 선택된 테스트 케이스들을 대상 폴더로 이동
      await Promise.all(
        selectedTestCases.map(testCaseId =>
          axios.put(`${config.apiUrl}/testcases/${testCaseId}`, {
            folder_id: targetFolderId
          })
        )
      );

      alert(`${selectedTestCases.length}개의 테스트 케이스가 성공적으로 이동되었습니다.`);
      setShowMoveModal(false);
      setSelectedTestCases([]);
      setTargetFolderId('');
      fetchData(); // 데이터 새로고침
    } catch (err) {
      console.error('❌ 폴더 이동 실패:', err);
      const errorMessage = err.response?.data?.error || err.message || '알 수 없는 오류가 발생했습니다.';
      alert('폴더 이동 중 오류가 발생했습니다: ' + errorMessage);
    }
  };

  // 아코디언 토글 함수
  const toggleFolder = (folderId) => {
    setExpandedFolders(prev => {
      const newSet = new Set(prev);
      if (newSet.has(folderId)) {
        newSet.delete(folderId);
      } else {
        newSet.add(folderId);
      }
      return newSet;
    });
  };

  // 테스트 케이스 상세 토글 함수
  const toggleTestCaseDetails = (testCaseId) => {
    setExpandedTestCases(prev => {
      const newSet = new Set(prev);
      if (newSet.has(testCaseId)) {
        newSet.delete(testCaseId);
      } else {
        newSet.add(testCaseId);
      }
      return newSet;
    });
  };

  // 폴더 트리에서 특정 ID의 폴더 정보 찾기
  const findFolderInTree = (nodes, folderId) => {
    for (const node of nodes) {
      if (node.id === folderId) {
        return node;
      }
      if (node.children) {
        const found = findFolderInTree(node.children, folderId);
        if (found) return found;
      }
    }
    return null;
  };

  // 환경 폴더의 모든 하위 폴더 ID들 가져오기
  const getEnvironmentFolderIds = (nodes, environmentFolderId) => {
    const environmentNode = findFolderInTree(nodes, environmentFolderId);
    
    if (!environmentNode || environmentNode.type !== 'environment') {
      return [];
    }
    
    const folderIds = [];
    if (environmentNode.children) {
      for (const child of environmentNode.children) {
        if (child.type === 'deployment_date') {
          folderIds.push(child.id);
          
          // 배포일자 폴더의 하위 기능명 폴더들도 추가
          if (child.children) {
            for (const featureChild of child.children) {
              if (featureChild.type === 'feature') {
                folderIds.push(featureChild.id);
              }
            }
          }
        }
      }
    }
    return folderIds;
  };

  // 배포일자 폴더의 모든 하위 폴더 ID들 가져오기
  const getDeploymentFolderIds = (nodes, deploymentFolderId) => {
    const deploymentNode = findFolderInTree(nodes, deploymentFolderId);
    
    if (!deploymentNode || deploymentNode.type !== 'deployment_date') {
      return [];
    }
    
    const folderIds = [deploymentNode.id]; // 배포일자 폴더 자체도 포함
    if (deploymentNode.children) {
      for (const child of deploymentNode.children) {
        if (child.type === 'feature') {
          folderIds.push(child.id);
        }
      }
    }
    return folderIds;
  };

  // 폴더 타입을 판단하는 함수 (백엔드에서 제공하는 type 사용)
  const getFolderType = (folderId) => {
    const folder = findFolderInTree(folderTree, folderId);
    if (!folder) return 'unknown';
    
    // 백엔드에서 제공하는 type 필드 사용
    return folder.type || 'unknown';
  };

  // 고급 검색을 위한 헬퍼 함수들
  const getUniqueEnvironments = () => {
    const uniqueEnvs = new Set();
    testCases.forEach(tc => {
      if (tc.environment) {
        uniqueEnvs.add(tc.environment);
      }
    });
    return Array.from(uniqueEnvs).sort();
  };

  const getUniqueCategories = () => {
    const uniqueCategories = new Set();
    testCases.forEach(tc => {
      if (tc.main_category) uniqueCategories.add(tc.main_category);
      if (tc.sub_category) uniqueCategories.add(`${tc.main_category} > ${tc.sub_category}`);
      if (tc.detail_category) uniqueCategories.add(`${tc.main_category} > ${tc.sub_category} > ${tc.detail_category}`);
    });
    return Array.from(uniqueCategories).sort();
  };

  const getUniqueCreators = () => {
    const uniqueCreators = new Set();
    testCases.forEach(tc => {
      if (tc.creator_name) {
        uniqueCreators.add(tc.creator_name);
      }
    });
    return Array.from(uniqueCreators).sort();
  };

  const getUniqueAssignees = () => {
    const uniqueAssignees = new Set();
    testCases.forEach(tc => {
      if (tc.assignee_name) {
        uniqueAssignees.add(tc.assignee_name);
      }
    });
    return Array.from(uniqueAssignees).sort();
  };

  const clearAllFilters = () => {
    setSearchTerm('');
    setStatusFilter('all');
    setEnvironmentFilter('all');
    setCategoryFilter('all');
    setCreatorFilter('all');
    setAssigneeFilter('all');
    setSortBy('name');
    setSortOrder('asc');
  };

  // 고급 검색 기능
  const getFilteredTestCases = () => {
    let filtered = selectedFolder 
      ? testCases.filter(tc => {
          const tcFolderId = Number(tc.folder_id);
          const selectedFolderId = Number(selectedFolder);
          
          // 선택된 폴더 정보 찾기
          const selectedFolderInfo = findFolderInTree(folderTree, selectedFolderId);
          const selectedFolderType = getFolderType(selectedFolderId);
          
          if (selectedFolderType === 'environment') {
            // 환경 폴더 선택 시: 해당 환경의 모든 하위 폴더의 테스트 케이스들
            const environmentFolderIds = getEnvironmentFolderIds(folderTree, selectedFolderId);
            return environmentFolderIds.includes(tcFolderId);
          } else if (selectedFolderType === 'deployment_date') {
            // 날짜 폴더 선택 시: 해당 날짜의 모든 하위 폴더의 테스트 케이스들
            const deploymentFolderIds = getDeploymentFolderIds(folderTree, selectedFolderId);
            return deploymentFolderIds.includes(tcFolderId);
          } else if (selectedFolderType === 'feature') {
            // 기능 폴더 선택 시: 해당 폴더의 테스트 케이스들만
            return tcFolderId === selectedFolderId;
          } else {
            // 알 수 없는 폴더 타입: 전체 테스트 케이스 표시
            return true;
          }
        })
      : testCases;

    // 검색어가 있으면 검색 필터링 적용
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(tc => 
        (tc.main_category && tc.main_category.toLowerCase().includes(searchLower)) ||
        (tc.sub_category && tc.sub_category.toLowerCase().includes(searchLower)) ||
        (tc.detail_category && tc.detail_category.toLowerCase().includes(searchLower)) ||
        (tc.expected_result && tc.expected_result.toLowerCase().includes(searchLower)) ||
        (tc.remark && tc.remark.toLowerCase().includes(searchLower)) ||
        (tc.creator_name && tc.creator_name.toLowerCase().includes(searchLower)) ||
        (tc.assignee_name && tc.assignee_name.toLowerCase().includes(searchLower))
      );
    }

    // 상태 필터 적용
    if (statusFilter !== 'all') {
      filtered = filtered.filter(tc => tc.result_status === statusFilter);
    }

    // 환경 필터 적용
    if (environmentFilter !== 'all') {
      filtered = filtered.filter(tc => tc.environment === environmentFilter);
    }

    // 카테고리 필터 적용
    if (categoryFilter !== 'all') {
      const categoryParts = categoryFilter.split(' > ');
      if (categoryParts.length === 1) {
        filtered = filtered.filter(tc => tc.main_category === categoryParts[0]);
      } else if (categoryParts.length === 2) {
        filtered = filtered.filter(tc => tc.main_category === categoryParts[0] && tc.sub_category === categoryParts[1]);
      } else if (categoryParts.length === 3) {
        filtered = filtered.filter(tc => tc.main_category === categoryParts[0] && tc.sub_category === categoryParts[1] && tc.detail_category === categoryParts[2]);
      }
    }

    // 작성자 필터 적용
    if (creatorFilter !== 'all') {
      filtered = filtered.filter(tc => tc.creator_name === creatorFilter);
    }

    // 담당자 필터 적용
    if (assigneeFilter !== 'all') {
      filtered = filtered.filter(tc => tc.assignee_name === assigneeFilter);
    }

    // 정렬 적용
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'name':
          comparison = (a.main_category || '').localeCompare(b.main_category || '');
          break;
        case 'created_at':
          comparison = new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime();
          break;
        case 'updated_at':
          comparison = new Date(a.updated_at || 0).getTime() - new Date(b.updated_at || 0).getTime();
          break;
        case 'environment':
          comparison = (a.environment || '').localeCompare(b.environment || '');
          break;
        case 'status':
          comparison = (a.result_status || '').localeCompare(b.result_status || '');
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  };

  const renderFolderTree = (nodes, level = 0) => {
    return nodes.map(node => {
      const hasChildren = node.children && node.children.length > 0;
      const isExpanded = expandedFolders.has(node.id);
      const isFolder = node.type === 'environment' || node.type === 'deployment_date' || node.type === 'feature';
      
      console.log(`렌더링 노드: ID=${node.id}, Name=${node.name}, Type=${node.type}, Level=${level}`);
      
      return (
        <div key={node.id} style={{ marginLeft: level * 20 }}>
          <div 
            className={`folder-item ${selectedFolder === node.id && isFolder ? 'selected' : ''} ${isFolder ? 'clickable' : ''}`}
            onClick={() => {
              if (isFolder) {
                const folderType = getFolderType(node.id);
                console.log(`클릭된 폴더: ID=${node.id}, Name=${node.name}, Type=${folderType}`);
                console.log('폴더 타입 상세:', {
                  id: node.id,
                  name: node.name,
                  parent_id: node.parent_folder_id,
                  calculated_type: folderType
                });
                handleFolderSelect(node.id);
              }
            }}
          >
            {hasChildren && (
              <span 
                className={`folder-toggle ${isExpanded ? 'expanded' : ''}`}
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFolder(node.id);
                }}
              >
                {isExpanded ? '▼' : '▶'}
              </span>
            )}
            <span className="folder-icon">
              {getFolderType(node.id) === 'environment' ? '🌍' : 
               getFolderType(node.id) === 'deployment_date' ? '📅' : 
               getFolderType(node.id) === 'feature' ? '🔧' : '📄'}
            </span>
            <span className="folder-name">{node.name}</span>
            {getFolderType(node.id) === 'test_case' && (
              <span className={`test-status ${(node.status || 'N/A').toLowerCase().replace('/', '-')}`}>
                {node.status || 'N/A'}
              </span>
            )}
            {isFolder && (
              <span className="folder-type-badge">
                {getFolderType(node.id) === 'environment' ? '환경' : 
                 getFolderType(node.id) === 'deployment_date' ? '배포일자' : 
                 getFolderType(node.id) === 'feature' ? '기능명' : ''}
              </span>
            )}
          </div>
          {hasChildren && (
            <div className={`folder-children ${isExpanded ? 'expanded' : 'collapsed'}`}>
              {isExpanded && renderFolderTree(node.children, level + 1)}
            </div>
          )}
        </div>
      );
    });
  };

  const filteredTestCases = getFilteredTestCases();

  // 필터링 완료

  if (loading) {
    return <div className="testcase-loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="testcase-error">{error}</div>;
  }

  return (
    <div className="testcase-container">
      <div className="testcase-header">
        <h1>테스트 케이스 관리</h1>
        <div className="header-actions">
          {user && (user.role === 'admin' || user.role === 'user') && (
            <button 
              className="btn btn-add"
              onClick={() => setShowAddModal(true)}
            >
              ➕ 테스트 케이스 추가
            </button>
          )}
          {user && (user.role === 'admin' || user.role === 'user') && (
            <button 
              className="btn btn-upload"
              onClick={() => setShowUploadModal(true)}
            >
              📤 엑셀 업로드
            </button>
          )}
          <button 
            className="btn btn-download"
            onClick={handleDownload}
          >
            📥 엑셀 다운로드
          </button>
          {user && (user.role === 'admin' || user.role === 'user') && selectedTestCases.length > 0 && (
            <button 
              className="btn btn-execute"
              onClick={() => setShowMoveModal(true)}
            >
              📁 폴더 이동 ({selectedTestCases.length})
            </button>
          )}
        </div>
      </div>

      {/* 고급 검색 기능 */}
      <div className="search-section">
        <div className="search-container">
          {/* 기본 검색 */}
          <div className="search-input-wrapper">
            <input
              type="text"
              placeholder="🔍 테스트 케이스 검색... (대분류, 중분류, 소분류, 기대결과, 비고, 작성자, 담당자)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            {searchTerm && (
              <button 
                className="btn btn-clear-search"
                onClick={() => setSearchTerm('')}
                title="검색어 지우기"
              >
                ✕
              </button>
            )}
          </div>

          {/* 고급 필터 */}
          <div className="advanced-filters">
            <div className="filter-row">
              <div className="filter-group">
                <label>상태:</label>
                <select
                  value={statusFilter}
                  onChange={(e) => setStatusFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">모든 상태</option>
                  <option value="Pass">Pass</option>
                  <option value="Fail">Fail</option>
                  <option value="N/T">N/T</option>
                  <option value="N/A">N/A</option>
                  <option value="Block">Block</option>
                </select>
              </div>

              <div className="filter-group">
                <label>환경:</label>
                <select
                  value={environmentFilter}
                  onChange={(e) => setEnvironmentFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">모든 환경</option>
                  {getUniqueEnvironments().map(env => (
                    <option key={env} value={env}>{env}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>카테고리:</label>
                <select
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">모든 카테고리</option>
                  {getUniqueCategories().map(cat => (
                    <option key={cat} value={cat}>{cat}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>작성자:</label>
                <select
                  value={creatorFilter}
                  onChange={(e) => setCreatorFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">모든 작성자</option>
                  {getUniqueCreators().map(creator => (
                    <option key={creator} value={creator}>{creator}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>담당자:</label>
                <select
                  value={assigneeFilter}
                  onChange={(e) => setAssigneeFilter(e.target.value)}
                  className="filter-select"
                >
                  <option value="all">모든 담당자</option>
                  {getUniqueAssignees().map(assignee => (
                    <option key={assignee} value={assignee}>{assignee}</option>
                  ))}
                </select>
              </div>

              <div className="filter-group">
                <label>정렬:</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value)}
                  className="filter-select"
                >
                  <option value="name">이름순</option>
                  <option value="created_at">생성일순</option>
                  <option value="updated_at">수정일순</option>
                  <option value="environment">환경순</option>
                  <option value="status">상태순</option>
                </select>
              </div>

              <button
                onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                className="btn btn-sort"
                title={sortOrder === 'asc' ? '오름차순' : '내림차순'}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>

              <button
                onClick={clearAllFilters}
                className="btn btn-clear-filters"
                title="모든 필터 초기화"
              >
                🗑️ 초기화
              </button>
            </div>
          </div>

          {/* 검색 결과 요약 */}
          <div className="search-summary">
            <span>총 {getFilteredTestCases().length}개 테스트 케이스</span>
            {searchTerm && <span> • 검색어: "{searchTerm}"</span>}
            {statusFilter !== 'all' && <span> • 상태: {statusFilter}</span>}
            {environmentFilter !== 'all' && <span> • 환경: {environmentFilter}</span>}
            {categoryFilter !== 'all' && <span> • 카테고리: {categoryFilter}</span>}
            {creatorFilter !== 'all' && <span> • 작성자: {creatorFilter}</span>}
            {assigneeFilter !== 'all' && <span> • 담당자: {assigneeFilter}</span>}
          </div>
        </div>
      </div>

      <div className="testcase-content">
        {/* 폴더 트리 */}
        <div className="folder-tree">
          <h3>폴더 구조</h3>
          <div className="folder-controls">
            {selectedFolder && (
              <button 
                className="btn btn-secondary"
                onClick={() => setSelectedFolder(null)}
                style={{ fontSize: '0.8em', padding: '4px 8px' }}
              >
                전체 보기
              </button>
            )}
          </div>
          <div className="tree-container">
            {renderFolderTree(folderTree)}
          </div>
        </div>

        {/* 테스트 케이스 목록 */}
        <div className="testcase-list">
          <div className="testcase-list-header">
            <div className="header-checkbox">
              <label className="select-all-checkbox">
                <input 
                  type="checkbox"
                  checked={selectedTestCases.length === filteredTestCases.length && filteredTestCases.length > 0}
                  onChange={handleSelectAll}
                />
                전체 선택
              </label>
            </div>
            <h3>
              테스트 케이스 ({filteredTestCases.length})
              {selectedFolder && (
                <span className="folder-filter-info">
                  - {findFolderInTree(folderTree, selectedFolder)?.type === 'environment' ? '환경' : 
                     findFolderInTree(folderTree, selectedFolder)?.type === 'deployment_date' ? '배포일자' : 
                     findFolderInTree(folderTree, selectedFolder)?.type === 'feature' ? '기능명' : ''} 필터링됨
                </span>
              )}
            </h3>
            <div className="selection-controls">
              {selectedTestCases.length > 0 && (
                <span className="selected-count">
                  {selectedTestCases.length}개 선택됨
                </span>
              )}
            </div>
          </div>

          <div className="testcase-list">
            {filteredTestCases.map(testCase => (
              <div key={testCase.id} className="testcase-list-item">
                <div className="testcase-header">
                  <div className="testcase-checkbox">
                    <input 
                      type="checkbox"
                      checked={selectedTestCases.includes(testCase.id)}
                      onChange={() => handleSelectTestCase(testCase.id)}
                    />
                  </div>
                  <div className="testcase-info">
                    <h4>
                      {testCase.main_category && testCase.sub_category && testCase.detail_category 
                        ? `${testCase.main_category} > ${testCase.sub_category} > ${testCase.detail_category}`
                        : testCase.expected_result || '제목 없음'
                      }
                    </h4>
                    <div className="testcase-meta">
                      <span className="environment-badge">{testCase.environment || 'dev'}</span>
                      {testCase.automation_code_path && (
                        <span className="automation-badge">🤖 자동화</span>
                      )}
                    </div>
                  </div>
                  <div className="status-section">
                    <span className={`status-badge ${(testCase.result_status || 'N/A').toLowerCase().replace('/', '-')}`}>
                      {testCase.result_status || 'N/A'}
                    </span>
                    <select
                      className="status-select"
                      value={testCase.result_status}
                      onChange={(e) => handleStatusChange(testCase.id, e.target.value)}
                    >
                      <option value="N/T">N/T</option>
                      <option value="Pass">Pass</option>
                      <option value="Fail">Fail</option>
                      <option value="N/A">N/A</option>
                      <option value="Block">Block</option>
                    </select>
                  </div>
                  {/* 자동화 실행 버튼 */}
                  {testCase.automation_code_path && (
                    <button 
                      className="btn btn-automation"
                      onClick={() => executeAutomationCode(testCase.id)}
                      title="자동화 실행"
                    >
                      🤖
                    </button>
                  )}
                  {/* 아코디언 버튼 */}
                  <button 
                    className="btn btn-details btn-icon"
                    onClick={() => toggleTestCaseDetails(testCase.id)}
                    title="상세보기"
                  >
                    {expandedTestCases.has(testCase.id) ? '📋' : '📄'}
                  </button>
                  {user && (user.role === 'admin' || user.role === 'user') && (
                    <button 
                      className="btn btn-edit-icon btn-icon"
                      onClick={() => {
                        setEditingTestCase(testCase);
                        setShowEditModal(true);
                      }}
                      title="수정"
                    >
                      ✏️
                    </button>
                  )}
                  {user && user.role === 'admin' && (
                    <button 
                      className="btn btn-delete-icon btn-icon"
                      onClick={() => handleDeleteTestCase(testCase.id)}
                      title="삭제"
                    >
                      ✕
                    </button>
                  )}
                </div>
                {expandedTestCases.has(testCase.id) && (
                  <div className="testcase-details expanded">
                    <div className="testcase-info-table">
                      <h5>📋 테스트 케이스 상세 정보</h5>
                      <table className="info-table">
                        <tbody>
                          <tr>
                            <th>대분류</th>
                            <td>{testCase.main_category || '없음'}</td>
                            <th>중분류</th>
                            <td>{testCase.sub_category || '없음'}</td>
                          </tr>
                          <tr>
                            <th>소분류</th>
                            <td>{testCase.detail_category || '없음'}</td>
                            <th>환경</th>
                            <td>
                              <span className={`environment-badge ${testCase.environment || 'dev'}`}>
                                {testCase.environment || 'dev'}
                              </span>
                            </td>
                          </tr>
                          <tr>
                            <th>테스트 타입</th>
                            <td>{testCase.test_type || '없음'}</td>
                            <th>자동화</th>
                            <td>
                              {testCase.automation_code_path ? (
                                <span className="automation-badge">🤖 자동화</span>
                              ) : (
                                <span className="manual-badge">📝 수동</span>
                              )}
                            </td>
                          </tr>
                          <tr>
                            <th>작성자</th>
                            <td>
                              <span className="creator-badge">
                                👤 {testCase.creator_name || '없음'}
                              </span>
                            </td>
                            <th>담당자</th>
                            <td>
                              <span className="assignee-badge">
                                👤 {testCase.assignee_name || '없음'}
                              </span>
                            </td>
                          </tr>
                          <tr>
                            <th>스크립트 경로</th>
                            <td colSpan="3" className="script-path">
                              {testCase.script_path || '없음'}
                            </td>
                          </tr>
                          <tr>
                            <th>사전조건</th>
                            <td colSpan="3" className="pre-condition">
                              {testCase.pre_condition || '없음'}
                            </td>
                          </tr>
                          <tr>
                            <th>기대결과</th>
                            <td colSpan="3" className="expected-result">
                              {testCase.expected_result || '없음'}
                            </td>
                          </tr>
                          <tr>
                            <th>비고</th>
                            <td colSpan="3" className="remark">
                              {testCase.remark || '없음'}
                            </td>
                          </tr>
                          {testCase.automation_code_path && (
                            <tr>
                              <th>자동화 코드</th>
                              <td colSpan="3" className="automation-code">
                                <code>{testCase.automation_code_path}</code>
                              </td>
                            </tr>
                          )}
                          <tr>
                            <th>생성일</th>
                            <td>{testCase.created_at ? formatUTCToKST(testCase.created_at) : '없음'}</td>
                            <th>수정일</th>
                            <td>{testCase.updated_at ? formatUTCToKST(testCase.updated_at) : '없음'}</td>
                          </tr>
                        </tbody>
                      </table>
                    </div>
                    
                    {/* 스크린샷 영역 */}
                    <div className="testcase-screenshots">
                      <h5>📸 실행 결과 스크린샷</h5>
                      <TestCaseScreenshots testCaseId={testCase.id} />
                    </div>
                    
                    {/* 자동화 실행 결과 */}
                    <div className="testcase-execution-results">
                      <h5>🤖 자동화 실행 결과</h5>
                      <TestCaseExecutionResults testCaseId={testCase.id} />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 테스트 케이스 추가 모달 */}
      {showAddModal && (
        <div 
          className="modal-overlay fullscreen-modal"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 2000,
            padding: '20px',
            width: '100vw',
            height: '100vh'
          }}
        >
          <div 
            className="modal fullscreen-modal-content"
            style={{
              width: '100%',
              maxWidth: '800px',
              maxHeight: '90vh',
              background: 'white',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              minWidth: 'auto',
              padding: 0,
              margin: 0,
              position: 'relative',
              top: 'auto',
              left: 'auto',
              right: 'auto',
              bottom: 'auto'
            }}
          >
            <div className="modal-header">
              <h3>새 테스트 케이스 추가</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowAddModal(false);
                  setNewTestCase({
                    main_category: '',
                    sub_category: '',
                    detail_category: '',
                    pre_condition: '',
                    expected_result: '',
                    result_status: 'N/T',
                    remark: '',
                    folder_id: null,
                    automation_code_path: '',
                    automation_code_type: 'playwright',
                    assignee_id: null
                  });
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>대분류</label>
                <input 
                  type="text" 
                  value={newTestCase.main_category}
                  onChange={(e) => setNewTestCase({...newTestCase, main_category: e.target.value})}
                  placeholder="대분류를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>중분류</label>
                <input 
                  type="text" 
                  value={newTestCase.sub_category}
                  onChange={(e) => setNewTestCase({...newTestCase, sub_category: e.target.value})}
                  placeholder="중분류를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>소분류</label>
                <input 
                  type="text" 
                  value={newTestCase.detail_category}
                  onChange={(e) => setNewTestCase({...newTestCase, detail_category: e.target.value})}
                  placeholder="소분류를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>사전조건</label>
                <textarea 
                  value={newTestCase.pre_condition}
                  onChange={(e) => setNewTestCase({...newTestCase, pre_condition: e.target.value})}
                  placeholder="사전조건을 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>기대결과</label>
                <textarea 
                  value={newTestCase.expected_result}
                  onChange={(e) => setNewTestCase({...newTestCase, expected_result: e.target.value})}
                  placeholder="기대결과를 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>결과 상태</label>
                <select 
                  value={newTestCase.result_status}
                  onChange={(e) => setNewTestCase({...newTestCase, result_status: e.target.value})}
                >
                  <option value="N/T">N/T (Not Tested)</option>
                  <option value="Pass">Pass</option>
                  <option value="Fail">Fail</option>
                  <option value="N/A">N/A</option>
                  <option value="Block">Block</option>
                </select>
              </div>
              <div className="form-group">
                <label>비고</label>
                <textarea 
                  value={newTestCase.remark}
                  onChange={(e) => setNewTestCase({...newTestCase, remark: e.target.value})}
                  placeholder="비고를 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>자동화 코드 경로</label>
                <input 
                  type="text" 
                  value={newTestCase.automation_code_path || ''}
                  onChange={(e) => setNewTestCase({...newTestCase, automation_code_path: e.target.value})}
                  placeholder="자동화 코드 파일 경로를 입력하세요 (예: test-scripts/playwright/login.spec.js)"
                />
              </div>
              <div className="form-group">
                <label>자동화 코드 타입</label>
                <select 
                  value={newTestCase.automation_code_type || 'playwright'}
                  onChange={(e) => setNewTestCase({...newTestCase, automation_code_type: e.target.value})}
                >
                  <option value="playwright">Playwright</option>
                  <option value="selenium">Selenium</option>
                  <option value="k6">k6 (성능 테스트)</option>
                </select>
              </div>
              <div className="form-group">
                <label>담당자</label>
                <select 
                  value={newTestCase.assignee_id || ''}
                  onChange={(e) => setNewTestCase({...newTestCase, assignee_id: e.target.value ? Number(e.target.value) : null})}
                >
                  <option value="">담당자를 선택하세요</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>
                      {user.username || user.first_name || user.email}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleAddTestCase}
              >
                추가
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowAddModal(false);
                  setNewTestCase({
                    main_category: '',
                    sub_category: '',
                    detail_category: '',
                    pre_condition: '',
                    expected_result: '',
                    result_status: 'N/T',
                    remark: '',
                    folder_id: null,
                    automation_code_path: '',
                    automation_code_type: 'playwright',
                    assignee_id: null
                  });
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 테스트 케이스 편집 모달 */}
      {showEditModal && editingTestCase && (
        <div 
          className="modal-overlay fullscreen-modal"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 2000,
            padding: '20px',
            width: '100vw',
            height: '100vh'
          }}
        >
          <div 
            className="modal fullscreen-modal-content"
            style={{
              width: '100%',
              maxWidth: '800px',
              maxHeight: '90vh',
              background: 'white',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              minWidth: 'auto',
              padding: 0,
              margin: 0,
              position: 'relative',
              top: 'auto',
              left: 'auto',
              right: 'auto',
              bottom: 'auto'
            }}
          >
            <div className="modal-header">
              <h3>테스트 케이스 편집</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingTestCase(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>대분류</label>
                <input 
                  type="text" 
                  value={editingTestCase.main_category}
                  onChange={(e) => setEditingTestCase({...editingTestCase, main_category: e.target.value})}
                  placeholder="대분류를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>중분류</label>
                <input 
                  type="text" 
                  value={editingTestCase.sub_category}
                  onChange={(e) => setEditingTestCase({...editingTestCase, sub_category: e.target.value})}
                  placeholder="중분류를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>소분류</label>
                <input 
                  type="text" 
                  value={editingTestCase.detail_category}
                  onChange={(e) => setEditingTestCase({...editingTestCase, detail_category: e.target.value})}
                  placeholder="소분류를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>사전조건</label>
                <textarea 
                  value={editingTestCase.pre_condition}
                  onChange={(e) => setEditingTestCase({...editingTestCase, pre_condition: e.target.value})}
                  placeholder="사전조건을 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>기대결과</label>
                <textarea 
                  value={editingTestCase.expected_result}
                  onChange={(e) => setEditingTestCase({...editingTestCase, expected_result: e.target.value})}
                  placeholder="기대결과를 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>결과 상태</label>
                <select 
                  value={editingTestCase.result_status}
                  onChange={(e) => setEditingTestCase({...editingTestCase, result_status: e.target.value})}
                >
                  <option value="N/T">N/T (Not Tested)</option>
                  <option value="Pass">Pass</option>
                  <option value="Fail">Fail</option>
                  <option value="Skip">Skip</option>
                </select>
              </div>
              <div className="form-group">
                <label>비고</label>
                <textarea 
                  value={editingTestCase.remark}
                  onChange={(e) => setEditingTestCase({...editingTestCase, remark: e.target.value})}
                  placeholder="비고를 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>자동화 코드 경로</label>
                <input 
                  type="text" 
                  value={editingTestCase.automation_code_path || ''}
                  onChange={(e) => setEditingTestCase({...editingTestCase, automation_code_path: e.target.value})}
                  placeholder="자동화 코드 파일 경로를 입력하세요 (예: test-scripts/playwright/login.spec.js)"
                />
              </div>
              <div className="form-group">
                <label>자동화 코드 타입</label>
                <select 
                  value={editingTestCase.automation_code_type || 'playwright'}
                  onChange={(e) => setEditingTestCase({...editingTestCase, automation_code_type: e.target.value})}
                >
                  <option value="playwright">Playwright</option>
                  <option value="selenium">Selenium</option>
                  <option value="k6">k6 (성능 테스트)</option>
                </select>
              </div>
              <div className="form-group">
                <label>담당자</label>
                <select 
                  value={editingTestCase.assignee_id || ''}
                  onChange={(e) => setEditingTestCase({...editingTestCase, assignee_id: e.target.value ? Number(e.target.value) : null})}
                >
                  <option value="">담당자를 선택하세요</option>
                  {users.map(user => (
                    <option key={user.id} value={user.id}>
                      {user.username || user.first_name || user.email}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleEditTestCase}
              >
                수정
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingTestCase(null);
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 폴더 이동 모달 */}
      {showMoveModal && (
        <div 
          className="modal-overlay fullscreen-modal"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 2000,
            padding: '20px',
            width: '100vw',
            height: '100vh'
          }}
        >
          <div 
            className="modal fullscreen-modal-content"
            style={{
              width: '100%',
              maxWidth: '800px',
              maxHeight: '90vh',
              background: 'white',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              minWidth: 'auto',
              padding: 0,
              margin: 0,
              position: 'relative',
              top: 'auto',
              left: 'auto',
              right: 'auto',
              bottom: 'auto'
            }}
          >
            <div className="modal-header">
              <h3>폴더 이동</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowMoveModal(false);
                  setTargetFolderId('');
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <p>선택된 {selectedTestCases.length}개의 테스트 케이스를 이동할 폴더를 선택하세요.</p>
              <div className="form-group">
                <label>대상 폴더</label>
                <select 
                  value={targetFolderId}
                  onChange={(e) => setTargetFolderId(e.target.value)}
                >
                  <option value="">폴더를 선택하세요</option>
                  {allFolders.map(folder => (
                    <option key={folder.id} value={folder.id}>
                      {folder.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleMoveToFolder}
              >
                이동
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowMoveModal(false);
                  setTargetFolderId('');
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 업로드 모달 */}
      {showUploadModal && (
        <div 
          className="modal-overlay fullscreen-modal"
          style={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(0, 0, 0, 0.8)',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: 2000,
            padding: '20px',
            width: '100vw',
            height: '100vh'
          }}
        >
          <div 
            className="modal fullscreen-modal-content"
            style={{
              width: '100%',
              maxWidth: '800px',
              maxHeight: '90vh',
              background: 'white',
              borderRadius: '12px',
              boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)',
              display: 'flex',
              flexDirection: 'column',
              overflow: 'hidden',
              minWidth: 'auto',
              padding: 0,
              margin: 0,
              position: 'relative',
              top: 'auto',
              left: 'auto',
              right: 'auto',
              bottom: 'auto'
            }}
          >
            <div className="modal-header">
              <h3>엑셀 파일 업로드</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowUploadModal(false);
                  setSelectedFile(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>엑셀 파일 선택</label>
                <input 
                  type="file" 
                  accept=".xlsx"
                  onChange={(e) => setSelectedFile(e.target.files[0])}
                />
                <p className="help-text">지원 형식: .xlsx 파일</p>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleFileUpload}
              >
                업로드
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowUploadModal(false);
                  setSelectedFile(null);
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestCaseAPP;
