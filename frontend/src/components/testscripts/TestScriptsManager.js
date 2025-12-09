import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import config from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import MonacoEditor from '@monaco-editor/react';
import './TestScriptsManager.css';

const TestScriptsManager = () => {
  const { user, token } = useAuth();
  const [s3Files, setS3Files] = useState([]);
  const [localFiles, setLocalFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState('');
  const [activeTab, setActiveTab] = useState('local'); // 's3' or 'local'
  const [editorLanguage, setEditorLanguage] = useState('javascript');
  const [isEditing, setIsEditing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [newFileContent, setNewFileContent] = useState('');
  const [showFolderUploadModal, setShowFolderUploadModal] = useState(false);
  const [uploadingFolder, setUploadingFolder] = useState(false);
  const [currentPath, setCurrentPath] = useState('test-scripts');
  const [pathHistory, setPathHistory] = useState(['test-scripts']);
  const [s3PathHistory, setS3PathHistory] = useState(['test-scripts/']);
  const [s3Folders, setS3Folders] = useState([]);
  const [showFolderSelectModal, setShowFolderSelectModal] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState('test-scripts/');
  const [tempFileName, setTempFileName] = useState('');
  const [isLocalFileSave, setIsLocalFileSave] = useState(false);
  // 신규: 사용자 지정 기본 경로 설정 상태 (서버 저장)
  const [showFolderSettingsModal, setShowFolderSettingsModal] = useState(false);
  const [s3BasePrefix, setS3BasePrefix] = useState('test-scripts/');
  const [localBasePath, setLocalBasePath] = useState('test-scripts');
  // S3 폴더 컨텍스트 메뉴 상태
  const [contextMenu, setContextMenu] = useState({ visible: false, x: 0, y: 0, folder: null });

  // 파일 확장자에 따른 언어 감지
  const getFileLanguage = (filename) => {
    if (filename.endsWith('.js') || filename.endsWith('.jsx')) return 'javascript';
    if (filename.endsWith('.ts') || filename.endsWith('.tsx')) return 'typescript';
    if (filename.endsWith('.py')) return 'python';
    if (filename.endsWith('.json')) return 'json';
    if (filename.endsWith('.md')) return 'markdown';
    if (filename.endsWith('.html') || filename.endsWith('.htm')) return 'html';
    if (filename.endsWith('.css') || filename.endsWith('.scss') || filename.endsWith('.sass')) return 'css';
    if (filename.endsWith('.xml')) return 'xml';
    if (filename.endsWith('.yaml') || filename.endsWith('.yml')) return 'yaml';
    if (filename.endsWith('.sql')) return 'sql';
    if (filename.endsWith('.sh') || filename.endsWith('.bash')) return 'bash';
    if (filename.endsWith('.env')) return 'properties';
    return 'plaintext';
  };

  // 파일 타입에 따른 아이콘 반환
  const getFileIcon = (filename) => {
    if (filename.endsWith('.js')) return '📄';
    if (filename.endsWith('.py')) return '🐍';
    if (filename.endsWith('.spec.js')) return '🧪';
    if (filename.endsWith('.json')) return '⚙️';
    if (filename.endsWith('.md')) return '📝';
    if (filename.endsWith('.png') || filename.endsWith('.jpg') || filename.endsWith('.jpeg')) return '🖼️';
    return '📄';
  };

  // 초기 설정 로드 (서버에서 사용자별 S3 프리픽스)
  useEffect(() => {
    const fetchUserS3Prefix = async () => {
      try {
        const res = await axios.get(`${config.apiUrl}/api/test-scripts/s3/settings/prefix`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        const prefix = res.data?.s3_base_prefix || 'test-scripts/';
        setS3BasePrefix(prefix);
        setS3PathHistory([prefix]);
      } catch (e) {
        console.error('사용자 S3 프리픽스 조회 오류:', e);
        setS3BasePrefix('test-scripts/');
        setS3PathHistory(['test-scripts/']);
      }
    };
    fetchUserS3Prefix();
    // 로컬 기본 경로는 기존 기본값 유지 (요구사항 3-A로 S3만 적용)
    setPathHistory([localBasePath]);
    setCurrentPath(localBasePath);
    // 전역 클릭 시 컨텍스트 메뉴 닫기
    const handleGlobalClick = () => setContextMenu({ visible: false, x: 0, y: 0, folder: null });
    window.addEventListener('click', handleGlobalClick);
    return () => window.removeEventListener('click', handleGlobalClick);
  }, [token]);

  // S3 파일 목록 로드
  const loadS3Files = useCallback(async () => {
    try {
      setLoading(true);
      const prefix = s3PathHistory.length > 0 ? s3PathHistory[s3PathHistory.length - 1] : s3BasePrefix;
      const response = await axios.get(`${config.apiUrl}/api/test-scripts/s3/list?prefix=${encodeURIComponent(prefix)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      setS3Files(response.data.files || []);
    } catch (err) {
      console.error('S3 파일 목록 로드 오류:', err);
      // S3가 설정되지 않은 경우 빈 배열로 설정
      setS3Files([]);
    } finally {
      setLoading(false);
    }
  }, [token, s3BasePrefix, s3PathHistory]);

  // S3 폴더 목록 로드
  const loadS3Folders = useCallback(async () => {
    try {
      const response = await axios.get(`${config.apiUrl}/api/test-scripts/s3/folders?prefix=${encodeURIComponent(s3BasePrefix)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data.success) {
        setS3Folders(response.data.folders || []);
      } else {
        console.error('S3 폴더 목록 조회 실패:', response.data.error);
        setS3Folders([]);
      }
    } catch (err) {
      console.error('S3 폴더 목록 조회 오류:', err);
      setS3Folders([]);
    }
  }, [token, s3BasePrefix]);

  // 로컬 파일 목록 로드
  const loadLocalFiles = useCallback(async (path = localBasePath) => {
    try {
      setLoading(true);
      const targetPath = path || localBasePath || 'test-scripts';
      const response = await axios.get(`${config.apiUrl}/api/test-scripts/explore?path=${encodeURIComponent(targetPath)}`);
      setLocalFiles(response.data.children || []);
      setCurrentPath(targetPath);
    } catch (err) {
      console.error('로컬 파일 목록 로드 오류:', err);
      console.error('오류 상세:', err.response?.data);
      setError('로컬 파일 목록을 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  }, [localBasePath]);

  // 하위 폴더 탐색
  const exploreDirectory = (directory) => {
    if (activeTab === 's3') {
      // S3 폴더 탐색
      exploreS3Directory(directory);
    } else {
      // 로컬 폴더 탐색
      const newPath = directory.path.replace('/Users/ggpark/Desktop/Team_Git/integrated-test-platform/', '');
      setPathHistory(prev => [...prev, newPath]);
      loadLocalFiles(newPath);
    }
  };

  // S3 하위 폴더 탐색
  const exploreS3Directory = async (directory) => {
    try {
      setLoading(true);
      const prefix = directory.key.endsWith('/') ? directory.key : `${directory.key}/`;
      const response = await axios.get(`${config.apiUrl}/api/test-scripts/s3/list?prefix=${encodeURIComponent(prefix)}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data.success) {
        setS3Files(response.data.files);
        setS3PathHistory(prev => [...prev, prefix]);
      }
    } catch (error) {
      console.error('S3 폴더 탐색 오류:', error);
      setError('S3 폴더를 탐색할 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 상위 폴더로 이동
  const goBack = () => {
    if (activeTab === 's3') {
      // S3 뒤로가기
      goBackS3();
    } else {
      // 로컬 뒤로가기
      if (pathHistory.length > 1) {
        const newHistory = [...pathHistory];
        newHistory.pop(); // 현재 경로 제거
        const parentPath = newHistory[newHistory.length - 1];
        setPathHistory(newHistory);
        loadLocalFiles(parentPath);
      }
    }
  };

  // S3 상위 폴더로 이동
  const goBackS3 = async () => {
    if (s3PathHistory.length > 1) {
      const newHistory = [...s3PathHistory];
      newHistory.pop(); // 현재 경로 제거
      const parentPath = newHistory[newHistory.length - 1];
      setS3PathHistory(newHistory);
      
      try {
        setLoading(true);
        const prefix = parentPath.endsWith('/') ? parentPath : `${parentPath}/`;
        const response = await axios.get(`${config.apiUrl}/api/test-scripts/s3/list?prefix=${encodeURIComponent(prefix)}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        
        if (response.data.success) {
          setS3Files(response.data.files);
        }
      } catch (error) {
        console.error('S3 뒤로가기 오류:', error);
        setError('S3 폴더를 탐색할 수 없습니다.');
      } finally {
        setLoading(false);
      }
    }
  };

  // 파일 내용 로드
  const loadFileContent = async (file) => {
    try {
      setLoading(true);
      let content;
      
      if (activeTab === 's3') {
        const response = await axios.get(`${config.apiUrl}/api/test-scripts/s3/content?key=${encodeURIComponent(file.key)}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        content = response.data.content;
      } else {
        const response = await axios.get(`${config.apiUrl}/api/test-scripts/file-content?path=${encodeURIComponent(file.path)}`);
        content = response.data.content;
      }
      
      setFileContent(content);
      setSelectedFile(file);
      setEditorLanguage(getFileLanguage(file.name || file.key));
      setIsEditing(false);
      
      // 디버깅용 로그
      console.log('선택된 파일:', file);
      console.log('파일 키:', file.key);
      console.log('파일 경로:', file.path);
      console.log('파일 이름:', file.name);
    } catch (err) {
      console.error('파일 내용 로드 오류:', err);
      alert('파일 내용을 불러올 수 없습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 파일 저장
  const saveFile = async () => {
    if (!selectedFile) return;
    
    try {
      setLoading(true);
      
      if (activeTab === 's3') {
        // S3 파일 수정 (덮어쓰기)
        await axios.post(`${config.apiUrl}/api/test-scripts/s3/upload-content`, {
          content: fileContent,
          filename: selectedFile.key.split('/').pop(),
          is_new_file: false,
          existing_s3_key: selectedFile.key
        }, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        alert('파일이 성공적으로 저장되었습니다.');
        loadS3Files(); // 목록 새로고침
        setIsEditing(false);
      } else {
        // 로컬 파일 편집 - 폴더 선택 모달 표시
        await loadS3Folders();
        
        // 기본 파일명 설정
        const defaultFileName = selectedFile.name || selectedFile.path.split('/').pop();
        setTempFileName(defaultFileName);
        setSelectedFolder(s3BasePrefix || 'test-scripts/');
        setIsLocalFileSave(true);
        setShowFolderSelectModal(true);
      }
    } catch (err) {
      console.error('파일 저장 오류:', err);
      alert('파일 저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 다른 이름으로 저장 (폴더 선택 모달 표시)
  const saveAsFile = async () => {
    if (!selectedFile) return;
    
    // 폴더 목록 로드
    await loadS3Folders();
    
    // 기본 파일명 설정
    const defaultFileName = selectedFile.key?.split('/').pop() || selectedFile.name;
    setTempFileName(defaultFileName);
    setSelectedFolder(s3BasePrefix || 'test-scripts/');
    setIsLocalFileSave(false);
    setShowFolderSelectModal(true);
  };

  // 폴더 선택 후 실제 저장
  const confirmSaveAs = async () => {
    if (!tempFileName) {
      alert('파일명을 입력해주세요.');
      return;
    }
    
    try {
      setLoading(true);
      
      // 선택된 폴더에 새 파일명으로 저장 (항상 새 파일 생성)
      const fullPath = selectedFolder.endsWith('/') ? selectedFolder + tempFileName : selectedFolder + '/' + tempFileName;
      
      await axios.post(`${config.apiUrl}/api/test-scripts/s3/upload-content`, {
        content: fileContent,
        filename: fullPath,
        is_new_file: true
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      alert(`파일이 "${fullPath}"에 저장되었습니다.`);
      loadS3Files(); // 목록 새로고침
      setIsEditing(false);
      setShowFolderSelectModal(false);
      setIsLocalFileSave(false);
    } catch (err) {
      console.error('파일 저장 오류:', err);
      alert('파일 저장 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 새 파일 생성
  const createNewFile = async () => {
    if (!newFileName || !newFileContent) {
      alert('파일명과 내용을 입력해주세요.');
      return;
    }
    
    try {
      setLoading(true);
      await axios.post(`${config.apiUrl}/api/test-scripts/s3/upload-content`, {
        content: newFileContent,
        filename: newFileName,
        is_new_file: true
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      alert('새 파일이 성공적으로 생성되었습니다.');
      setShowUploadModal(false);
      setNewFileName('');
      setNewFileContent('');
      loadS3Files(); // 목록 새로고침
    } catch (err) {
      console.error('파일 생성 오류:', err);
      alert('파일 생성 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 파일 삭제
  const deleteFile = async (file) => {
    if (!window.confirm('정말로 이 파일을 삭제하시겠습니까?')) return;
    
    try {
      setLoading(true);
      
      if (activeTab === 's3') {
        await axios.delete(`${config.apiUrl}/api/test-scripts/s3/delete`, {
          data: { s3_key: file.key },
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        alert('파일이 성공적으로 삭제되었습니다.');
        loadS3Files(); // 목록 새로고침
      } else {
        alert('로컬 파일은 삭제할 수 없습니다.');
      }
    } catch (err) {
      console.error('파일 삭제 오류:', err);
      alert('파일 삭제 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // 파일 다운로드
  const downloadFile = async (file) => {
    try {
      if (activeTab === 's3') {
        const response = await axios.get(`${config.apiUrl}/api/test-scripts/s3/download-url?key=${encodeURIComponent(file.key)}`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
        window.open(response.data.download_url, '_blank');
      } else {
        // 로컬 파일 다운로드는 현재 지원하지 않음
        alert('로컬 파일 다운로드는 지원하지 않습니다.');
      }
    } catch (err) {
      console.error('파일 다운로드 오류:', err);
      alert('파일 다운로드 중 오류가 발생했습니다.');
    }
  };

  // 파일 업로드
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    try {
      setLoading(true);
      setUploadProgress(0);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post(`${config.apiUrl}/api/test-scripts/s3/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${token}`
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        }
      });
      
      alert('파일이 성공적으로 업로드되었습니다.');
      loadS3Files(); // 목록 새로고침
    } catch (err) {
      console.error('파일 업로드 오류:', err);
      alert('파일 업로드 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  // 폴더 업로드
  const uploadFolderToS3 = async (folderPath) => {
    try {
      setUploadingFolder(true);
      setUploadProgress(0);
      
      const response = await axios.post(`${config.apiUrl}/api/test-scripts/s3/upload-folder`, {
        folder_path: folderPath
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (response.data.success) {
        alert(`폴더 업로드 완료!\n업로드된 파일: ${response.data.total_uploaded}개\n실패한 파일: ${response.data.total_failed}개`);
        loadS3Files(); // S3 목록 새로고침
      } else {
        alert('폴더 업로드 중 오류가 발생했습니다.');
      }
    } catch (err) {
      console.error('폴더 업로드 오류:', err);
      alert('폴더 업로드 중 오류가 발생했습니다.');
    } finally {
      setUploadingFolder(false);
      setUploadProgress(0);
    }
  };

  // 전체 test-scripts 폴더 업로드
  const uploadAllToS3 = () => {
    if (window.confirm('전체 test-scripts 폴더를 S3에 업로드하시겠습니까?')) {
      uploadFolderToS3('test-scripts');
    }
  };

  // S3 폴더 컨텍스트 메뉴에서 "여기에 저장"
  const saveHereToS3 = async () => {
    if (!contextMenu.folder) return;
    try {
      const folderKey = contextMenu.folder.key.endsWith('/') ? contextMenu.folder.key : `${contextMenu.folder.key}/`;
      const defaultName = (selectedFile?.name) || (selectedFile?.key ? selectedFile.key.split('/').pop() : 'new-script.js');
      const name = window.prompt('저장할 파일명을 입력하세요', defaultName);
      if (!name) return;
      const fullPath = folderKey + name;
      await axios.post(`${config.apiUrl}/api/test-scripts/s3/upload-content`, {
        content: fileContent,
        filename: fullPath,
        is_new_file: true
      }, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      alert(`파일이 "${fullPath}"에 저장되었습니다.`);
      // 현재 폴더가 컨텍스트 폴더와 같으면 목록 새로고침
      const currentPrefix = (s3PathHistory[s3PathHistory.length - 1] || s3BasePrefix);
      if (currentPrefix === folderKey) {
        await loadS3Files();
      }
    } catch (e) {
      console.error('여기에 저장 오류:', e);
      alert('저장 중 오류가 발생했습니다.');
    } finally {
      setContextMenu({ visible: false, x: 0, y: 0, folder: null });
    }
  };

  useEffect(() => {
    if (activeTab === 's3') {
      // 기본 프리픽스로 경로 초기화
      if (!s3PathHistory || s3PathHistory.length === 0) {
        setS3PathHistory([s3BasePrefix]);
      }
      loadS3Files();
    } else {
      // 기본 로컬 경로로 초기화
      if (!pathHistory || pathHistory.length === 0) {
        setPathHistory([localBasePath]);
      }
      loadLocalFiles(localBasePath);
    }
  }, [activeTab, loadS3Files, loadLocalFiles, s3BasePrefix, localBasePath]);

  const currentFiles = activeTab === 's3' ? s3Files : localFiles;

  if (loading && currentFiles.length === 0) {
    return (
      <div className="test-scripts-manager">
        <div className="loading-container">
          <div className="test-scripts-loading-spinner">⏳</div>
          <p>파일 목록을 불러오는 중...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="test-scripts-manager">
      <div className="manager-header">
        <h2>📁 테스트 스크립트 관리</h2>
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
          <div className="tab-buttons">
            <button 
              className={`tab-button ${activeTab === 's3' ? 'active' : ''}`}
              onClick={() => setActiveTab('s3')}
            >
              ☁️ S3 클라우드
            </button>
            <button 
              className={`tab-button ${activeTab === 'local' ? 'active' : ''}`}
              onClick={() => setActiveTab('local')}
            >
              💻 로컬 파일
            </button>
          </div>
          {/* 신규: 폴더 설정 버튼 */}
          <button 
            className="create-button"
            onClick={() => {
              setShowFolderSettingsModal(true);
              loadS3Folders();
            }}
            title="기본 폴더 설정"
          >
            🛠️ 폴더 설정
          </button>
          
          {activeTab === 's3' && (
            <div className="action-buttons">
              <label className="upload-button">
                📤 파일 업로드
                <input
                  type="file"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  accept=".js,.py,.json,.md,.txt,.spec.js"
                />
              </label>
              <button 
                className="create-button"
                onClick={() => setShowUploadModal(true)}
              >
                ➕ 새 파일
              </button>
            </div>
          )}
          
          {activeTab === 'local' && (
            <div className="action-buttons">
              <button 
                className="upload-folder-button"
                onClick={uploadAllToS3}
                disabled={uploadingFolder}
              >
                {uploadingFolder ? '⏳ 업로드 중...' : '📁 전체 폴더 S3 업로드'}
              </button>
            </div>
          )}
        </div>
      </div>

      {uploadProgress > 0 && (
        <div className="upload-progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <span>{uploadProgress}% 업로드 중...</span>
        </div>
      )}

      <div className="manager-content">
        <div className="file-list-panel">
          <div className="file-list-header">
            <h3>{activeTab === 's3' ? 'S3 파일 목록' : '로컬 파일 목록'}</h3>
            <div className="header-actions">
              {((activeTab === 'local' && pathHistory.length > 1) || (activeTab === 's3' && s3PathHistory.length > 1)) && (
                <button 
                  className="back-button"
                  onClick={goBack}
                  title="뒤로가기"
                >
                  ⬅️ 뒤로
                </button>
              )}
              <button 
                className="refresh-button"
                onClick={() => activeTab === 's3' ? loadS3Files() : loadLocalFiles(currentPath)}
              >
                🔄 새로고침
              </button>
            </div>
          </div>
          
          <div className="current-path">
            📍 현재 경로: {activeTab === 's3' ? (s3PathHistory.length > 0 ? s3PathHistory[s3PathHistory.length - 1] : s3BasePrefix) : currentPath}
          </div>
          
          <div className="file-list">
            {currentFiles.length === 0 ? (
              <div className="no-files">
                {activeTab === 's3' ? 'S3에 저장된 파일이 없습니다.' : '로컬 파일이 없습니다.'}
              </div>
            ) : (
              currentFiles.map((file, index) => (
                <div 
                  key={index}
                  className={`file-item ${selectedFile && (
                    (selectedFile.key && file.key && selectedFile.key === file.key) ||
                    (selectedFile.path && file.path && selectedFile.path === file.path) ||
                    (selectedFile.name && file.name && selectedFile.name === file.name)
                  ) ? 'selected' : ''}`}
                  onClick={() => {
                    if (file.type === 'directory' || file.type === 'folder') {
                      // 디렉토리인 경우 하위 폴더 탐색
                      exploreDirectory(file);
                    } else {
                      // 파일인 경우 내용 로드
                      loadFileContent(file);
                    }
                  }}
                  onContextMenu={(e) => {
                    if (activeTab === 's3' && (file.type === 'directory' || file.type === 'folder')) {
                      e.preventDefault();
                      setContextMenu({ visible: true, x: e.clientX, y: e.clientY, folder: file });
                    }
                  }}
                >
                  <div className="file-info">
                    <span className="file-icon">
                      {(file.type === 'directory' || file.type === 'folder') ? '📁' : getFileIcon(file.name || (file.key ? file.key.split('/').pop() : 'file'))}
                    </span>
                    <span className="file-name">
                      {file.name || (file.key ? file.key.split('/').pop() : 'Unknown')}
                      {(file.type === 'directory' || file.type === 'folder') && ` (${file.children_count || 0}개 항목)`}
                    </span>
                    <span className="file-size">
                      {file.size ? `${(file.size / 1024).toFixed(1)}KB` : ''}
                    </span>
                  </div>
                  <div className="file-actions">
                    {file.type === 'file' && (
                      <button 
                        className="action-btn download-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          downloadFile(file);
                        }}
                        title="다운로드"
                      >
                        ⬇️
                      </button>
                    )}
                    {activeTab === 's3' && file.type === 'file' && (
                      <button 
                        className="action-btn delete-btn"
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteFile(file);
                        }}
                        title="삭제"
                      >
                        🗑️
                      </button>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="editor-panel">
          {selectedFile ? (
            <div className="editor-container">
              <div className="editor-header">
                <div className="file-info">
                  <span className="file-icon">{getFileIcon(selectedFile.name || selectedFile.key)}</span>
                  <span className="file-name">{selectedFile.name || selectedFile.key.split('/').pop()}</span>
                  <span className="file-language">{editorLanguage}</span>
                </div>
                <div className="editor-actions">
                  {isEditing ? (
                    <>
                      <button 
                        className="save-button"
                        onClick={saveFile}
                        disabled={loading}
                      >
                        💾 저장
                      </button>
                      <button 
                        className="save-as-button"
                        onClick={saveAsFile}
                        disabled={loading}
                        style={{ backgroundColor: '#28a745', color: 'white' }}
                      >
                        📄 다른 이름으로 저장
                      </button>
                      <button 
                        className="cancel-button"
                        onClick={() => {
                          setIsEditing(false);
                          loadFileContent(selectedFile);
                        }}
                      >
                        ❌ 취소
                      </button>
                    </>
                  ) : (
                    <button 
                      className="edit-button"
                      onClick={() => setIsEditing(true)}
                    >
                      ✏️ 편집
                    </button>
                  )}
                </div>
              </div>
              
              <div className="monaco-editor-container">
                <MonacoEditor
                  height="100%"
                  language={editorLanguage}
                  value={fileContent}
                  onChange={(value) => setFileContent(value || '')}
                  options={{
                    readOnly: !isEditing,
                    theme: 'vs-dark',
                    fontSize: 14,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    wordWrap: 'on',
                    lineNumbers: 'on',
                    folding: true,
                    selectOnLineNumbers: true,
                    roundedSelection: false,
                    cursorStyle: 'line',
                    automaticLayout: true,
                  }}
                />
              </div>
            </div>
          ) : (
            <div className="no-file-selected">
              <div className="no-file-icon">📄</div>
              <p>파일을 선택하여 내용을 확인하세요</p>
            </div>
          )}
        </div>
      </div>

      {/* 새 파일 생성 모달 */}
      {showUploadModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>새 파일 생성</h3>
              <button 
                className="close-button"
                onClick={() => setShowUploadModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>파일명:</label>
                <input
                  type="text"
                  value={newFileName}
                  onChange={(e) => setNewFileName(e.target.value)}
                  placeholder="예: test-script.js"
                />
              </div>
              <div className="form-group">
                <label>파일 내용:</label>
                <MonacoEditor
                  height="300px"
                  language={getFileLanguage(newFileName)}
                  value={newFileContent}
                  onChange={(value) => setNewFileContent(value || '')}
                  options={{
                    theme: 'vs-dark',
                    fontSize: 14,
                    minimap: { enabled: false },
                    scrollBeyondLastLine: false,
                    automaticLayout: true,
                    wordWrap: 'on',
                    lineNumbers: 'on',
                  }}
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="cancel-button"
                onClick={() => setShowUploadModal(false)}
              >
                취소
              </button>
              <button 
                className="create-button"
                onClick={createNewFile}
                disabled={!newFileName || !newFileContent || loading}
              >
                생성
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 폴더 선택 모달 (다른 이름으로 저장) */}
      {showFolderSelectModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{isLocalFileSave ? '로컬 파일을 S3에 저장' : '다른 이름으로 저장'}</h3>
              <button 
                className="close-button"
                onClick={() => {
                  setShowFolderSelectModal(false);
                  setIsLocalFileSave(false);
                }}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>파일명:</label>
                <input
                  type="text"
                  value={tempFileName}
                  onChange={(e) => setTempFileName(e.target.value)}
                  placeholder="예: new-script.js"
                />
              </div>
              <div className="form-group">
                <label>저장할 폴더:</label>
                <select
                  value={selectedFolder}
                  onChange={(e) => setSelectedFolder(e.target.value)}
                  className="folder-select"
                >
                  <option value={s3BasePrefix}>{s3BasePrefix} (루트)</option>
                  {s3Folders.map((folder, index) => (
                    <option key={index} value={folder.key}>
                      {'  '.repeat(folder.level || 0)}📁 {folder.display_name || folder.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>저장 경로 미리보기:</label>
                <div className="path-preview">
                  {selectedFolder.endsWith('/') ? selectedFolder + tempFileName : selectedFolder + '/' + tempFileName}
                </div>
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="cancel-button"
                onClick={() => {
                  setShowFolderSelectModal(false);
                  setIsLocalFileSave(false);
                }}
              >
                취소
              </button>
              <button 
                className="save-as-button"
                onClick={confirmSaveAs}
                disabled={!tempFileName || loading}
                style={{ backgroundColor: '#ff9800', color: 'white' }}
              >
                {isLocalFileSave ? '📤 S3에 저장' : '📄 저장'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* S3 폴더 컨텍스트 메뉴 */}
      {contextMenu.visible && (
        <div 
          className="context-menu"
          style={{ position: 'fixed', top: contextMenu.y, left: contextMenu.x, background: '#fff', border: '1px solid #ddd', borderRadius: 6, boxShadow: '0 4px 12px rgba(0,0,0,0.12)', zIndex: 1000 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button 
            className="context-menu-item"
            style={{ display: 'block', padding: '8px 12px', width: '180px', textAlign: 'left', background: 'transparent', border: 'none', cursor: 'pointer' }}
            onClick={saveHereToS3}
          >
            📥 여기에 저장
          </button>
        </div>
      )}

      {/* 기본 폴더 설정 모달 */}
      {showFolderSettingsModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>기본 폴더 설정</h3>
              <button 
                className="close-button"
                onClick={() => setShowFolderSettingsModal(false)}
              >
                ✕
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>S3 기본 프리픽스:</label>
                <select
                  value={s3BasePrefix}
                  onChange={(e) => setS3BasePrefix(e.target.value)}
                  className="folder-select"
                >
                  <option value={s3BasePrefix}>{s3BasePrefix}</option>
                  {s3Folders.map((folder, index) => (
                    <option key={index} value={folder.key + '/'}>
                      {'  '.repeat(folder.level || 0)}📁 {folder.display_name || folder.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>로컬 기본 경로:</label>
                <input
                  type="text"
                  value={localBasePath}
                  onChange={(e) => setLocalBasePath(e.target.value)}
                  placeholder="예: test-scripts 또는 src/tests 등"
                />
              </div>
            </div>
            <div className="modal-footer">
              <button 
                className="cancel-button"
                onClick={() => setShowFolderSettingsModal(false)}
              >
                취소
              </button>
              <button 
                className="save-button"
                onClick={async () => {
                  try {
                    const res = await axios.post(`${config.apiUrl}/api/test-scripts/s3/settings/prefix`, {
                      s3_base_prefix: s3BasePrefix
                    }, {
                      headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                      }
                    });
                    const newPrefix = res.data?.s3_base_prefix || s3BasePrefix;
                    setS3BasePrefix(newPrefix);
                    setS3PathHistory([newPrefix]);
                    await loadS3Files();
                    setShowFolderSettingsModal(false);
                  } catch (e) {
                    console.error('S3 프리픽스 저장 오류:', e);
                    alert('S3 기본 프리픽스를 저장하지 못했습니다.');
                  }
                }}
              >
                저장
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default TestScriptsManager;