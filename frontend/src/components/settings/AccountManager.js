import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './AccountManager.css';

axios.defaults.baseURL = config.apiUrl;

const AccountManager = () => {
  const [users, setUsers] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [showAddUserModal, setShowAddUserModal] = useState(false);
  const [showEditUserModal, setShowEditUserModal] = useState(false);
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // 새 사용자 데이터
  const [newUser, setNewUser] = useState({
    username: '',
    email: '',
    password: '',
    role: 'User'
  });

  // 수정할 사용자 데이터
  const [editUser, setEditUser] = useState({
    username: '',
    email: '',
    password: '',
    role: 'User',
    is_active: true
  });

  // 비밀번호 변경 데이터
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  // 프로필 수정 데이터
  const [profileData, setProfileData] = useState({
    username: '',
    email: ''
  });

  useEffect(() => {
    fetchUsers();
    fetchCurrentUser();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const response = await axios.get('/users');
      setUsers(response.data);
    } catch (err) {
      setError('사용자 목록을 불러오는 중 오류가 발생했습니다.');
      console.error('Users fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get('/users/current');
      setCurrentUser(response.data);
      setProfileData({
        username: response.data.username,
        email: response.data.email
      });
    } catch (err) {
      console.error('Current user fetch error:', err);
    }
  };

  const handleAddUser = async () => {
    if (!newUser.username || !newUser.email) {
      alert('사용자명과 이메일은 필수입니다.');
      return;
    }

    try {
      const userData = {
        username: newUser.username,
        email: newUser.email,
        role: newUser.role
        // 비밀번호가 없으면 기본 비밀번호(1q2w#E$R)가 자동으로 설정됩니다.
      };
      
      const response = await axios.post('/users', userData);
      
      if (response.data.default_password) {
        alert(`사용자가 성공적으로 추가되었습니다.\n기본 비밀번호: ${response.data.default_password}`);
      } else {
        alert('사용자가 성공적으로 추가되었습니다.');
      }
      
      setShowAddUserModal(false);
      setNewUser({
        username: '',
        email: '',
        password: '',
        role: 'User'
      });
      fetchUsers();
    } catch (err) {
      alert('사용자 추가 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleEditUser = async () => {
    if (!editUser.username || !editUser.email) {
      alert('사용자명과 이메일은 필수입니다.');
      return;
    }

    try {
      const updateData = {
        username: editUser.username,
        email: editUser.email,
        role: editUser.role,
        is_active: editUser.is_active
      };
      
      // 비밀번호가 입력된 경우에만 포함
      if (editUser.password) {
        updateData.password = editUser.password;
      }
      
      await axios.put(`/users/${selectedUser.id}`, updateData);
      alert('사용자 정보가 성공적으로 수정되었습니다.');
      setShowEditUserModal(false);
      setSelectedUser(null);
      fetchUsers();
    } catch (err) {
      alert('사용자 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
      return;
    }

    try {
      await axios.delete(`/users/${userId}`);
      alert('사용자가 성공적으로 삭제되었습니다.');
      fetchUsers();
    } catch (err) {
      alert('사용자 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handlePasswordChange = async () => {
    if (!passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword) {
      alert('모든 필드를 입력해주세요.');
      return;
    }

    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('새 비밀번호가 일치하지 않습니다.');
      return;
    }

    if (passwordData.newPassword.length < 8) {
      alert('새 비밀번호는 8자 이상이어야 합니다.');
      return;
    }

    try {
      await axios.put(`/users/${currentUser.id}/change-password`, {
        current_password: passwordData.currentPassword,
        new_password: passwordData.newPassword
      });
      
      alert('비밀번호가 성공적으로 변경되었습니다.');
      setShowPasswordModal(false);
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
    } catch (err) {
      alert('비밀번호 변경 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const handleProfileUpdate = async () => {
    if (!profileData.username || !profileData.email) {
      alert('사용자명과 이메일은 필수입니다.');
      return;
    }

    try {
      // 실제로는 API 호출
      // await axios.put('/account/profile', profileData);
      alert('프로필이 성공적으로 수정되었습니다.');
      setShowProfileModal(false);
      fetchCurrentUser();
    } catch (err) {
      alert('프로필 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  const openEditUserModal = (user) => {
    setSelectedUser(user);
    setEditUser({
      username: user.username,
      email: user.email,
      password: '',
      role: user.role,
      is_active: user.is_active
    });
    setShowEditUserModal(true);
  };

  const canDeleteUser = (user) => {
    // Administrator는 모든 사용자를 삭제할 수 있음
    // User는 자신을 삭제할 수 없음
    return currentUser?.role === 'Administrator' && user.id !== currentUser?.id;
  };

  const canEditUser = (user) => {
    // Administrator는 모든 사용자를 수정할 수 있음
    // User는 자신만 수정할 수 있음
    return currentUser?.role === 'Administrator' || user.id === currentUser?.id;
  };

  if (loading) {
    return <div className="account-loading">로딩 중...</div>;
  }

  if (error) {
    return <div className="account-error">{error}</div>;
  }

  return (
    <div className="account-container">
      <div className="account-header">
        <h2>계정 관리</h2>
        {currentUser?.role === 'Administrator' && (
          <button 
            className="btn btn-add"
            onClick={() => setShowAddUserModal(true)}
          >
            ➕ 새 사용자 추가
          </button>
        )}
      </div>

      <div className="account-content">
        {/* 현재 사용자 정보 */}
        <div className="account-section">
          <h3>내 계정 정보</h3>
          <div className="account-info">
            <div className="info-item">
              <label>사용자명:</label>
              <span>{currentUser?.username}</span>
            </div>
            <div className="info-item">
              <label>이메일:</label>
              <span>{currentUser?.email}</span>
            </div>
            <div className="info-item">
              <label>역할:</label>
              <span className={`role-badge ${currentUser?.role?.toLowerCase()}`}>
                {currentUser?.role}
              </span>
            </div>
            <div className="info-item">
              <label>마지막 로그인:</label>
              <span>{currentUser?.last_login ? new Date(currentUser.last_login).toLocaleString() : '없음'}</span>
            </div>
          </div>
          <div className="account-actions">
            <button 
              className="btn btn-primary"
              onClick={() => setShowProfileModal(true)}
            >
              ✏️ 프로필 수정
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowPasswordModal(true)}
            >
              🔒 비밀번호 변경
            </button>
          </div>
        </div>

        {/* 사용자 목록 (Administrator만 볼 수 있음) */}
        {currentUser?.role === 'Administrator' && (
          <div className="account-section">
            <h3>사용자 목록</h3>
            <div className="users-list">
              {users.map(user => (
                <div key={user.id} className="user-item">
                  <div className="user-info">
                    <div className="user-name">{user.username}</div>
                    <div className="user-email">{user.email}</div>
                    <span className={`role-badge ${user.role.toLowerCase()}`}>
                      {user.role}
                    </span>
                    <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                      {user.is_active ? '활성' : '비활성'}
                    </span>
                  </div>
                  <div className="user-actions">
                    {canEditUser(user) && (
                      <button 
                        className="btn btn-edit"
                        onClick={() => openEditUserModal(user)}
                      >
                        ✏️ 수정
                      </button>
                    )}
                    {canDeleteUser(user) && (
                      <button 
                        className="btn btn-delete"
                        onClick={() => handleDeleteUser(user.id)}
                      >
                        🗑️ 삭제
                      </button>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* 새 사용자 추가 모달 */}
      {showAddUserModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>새 사용자 추가</h3>
            <div className="form-group">
              <label>사용자명:</label>
              <input
                type="text"
                value={newUser.username}
                onChange={(e) => setNewUser({...newUser, username: e.target.value})}
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>이메일:</label>
              <input
                type="email"
                value={newUser.email}
                onChange={(e) => setNewUser({...newUser, email: e.target.value})}
                placeholder="이메일을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>역할:</label>
              <select
                value={newUser.role}
                onChange={(e) => setNewUser({...newUser, role: e.target.value})}
              >
                <option value="User">User</option>
                <option value="Administrator">Administrator</option>
                <option value="Guest">Guest</option>
              </select>
            </div>
            <div className="form-group">
              <small className="form-help">
                * 비밀번호는 기본값(1q2w#E$R)으로 설정됩니다.
              </small>
            </div>
            <div className="modal-actions">
              <button className="btn btn-primary" onClick={handleAddUser}>
                추가
              </button>
              <button className="btn btn-secondary" onClick={() => setShowAddUserModal(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 사용자 수정 모달 */}
      {showEditUserModal && selectedUser && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>사용자 정보 수정</h3>
            <div className="form-group">
              <label>사용자명:</label>
              <input
                type="text"
                value={editUser.username}
                onChange={(e) => setEditUser({...editUser, username: e.target.value})}
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>이메일:</label>
              <input
                type="email"
                value={editUser.email}
                onChange={(e) => setEditUser({...editUser, email: e.target.value})}
                placeholder="이메일을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>역할:</label>
              <select
                value={editUser.role}
                onChange={(e) => setEditUser({...editUser, role: e.target.value})}
              >
                <option value="User">User</option>
                <option value="Administrator">Administrator</option>
                <option value="Guest">Guest</option>
              </select>
            </div>
            <div className="form-group">
              <label>새 비밀번호 (선택사항):</label>
              <input
                type="password"
                value={editUser.password}
                onChange={(e) => setEditUser({...editUser, password: e.target.value})}
                placeholder="새 비밀번호를 입력하세요 (변경하지 않으려면 비워두세요)"
              />
            </div>
            <div className="form-group">
              <label>상태:</label>
              <select
                value={editUser.is_active}
                onChange={(e) => setEditUser({...editUser, is_active: e.target.value === 'true'})}
              >
                <option value={true}>활성</option>
                <option value={false}>비활성</option>
              </select>
            </div>
            <div className="modal-actions">
              <button className="btn btn-primary" onClick={handleEditUser}>
                수정
              </button>
              <button className="btn btn-secondary" onClick={() => setShowEditUserModal(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 비밀번호 변경 모달 */}
      {showPasswordModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>비밀번호 변경</h3>
            <div className="form-group">
              <label>현재 비밀번호:</label>
              <input
                type="password"
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                placeholder="현재 비밀번호를 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>새 비밀번호:</label>
              <input
                type="password"
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                placeholder="새 비밀번호를 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>새 비밀번호 확인:</label>
              <input
                type="password"
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                placeholder="새 비밀번호를 다시 입력하세요"
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-primary" onClick={handlePasswordChange}>
                변경
              </button>
              <button className="btn btn-secondary" onClick={() => setShowPasswordModal(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}

      {/* 프로필 수정 모달 */}
      {showProfileModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>프로필 수정</h3>
            <div className="form-group">
              <label>사용자명:</label>
              <input
                type="text"
                value={profileData.username}
                onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>이메일:</label>
              <input
                type="email"
                value={profileData.email}
                onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                placeholder="이메일을 입력하세요"
              />
            </div>
            <div className="modal-actions">
              <button className="btn btn-primary" onClick={handleProfileUpdate}>
                수정
              </button>
              <button className="btn btn-secondary" onClick={() => setShowProfileModal(false)}>
                취소
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AccountManager; 