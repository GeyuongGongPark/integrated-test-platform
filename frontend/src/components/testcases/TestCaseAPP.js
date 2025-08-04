// src/TestCaseApp.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './TestCaseAPP.css';

// axios 기본 URL 설정
axios.defaults.baseURL = config.apiUrl;

const TestCaseAPP = () => {
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
    main_category: '',
    sub_category: '',
    detail_category: '',
    pre_condition: '',
    expected_result: '',
    remark: '',
    folder_id: null
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [testCasesRes, treeRes] = await Promise.all([
        axios.get('/testcases'),
        axios.get('/folders/tree')
      ]);

      setTestCases(testCasesRes.data);
      setFolderTree(treeRes.data);
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
      console.error('Test case data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFolderSelect = (folderId) => {
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
      const response = await axios.post('/testcases/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
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
      await axios.post('/testcases', newTestCase);
      alert('테스트 케이스가 성공적으로 추가되었습니다.');
      setShowAddModal(false);
      setNewTestCase({
        main_category: '',
        sub_category: '',
        detail_category: '',
        pre_condition: '',
        expected_result: '',
        remark: '',
        folder_id: null
      });
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('테스트 케이스 추가 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleEditTestCase = async () => {
    if (!editingTestCase.main_category || !editingTestCase.sub_category || !editingTestCase.detail_category) {
      alert('필수 항목을 입력해주세요.');
      return;
    }

    try {
      await axios.put(`/testcases/${editingTestCase.id}`, editingTestCase);
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
      await axios.delete(`/testcases/${testCaseId}`);
      alert('테스트 케이스가 성공적으로 삭제되었습니다.');
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('테스트 케이스 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleStatusChange = async (testCaseId, newStatus) => {
    try {
      await axios.put(`/testcases/${testCaseId}/status`, { status: newStatus });
      console.log('테스트 케이스 상태 변경 완료:', newStatus);
      fetchData(); // 데이터 새로고침
    } catch (err) {
      alert('테스트 케이스 상태 변경 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleDownload = async () => {
    try {
      const response = await axios.get('/testcases/download', {
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

  const renderFolderTree = (nodes, level = 0) => {
    return nodes.map(node => (
      <div key={node.id} style={{ marginLeft: level * 20 }}>
        <div 
          className={`folder-item ${selectedFolder === node.id ? 'selected' : ''}`}
          onClick={() => handleFolderSelect(node.id)}
        >
          <span className="folder-icon">
            {node.type === 'environment' ? '🌍' : 
             node.type === 'deployment_date' ? '📅' : '📄'}
          </span>
          <span className="folder-name">{node.name}</span>
          {node.type === 'test_case' && (
            <span className={`test-status ${node.status.toLowerCase().replace('/', '-')}`}>
              {node.status}
            </span>
          )}
        </div>
        {node.children && node.children.length > 0 && (
          <div className="folder-children">
            {renderFolderTree(node.children, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  const filteredTestCases = selectedFolder 
    ? testCases.filter(tc => tc.folder_id === selectedFolder)
    : testCases;

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
          <button 
            className="btn btn-add"
            onClick={() => setShowAddModal(true)}
          >
            ➕ 테스트 케이스 추가
          </button>
          <button 
            className="btn btn-upload"
            onClick={() => setShowUploadModal(true)}
          >
            📤 엑셀 업로드
          </button>
          <button 
            className="btn btn-download"
            onClick={handleDownload}
          >
            📥 엑셀 다운로드
          </button>
        </div>
      </div>

      <div className="testcase-content">
        {/* 폴더 트리 */}
        <div className="folder-tree">
          <h3>폴더 구조</h3>
          <div className="tree-container">
            {renderFolderTree(folderTree)}
          </div>
        </div>

        {/* 테스트 케이스 목록 */}
        <div className="testcase-list">
          <h3>테스트 케이스 ({filteredTestCases.length})</h3>
          <div className="testcase-grid">
            {filteredTestCases.map(testCase => (
              <div key={testCase.id} className="testcase-card">
                <div className="testcase-header">
                  <h4>{testCase.expected_result || testCase.main_category + ' - ' + testCase.sub_category}</h4>
                  <div className="status-section">
                    <span className={`status-badge ${testCase.result_status.toLowerCase().replace('/', '-')}`}>
                      {testCase.result_status}
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
                </div>
                <div className="testcase-details">
                  <p><strong>대분류:</strong> {testCase.main_category}</p>
                  <p><strong>중분류:</strong> {testCase.sub_category}</p>
                  <p><strong>소분류:</strong> {testCase.detail_category}</p>
                  <p><strong>사전조건:</strong> {testCase.pre_condition}</p>
                  <p><strong>기대결과:</strong> {testCase.expected_result}</p>
                  <p><strong>비고:</strong> {testCase.remark || '없음'}</p>
                  {testCase.automation_code_path && (
                    <p><strong>자동화 코드:</strong> {testCase.automation_code_path}</p>
                  )}
                </div>
                <div className="testcase-actions">
                  {testCase.automation_code_path && (
                    <button 
                      className="btn btn-execute"
                      onClick={() => executeAutomationCode(testCase.id)}
                    >
                      ▶ 실행
                    </button>
                  )}
                  <button 
                    className="btn btn-edit"
                    onClick={() => {
                      setEditingTestCase(testCase);
                      setShowEditModal(true);
                    }}
                  >
                    ✏️ 편집
                  </button>
                  <button 
                    className="btn btn-delete"
                    onClick={() => handleDeleteTestCase(testCase.id)}
                  >
                    🗑️ 삭제
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 테스트 케이스 추가 모달 */}
      {showAddModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>새 테스트 케이스 추가</h3>
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
              <input 
                type="text" 
                value={newTestCase.pre_condition}
                onChange={(e) => setNewTestCase({...newTestCase, pre_condition: e.target.value})}
                placeholder="사전조건을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>기대결과</label>
              <input 
                type="text" 
                value={newTestCase.expected_result}
                onChange={(e) => setNewTestCase({...newTestCase, expected_result: e.target.value})}
                placeholder="기대결과를 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>비고</label>
              <input 
                type="text" 
                value={newTestCase.remark}
                onChange={(e) => setNewTestCase({...newTestCase, remark: e.target.value})}
                placeholder="비고를 입력하세요"
              />
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
                    remark: '',
                    folder_id: null
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
        <div className="modal-overlay">
          <div className="modal">
            <h3>테스트 케이스 편집</h3>
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
              <input 
                type="text" 
                value={editingTestCase.pre_condition}
                onChange={(e) => setEditingTestCase({...editingTestCase, pre_condition: e.target.value})}
                placeholder="사전조건을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>기대결과</label>
              <input 
                type="text" 
                value={editingTestCase.expected_result}
                onChange={(e) => setEditingTestCase({...editingTestCase, expected_result: e.target.value})}
                placeholder="기대결과를 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>비고</label>
              <input 
                type="text" 
                value={editingTestCase.remark}
                onChange={(e) => setEditingTestCase({...editingTestCase, remark: e.target.value})}
                placeholder="비고를 입력하세요"
              />
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

      {/* 업로드 모달 */}
      {showUploadModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>엑셀 파일 업로드</h3>
            <input 
              type="file" 
              accept=".xlsx"
              onChange={(e) => setSelectedFile(e.target.files[0])}
            />
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
