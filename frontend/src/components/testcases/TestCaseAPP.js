// src/TestCaseApp.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './TestCaseAPP.css';

// axios 기본 URL 설정
axios.defaults.baseURL = config.apiUrl;

const TestCaseAPP = () => {
  const [testCases, setTestCases] = useState([]);
  const [folders, setFolders] = useState([]);
  const [folderTree, setFolderTree] = useState([]);
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [testCasesRes, foldersRes, treeRes] = await Promise.all([
        axios.get('/testcases'),
        axios.get('/folders'),
        axios.get('/folders/tree')
      ]);

      setTestCases(testCasesRes.data);
      setFolders(foldersRes.data);
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
                  <h4>{testCase.description}</h4>
                  <span className={`status-badge ${testCase.result_status.toLowerCase().replace('/', '-')}`}>
                    {testCase.result_status}
                  </span>
                </div>
                <div className="testcase-details">
                  <p><strong>환경:</strong> {testCase.environment}</p>
                                     <p><strong>카테고리:</strong> {testCase.main_category} &gt; {testCase.sub_category}</p>
                  <p><strong>전제조건:</strong> {testCase.pre_condition}</p>
                  <p><strong>비고:</strong> {testCase.remark}</p>
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
                  <button className="btn btn-edit">✏️ 편집</button>
                  <button className="btn btn-delete">🗑️ 삭제</button>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

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
