import React, { useEffect, useState } from 'react';
import { useAuth } from '@tms/contexts/AuthContext';
import { formatUTCToKST } from '@tms/utils/dateUtils';
import './Auth.css';
import './UserProfile.css';

const UserProfile = () => {
  const { user, changePassword, logout } = useAuth();
  const [activeMenu, setActiveMenu] = useState('account'); // account, notifications, login, login-fail, security, logout
  const [showPasswordForm, setShowPasswordForm] = useState(false);
  const isGuest = user?.role === 'guest';
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

  useEffect(() => {
    if (isGuest && !['account', 'logout'].includes(activeMenu)) {
      setActiveMenu('account');
    }
  }, [activeMenu, isGuest]);

  const renderAccountSection = () => (
    <>
      <div className="profile-section-header">
        <h2>계정 설정</h2>
        <p>기본 프로필 정보와 비밀번호를 관리합니다.</p>
      </div>

      <div className="profile-info">
        <div className="profile-field">
          <label>로그인 아이디</label>
          <span>{user?.email || user?.username}</span>
        </div>
        <div className="profile-field">
          <label>이름</label>
          <span>{user?.first_name || '미설정'}</span>
        </div>
        <div className="profile-field">
          <label>성</label>
          <span>{user?.last_name || '미설정'}</span>
        </div>
        <div className="profile-field">
          <label>역할</label>
          <span>{user?.role === 'admin' ? '관리자' : user?.role === 'user' ? '사용자' : user?.role || '알 수 없음'}</span>
        </div>
        {!isGuest && (
          <div className="profile-field">
            <label>가입일</label>
            <span>{user?.created_at ? formatUTCToKST(user.created_at) : '알 수 없음'}</span>
          </div>
        )}
        {isGuest && (
          <div className="profile-field">
            <label>로그인 일시</label>
            <span>{user?.created_at ? formatUTCToKST(user.created_at) : '알 수 없음'}</span>
          </div>
        )}
      </div>

      {message.text && (
        <div className={`auth-${message.type}`}>
          {message.type === 'success' ? '✅' : '❌'} {message.text}
        </div>
      )}

      {!isGuest && (
        <div className="profile-actions">
          <button
            type="button"
            className="auth-button auth-button-secondary"
            onClick={() => setShowPasswordForm(!showPasswordForm)}
          >
            {showPasswordForm ? '비밀번호 변경 취소' : '🔒 비밀번호 변경'}
          </button>
        </div>
      )}

      {!isGuest && showPasswordForm && (
        <form onSubmit={handlePasswordSubmit} className="auth-form profile-password-form">
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

          <div className="profile-actions">
            <button
              type="submit"
              className="auth-button auth-button-primary"
              disabled={loading}
            >
              {loading ? '변경 중...' : '비밀번호 변경'}
            </button>
          </div>
        </form>
      )}
    </>
  );

  const renderNotificationsSection = () => (
    <div className="profile-placeholder">
      <h2>알림 / 이메일 수신 설정</h2>
      <p>이 화면에서는 추후 Slack/이메일/인앱 알림 수신 여부를 세부적으로 설정할 수 있도록 확장할 예정입니다.</p>
      <p>현재는 슬랙 웹훅 알림만 사용 중이며, 이메일 알림 기능을 준비 중입니다.</p>
    </div>
  );

  const renderLoginHistorySection = () => (
    <div className="profile-placeholder">
      <h2>로그인 기록</h2>
      <p>최근 로그인 이력, IP, 브라우저 정보 등을 확인하는 화면으로 확장할 수 있습니다.</p>
      <p>지금은 UI 레이아웃만 준비해 두었습니다.</p>
    </div>
  );

  const renderLoginFailSection = () => (
    <div className="profile-placeholder">
      <h2>로그인 실패 기록</h2>
      <p>보안 강화를 위해 실패한 로그인 시도 내역을 보여줄 수 있습니다.</p>
      <p>추후 보안 요구사항에 맞춰 구현 가능합니다.</p>
    </div>
  );

  const renderSecuritySection = () => (
    <div className="profile-placeholder">
      <h2>보안 설정</h2>
      <p>2단계 인증, 세션 만료 시간, 접속 허용 IP 등 고급 보안 설정을 배치할 수 있는 영역입니다.</p>
    </div>
  );

  const renderLogoutSection = () => (
    <div className="profile-placeholder">
      <h2>로그아웃</h2>
      <p>현재 로그인된 계정에서 로그아웃합니다.</p>
      <div className="profile-actions">
        <button
          type="button"
          className="auth-button auth-button-danger"
          onClick={handleLogout}
        >
          🚪 로그아웃
        </button>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (activeMenu) {
      case 'account':
        return renderAccountSection();
      case 'notifications':
        return renderNotificationsSection();
      case 'login':
        return renderLoginHistorySection();
      case 'login-fail':
        return renderLoginFailSection();
      case 'security':
        return renderSecuritySection();
      case 'logout':
        return renderLogoutSection();
      default:
        return renderAccountSection();
    }
  };

  return (
    <div className="profile-page-container">
      <div className="profile-page-content">
        <div className="profile-main-card">
          {renderContent()}
        </div>

        <div className="profile-snb settings-snb">
          <nav className="snb-menu">
            <h3>회원 정보</h3>
            <ul>
              <li>
                <button
                  className={`snb-item ${activeMenu === 'account' ? 'active' : ''}`}
                  onClick={() => setActiveMenu('account')}
                >
                  계정 설정
                </button>
              </li>
              {!isGuest && (
                <li>
                  <button
                    className={`snb-item ${activeMenu === 'notifications' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('notifications')}
                  >
                    알림 / 이메일 수신 설정
                  </button>
                </li>
              )}
              {!isGuest && (
                <li>
                  <button
                    className={`snb-item ${activeMenu === 'login' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('login')}
                  >
                    로그인 기록
                  </button>
                </li>
              )}
              {!isGuest && (
                <li>
                  <button
                    className={`snb-item ${activeMenu === 'login-fail' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('login-fail')}
                  >
                    로그인 실패 기록
                  </button>
                </li>
              )}
              {!isGuest && (
                <li>
                  <button
                    className={`snb-item ${activeMenu === 'security' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('security')}
                  >
                    보안
                  </button>
                </li>
              )}
              <li>
                <button
                  className="snb-item"
                  onClick={handleLogout}
                >
                  로그아웃
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  );
};

export default UserProfile;
