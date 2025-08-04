import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './FolderManager.css';

const FolderManager = () => {
  const [folders, setFolders] = useState([]);
  const [folderTree, setFolderTree] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingFolder, setEditingFolder] = useState(null);
  const [editFormData, setEditFormData] = useState({
    folder_name: '',
    parent_folder_id: null,
    folder_type: 'environment',
    environment: 'dev',
    deployment_date: ''
  });
  const [formData, setFormData] = useState({
    folder_name: '',
    parent_folder_id: null,
    folder_type: 'environment',
    environment: 'dev',
    deployment_date: ''
  });

  useEffect(() => {
    fetchFolders();
    fetchFolderTree();
  }, []);

  const fetchFolders = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/folders');
      setFolders(response.data);
      setError(null);
    } catch (err) {
      console.error('폴더 조회 오류:', err);
      setError('폴더 조회 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const fetchFolderTree = async () => {
    try {
      const response = await axios.get('/folders/tree');
      setFolderTree(response.data);
    } catch (err) {
      console.error('폴더 트리 조회 오류:', err);
    }
  };

  const handleCreateFolder = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post('/folders', formData);
      console.log('폴더 생성 완료:', response.data);
      setShowCreateForm(false);
      setFormData({
        folder_name: '',
        parent_folder_id: null,
        folder_type: 'environment',
        environment: 'dev',
        deployment_date: ''
      });
      fetchFolders();
      fetchFolderTree();
    } catch (err) {
      console.error('폴더 생성 오류:', err);
      setError(err.response?.data?.error || '폴더 생성 중 오류가 발생했습니다.');
    }
  };

  const handleUpdateFolder = async (id) => {
    try {
      await axios.put(`/folders/${id}`, editFormData);
      console.log('폴더 수정 완료');
      setEditingFolder(null);
      setEditFormData({
        folder_name: '',
        parent_folder_id: null,
        folder_type: 'environment',
        environment: 'dev',
        deployment_date: ''
      });
      fetchFolders();
      fetchFolderTree();
    } catch (err) {
      console.error('폴더 수정 오류:', err);
      setError(err.response?.data?.error || '폴더 수정 중 오류가 발생했습니다.');
    }
  };

  const handleDeleteFolder = async (id) => {
    if (!window.confirm('정말로 이 폴더를 삭제하시겠습니까?')) {
      return;
    }
    
    try {
      await axios.delete(`/folders/${id}`);
      console.log('폴더 삭제 완료');
      fetchFolders();
      fetchFolderTree();
    } catch (err) {
      console.error('폴더 삭제 오류:', err);
      setError(err.response?.data?.error || '폴더 삭제 중 오류가 발생했습니다.');
    }
  };

  const renderFolderTree = (nodes, level = 0) => {
    return nodes.map((node) => (
      <div key={node.id} style={{ marginLeft: level * 20 }}>
        <div className="folder-node">
          <span className="folder-icon">
            {node.type === 'environment' ? '🌍' : 
             node.type === 'deployment_date' ? '📅' : '📄'}
          </span>
          <span className="folder-name">{node.name}</span>
          <div className="folder-actions">
                         {node.type !== 'test_case' && (
               <>
                 <button 
                   className="btn-edit"
                   onClick={() => {
                     setEditingFolder(node);
                     setEditFormData({
                       folder_name: node.name,
                       parent_folder_id: node.parent_folder_id || null,
                       folder_type: node.type,
                       environment: node.environment || 'dev',
                       deployment_date: node.deployment_date || ''
                     });
                   }}
                 >
                   수정
                 </button>
                 <button 
                   className="btn-delete"
                   onClick={() => handleDeleteFolder(node.id)}
                 >
                   삭제
                 </button>
               </>
             )}
          </div>
        </div>
        {node.children && node.children.length > 0 && (
          <div className="folder-children">
            {renderFolderTree(node.children, level + 1)}
          </div>
        )}
      </div>
    ));
  };

  if (loading) {
    return <div className="loading">폴더 정보를 불러오는 중...</div>;
  }

  return (
    <div className="folder-manager">
      <div className="folder-header">
        <h2>📁 폴더 관리</h2>
        <button 
          className="btn-create"
          onClick={() => setShowCreateForm(true)}
        >
          + 새 폴더 생성
        </button>
      </div>

      {error && (
        <div className="error-message">
          {error}
          <button onClick={() => setError(null)}>✕</button>
        </div>
      )}

      {showCreateForm && (
        <div className="create-form">
          <h3>새 폴더 생성</h3>
          <form onSubmit={handleCreateFolder}>
            <div className="form-group">
              <label>폴더명 *</label>
              <input
                type="text"
                value={formData.folder_name}
                onChange={(e) => setFormData({...formData, folder_name: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label>폴더 타입</label>
              <select
                value={formData.folder_type}
                onChange={(e) => setFormData({...formData, folder_type: e.target.value})}
              >
                <option value="environment">환경 (Environment)</option>
                <option value="deployment_date">배포일자 (Deployment Date)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>환경</label>
              <select
                value={formData.environment}
                onChange={(e) => setFormData({...formData, environment: e.target.value})}
              >
                <option value="dev">DEV</option>
                <option value="alpha">ALPHA</option>
                <option value="production">PRODUCTION</option>
              </select>
            </div>
            
            {formData.folder_type === 'deployment_date' && (
              <div className="form-group">
                <label>배포일자</label>
                <input
                  type="date"
                  value={formData.deployment_date}
                  onChange={(e) => setFormData({...formData, deployment_date: e.target.value})}
                />
              </div>
            )}
            
            <div className="form-group">
              <label>상위 폴더</label>
              <select
                value={formData.parent_folder_id || ''}
                onChange={(e) => setFormData({...formData, parent_folder_id: e.target.value ? parseInt(e.target.value) : null})}
              >
                <option value="">없음 (최상위)</option>
                {folders.map(folder => (
                  <option key={folder.id} value={folder.id}>
                    {folder.folder_name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-actions">
              <button type="submit" className="btn-submit">생성</button>
              <button 
                type="button" 
                className="btn-cancel"
                onClick={() => setShowCreateForm(false)}
              >
                취소
              </button>
            </div>
          </form>
        </div>
      )}

      {editingFolder && (
        <div className="edit-form">
          <h3>폴더 수정</h3>
          <form onSubmit={(e) => { e.preventDefault(); handleUpdateFolder(editingFolder.id); }}>
            <div className="form-group">
              <label>폴더명 *</label>
              <input
                type="text"
                value={editFormData.folder_name}
                onChange={(e) => setEditFormData({...editFormData, folder_name: e.target.value})}
                required
              />
            </div>
            
            <div className="form-group">
              <label>폴더 타입</label>
              <select
                value={editFormData.folder_type}
                onChange={(e) => setEditFormData({...editFormData, folder_type: e.target.value})}
              >
                <option value="environment">환경 (Environment)</option>
                <option value="deployment_date">배포일자 (Deployment Date)</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>환경</label>
              <select
                value={editFormData.environment}
                onChange={(e) => setEditFormData({...editFormData, environment: e.target.value})}
              >
                <option value="dev">DEV</option>
                <option value="alpha">ALPHA</option>
                <option value="production">PRODUCTION</option>
              </select>
            </div>
            
            {editFormData.folder_type === 'deployment_date' && (
              <div className="form-group">
                <label>배포일자</label>
                <input
                  type="date"
                  value={editFormData.deployment_date}
                  onChange={(e) => setEditFormData({...editFormData, deployment_date: e.target.value})}
                />
              </div>
            )}
            
            <div className="form-group">
              <label>상위 폴더</label>
              <select
                value={editFormData.parent_folder_id || ''}
                onChange={(e) => setEditFormData({...editFormData, parent_folder_id: e.target.value ? parseInt(e.target.value) : null})}
              >
                <option value="">없음 (최상위)</option>
                {folders.filter(f => f.id !== editingFolder.id).map(folder => (
                  <option key={folder.id} value={folder.id}>
                    {folder.folder_name}
                  </option>
                ))}
              </select>
            </div>
            
            <div className="form-actions">
              <button type="submit" className="btn-submit">수정</button>
              <button 
                type="button" 
                className="btn-cancel"
                onClick={() => {
                  setEditingFolder(null);
                  setEditFormData({
                    folder_name: '',
                    parent_folder_id: null,
                    folder_type: 'environment',
                    environment: 'dev',
                    deployment_date: ''
                  });
                }}
              >
                취소
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="folder-content">
        <div className="folder-tree">
          <h3>📂 폴더 구조</h3>
          {folderTree.length > 0 ? (
            renderFolderTree(folderTree)
          ) : (
            <p>폴더가 없습니다. 새 폴더를 생성해보세요.</p>
          )}
        </div>
        
        <div className="folder-list">
          <h3>📋 폴더 목록</h3>
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>폴더명</th>
                <th>타입</th>
                <th>환경</th>
                <th>배포일자</th>
                <th>작업</th>
              </tr>
            </thead>
            <tbody>
              {folders.map(folder => (
                <tr key={folder.id}>
                  <td>{folder.id}</td>
                  <td>{folder.folder_name}</td>
                  <td>{folder.folder_type}</td>
                  <td>{folder.environment}</td>
                  <td>{folder.deployment_date || '-'}</td>
                  <td>
                                       <button 
                     className="btn-edit-small"
                     onClick={() => {
                       setEditingFolder(folder);
                       setEditFormData({
                         folder_name: folder.folder_name,
                         parent_folder_id: folder.parent_folder_id,
                         folder_type: folder.folder_type,
                         environment: folder.environment,
                         deployment_date: folder.deployment_date || ''
                       });
                     }}
                   >
                     수정
                   </button>
                    <button 
                      className="btn-delete-small"
                      onClick={() => handleDeleteFolder(folder.id)}
                    >
                      삭제
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default FolderManager; 