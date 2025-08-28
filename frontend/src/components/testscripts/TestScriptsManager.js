import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { tomorrow } from 'react-syntax-highlighter/dist/esm/styles/prism';
import './TestScriptsManager.css';

// 파일/폴더 아이템 컴포넌트 (테스트 케이스 폴더 트리 형태)
const FileTreeItem = ({ item, level = 0, onFileClick, getFileIcon, getFolderIcon }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(false);

  const isDirectory = item.type === 'directory';

  const toggleExpanded = async () => {
    if (!isDirectory) return;
    
    if (isExpanded) {
      setIsExpanded(false);
      return;
    }

    if (children.length === 0 && !loading) {
      await loadChildren();
    }
    setIsExpanded(true);
  };

  const loadChildren = async () => {
    try {
      setLoading(true);
      
      // 절대 경로를 상대 경로로 변환
      let relativePath = item.path;
      if (item.path.includes('test-scripts')) {
        // test-scripts 이후의 경로만 추출
        const testScriptsIndex = item.path.indexOf('test-scripts');
        relativePath = item.path.substring(testScriptsIndex);
      }
      
      // 개발 환경에서만 로그 출력
      if (process.env.NODE_ENV === 'development') {
        console.log('요청 경로:', relativePath);
      }
      const response = await axios.get(`/api/test-scripts/explore?path=${encodeURIComponent(relativePath)}`);
      if (process.env.NODE_ENV === 'development') {
        console.log('백엔드 응답:', response.data);
      }
      setChildren(response.data.children || []);
    } catch (err) {
      console.error('하위 항목 로드 오류:', err);
      setChildren([]);
    } finally {
      setLoading(false);
    }
  };

  const handleItemClick = () => {
    if (isDirectory) {
      toggleExpanded();
    } else {
      // 파일 클릭 시 콜백 호출
      onFileClick(item);
    }
  };

  return (
    <div className="file-tree-item" style={{ marginLeft: level * 20 }}>
      <div 
        className={`folder-item ${isDirectory ? 'clickable' : ''}`}
        onClick={handleItemClick}
      >
        {isDirectory && (
          <span 
            className={`folder-toggle ${isExpanded ? 'expanded' : ''}`}
            onClick={(e) => {
              e.stopPropagation();
              toggleExpanded();
            }}
          >
            {loading ? '⏳' : isExpanded ? '▼' : '▶'}
          </span>
        )}
        <span className="folder-icon">
          {isDirectory ? getFolderIcon(item.name) : getFileIcon(item.name)}
        </span>
        <span className="folder-name">{item.name}</span>
        {!isDirectory && (
          <span className="file-size">
            {item.size ? `(${(item.size / 1024).toFixed(1)} KB)` : ''}
          </span>
        )}
      </div>
      
      {isDirectory && isExpanded && children.length > 0 && (
        <div className="folder-children expanded">
          {children.map((child, index) => (
            <FileTreeItem 
              key={`${child.path}-${index}`} 
              item={child} 
              level={level + 1}
              onFileClick={onFileClick}
              getFileIcon={getFileIcon}
              getFolderIcon={getFolderIcon}
            />
          ))}
        </div>
      )}
    </div>
  );
};

// 테스트 스크립트 매니저 메인 컴포넌트
const TestScriptsManager = () => {
  const [rootItems, setRootItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileContent, setFileContent] = useState(null);
  const [activeCategory, setActiveCategory] = useState('all'); // 'all', 'performance', 'playwright'

  // 파일 타입에 따른 아이콘 반환
  const getFileIcon = (filename) => {
    if (filename.endsWith('.js')) return '📄';
    if (filename.endsWith('.py')) return '🐍';
    if (filename.endsWith('.spec.js')) return '🧪';
    if (filename.endsWith('.json')) return '⚙️';
    if (filename.endsWith('.md')) return '📝';
    if (filename.endsWith('.png') || filename.endsWith('.jpg') || filename.endsWith('.jpeg')) return '🖼️';
    if (filename.endsWith('.DS_Store')) return '🗑️';
    return '📄';
  };

  // 파일 타입에 따른 언어 감지
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

  // 파일 타입에 따른 에디터 테마
  const getEditorTheme = (filename) => {
    const language = getFileLanguage(filename);
    if (['javascript', 'typescript', 'jsx', 'tsx'].includes(language)) return 'javascript';
    if (language === 'python') return 'python';
    if (language === 'json') return 'json';
    if (language === 'markdown') return 'markdown';
    if (language === 'html') return 'html';
    if (language === 'css') return 'css';
    return 'plaintext';
  };

  // 폴더 타입에 따른 아이콘 반환
  const getFolderIcon = (folderName) => {
    if (folderName === 'performance') return '⚡';
    if (folderName === 'playwright') return '🎭';
    if (folderName === 'screenshots') return '📸';
    if (folderName === 'Result') return '📊';
    if (folderName === 'python') return '🐍';
    if (folderName === 'clm') return '📋';
    if (folderName === 'advice') return '💡';
    if (folderName === 'login') return '🔐';
    if (folderName === 'litigation') return '⚖️';
    if (folderName === 'dashboard') return '📊';
    if (folderName === 'common') return '🔧';
    if (folderName === 'url') return '🔗';
    if (folderName === 'nomerl') return '📝';
    if (folderName === 'multi') return '🔄';
    if (folderName === 'dist' || folderName === 'build') return '🏗️';
    if (folderName === '__pycache__') return '💾';
    return '📁';
  };

  useEffect(() => {
    loadRootStructure();
  }, []);

  const loadRootStructure = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // 백엔드에서 루트 구조 로드
      if (process.env.NODE_ENV === 'development') {
        console.log('백엔드 API 호출 시도...');
      }
      const response = await axios.get('/api/test-scripts/explore');
      if (process.env.NODE_ENV === 'development') {
        console.log('백엔드 응답:', response.data);
      }
      setRootItems(response.data.children || []);
    } catch (err) {
      console.error('테스트 스크립트 구조 로드 오류:', err);
      setError(`백엔드 연결 실패: ${err.message}`);
      
      // 오류 시 기본 구조 표시 (정적 데이터)
      if (process.env.NODE_ENV === 'development') {
        console.log('정적 데이터로 폴더 구조 표시');
      }
      setRootItems([
        {
          name: 'performance',
          type: 'directory',
          path: 'test-scripts/performance',
          children_count: 12
        },
        {
          name: 'playwright',
          type: 'directory',
          path: 'test-scripts/playwright',
          children_count: 1
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleFileClick = async (file) => {
    try {
      // 절대 경로를 상대 경로로 변환
      let relativePath = file.path;
      if (file.path.includes('test-scripts')) {
        // test-scripts 이후의 경로만 추출
        const testScriptsIndex = file.path.indexOf('test-scripts');
        relativePath = file.path.substring(testScriptsIndex);
      }
      
      // 개발 환경에서만 로그 출력
      if (process.env.NODE_ENV === 'development') {
        console.log('파일 요청 경로:', relativePath);
      }
      const response = await axios.get(`/api/test-scripts/file-content?path=${encodeURIComponent(relativePath)}`);
      setFileContent({
        path: file.path,
        content: response.data.content,
        size: response.data.size
      });
      setSelectedFile(file);
    } catch (err) {
      console.error('파일 내용 로드 오류:', err);
      alert('파일 내용을 불러올 수 없습니다.');
    }
  };

  const closeFileView = () => {
    setFileContent(null);
    setSelectedFile(null);
  };

  const getFilteredItems = () => {
    if (activeCategory === 'all') {
      return rootItems;
    } else if (activeCategory === 'performance') {
      return rootItems.filter(item => item.name === 'performance');
    } else if (activeCategory === 'playwright') {
      return rootItems.filter(item => item.name === 'playwright');
    }
    return rootItems;
  };

  if (loading) {
    return (
      <div className="test-scripts-manager">
        <div className="manager-header">
          <h2>📁 테스트 스크립트</h2>
        </div>
        <div className="loading-container">
          <div className="loading-spinner">⏳</div>
          <p>테스트 스크립트 구조를 불러오는 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="test-scripts-manager">
        <div className="manager-header">
          <h2>📁 테스트 스크립트</h2>
          <button className="btn btn-refresh" onClick={loadRootStructure}>
            🔄 새로고침
          </button>
        </div>
        <div className="error-container">
          <p className="error-message">❌ {error}</p>
          <p className="error-note">
            현재 정적 데이터로 표시됩니다. 백엔드 연결을 확인해주세요.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="test-scripts-manager">
      <div className="manager-header">
        <h2>📁 테스트 스크립트</h2>
        <div className="header-actions">
          <button className="btn btn-refresh" onClick={loadRootStructure}>
            🔄 새로고침
          </button>
        </div>
      </div>

      {/* 카테고리 필터 */}
      <div className="category-filter">
        <button 
          className={`category-btn ${activeCategory === 'all' ? 'active' : ''}`}
          onClick={() => setActiveCategory('all')}
        >
          📂 전체
        </button>
        <button 
          className={`category-btn ${activeCategory === 'performance' ? 'active' : ''}`}
          onClick={() => setActiveCategory('performance')}
        >
          ⚡ 성능 테스트
        </button>
        <button 
          className={`category-btn ${activeCategory === 'playwright' ? 'active' : ''}`}
          onClick={() => setActiveCategory('playwright')}
        >
          🎭 자동화 테스트
        </button>
      </div>

      <div className="manager-content">
        <div className="file-tree-container">
          <div className="tree-header">
            <h3>📂 폴더 구조</h3>
            <p className="tree-description">
              테스트 스크립트를 폴더별로 탐색할 수 있습니다.
            </p>
          </div>
          
          <div className="folder-tree">
            {getFilteredItems().map((item, index) => (
              <FileTreeItem 
                key={`${item.path}-${index}`} 
                item={item}
                getFileIcon={getFileIcon}
                getFolderIcon={getFolderIcon}
                onFileClick={handleFileClick}
              />
            ))}
          </div>
        </div>

        {fileContent && (
          <div className="file-view-container">
            <div className="file-view-header">
              <div className="file-header-info">
                <span className="file-type-icon">
                  {getFileIcon(fileContent.path.split('/').pop())}
                </span>
                <h3>📄 {fileContent.path.split('/').pop()}</h3>
                <span className="file-language-badge">
                  {getFileLanguage(fileContent.path)}
                </span>
              </div>
              <button className="btn btn-close" onClick={closeFileView}>
                ✕
              </button>
            </div>
            <div className="file-content">
              <div className="code-editor">
                <SyntaxHighlighter 
                  language={getFileLanguage(fileContent.path)} 
                  style={tomorrow}
                  customStyle={{
                    margin: 0,
                    borderRadius: '8px',
                    fontSize: '13px',
                    lineHeight: '1.5'
                  }}
                  showLineNumbers={true}
                  wrapLines={true}
                >
                  {fileContent.content}
                </SyntaxHighlighter>
              </div>
              <div className="file-info">
                <div className="file-stats">
                  <span className="stat-item">
                    <strong>크기:</strong> {(fileContent.size / 1024).toFixed(1)} KB
                  </span>
                  <span className="stat-item">
                    <strong>언어:</strong> {getFileLanguage(fileContent.path)}
                  </span>
                  <span className="stat-item">
                    <strong>경로:</strong> {fileContent.path}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      <div className="manager-footer">
        <div className="footer-info">
          <p>
            <strong>📊 Performance:</strong> K6 성능 테스트 스크립트
          </p>
          <p>
            <strong>🎭 Playwright:</strong> 자동화 테스트 스크립트
          </p>
        </div>
      </div>
    </div>
  );
};

export default TestScriptsManager;
