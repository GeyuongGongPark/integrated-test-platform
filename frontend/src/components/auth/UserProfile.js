import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { formatUTCToKST } from '../../utils/dateUtils';
import './Auth.css';

const UserProfile = () => {
  const { user, changePassword, logout } = useAuth();
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handlePasswordChange = (e) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value
    });
  };

  const validatePasswordForm = () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setMessage({ type: 'error', text: '새 비밀번호가 일치하지 않습니다.' });
      return false;
    }
    
    if (passwordData.newPassword.length < 8) {
      setMessage({ type: 'error', text: '새 비밀번호는 최소 8자 이상이어야 합니다.' });
      return false;
    }
    
    return true;
  };

  const handlePasswordSubmit = async (e) => {
    e.preventDefault();
    
    if (!validatePasswordForm()) {
      return;
    }
    
    setLoading(true);
    setMessage({ type: '', text: '' });

    const result = await changePassword(passwordData.currentPassword, passwordData.newPassword);
    
    if (result.success) {
      setMessage({ type: 'success', text: result.message });
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setShowPasswordForm(false);
    } else {
      setMessage({ type: 'error', text: result.error });
    }
    
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h2>👤 사용자 프로필</h2>
          <p>계정 정보를 확인하고 관리하세요</p>
        </div>

        <div className="profile-info">
          <div className="profile-field">
            <label>사용자명:</label>
            <span>{user?.username}</span>
          </div>
          
          <div className="profile-field">
            <label>이메일:</label>
            <span>{user?.email}</span>
          </div>
          
          <div className="profile-field">
            <label>이름:</label>
            <span>{user?.first_name || '미설정'}</span>
          </div>
          
          <div className="profile-field">
            <label>성:</label>
            <span>{user?.last_name || '미설정'}</span>
          </div>
          
          <div className="profile-field">
            <label>역할:</label>
            <span>{user?.role === 'admin' ? '관리자' : '사용자'}</span>
          </div>
          
          <div className="profile-field">
            <label>가입일:</label>
            <span>{user?.created_at ? formatUTCToKST(user.created_at) : '알 수 없음'}</span>
          </div>
        </div>

        {message.text && (
          <div className={`auth-${message.type}`}>
            {message.type === 'success' ? '✅' : '❌'} {message.text}
          </div>
        )}

        <div className="profile-actions">
          <button
            type="button"
            className="auth-button auth-button-secondary"
            onClick={() => setShowPasswordForm(!showPasswordForm)}
          >
            {showPasswordForm ? '비밀번호 변경 취소' : '🔒 비밀번호 변경'}
          </button>

          <button
            type="button"
            className="auth-button auth-button-danger"
            onClick={handleLogout}
          >
            🚪 로그아웃
          </button>
        </div>

        {showPasswordForm && (
          <form onSubmit={handlePasswordSubmit} className="auth-form">
            <div className="form-group">
              <label htmlFor="currentPassword">현재 비밀번호</label>
              <input
                type="password"
                id="currentPassword"
                name="currentPassword"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
                required
                placeholder="현재 비밀번호를 입력하세요"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="newPassword">새 비밀번호</label>
              <input
                type="password"
                id="newPassword"
                name="newPassword"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
                required
                placeholder="새 비밀번호를 입력하세요 (8자 이상)"
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">새 비밀번호 확인</label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
                required
                placeholder="새 비밀번호를 다시 입력하세요"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              className="auth-button auth-button-primary"
              disabled={loading}
            >
              {loading ? '변경 중...' : '비밀번호 변경'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

export default UserProfile;
