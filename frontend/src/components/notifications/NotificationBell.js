import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import config from '../../config';
import './NotificationBell.css';

const NotificationBell = () => {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    fetchNotifications();
    // 30초마다 알림 새로고침
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  // 외부 클릭 시 드롭다운 닫기
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      if (!token) {
        console.warn('토큰이 없습니다.');
        return;
      }
      
      const response = await axios.get(`${config.apiUrl}/notifications?unread_only=false&limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      console.log('🔔 알림 조회 응답:', response.data);
      console.log('🔔 알림 배열:', response.data?.notifications);
      console.log('🔔 읽지 않은 알림 수:', response.data?.unread_count);
      
      if (response.data && response.data.notifications) {
        const notificationsList = response.data.notifications || [];
        const unreadCountValue = response.data.unread_count || 0;
        
        console.log(`✅ 알림 설정: ${notificationsList.length}개 알림, ${unreadCountValue}개 읽지 않음`);
        
        setNotifications(notificationsList);
        setUnreadCount(unreadCountValue);
      } else {
        console.warn('⚠️ 알림 데이터 형식이 올바르지 않습니다:', response.data);
        setNotifications([]);
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('알림 조회 오류:', error);
      if (error.response) {
        console.error('응답 상태:', error.response.status);
        console.error('응답 데이터:', error.response.data);
      }
      setNotifications([]);
      setUnreadCount(0);
    } finally {
      setLoading(false);
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${config.apiUrl}/notifications/${notificationId}/read`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      // 알림 목록 업데이트
      setNotifications(prev => 
        prev.map(notif => 
          notif.id === notificationId ? { ...notif, read: true } : notif
        )
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('알림 읽음 처리 오류:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('token');
      await axios.post(`${config.apiUrl}/notifications/read-all`, {}, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setNotifications(prev => prev.map(notif => ({ ...notif, read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('전체 알림 읽음 처리 오류:', error);
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      const token = localStorage.getItem('token');
      await axios.delete(`${config.apiUrl}/notifications/${notificationId}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setNotifications(prev => prev.filter(notif => notif.id !== notificationId));
      // 읽지 않은 알림이 삭제된 경우 카운트 감소
      const deletedNotif = notifications.find(n => n.id === notificationId);
      if (deletedNotif && !deletedNotif.read) {
        setUnreadCount(prev => Math.max(0, prev - 1));
      }
    } catch (error) {
      console.error('알림 삭제 오류:', error);
    }
  };

  const formatTime = (dateString) => {
    if (!dateString) return '';
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '방금 전';
    if (minutes < 60) return `${minutes}분 전`;
    if (hours < 24) return `${hours}시간 전`;
    if (days < 7) return `${days}일 전`;
    return date.toLocaleDateString('ko-KR');
  };

  const getNotificationIcon = (type) => {
    switch (type) {
      case 'mention':
        return '💬';
      case 'test_execution':
        return '🧪';
      case 'schedule':
        return '📅';
      case 'workflow':
        return '🔄';
      default:
        return '🔔';
    }
  };

  const displayCount = unreadCount > 99 ? '99+' : unreadCount;
  
  // 디버깅: 알림 상태 확인
  useEffect(() => {
    console.log('🔔 알림 상태 업데이트:', {
      notificationsCount: notifications.length,
      unreadCount: unreadCount,
      displayCount: displayCount
    });
  }, [notifications, unreadCount, displayCount]);

  return (
    <div className="notification-bell-container" ref={dropdownRef}>
      <button 
        className="notification-bell-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="알림"
      >
        <div className="bell-icon-wrapper">
          <svg 
            className="bell-icon" 
            width="24" 
            height="24" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 0 1-3.46 0" />
          </svg>
          {unreadCount > 0 && (
            <span className="notification-badge">{displayCount}</span>
          )}
        </div>
        {unreadCount > 0 && (
          <span className="notification-text">
            새로운 알림 <span className="notification-count">{displayCount}</span>건
          </span>
        )}
      </button>

      {isOpen && (
        <div className="notification-dropdown">
          <div className="notification-header">
            <h3>알림</h3>
            {unreadCount > 0 && (
              <button 
                className="mark-all-read-btn"
                onClick={markAllAsRead}
              >
                모두 읽음
              </button>
            )}
          </div>

          <div className="notification-list">
            {loading ? (
              <div className="notification-loading">로딩 중...</div>
            ) : notifications.length === 0 ? (
              <div className="notification-empty">알림이 없습니다</div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id} 
                  className={`notification-item ${!notification.read ? 'unread' : ''}`}
                  onClick={() => !notification.read && markAsRead(notification.id)}
                >
                  <div className="notification-icon">
                    {getNotificationIcon(notification.notification_type)}
                  </div>
                  <div className="notification-content">
                    <div className="notification-message">{notification.message}</div>
                    <div className="notification-time">{formatTime(notification.created_at)}</div>
                  </div>
                  <div className="notification-actions">
                    {!notification.read && (
                      <span className="unread-dot"></span>
                    )}
                    <button 
                      className="delete-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteNotification(notification.id);
                      }}
                      aria-label="삭제"
                    >
                      ×
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default NotificationBell;

