// src/PerformanceTestManager.js
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import config from '@tms/config';
import { useAuth } from '@tms/contexts/AuthContext';
import { formatUTCToKST } from '@tms/utils/dateUtils';
import './PerformanceTestManager.css';
import '../common/Modal.css';

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

// axios 기본 URL 설정
axios.defaults.baseURL = config.apiUrl;

const PerformanceTestManager = () => {
    const { user } = useAuth();
    const [performanceTests, setPerformanceTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTest, setEditingTest] = useState(null);
    const [newTest, setNewTest] = useState({
        name: '',
        description: '',
    script_path: '',
        environment: 'prod',
    parameters: {},
    assignee_id: null
  });
  
  // 사용자 목록 관련 상태
  const [users, setUsers] = useState([]);
  
  // 다중 선택 관련 상태
  const [selectedTests, setSelectedTests] = useState([]);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  
  // 상세보기 모달 관련 상태
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [selectedTest, setSelectedTest] = useState(null);
  
  // 검색 관련 상태
  const [searchTerm, setSearchTerm] = useState('');
  const [environmentFilter, setEnvironmentFilter] = useState('all');
  const [creatorFilter, setCreatorFilter] = useState('all');
  const [assigneeFilter, setAssigneeFilter] = useState('all');
  
  // 테이블 정렬 상태
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // 실행 중 상태
    const [executing, setExecuting] = useState(false);

    useEffect(() => {
    fetchData();
    fetchUsers(); // 사용자 목록도 함께 가져오기
    }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get(`${config.apiUrl}/performance-tests`);
      setPerformanceTests(response.data);
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 사용자 목록을 별도로 가져오는 함수
  const fetchUsers = async () => {
    try {
      console.log('🔍 사용자 목록 가져오기 시작...');
      const response = await axios.get(`${config.apiUrl}/users/list`);
      console.log('✅ 사용자 목록 로드 성공:', response.data);
      setUsers(response.data);
        } catch (error) {
      console.error('❌ 사용자 목록 로드 실패:', error);
      setUsers([]);
    }
  };

  const handleAddTest = async () => {
    if (!newTest.name || !newTest.script_path) {
      alert('테스트명과 스크립트 경로를 입력해주세요.');
            return;
        }

        try {
      await axios.post(`${config.apiUrl}/performance-tests`, newTest);
      alert('성능 테스트가 성공적으로 추가되었습니다.');
      setShowAddModal(false);
            setNewTest({
                name: '',
                description: '',
        script_path: '',
                environment: 'prod',
        parameters: {},
        assignee_id: null
      });
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('성능 테스트 추가 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message));
        }
    };

    const handleEditTest = async () => {
    if (!editingTest.name || !editingTest.script_path) {
            alert('테스트명과 스크립트 경로를 입력해주세요.');
            return;
        }

        try {
      await axios.put(`${config.apiUrl}/performance-tests/${editingTest.id}`, editingTest);
            alert('성능 테스트가 성공적으로 수정되었습니다.');
            setShowEditModal(false);
            setEditingTest(null);
      fetchData(); // 데이터 새로고침
        } catch (err) {
            alert('성능 테스트 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
        }
    };

  const handleDeleteTest = async (testId) => {
        if (!window.confirm('정말로 이 성능 테스트를 삭제하시겠습니까?')) {
            return;
        }
        
        try {
      await axios.delete(`${config.apiUrl}/performance-tests/${testId}`);
            alert('성능 테스트가 성공적으로 삭제되었습니다.');
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('성능 테스트 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  // 담당자 변경 함수
  const handleAssigneeChange = async (testId, newAssigneeId) => {
    try {
      console.log('담당자 변경 시도:', { testId, newAssigneeId, users });
      
      // 빈 값이면 담당자 제거
      if (!newAssigneeId || newAssigneeId === '') {
        const response = await axios.put(`${config.apiUrl}/performance-tests/${testId}`, {
          assignee_id: null
        });
        
        if (response.status === 200) {
          // 로컬 상태 업데이트 - 담당자 제거
          setPerformanceTests(prev => prev.map(test => {
            if (test.id === testId) {
              return { 
                ...test, 
                assignee_id: null,
                assignee_name: null
              };
            }
            return test;
          }));
          
          // 성공 메시지
          alert('담당자가 제거되었습니다.');
        }
        return;
      }

      // 새로운 담당자 설정
      const response = await axios.put(`${config.apiUrl}/performance-tests/${testId}`, {
        assignee_id: newAssigneeId
      });
      
      if (response.status === 200) {
        // 로컬 상태 업데이트
        setPerformanceTests(prev => prev.map(test => {
          if (test.id === testId) {
            const selectedUser = users.find(u => u.id === parseInt(newAssigneeId));
            console.log('선택된 사용자:', selectedUser);
            return { 
              ...test, 
              assignee_id: parseInt(newAssigneeId),
              assignee_name: selectedUser ? (selectedUser.username || selectedUser.name) : '없음'
            };
          }
          return test;
        }));
        
        // 성공 메시지
        alert('담당자가 성공적으로 변경되었습니다.');
      }
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || '알 수 없는 오류가 발생했습니다.';
      alert('담당자 변경 중 오류가 발생했습니다: ' + errorMessage);
        }
    };

    const executePerformanceTest = async (testId) => {
        setExecuting(true);
        try {
      const response = await axios.post(`${config.apiUrl}/performance-tests/${testId}/execute`, {
                environment_vars: {}
            });
            if (process.env.NODE_ENV === 'development') {
                console.log('테스트 실행 결과:', response.data);
            }
      alert('성능 테스트가 실행되었습니다.');
      fetchData();
        } catch (error) {
            console.error('성능 테스트 실행 오류:', error);
      alert('성능 테스트 실행 중 오류가 발생했습니다: ' + (error.response?.data?.error || error.message));
        } finally {
            setExecuting(false);
        }
    };

  // 체크박스 관련 함수들
  const handleSelectTest = (testId) => {
    setSelectedTests(prev => 
      prev.includes(testId) 
        ? prev.filter(id => id !== testId)
        : [...prev, testId]
    );
  };

  const handleSelectAll = () => {
    if (selectedTests.length === performanceTests.length) {
      setSelectedTests([]);
    } else {
      setSelectedTests(performanceTests.map(test => test.id));
    }
  };

  const handleMultiDelete = async () => {
    if (selectedTests.length === 0) {
      alert('삭제할 성능 테스트를 선택해주세요.');
      return;
    }

    try {
      console.log('🗑️ 다중 삭제 시도:', { selectedTests });
      
      // 다중 삭제 API 호출
      const response = await axios.post(`${config.apiUrl}/performance-tests/bulk-delete`, {
        test_ids: selectedTests
      });

      const { deleted_count, total_requested, failed_deletions, warning } = response.data;
      
      let message = `${deleted_count}개의 성능 테스트가 성공적으로 삭제되었습니다.`;
      if (warning) {
        message += `\n\n${warning}`;
      }
      if (failed_deletions && failed_deletions.length > 0) {
        message += `\n\n실패한 삭제:\n${failed_deletions.map(f => `- ID ${f.id}: ${f.error}`).join('\n')}`;
      }
      
      alert(message);
      setShowDeleteModal(false);
      setSelectedTests([]);
      fetchData(); // 데이터 새로고침
    } catch (err) {
      console.error('❌ 다중 삭제 실패:', err);
      const errorMessage = err.response?.data?.error || err.message || '알 수 없는 오류가 발생했습니다.';
      alert('다중 삭제 중 오류가 발생했습니다: ' + errorMessage);
    }
  };

  // 테이블 정렬 함수
  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
            } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  // 고급 검색을 위한 헬퍼 함수들
  const getUniqueEnvironments = () => {
    const uniqueEnvs = new Set();
    performanceTests.forEach(test => {
      if (test.environment) {
        uniqueEnvs.add(test.environment);
      }
    });
    return Array.from(uniqueEnvs).sort();
  };

  const getUniqueCreators = () => {
    const uniqueCreators = new Set();
    performanceTests.forEach(test => {
      if (test.creator_name) {
        uniqueCreators.add(test.creator_name);
      }
    });
    return Array.from(uniqueCreators).sort();
  };

  const getUniqueAssignees = () => {
    const uniqueAssignees = new Set();
    performanceTests.forEach(test => {
      if (test.assignee_name) {
        uniqueAssignees.add(test.assignee_name);
      }
    });
    return Array.from(uniqueAssignees).sort();
  };

  const clearAllFilters = () => {
    setSearchTerm('');
    setEnvironmentFilter('all');
    setCreatorFilter('all');
    setAssigneeFilter('all');
  };

  // 고급 검색 기능
  const getFilteredTests = () => {
    let filtered = performanceTests;

    // 검색어가 있으면 검색 필터링 적용
    if (searchTerm.trim()) {
      const searchLower = searchTerm.toLowerCase();
      filtered = filtered.filter(test => 
        (test.name && test.name.toLowerCase().includes(searchLower)) ||
        (test.description && test.description.toLowerCase().includes(searchLower)) ||
        (test.script_path && test.script_path.toLowerCase().includes(searchLower)) ||
        (test.creator_name && test.creator_name.toLowerCase().includes(searchLower)) ||
        (test.assignee_name && test.assignee_name.toLowerCase().includes(searchLower))
      );
    }

    // 환경 필터 적용
    if (environmentFilter !== 'all') {
      filtered = filtered.filter(test => test.environment === environmentFilter);
    }

    // 작성자 필터 적용
    if (creatorFilter !== 'all') {
      filtered = filtered.filter(test => test.creator_name === creatorFilter);
    }

    // 담당자 필터 적용
    if (assigneeFilter !== 'all') {
      filtered = filtered.filter(test => test.assignee_name === assigneeFilter);
    }

    // 정렬 적용
    filtered.sort((a, b) => {
      let comparison = 0;
      switch (sortBy) {
        case 'id':
          comparison = (a.id || 0) - (b.id || 0);
          break;
        case 'name':
          comparison = (a.name || '').localeCompare(b.name || '');
          break;
        case 'environment':
          comparison = (a.environment || '').localeCompare(b.environment || '');
          break;
        case 'assignee':
          comparison = (a.assignee_name || '').localeCompare(b.assignee_name || '');
          break;
        case 'creator':
          comparison = (a.creator_name || '').localeCompare(b.creator_name || '');
          break;
        case 'created_at':
          comparison = new Date(a.created_at || 0).getTime() - new Date(b.created_at || 0).getTime();
          break;
        case 'updated_at':
          comparison = new Date(a.updated_at || 0).getTime() - new Date(b.updated_at || 0).getTime();
          break;
      }
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  };

  const filteredTests = getFilteredTests();

  if (loading) {
    return <div className="performance-loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="performance-error">{error}</div>;
  }

    return (
    <div className="performance-container">
            <div className="performance-header">
        <h1>성능 테스트 관리</h1>
        {user && user.role === 'guest' && (
          <div className="guest-notice" style={{ 
            padding: '10px', 
            backgroundColor: '#fff3cd', 
            border: '1px solid #ffc107', 
            borderRadius: '4px',
            marginBottom: '10px',
            fontSize: '14px'
          }}>
            👀 게스트 모드: 조회만 가능합니다.
          </div>
        )}
        <div className="header-actions">
          {user && (user.role === 'admin' || user.role === 'user') && (
                    <button 
                        className="performance-btn performance-btn-add"
              onClick={() => setShowAddModal(true)}
            >
              ➕ 성능 테스트 추가
            </button>
          )}
          {user && user.role === 'admin' && selectedTests.length > 0 && (
            <button 
              className="btn btn-delete"
              onClick={() => setShowDeleteModal(true)}
            >
              🗑️ 다중 삭제 ({selectedTests.length})
                    </button>
                )}
        </div>
            </div>
            
      {/* 고급 검색 기능 */}
      <div className="performance-search-section">
        <div className="performance-search-container">
          {/* 기본 검색 */}
          <div className="performance-search-input-wrapper">
            <input 
              type="text" 
              placeholder="🔍 성능 테스트 검색... (테스트명, 설명, 스크립트 경로, 작성자, 담당자)"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="performance-search-input"
            />
            {searchTerm && (
              <button 
                className="performance-btn-clear-search"
                onClick={() => setSearchTerm('')}
                title="검색어 지우기"
              >
                ✕
              </button>
            )}
          </div>

          {/* 고급 필터 */}
          <div className="performance-advanced-filters">
            <div className="performance-filter-row">
              <div className="performance-filter-group">
                <label>환경:</label>
                <select
                  value={environmentFilter}
                  onChange={(e) => setEnvironmentFilter(e.target.value)}
                  className="performance-filter-select"
                >
                  <option value="all">모든 환경</option>
                  {getUniqueEnvironments().map(env => (
                    <option key={env} value={env}>{env}</option>
                  ))}
                </select>
                        </div>

              <div className="performance-filter-group">
                <label>작성자:</label>
                <select
                  value={creatorFilter}
                  onChange={(e) => setCreatorFilter(e.target.value)}
                  className="performance-filter-select"
                >
                  <option value="all">모든 작성자</option>
                  {getUniqueCreators().map(creator => (
                    <option key={creator} value={creator}>{creator}</option>
                  ))}
                </select>
                    </div>

              <div className="performance-filter-group">
                <label>담당자:</label>
                            <select 
                  value={assigneeFilter}
                  onChange={(e) => setAssigneeFilter(e.target.value)}
                  className="performance-filter-select"
                >
                  <option value="all">모든 담당자</option>
                  {getUniqueAssignees().map(assignee => (
                    <option key={assignee} value={assignee}>{assignee}</option>
                  ))}
                            </select>
                        </div>

                        <button 
                onClick={clearAllFilters}
                className="performance-btn performance-btn-clear-filters"
                title="모든 필터 초기화"
              >
                🗑️
                        </button>
                    </div>
                </div>

          {/* 검색 결과 요약 */}
          <div className="performance-search-summary">
            <span>총 {filteredTests.length}개 성능 테스트</span>
            {searchTerm && <span> • 검색어: "{searchTerm}"</span>}
            {environmentFilter !== 'all' && <span> • 환경: {environmentFilter}</span>}
            {creatorFilter !== 'all' && <span> • 작성자: {creatorFilter}</span>}
            {assigneeFilter !== 'all' && <span> • 담당자: {assigneeFilter}</span>}
          </div>
        </div>
      </div>

      {/* 성능 테스트 목록 */}
      <div className="performance-list">
        <div className="performance-list-header">
          <div className="header-checkbox">
          </div>
          <h3>
            성능 테스트 ({filteredTests.length})
          </h3>
          <div className="selection-controls">
            {selectedTests.length > 0 && (
              <span className="selected-count">
                {selectedTests.length}개 선택됨
              </span>
            )}
          </div>
        </div>

        {/* 테이블 형태로 변경 */}
        <div className="performance-table-container">
          <table className="performance-table">
            <thead>
              <tr>
                <th className="checkbox-column">
                  <input 
                    type="checkbox"
                    checked={selectedTests.length === filteredTests.length && filteredTests.length > 0}
                    onChange={handleSelectAll}
                  />
                </th>
                <th 
                  className="no-column sortable" 
                  onClick={() => handleSort('id')}
                  style={{ cursor: 'pointer' }}
                >
                  No {sortBy === 'id' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="name-column sortable" 
                  onClick={() => handleSort('name')}
                  style={{ cursor: 'pointer' }}
                >
                  테스트명 {sortBy === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="environment-column sortable" 
                  onClick={() => handleSort('environment')}
                  style={{ cursor: 'pointer' }}
                >
                  환경 {sortBy === 'environment' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="assignee-column sortable" 
                  onClick={() => handleSort('assignee')}
                  style={{ cursor: 'pointer' }}
                >
                  담당자 {sortBy === 'assignee' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th 
                  className="creator-column sortable" 
                  onClick={() => handleSort('creator')}
                  style={{ cursor: 'pointer' }}
                >
                  작성자 {sortBy === 'creator' && (sortOrder === 'asc' ? '↑' : '↓')}
                </th>
                <th className="actions-column">동작</th>
              </tr>
            </thead>
            <tbody>
              {filteredTests.map((test, index) => (
                <tr key={test.id} className="performance-table-row">
                  <td className="checkbox-column">
                    <input 
                      type="checkbox"
                      checked={selectedTests.includes(test.id)}
                      onChange={() => handleSelectTest(test.id)}
                    />
                  </td>
                  <td className="no-column">{index + 1}</td>
                  <td className="name-column">
                    <div className="test-summary">
                      <div className="test-title">
                        {test.name}
                      </div>
                            <div className="test-meta">
                        <span className="environment-badge">{test.environment || 'prod'}</span>
                        {test.script_path && (
                          <span className="script-badge">📄 {test.script_path.split('/').pop()}</span>
                        )}
                            </div>
                        </div>
                  </td>
                  <td className="environment-column">
                    <span className="environment-badge">{test.environment || 'prod'}</span>
                  </td>
                  <td className="assignee-column">
                    <div className="assignee-section">
                      <span className="assignee-badge">
                        👤 {test.assignee_name || '없음'}
                      </span>
                      <select
                        className="assignee-select"
                        value={test.assignee_id || ''}
                        onChange={(e) => handleAssigneeChange(test.id, e.target.value)}
                      >
                        <option value="">담당자 변경</option>
                        {users && users.length > 0 ? (
                          users.map(user => (
                            <option key={user.id} value={user.id}>
                              {user.username || user.name || 'Unknown'}
                            </option>
                          ))
                        ) : (
                          <option value="" disabled>사용자 목록 로딩 중...</option>
                        )}
                      </select>
                    </div>
                  </td>
                  <td className="creator-column">
                    <span className="creator-badge">
                      👤 {test.creator_name || '없음'}
                    </span>
                  </td>
                  <td className="actions-column">
                    <div className="action-buttons">
                      {/* 실행 버튼 */}
                                <button 
                        className="performance-btn performance-btn-automation performance-btn-icon"
                                    onClick={() => executePerformanceTest(test.id)}
                                    disabled={executing}
                        title="테스트 실행"
                                >
                                    {executing ? '⏳' : '▶️'}
                                </button>
                      {/* 상세보기 버튼 */}
                            <button 
                                className="performance-btn performance-btn-details performance-btn-icon"
                        onClick={() => {
                          setSelectedTest(test);
                          setShowDetailModal(true);
                        }}
                                title="상세보기"
                            >
                        📄
                            </button>
                      {/* 수정 버튼 */}
                            {user && (user.role === 'admin' || user.role === 'user') && (
                                <button 
                          className="performance-btn performance-btn-edit performance-btn-icon"
                                    onClick={() => {
                                        setEditingTest(test);
                                        setShowEditModal(true);
                                    }}
                                    title="수정"
                                >
                                    ✏️
                                </button>
                            )}
                      {/* 삭제 버튼 */}
                            {user && user.role === 'admin' && (
                                <button 
                                    className="performance-btn performance-btn-delete performance-btn-icon"
                          onClick={() => handleDeleteTest(test.id)}
                          title="삭제"
                                >
                                    ✕
                                </button>
                            )}
                        </div>
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>

      {/* 성능 테스트 추가 모달 */}
      {showAddModal && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>새 성능 테스트 추가</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowAddModal(false);
                  setNewTest({
                    name: '',
                    description: '',
                    script_path: '',
                    environment: 'prod',
                    parameters: {},
                    assignee_id: null
                  });
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>테스트명 *</label>
                <input 
                  type="text" 
                  value={newTest.name}
                  onChange={(e) => setNewTest({...newTest, name: e.target.value})}
                  placeholder="테스트명을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea 
                  value={newTest.description}
                  onChange={(e) => setNewTest({...newTest, description: e.target.value})}
                  placeholder="테스트 설명을 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>스크립트 경로 *</label>
                <input 
                  type="text" 
                  value={newTest.script_path}
                  onChange={(e) => setNewTest({...newTest, script_path: e.target.value})}
                  placeholder="k6 스크립트 파일 경로를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>환경</label>
                <select 
                  value={newTest.environment}
                  onChange={(e) => setNewTest({...newTest, environment: e.target.value})}
                >
                  <option value="prod">Production</option>
                  <option value="staging">Staging</option>
                  <option value="dev">Development</option>
                </select>
              </div>
              <div className="form-group">
                <label>매개변수 (JSON)</label>
                <textarea 
                  value={newTest.parameters ? JSON.stringify(newTest.parameters, null, 2) : ''}
                  onChange={(e) => {
                    try {
                      const params = e.target.value ? JSON.parse(e.target.value) : {};
                      setNewTest({...newTest, parameters: params});
                    } catch (err) {
                      // JSON 파싱 오류 무시
                    }
                  }}
                  placeholder='{"timeout": 30, "retries": 3}'
                  rows="5"
                />
                    </div>
              <div className="form-group">
                <label>담당자</label>
                <select 
                  value={newTest.assignee_id || ''}
                  onChange={(e) => setNewTest({...newTest, assignee_id: e.target.value ? Number(e.target.value) : null})}
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
                className="performance-btn performance-btn-primary"
                onClick={handleAddTest}
              >
                추가
              </button>
              <button 
                className="performance-btn performance-btn-secondary"
                onClick={() => {
                  setShowAddModal(false);
                  setNewTest({
                    name: '',
                    description: '',
                    script_path: '',
                    environment: 'prod',
                    parameters: {},
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
            
      {/* 성능 테스트 편집 모달 */}
            {showEditModal && editingTest && (
                <div className="modal-overlay fullscreen-modal">
                    <div className="modal fullscreen-modal-content">
                        <div className="modal-header">
              <h3>성능 테스트 편집</h3>
                            <button 
                                className="modal-close"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingTest(null);
                }}
                            >
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="form-group">
                                <label>테스트명 *</label>
                                <input
                                    type="text"
                                    value={editingTest.name}
                                    onChange={(e) => setEditingTest({...editingTest, name: e.target.value})}
                                    placeholder="테스트명을 입력하세요"
                                />
                            </div>
                            <div className="form-group">
                                <label>설명</label>
                                <textarea
                                    value={editingTest.description}
                                    onChange={(e) => setEditingTest({...editingTest, description: e.target.value})}
                                    placeholder="테스트 설명을 입력하세요"
                                    rows="3"
                                />
                            </div>
                            <div className="form-group">
                <label>스크립트 경로 *</label>
                                <input
                                    type="text"
                  value={editingTest.script_path}
                  onChange={(e) => setEditingTest({...editingTest, script_path: e.target.value})}
                                    placeholder="k6 스크립트 파일 경로를 입력하세요"
                                />
                            </div>
                            <div className="form-group">
                                <label>환경</label>
                                <select
                                    value={editingTest.environment}
                                    onChange={(e) => setEditingTest({...editingTest, environment: e.target.value})}
                                >
                                    <option value="prod">Production</option>
                                    <option value="staging">Staging</option>
                                    <option value="dev">Development</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>매개변수 (JSON)</label>
                                <textarea
                                    value={editingTest.parameters ? JSON.stringify(editingTest.parameters, null, 2) : ''}
                                    onChange={(e) => {
                                        try {
                                            const params = e.target.value ? JSON.parse(e.target.value) : {};
                                            setEditingTest({...editingTest, parameters: params});
                                        } catch (err) {
                                            // JSON 파싱 오류 무시
                                        }
                                    }}
                                    placeholder='{"timeout": 30, "retries": 3}'
                                    rows="5"
                                />
                            </div>
              <div className="form-group">
                <label>담당자</label>
                <select 
                  value={editingTest.assignee_id || ''}
                  onChange={(e) => setEditingTest({...editingTest, assignee_id: e.target.value ? Number(e.target.value) : null})}
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
                className="performance-btn performance-btn-primary"
                                onClick={handleEditTest}
                            >
                                수정
                            </button>
              <button 
                className="performance-btn performance-btn-secondary"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingTest(null);
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 다중 삭제 모달 */}
      {showDeleteModal && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>🗑️ 다중 삭제 확인</h3>
              <button 
                className="modal-close"
                onClick={() => setShowDeleteModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div style={{ textAlign: 'center', padding: '20px' }}>
                <div style={{ fontSize: '48px', marginBottom: '20px' }}>⚠️</div>
                <h4 style={{ color: '#d32f2f', marginBottom: '16px' }}>
                  정말로 삭제하시겠습니까?
                </h4>
                <p style={{ fontSize: '16px', marginBottom: '20px' }}>
                  선택된 <strong>{selectedTests.length}개</strong>의 성능 테스트가 영구적으로 삭제됩니다.
                </p>
                <div style={{ 
                  background: '#fff3cd', 
                  border: '1px solid #ffeaa7', 
                  borderRadius: '8px', 
                  padding: '16px', 
                  marginBottom: '20px' 
                }}>
                  <p style={{ margin: 0, color: '#856404' }}>
                    <strong>주의:</strong> 이 작업은 되돌릴 수 없습니다. 삭제된 성능 테스트와 관련된 모든 데이터가 함께 삭제됩니다.
                  </p>
                </div>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="performance-btn performance-btn-delete"
                onClick={handleMultiDelete}
                style={{ 
                  backgroundColor: '#d32f2f', 
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '6px',
                  fontSize: '16px',
                  fontWeight: 'bold',
                  cursor: 'pointer'
                }}
              >
                🗑️ 삭제하기
              </button>
              <button 
                className="performance-btn performance-btn-secondary"
                onClick={() => setShowDeleteModal(false)}
                style={{ 
                  backgroundColor: '#6c757d', 
                  color: 'white',
                  border: 'none',
                  padding: '12px 24px',
                  borderRadius: '6px',
                  fontSize: '16px',
                  marginLeft: '12px',
                  cursor: 'pointer'
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 상세보기 모달 */}
      {showDetailModal && selectedTest && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>📋 성능 테스트 상세 정보</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedTest(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body" style={{ padding: '24px', overflowY: 'auto' }}>
              <div className="test-info-table">
                <table className="info-table">
                  <tbody>
                    <tr>
                      <th>테스트명</th>
                      <td>{selectedTest.name || '없음'}</td>
                      <th>환경</th>
                      <td>
                        <span className={`environment-badge ${selectedTest.environment || 'prod'}`}>
                          {selectedTest.environment || 'prod'}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <th>작성자</th>
                      <td>
                        <span className="creator-badge">
                          👤 {selectedTest.creator_name || '없음'}
                        </span>
                      </td>
                      <th>담당자</th>
                      <td>
                        <span className="assignee-badge">
                          👤 {selectedTest.assignee_name || '없음'}
                        </span>
                      </td>
                    </tr>
                    <tr>
                      <th>스크립트 경로</th>
                      <td colSpan="3" className="script-path">
                        {selectedTest.script_path || '없음'}
                      </td>
                    </tr>
                    <tr>
                      <th>설명</th>
                      <td colSpan="3" className="description">
                        {selectedTest.description || '없음'}
                      </td>
                    </tr>
                    <tr>
                      <th>매개변수</th>
                      <td colSpan="3" className="parameters">
                        <pre>{selectedTest.parameters ? JSON.stringify(selectedTest.parameters, null, 2) : '없음'}</pre>
                      </td>
                    </tr>
                    <tr>
                      <th>생성일</th>
                      <td>{selectedTest.created_at ? formatUTCToKST(selectedTest.created_at) : '없음'}</td>
                      <th>수정일</th>
                      <td>{selectedTest.updated_at ? formatUTCToKST(selectedTest.updated_at) : '없음'}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowDetailModal(false);
                  setSelectedTest(null);
                }}
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      )}
        </div>
    );
};

export default PerformanceTestManager; 