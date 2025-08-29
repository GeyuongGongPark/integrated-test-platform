import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import AutomationTestDetail from './AutomationTestDetail';
import './AutomationTestManager.css';

axios.defaults.baseURL = config.apiUrl;

const AutomationTestManager = () => {
  const { user } = useAuth();
  const [automationTests, setAutomationTests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingTest, setEditingTest] = useState(null);
  // 하단 전체 화면 구조로 변경
  const [selectedTest, setSelectedTest] = useState(null);
  const [showDetail, setShowDetail] = useState(false);
  const [users, setUsers] = useState([]);
  const [newTest, setNewTest] = useState({
    name: '',
    description: '',
    test_type: 'playwright',
    script_path: '',
    environment: 'dev',
    parameters: '',
    assignee_id: null
  });

  useEffect(() => {
    fetchAutomationTests();
  }, []);

  const fetchAutomationTests = async () => {
    try {
      setLoading(true);
      
      // 자동화 테스트 목록은 항상 가져오기
      const automationRes = await axios.get('/automation-tests');
      setAutomationTests(automationRes.data.items || automationRes.data);
      
      // 사용자 목록은 admin이나 user만 가져오기 (게스트는 제외)
      if (user && (user.role === 'admin' || user.role === 'user')) {
        try {
          const usersRes = await axios.get('/users/list');
          setUsers(usersRes.data);
        } catch (userErr) {
          console.error('사용자 목록 조회 오류:', userErr);
          setUsers([]);
        }
      } else {
        setUsers([]);
      }
    } catch (err) {
      setError('자동화 테스트 목록을 불러오는 중 오류가 발생했습니다.');
      console.error('Automation test fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddTest = async () => {
    if (!newTest.name || !newTest.script_path) {
      alert('테스트명과 스크립트 경로를 입력해주세요.');
      return;
    }

    try {
      await axios.post('/automation-tests', newTest);
      alert('자동화 테스트가 성공적으로 추가되었습니다.');
      setShowAddModal(false);
      setNewTest({
        name: '',
        description: '',
        test_type: 'playwright',
        script_path: '',
        environment: 'dev',
        parameters: '',
        assignee_id: null
      });
      fetchAutomationTests();
    } catch (err) {
      alert('자동화 테스트 추가 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleEditTest = async () => {
    if (!editingTest.name || !editingTest.script_path) {
      alert('테스트명과 스크립트 경로를 입력해주세요.');
      return;
    }

    try {
      await axios.put(`/automation-tests/${editingTest.id}`, editingTest);
      alert('자동화 테스트가 성공적으로 수정되었습니다.');
      setShowEditModal(false);
      setEditingTest(null);
      fetchAutomationTests();
    } catch (err) {
      alert('자동화 테스트 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleEditClick = (test) => {
    setEditingTest({
      ...test,
      assignee_id: test.assignee_id || null
    });
    setShowEditModal(true);
  };

  const handleDeleteTest = async (testId) => {
    if (!window.confirm('정말로 이 자동화 테스트를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await axios.delete(`/automation-tests/${testId}`);
      alert('자동화 테스트가 성공적으로 삭제되었습니다.');
      fetchAutomationTests();
    } catch (err) {
      alert('자동화 테스트 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleExecuteTest = async (testId) => {
    if (!window.confirm('이 자동화 테스트를 실행하시겠습니까?')) {
      return;
    }

    try {
      await axios.post(`/automation-tests/${testId}/execute`);
      alert('자동화 테스트 실행이 완료되었습니다.');
      fetchAutomationTests();
    } catch (err) {
      alert('자동화 테스트 실행 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  // 상세보기 토글 함수를 하단 전체 화면용으로 변경
  const toggleTestDetails = (test) => {
    if (selectedTest && selectedTest.id === test.id) {
      // 같은 테스트를 다시 클릭하면 닫기
      setSelectedTest(null);
      setShowDetail(false);
    } else {
      // 다른 테스트를 클릭하면 선택하고 표시
      setSelectedTest(test);
      setShowDetail(true);
    }
  };

  // 상세보기 닫기
  const closeDetail = () => {
    setSelectedTest(null);
    setShowDetail(false);
  };

  if (loading) {
    return <div className="loading">자동화 테스트 목록을 불러오는 중...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="automation-test-manager">
      <div className="automation-header">
        <h2>자동화 테스트 관리</h2>
        <div className="header-actions">
          {user && (user.role === 'admin' || user.role === 'user') && (
            <button 
              className="btn btn-add"
              onClick={() => setShowAddModal(true)}
            >
              ➕ 자동화 테스트 추가
            </button>
          )}
        </div>
      </div>

      {/* 테스트 목록 */}
      <div className="automation-list">
        {automationTests.length === 0 ? (
          <div className="empty-state">
            <p>등록된 자동화 테스트가 없습니다.</p>
            {user && (user.role === 'admin' || user.role === 'user') && (
              <button 
                className="btn btn-primary"
                onClick={() => setShowAddModal(true)}
              >
                첫 번째 자동화 테스트 추가하기
              </button>
            )}
          </div>
        ) : (
          automationTests.map(test => (
            <div 
              key={test.id} 
              className={`automation-item ${selectedTest && selectedTest.id === test.id ? 'selected' : ''}`}
            >
              <div className="automation-item-header" onClick={() => toggleTestDetails(test)}>
                <div className="automation-header">
                  <h3 className="automation-name">{test.name}</h3>
                  <p className="automation-description">{test.description}</p>
                </div>
                <div className="automation-actions" onClick={(e) => e.stopPropagation()}>
                  {user && (user.role === 'admin' || user.role === 'user') && (
                    <button 
                      className="btn btn-automation btn-icon"
                      onClick={() => handleExecuteTest(test.id)}
                      title="자동화 실행"
                    >
                      🤖
                    </button>
                  )}
                  <button 
                    className="btn btn-details btn-icon"
                    onClick={() => toggleTestDetails(test)}
                    title="상세보기"
                  >
                    {selectedTest && selectedTest.id === test.id ? '📋' : '📄'}
                  </button>
                  {user && (user.role === 'admin' || user.role === 'user') && (
                    <button 
                      className="btn btn-edit-icon btn-icon"
                      onClick={() => handleEditClick(test)}
                      title="수정"
                    >
                      ✏️
                    </button>
                  )}
                  {user && user.role === 'admin' && (
                    <button 
                      className="btn btn-delete-icon btn-icon"
                      onClick={() => handleDeleteTest(test.id)}
                      title="삭제"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>
              
              {/* 상세 정보 인라인 표시 */}
              {selectedTest && selectedTest.id === test.id && (
                <div className="automation-detail-inline">
                  <AutomationTestDetail 
                    test={test}
                    onClose={closeDetail}
                    onRefresh={fetchAutomationTests}
                  />
                </div>
              )}
            </div>
          ))
        )}
      </div>

      {/* 하단 전체 화면 구조 제거 */}
      {/* {showDetail && selectedTest && (
        <div className="automation-detail-bottom">
          <AutomationTestDetail 
            test={selectedTest}
            onClose={closeDetail}
            onRefresh={fetchAutomationTests}
          />
        </div>
      )} */}

      {/* 추가 모달 */}
      {showAddModal && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>자동화 테스트 추가</h3>
              <button 
                className="modal-close"
                onClick={() => setShowAddModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>테스트명 *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newTest.name}
                  onChange={(e) => setNewTest({...newTest, name: e.target.value})}
                  placeholder="테스트명을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea
                  className="form-control"
                  value={newTest.description}
                  onChange={(e) => setNewTest({...newTest, description: e.target.value})}
                  placeholder="테스트 설명을 입력하세요"
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>테스트 타입 *</label>
                <select
                  className="form-control"
                  value={newTest.test_type}
                  onChange={(e) => setNewTest({...newTest, test_type: e.target.value})}
                >
                  <option value="playwright">Playwright</option>
                  <option value="selenium">Selenium</option>
                  <option value="cypress">Cypress</option>
                  <option value="puppeteer">Puppeteer</option>
                </select>
              </div>
              <div className="form-group">
                <label>스크립트 경로 *</label>
                <input
                  type="text"
                  className="form-control"
                  value={newTest.script_path}
                  onChange={(e) => setNewTest({...newTest, script_path: e.target.value})}
                  placeholder="스크립트 파일 경로를 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>환경</label>
                <select
                  className="form-control"
                  value={newTest.environment}
                  onChange={(e) => setNewTest({...newTest, environment: e.target.value})}
                >
                  <option value="dev">DEV</option>
                  <option value="alpha">ALPHA</option>
                  <option value="production">PRODUCTION</option>
                </select>
              </div>
              <div className="form-group">
                <label>매개변수 (JSON)</label>
                <textarea
                  className="form-control"
                  value={newTest.parameters}
                  onChange={(e) => setNewTest({...newTest, parameters: e.target.value})}
                  placeholder='{"timeout": 30, "retries": 3}'
                  rows="5"
                />
              </div>
              {user && (user.role === 'admin' || user.role === 'user') && (
                <div className="form-group">
                  <label>담당자</label>
                  <select
                    className="form-control"
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
              )}
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-cancel"
                onClick={() => setShowAddModal(false)}
              >
                취소
              </button>
              <button 
                className="btn btn-save"
                onClick={handleAddTest}
              >
                추가
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 수정 모달 */}
      {showEditModal && editingTest && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>자동화 테스트 수정</h3>
              <button 
                className="modal-close"
                onClick={() => setShowEditModal(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>테스트명 *</label>
                <input
                  type="text"
                  className="form-control"
                  value={editingTest.name}
                  onChange={(e) => setEditingTest({...editingTest, name: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea
                  className="form-control"
                  value={editingTest.description}
                  onChange={(e) => setEditingTest({...editingTest, description: e.target.value})}
                  rows="3"
                />
              </div>
              <div className="form-group">
                <label>테스트 타입 *</label>
                <select
                  className="form-control"
                  value={editingTest.test_type}
                  onChange={(e) => setEditingTest({...editingTest, test_type: e.target.value})}
                >
                  <option value="playwright">Playwright</option>
                  <option value="selenium">Selenium</option>
                  <option value="cypress">Cypress</option>
                  <option value="puppeteer">Puppeteer</option>
                </select>
              </div>
              <div className="form-group">
                <label>스크립트 경로 *</label>
                <input
                  type="text"
                  className="form-control"
                  value={editingTest.script_path}
                  onChange={(e) => setEditingTest({...editingTest, script_path: e.target.value})}
                />
              </div>
              <div className="form-group">
                <label>환경</label>
                <select
                  className="form-control"
                  value={editingTest.environment}
                  onChange={(e) => setEditingTest({...editingTest, environment: e.target.value})}
                >
                  <option value="dev">DEV</option>
                  <option value="alpha">ALPHA</option>
                  <option value="production">PRODUCTION</option>
                </select>
              </div>
              <div className="form-group">
                <label>매개변수 (JSON)</label>
                <textarea
                  className="form-control"
                  value={editingTest.parameters}
                  onChange={(e) => setEditingTest({...editingTest, parameters: e.target.value})}
                  rows="5"
                />
              </div>
              {user && (user.role === 'admin' || user.role === 'user') && (
                <div className="form-group">
                  <label>담당자</label>
                  <select
                    className="form-control"
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
              )}
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-cancel"
                onClick={() => setShowEditModal(false)}
              >
                취소
              </button>
              <button 
                className="btn btn-save"
                onClick={handleEditTest}
              >
                수정
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutomationTestManager; 
