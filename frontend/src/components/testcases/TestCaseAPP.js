// src/TestCaseApp.js
import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import config from '../../config';
import './TestCaseAPP.css';

// 스크린샷 컴포넌트
const TestCaseScreenshots = ({ testCaseId }) => {
  const [screenshots, setScreenshots] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchScreenshots = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/testcases/${testCaseId}/screenshots`);
      setScreenshots(response.data);
    } catch (err) {
      console.error('스크린샷 조회 오류:', err);
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

  if (screenshots.length === 0) {
    return <div className="no-screenshots">스크린샷이 없습니다.</div>;
  }

  return (
    <div className="screenshots-container">
      {screenshots.map((screenshot, index) => (
        <div key={screenshot.id} className="screenshot-item">
          <img 
            src={`${config.apiUrl}/screenshots/${screenshot.screenshot_path}`}
            alt={`스크린샷 ${index + 1}`}
            className="screenshot-image"
          />
          <div className="screenshot-info">
            <span className="screenshot-timestamp">
              {new Date(screenshot.timestamp).toLocaleString()}
            </span>
          </div>
        </div>
      ))}
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
      const response = await axios.get(`/testresults/${testCaseId}`);
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
        <div key={result.id} className={`result-item ${result.result.toLowerCase()}`}>
          <div className="result-header">
            <span className={`result-status ${result.result.toLowerCase()}`}>
              {result.result}
            </span>
            <span className="result-timestamp">
              {new Date(result.executed_at).toLocaleString()}
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
    result_status: 'N/T',
    remark: '',
    folder_id: null,
    automation_code_path: '',
    automation_code_type: 'playwright'
  });
  
  // 폴더 이동 관련 상태
  const [selectedTestCases, setSelectedTestCases] = useState([]);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [targetFolderId, setTargetFolderId] = useState('');
  const [allFolders, setAllFolders] = useState([]);
  
  // 아코디언 관련 상태
  const [expandedFolders, setExpandedFolders] = useState(new Set());
  const [expandedTestCases, setExpandedTestCases] = useState(new Set());

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [testCasesRes, treeRes, foldersRes] = await Promise.all([
        axios.get('/testcases'),
        axios.get('/folders/tree'),
        axios.get('/folders')
      ]);

      console.log('받아온 테스트 케이스 데이터:', testCasesRes.data);
      setTestCases(testCasesRes.data);
      setFolderTree(treeRes.data);
      setAllFolders(foldersRes.data);
    } catch (err) {
      setError('데이터를 불러오는 중 오류가 발생했습니다.');
      console.error('Test case data fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFolderSelect = (folderId) => {
    console.log('=== handleFolderSelect 디버깅 ===');
    console.log('전달받은 folderId:', folderId, '타입:', typeof folderId);
    console.log('현재 folderTree:', folderTree);
    
    const selectedFolderInfo = findFolderInTree(folderTree, folderId);
    console.log('선택된 폴더 정보:', selectedFolderInfo);
    setSelectedFolder(folderId);
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      alert('파일을 선택해주세요.');
      return;
    }

    console.log('=== 파일 업로드 디버깅 ===');
    console.log('선택된 파일:', selectedFile);
    console.log('파일명:', selectedFile.name);
    console.log('파일 크기:', selectedFile.size);
    console.log('파일 타입:', selectedFile.type);

    const formData = new FormData();
    formData.append('file', selectedFile);

    // FormData 내용 확인
    console.log('FormData 내용:');
    for (let [key, value] of formData.entries()) {
      console.log(`${key}:`, value);
    }

    try {
      console.log('업로드 요청 시작...');
      const response = await axios.post('/testcases/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        transformRequest: [function (data) {
          return data; // FormData를 그대로 전송
        }],
      });

      console.log('업로드 성공:', response.data);
      alert(response.data.message);
      setShowUploadModal(false);
      setSelectedFile(null);
      fetchData(); // 데이터 새로고침
    } catch (err) {
      console.error('업로드 오류:', err);
      console.error('오류 응답:', err.response?.data);
      alert('파일 업로드 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleAddTestCase = async () => {
    if (!newTestCase.main_category || !newTestCase.sub_category || !newTestCase.detail_category) {
      alert('필수 항목을 입력해주세요.');
      return;
    }

    try {
      console.log('전송할 테스트 케이스 데이터:', newTestCase);
      await axios.post('/testcases', newTestCase);
      alert('테스트 케이스가 성공적으로 추가되었습니다.');
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
        automation_code_type: 'playwright'
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
      // 선택된 테스트 케이스들을 대상 폴더로 이동
      await Promise.all(
        selectedTestCases.map(testCaseId =>
          axios.put(`/testcases/${testCaseId}`, {
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
      alert('폴더 이동 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
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
    console.log('=== findFolderInTree 디버깅 ===');
    console.log('찾을 folderId:', folderId, '타입:', typeof folderId);
    console.log('nodes:', nodes);
    
    for (const node of nodes) {
      console.log('현재 노드 ID:', node.id, '타입:', typeof node.id);
      if (node.id === folderId) {
        console.log('노드 찾음:', node);
        return node;
      }
      if (node.children) {
        const found = findFolderInTree(node.children, folderId);
        if (found) return found;
      }
    }
    console.log('노드를 찾을 수 없음');
    return null;
  };

  // 환경 폴더의 모든 하위 폴더 ID들 가져오기
  const getEnvironmentFolderIds = (nodes, environmentFolderId) => {
    console.log('=== getEnvironmentFolderIds 디버깅 ===');
    console.log('입력 nodes:', nodes);
    console.log('입력 environmentFolderId:', environmentFolderId);
    
    const environmentNode = findFolderInTree(nodes, environmentFolderId);
    console.log('찾은 환경 노드:', environmentNode);
    
    if (!environmentNode || environmentNode.type !== 'environment') {
      console.log('환경 노드를 찾을 수 없거나 타입이 맞지 않음');
      return [];
    }
    
    const folderIds = [];
    if (environmentNode.children) {
      console.log('환경 노드의 자식들:', environmentNode.children);
      for (const child of environmentNode.children) {
        console.log('자식 노드 확인:', child);
        if (child.type === 'deployment_date') {
          folderIds.push(child.id);
          console.log('배포일자 폴더 추가:', child.id, child.name);
          
          // 배포일자 폴더의 하위 기능명 폴더들도 추가
          if (child.children) {
            for (const featureChild of child.children) {
              if (featureChild.type === 'feature') {
                folderIds.push(featureChild.id);
                console.log('기능명 폴더 추가:', featureChild.id, featureChild.name);
              }
            }
          }
        } else {
          console.log('배포일자가 아닌 자식 노드:', child.type, child.name);
        }
      }
    } else {
      console.log('환경 노드에 자식이 없음');
    }
    console.log('최종 폴더 IDs:', folderIds);
    return folderIds;
  };

  // 배포일자 폴더의 모든 하위 폴더 ID들 가져오기
  const getDeploymentFolderIds = (nodes, deploymentFolderId) => {
    console.log('=== getDeploymentFolderIds 디버깅 ===');
    console.log('입력 nodes:', nodes);
    console.log('입력 deploymentFolderId:', deploymentFolderId);
    
    const deploymentNode = findFolderInTree(nodes, deploymentFolderId);
    console.log('찾은 배포일자 노드:', deploymentNode);
    
    if (!deploymentNode || deploymentNode.type !== 'deployment_date') {
      console.log('배포일자 노드를 찾을 수 없거나 타입이 맞지 않음');
      return [];
    }
    
    const folderIds = [deploymentNode.id]; // 배포일자 폴더 자체도 포함
    if (deploymentNode.children) {
      console.log('배포일자 노드의 자식들:', deploymentNode.children);
      for (const child of deploymentNode.children) {
        console.log('자식 노드 확인:', child);
        if (child.type === 'feature') {
          folderIds.push(child.id);
          console.log('기능명 폴더 추가:', child.id, child.name);
        } else {
          console.log('기능명이 아닌 자식 노드:', child.type, child.name);
        }
      }
    } else {
      console.log('배포일자 노드에 자식이 없음');
    }
    console.log('최종 폴더 IDs:', folderIds);
    return folderIds;
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
                console.log(`클릭된 폴더: ID=${node.id}, Name=${node.name}, Type=${node.type}`);
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
              {node.type === 'environment' ? '🌍' : 
               node.type === 'deployment_date' ? '📅' : 
               node.type === 'feature' ? '🔧' : '📄'}
            </span>
            <span className="folder-name">{node.name}</span>
            {node.type === 'test_case' && (
              <span className={`test-status ${node.status.toLowerCase().replace('/', '-')}`}>
                {node.status}
              </span>
            )}
            {isFolder && (
              <span className="folder-type-badge">
                {node.type === 'environment' ? '환경' : 
                 node.type === 'deployment_date' ? '배포일자' : 
                 node.type === 'feature' ? '기능명' : ''}
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

  const filteredTestCases = selectedFolder 
    ? testCases.filter(tc => {
        const tcFolderId = Number(tc.folder_id);
        const selectedFolderId = Number(selectedFolder);
        
        // 선택된 폴더 정보 찾기
        const selectedFolderInfo = findFolderInTree(folderTree, selectedFolderId);
        
        console.log('=== 필터링 디버깅 ===');
        console.log('테스트 케이스:', tc.expected_result || tc.main_category);
        console.log('tc.folder_id:', tc.folder_id, '->', tcFolderId);
        console.log('selectedFolder:', selectedFolder, '->', selectedFolderId);
        console.log('selectedFolderInfo:', selectedFolderInfo);
        console.log('전체 testCases:', testCases.length);
        console.log('전체 folderTree:', folderTree);
        
        if (selectedFolderInfo?.type === 'environment') {
          // 환경 폴더 선택 시: 해당 환경의 모든 하위 폴더의 테스트 케이스들
          const environmentFolderIds = getEnvironmentFolderIds(folderTree, selectedFolderId);
          console.log(`환경 필터링: ${selectedFolderInfo.name}, 폴더 IDs:`, environmentFolderIds);
          console.log(`테스트 케이스 folder_id: ${tcFolderId}, 포함 여부:`, environmentFolderIds.includes(tcFolderId));
          const result = environmentFolderIds.includes(tcFolderId);
          console.log('필터링 결과:', result);
          return result;
        } else if (selectedFolderInfo?.type === 'deployment_date') {
          // 배포일자 폴더 선택 시: 해당 배포일자의 모든 하위 폴더의 테스트 케이스들
          const deploymentFolderIds = getDeploymentFolderIds(folderTree, selectedFolderId);
          console.log(`배포일자 필터링: ${selectedFolderInfo.name}, 폴더 IDs:`, deploymentFolderIds);
          console.log(`테스트 케이스 folder_id: ${tcFolderId}, 포함 여부:`, deploymentFolderIds.includes(tcFolderId));
          const result = deploymentFolderIds.includes(tcFolderId);
          console.log('필터링 결과:', result);
          return result;
        } else {
          // 기능명 폴더 선택 시: 해당 폴더의 테스트 케이스들만
          console.log(`폴더 필터링: tc.folder_id ${tcFolderId} === selectedFolder ${selectedFolderId}`);
          const result = tcFolderId === selectedFolderId;
          console.log('필터링 결과:', result);
          return result;
        }
      })
    : testCases;

  // 디버깅을 위한 로그
  console.log('=== 필터링 디버깅 ===');
  console.log('전체 테스트 케이스:', testCases.length);
  console.log('선택된 폴더 ID:', selectedFolder);
  console.log('필터링된 테스트 케이스:', filteredTestCases.length);
  console.log('폴더 트리:', folderTree);

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
          {selectedTestCases.length > 0 && (
            <button 
              className="btn btn-execute"
              onClick={() => setShowMoveModal(true)}
            >
              📁 폴더 이동 ({selectedTestCases.length})
            </button>
          )}
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
                    className="btn btn-details"
                    onClick={() => toggleTestCaseDetails(testCase.id)}
                    title="상세보기"
                  >
                    {expandedTestCases.has(testCase.id) ? '📋' : '📄'}
                  </button>
                  <button 
                    className="btn btn-edit-icon"
                    onClick={() => {
                      setEditingTestCase(testCase);
                      setShowEditModal(true);
                    }}
                    title="수정"
                  >
                    ✏️
                  </button>
                  <button 
                    className="btn btn-delete-icon"
                    onClick={() => handleDeleteTestCase(testCase.id)}
                    title="삭제"
                  >
                    ✕
                  </button>
                </div>
                {expandedTestCases.has(testCase.id) && (
                  <div className="testcase-details">
                    <div className="testcase-info">
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
                    folder_id: null
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
                      {folder.folder_name}
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
