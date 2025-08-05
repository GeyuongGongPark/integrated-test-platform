import React, { useState } from 'react';
import ProjectManager from './ProjectManager';
import FolderManager from './FolderManager';
import AccountManager from './AccountManager';
import './Settings.css';

const Settings = () => {
  const [activeMenu, setActiveMenu] = useState('projects');

  const renderContent = () => {
    switch (activeMenu) {
      case 'projects':
        return <ProjectManager />;
      case 'folders':
        return <FolderManager />;
      case 'accounts':
        return <AccountManager />;
      default:
        return <ProjectManager />;
    }
  };

  return (
    <div className="settings-container">
      <div className="settings-header">
        <h1>설정</h1>
      </div>
      
      <div className="settings-content">
        <div className="settings-main">
          {renderContent()}
        </div>
        
        <div className="settings-snb">
          <nav className="snb-menu">
            <h3>설정 메뉴</h3>
            <ul>
              <li>
                <button 
                  className={`snb-item ${activeMenu === 'projects' ? 'active' : ''}`}
                  onClick={() => setActiveMenu('projects')}
                >
                  📋 프로젝트 관리
                </button>
              </li>
              <li>
                <button 
                  className={`snb-item ${activeMenu === 'folders' ? 'active' : ''}`}
                  onClick={() => setActiveMenu('folders')}
                >
                  📁 폴더 관리
                </button>
              </li>
              <li>
                <button 
                  className={`snb-item ${activeMenu === 'accounts' ? 'active' : ''}`}
                  onClick={() => setActiveMenu('accounts')}
                >
                  👤 계정 관리
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </div>
    </div>
  );
};

export default Settings; 