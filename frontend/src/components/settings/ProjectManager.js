import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import { useAuth } from '../../contexts/AuthContext';
import './ProjectManager.css';

axios.defaults.baseURL = config.apiUrl;

const ProjectManager = () => {
  const { user: currentUser, token } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingProject, setEditingProject] = useState(null);
  const [newProject, setNewProject] = useState({
    name: '',
    description: ''
  });

  // 권한 체크 함수들
  const canAddProject = () => {
    return currentUser?.role === 'admin';
  };
  const canEditProject = () => {
    return currentUser?.role === 'admin';
  };
  const canDeleteProject = () => {
    return currentUser?.role === 'admin';
  };

  const getErrorMessage = (err, fallback) => {
    return err?.response?.data?.error || err?.response?.data?.message || err?.message || fallback;
  };

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
    fetchProjects();
  }, [token]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      
      const response = await axios.get('/projects');
      setProjects(response.data);
    } catch (err) {
      // 오류는 조용히 처리
      setError('프로젝트 목록을 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const handleAddProject = async () => {
    if (!newProject.name) {
      alert('프로젝트명을 입력해주세요.');
      return;
    }

    try {
      await axios.post('/projects', newProject);
      alert('프로젝트가 성공적으로 추가되었습니다.');
      setShowAddModal(false);
      setNewProject({ name: '', description: '' });
      fetchProjects();
    } catch (err) {
      const message = getErrorMessage(err, '프로젝트 추가 중 오류가 발생했습니다.');
      alert(message);
    }
  };

  const handleEditProject = async () => {
    if (!editingProject.name) {
      alert('프로젝트명을 입력해주세요.');
      return;
    }

    try {
      await axios.put(`/projects/${editingProject.id}`, editingProject);
      alert('프로젝트가 성공적으로 수정되었습니다.');
      setShowEditModal(false);
      setEditingProject(null);
      fetchProjects();
    } catch (err) {
      const message = getErrorMessage(err, '프로젝트 수정 중 오류가 발생했습니다.');
      alert(message);
    }
  };

  const handleDeleteProject = async (projectId) => {
    if (!window.confirm('정말로 이 프로젝트를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await axios.delete(`/projects/${projectId}`);
      alert('프로젝트가 성공적으로 삭제되었습니다.');
      fetchProjects();
    } catch (err) {
      const message = getErrorMessage(err, '프로젝트 삭제 중 오류가 발생했습니다.');
      alert(message);
    }
  };

  if (loading) {
    return <div className="loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="error">{error}</div>;
  }

  return (
    <div className="project-manager">
      <div className="project-header">
        <h2>프로젝트 관리</h2>
        {canAddProject() && (
          <button 
            className="btn btn-add"
            onClick={() => setShowAddModal(true)}
          >
            ➕ 새 프로젝트
          </button>
        )}
      </div>

      <div className="project-list">
        {projects.map(project => (
          <div key={project.id} className="project-card">
            <div className="project-info">
              <h3>{project.name}</h3>
              <p>{project.description || '설명 없음'}</p>
            </div>
            <div className="project-actions">
              {canEditProject() && (
                <button 
                  className="btn btn-edit"
                  onClick={() => {
                    setEditingProject(project);
                    setShowEditModal(true);
                  }}
                >
                  ✏️ 수정
                </button>
              )}
              {canDeleteProject() && (
                <button 
                  className="btn btn-delete"
                  onClick={() => handleDeleteProject(project.id)}
                >
                  🗑️ 삭제
                </button>
              )}
            </div>
          </div>
        ))}
        
        {projects.length === 0 && (
          <div className="empty-state">
            <p>등록된 프로젝트가 없습니다.</p>
            {canAddProject() && (
              <button 
                className="btn btn-add"
                onClick={() => setShowAddModal(true)}
              >
                첫 번째 프로젝트 추가하기
              </button>
            )}
          </div>
        )}
      </div>

      {/* 프로젝트 추가 모달 */}
      {showAddModal && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>새 프로젝트 추가</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowAddModal(false);
                  setNewProject({ name: '', description: '' });
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>프로젝트명</label>
                <input 
                  type="text" 
                  value={newProject.name}
                  onChange={(e) => setNewProject({...newProject, name: e.target.value})}
                  placeholder="프로젝트명을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea 
                  value={newProject.description}
                  onChange={(e) => setNewProject({...newProject, description: e.target.value})}
                  placeholder="프로젝트 설명을 입력하세요"
                  rows="5"
                />
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleAddProject}
              >
                추가
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowAddModal(false);
                  setNewProject({ name: '', description: '' });
                }}
              >
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 프로젝트 편집 모달 */}
      {showEditModal && editingProject && (
        <div className="modal-overlay fullscreen-modal">
          <div className="modal fullscreen-modal-content">
            <div className="modal-header">
              <h3>프로젝트 수정</h3>
              <button 
                className="modal-close"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingProject(null);
                }}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>프로젝트명</label>
                <input 
                  type="text" 
                  value={editingProject.name}
                  onChange={(e) => setEditingProject({...editingProject, name: e.target.value})}
                  placeholder="프로젝트명을 입력하세요"
                />
              </div>
              <div className="form-group">
                <label>설명</label>
                <textarea 
                  value={editingProject.description}
                  onChange={(e) => setEditingProject({...editingProject, description: e.target.value})}
                  placeholder="프로젝트 설명을 입력하세요"
                  rows="5"
                />
              </div>
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleEditProject}
              >
                수정
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowEditModal(false);
                  setEditingProject(null);
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

export default ProjectManager; 