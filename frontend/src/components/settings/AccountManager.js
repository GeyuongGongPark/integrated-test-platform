import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './AccountManager.css';

axios.defaults.baseURL = config.apiUrl;

const AccountManager = () => {
  const [userInfo, setUserInfo] = useState({
    username: 'admin',
    email: 'admin@example.com',
    role: 'Administrator',
    lastLogin: '2024-01-15 10:30:00'
  });
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [profileData, setProfileData] = useState({
    username: '',
    email: ''
  });

  useEffect(() => {
    // 실제로는 API에서 사용자 정보를 가져옴
    setProfileData({
      username: userInfo.username,
      email: userInfo.email
    });
  }, [userInfo]);

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
      // 실제로는 API 호출
      // await axios.put('/account/password', passwordData);
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
      alert('모든 필드를 입력해주세요.');
      return;
    }

    try {
      // 실제로는 API 호출
      // await axios.put('/account/profile', profileData);
      alert('프로필이 성공적으로 업데이트되었습니다.');
      setShowProfileModal(false);
      setUserInfo({
        ...userInfo,
        username: profileData.username,
        email: profileData.email
      });
    } catch (err) {
      alert('프로필 업데이트 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    }
  };

  return (
    <div className="account-manager">
      <div className="account-header">
        <h2>계정 관리</h2>
      </div>

      <div className="account-content">
        <div className="account-section">
          <h3>계정 정보</h3>
          <div className="account-info">
            <div className="info-item">
              <label>사용자명:</label>
              <span>{userInfo.username}</span>
            </div>
            <div className="info-item">
              <label>이메일:</label>
              <span>{userInfo.email}</span>
            </div>
            <div className="info-item">
              <label>역할:</label>
              <span>{userInfo.role}</span>
            </div>
            <div className="info-item">
              <label>마지막 로그인:</label>
              <span>{userInfo.lastLogin}</span>
            </div>
          </div>
        </div>

        <div className="account-section">
          <h3>계정 설정</h3>
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

        <div className="account-section">
          <h3>시스템 정보</h3>
          <div className="system-info">
            <div className="info-item">
              <label>플랫폼 버전:</label>
              <span>v1.0.0</span>
            </div>
            <div className="info-item">
              <label>데이터베이스:</label>
              <span>PostgreSQL</span>
            </div>
            <div className="info-item">
              <label>백엔드:</label>
              <span>Flask</span>
            </div>
            <div className="info-item">
              <label>프론트엔드:</label>
              <span>React</span>
            </div>
          </div>
        </div>
      </div>

      {/* 비밀번호 변경 모달 */}
      {showPasswordModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>비밀번호 변경</h3>
            <div className="form-group">
              <label>현재 비밀번호</label>
              <input 
                type="password" 
                value={passwordData.currentPassword}
                onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                placeholder="현재 비밀번호를 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>새 비밀번호</label>
              <input 
                type="password" 
                value={passwordData.newPassword}
                onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                placeholder="새 비밀번호를 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>새 비밀번호 확인</label>
              <input 
                type="password" 
                value={passwordData.confirmPassword}
                onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                placeholder="새 비밀번호를 다시 입력하세요"
              />
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handlePasswordChange}
              >
                변경
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowPasswordModal(false);
                  setPasswordData({
                    currentPassword: '',
                    newPassword: '',
                    confirmPassword: ''
                  });
                }}
              >
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
              <label>사용자명</label>
              <input 
                type="text" 
                value={profileData.username}
                onChange={(e) => setProfileData({...profileData, username: e.target.value})}
                placeholder="사용자명을 입력하세요"
              />
            </div>
            <div className="form-group">
              <label>이메일</label>
              <input 
                type="email" 
                value={profileData.email}
                onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                placeholder="이메일을 입력하세요"
              />
            </div>
            <div className="modal-actions">
              <button 
                className="btn btn-primary"
                onClick={handleProfileUpdate}
              >
                수정
              </button>
              <button 
                className="btn btn-secondary"
                onClick={() => {
                  setShowProfileModal(false);
                  setProfileData({
                    username: userInfo.username,
                    email: userInfo.email
                  });
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

export default AccountManager; 