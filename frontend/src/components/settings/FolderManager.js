import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './FolderManager.css';

axios.defaults.baseURL = config.apiUrl;

const FolderManager = () => {
  const [folders, setFolders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingFolder, setEditingFolder] = useState(null);
  const [newFolder, setNewFolder] = useState({
    folder_name: '',
    folder_type: 'environment',
    environment: 'dev',
    parent_folder_id: null,
    deployment_date: ''
  });
  const [folderTree, setFolderTree] = useState([]);

  useEffect(() => {
    fetchFolders();
    fetchFolderTree();
  }, []);

  const fetchFolders = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/folders');
      setFolders(response.data.items || response.data);
    } catch (err) {
      setError('폴더 목록을 불러오는 중 오류가 발생했습니다.');
      console.error('Folder fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchFolderTree = async () => {
    try {
      const response = await axios.get('/folders/tree');
      setFolderTree(response.data);
    } catch (err) {
      console.error('Folder tree fetch error:', err);
    }
  };

  const handleAddFolder = async () => {
    if (!newFolder.folder_name) {
      alert('폴더명을 입력해주세요.');
      return;
    }

    try {
      await axios.post('/folders', newFolder);
      alert('폴더가 성공적으로 추가되었습니다.');
      setShowAddModal(false);
      setNewFolder({
        folder_name: '',
        folder_type: 'environment',
        environment: 'dev',
        parent_folder_id: null,
        deployment_date: ''
      });
      fetchFolders();
    } catch (err) {
      alert('폴더 추가 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleEditFolder = async () => {
    if (!editingFolder.folder_name) {
      alert('폴더명을 입력해주세요.');
      return;
    }

    try {
      await axios.put(`/folders/${editingFolder.id}`, editingFolder);
      alert('폴더가 성공적으로 수정되었습니다.');
      setShowEditModal(false);
      setEditingFolder(null);
      fetchFolders();
    } catch (err) {
      alert('폴더 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleDeleteFolder = async (folderId) => {
    if (!window.confirm('정말로 이 폴더를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await axios.delete(`/folders/${folderId}`);
      alert('폴더가 성공적으로 삭제되었습니다.');
      fetchFolders();
    } catch (err) {
      alert('폴더 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const getParentFolderOptions = () => {
    const options = [];
    
    // 환경 폴더들 추가
    folderTree.forEach(envFolder => {
      options.push({
        id: envFolder.id,
        name: `🌍 ${envFolder.name} (환경)`,
        type: 'environment'
      });
      
      // 배포일자 폴더들 추가
      envFolder.children.forEach(depFolder => {
        options.push({
          id: depFolder.id,
          name: `📅 ${depFolder.name} (배포일자)`,
          type: 'deployment_date'
        });
        
        // 기능명 폴더들 추가
        depFolder.children.forEach(featureFolder => {
          options.push({
            id: featureFolder.id,
            name: `🔧 ${featureFolder.name} (기능명)`,
            type: 'feature'
          });
        });
      });
    });
    
    return options;
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="folder-manager">
      <div className="folder-header">
        <h2>폴더 관리</h2>
        <button 
          className="btn btn-add"
          onClick={() => setShowAddModal(true)}
        >
          ➕ 새 폴더
        </button>
      </div>

      <div className="folder-list">
        {folders.map(folder => (
          <div key={folder.id} className="folder-card">
            <div className="folder-info">
              <h3>{folder.folder_name}</h3>
              <p>타입: {
                folder.folder_type === 'environment' ? '환경' : 
                folder.folder_type === 'deployment_date' ? '배포일자' : 
                folder.folder_type === 'feature' ? '기능명' : 
                folder.folder_type ? folder.folder_type : '미분류'
              }</p>
              {folder.environment && <p>환경: {folder.environment}</p>}
              {folder.deployment_date && <p>배포일자: {folder.deployment_date}</p>}
            </div>
            <div className="folder-actions">
              <button 
                className="btn btn-edit"
                onClick={() => {
                  setEditingFolder(folder);
                  setShowEditModal(true);
                }}
              >
                ✏️ 수정
              </button>
              <button 
                className="btn btn-delete"
                onClick={() => handleDeleteFolder(folder.id)}
              >
                🗑️ 삭제
              </button>
            </div>
          </div>
        ))}
        
        {folders.length === 0 && (
          <div className="empty-state">
            <p>등록된 폴더가 없습니다.</p>
            <button 
              className="btn btn-add"
              onClick={() => setShowAddModal(true)}
            >
              첫 번째 폴더 추가하기
            </button>
          </div>
        )}
      </div>

      {/* 폴더 추가 모달 */}
      {showAddModal && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>새 폴더 추가</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowAddModal(false);
                  setNewFolder({
                    folder_name: '',
                    folder_type: 'environment',
                    environment: 'dev',
                    parent_folder_id: null,
                    deployment_date: ''
                  });
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>폴더명</label>
                <input 
                  type="text" 
                  value={newFolder.folder_name}
                  onChange={(e) => setNewFolder({...newFolder, folder_name: e.target.value})}
                  placeholder="폴더명을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>폴더 타입</label>
                <select 
                  value={newFolder.folder_type}
                  onChange={(e) => setNewFolder({...newFolder, folder_type: e.target.value})}
                >
                  <option value="environment">환경 (Environment)</option>
                  <option value="deployment_date">배포일자 (Deployment Date)</option>
                  <option value="feature">기능명 (Feature)</option>
                </select>
              </div>
              <div className="form-group">
                <label>환경</label>
                <select 
                  value={newFolder.environment}
                  onChange={(e) => setNewFolder({...newFolder, environment: e.target.value})}
                >
                  <option value="dev">DEV</option>
                  <option value="alpha">ALPHA</option>
                  <option value="production">PRODUCTION</option>
                </select>
              </div>
              <div className="form-group">
                <label>상위 폴더</label>
                <select 
                  value={newFolder.parent_folder_id || ''}
                  onChange={(e) => setNewFolder({...newFolder, parent_folder_id: e.target.value || null})}
                >
                  <option value="">없음 (최상위)</option>
                  {getParentFolderOptions().map(folder => (
                    <option key={folder.id} value={folder.id}>
                      {folder.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>배포일자</label>
                <input 
                  type="date" 
                  value={newFolder.deployment_date}
                  onChange={(e) => setNewFolder({...newFolder, deployment_date: e.target.value})}
                />
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleAddFolder}
              >
                추가
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowAddModal(false);
                  setNewFolder({
                    folder_name: '',
                    folder_type: 'environment',
                    environment: 'dev',
                    parent_folder_id: null,
                    deployment_date: ''
                  });
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 폴더 편집 모달 */}
      {showEditModal && editingFolder && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>폴더 수정</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingFolder(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>폴더명</label>
                <input 
                  type="text" 
                  value={editingFolder.folder_name}
                  onChange={(e) => setEditingFolder({...editingFolder, folder_name: e.target.value})}
                  placeholder="폴더명을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>폴더 타입</label>
                <select 
                  value={editingFolder.folder_type}
                  onChange={(e) => setEditingFolder({...editingFolder, folder_type: e.target.value})}
                >
                  <option value="environment">환경 (Environment)</option>
                  <option value="deployment_date">배포일자 (Deployment Date)</option>
                  <option value="feature">기능명 (Feature)</option>
                </select>
              </div>
              <div className="form-group">
                <label>환경</label>
                <select 
                  value={editingFolder.environment}
                  onChange={(e) => setEditingFolder({...editingFolder, environment: e.target.value})}
                >
                  <option value="dev">DEV</option>
                  <option value="alpha">ALPHA</option>
                  <option value="production">PRODUCTION</option>
                </select>
              </div>
              <div className="form-group">
                <label>상위 폴더</label>
                <select 
                  value={editingFolder.parent_folder_id || ''}
                  onChange={(e) => setEditingFolder({...editingFolder, parent_folder_id: e.target.value || null})}
                >
                  <option value="">없음 (최상위)</option>
                  {getParentFolderOptions().map(folder => (
                    <option key={folder.id} value={folder.id}>
                      {folder.name}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>배포일자</label>
                <input 
                  type="date" 
                  value={editingFolder.deployment_date}
                  onChange={(e) => setEditingFolder({...editingFolder, deployment_date: e.target.value})}
                />
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleEditFolder}
              >
                수정
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingFolder(null);
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

export default FolderManager; 