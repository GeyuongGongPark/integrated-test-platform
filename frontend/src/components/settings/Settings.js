import React, { useState } from 'react';
import ProjectManager from './ProjectManager';
import FolderManager from './FolderManager';
import AccountManager from './AccountManager';
import PromptSettings from './PromptSettings';
import { useAuth } from '@tms/contexts/AuthContext';
import './Settings.css';

const Settings = () => {
  const [activeMenu, setActiveMenu] = useState('accounts');
  const { user } = useAuth();

  // 권한별 메뉴 표시 조건
  const canAccessProjects = () => {
    return user && user.role === 'admin';
  };

  const canAccessFolders = () => {
    return user && (user.role === 'admin' || user.role === 'user');
  };

  const canAccessAccounts = () => {
    return user && (user.role === 'admin' || user.role === 'user');
  };

  const canAccessPromptSettings = () => {
    return user && (user.role === 'admin' || user.role === 'user');
  };

  const renderContent = () => {
    switch (activeMenu) {
      case 'projects':
        return canAccessProjects() ? <ProjectManager /> : <div>접근 권한이 없습니다.</div>;
      case 'folders':
        return canAccessFolders() ? <FolderManager /> : <div>접근 권한이 없습니다.</div>;
      case 'tc-prompt':
        return canAccessPromptSettings() ? <PromptSettings /> : <div>접근 권한이 없습니다.</div>;
      case 'accounts':
        return canAccessAccounts() ? <AccountManager /> : <div>접근 권한이 없습니다.</div>;
      default:
        return canAccessAccounts() ? <AccountManager /> : <div>접근 권한이 없습니다.</div>;
    }
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>설정</h1>
        <div className="user-role-info">
          <span>현재 사용자: {user?.username}</span>
          <span className={`role-badge ${user?.role}`}>
            {user?.role === 'admin' ? '관리자' : 
             user?.role === 'user' ? '사용자' : 
             user?.role === 'guest' ? '게스트' : '알 수 없음'}
          </span>
        </div>
      </div>
      
      <div className="settings-content">
        <div className="settings-main">
          {renderContent()}
        </div>
        
        <div className="settings-snb">
          <nav className="snb-menu">
            <h3>설정 메뉴</h3>
            <ul>
              {canAccessProjects() && (
                <li>
                  <button 
                    className={`snb-item ${activeMenu === 'projects' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('projects')}
                  >
                    📋 프로젝트 관리
                  </button>
                </li>
              )}
              {canAccessFolders() && (
                <li>
                  <button 
                    className={`snb-item ${activeMenu === 'folders' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('folders')}
                  >
                    📁 폴더 관리
                  </button>
                </li>
              )}
              {canAccessPromptSettings() && (
                <li>
                  <button 
                    className={`snb-item ${activeMenu === 'tc-prompt' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('tc-prompt')}
                  >
                    🤖 AI TC 프롬프트
                  </button>
                </li>
              )}
              {canAccessAccounts() && (
                <li>
                  <button 
                    className={`snb-item ${activeMenu === 'accounts' ? 'active' : ''}`}
                    onClick={() => setActiveMenu('accounts')}
                  >
                    👤 계정 관리
                  </button>
                </li>
              )}
            </ul>
          </nav>
        </div>
      </div>
    </div>
  );
};

export default Settings; 