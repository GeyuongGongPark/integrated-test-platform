import React, { createContext, useContext, useState, useEffect } from 'react';
import config from '../config';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  const handleAuthSuccess = (access_token, userData, source = 'login') => {
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('token', access_token);
  };

  const handleAuthError = (error, source = '요청') => {
    // 오류는 조용히 처리
  };

  // UTC를 KST로 변환하는 함수
  const toKST = (timestamp) => {
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleString('ko-KR', {
        timeZone: 'Asia/Seoul',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
      });
    } catch (error) {
      return '시간 변환 오류';
    }
  };

  // 토큰 만료 체크 함수
  const isTokenExpired = (token) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      const expirationTime = payload.exp;
      
      return currentTime >= expirationTime;
    } catch (error) {
      return true; // 파싱 오류 시 만료된 것으로 간주
    }
  };

  // 토큰이 있으면 사용자 정보 가져오기
  useEffect(() => {
    const now = new Date().toLocaleString('ko-KR', {
      timeZone: 'Asia/Seoul',
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      hour12: true
    });
    
    if (token) {
      // 토큰 만료 시간 체크
      if (isTokenExpired(token)) {
        logout();
        return;
      }
      
      fetchUserProfile();
    } else {
      setLoading(false);
    }
  }, [token]);

  // 주기적 토큰 만료 체크 (5분마다)
  useEffect(() => {
    if (!token) return;
    
    const checkTokenExpiry = () => {
      const now = new Date().toLocaleString('ko-KR', {
        timeZone: 'Asia/Seoul',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
      });
      
      if (isTokenExpired(token)) {
        logout();
      }
    };
    
    const interval = setInterval(checkTokenExpiry, 5 * 60 * 1000); // 5분마다
    
    return () => clearInterval(interval);
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      const authHeader = `Bearer ${token}`;
      
      const response = await fetch(`${config.apiUrl}/auth/profile`, {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        // 토큰이 유효하지 않으면 제거
        logout();
      }
    } catch (error) {
      handleAuthError(error, '프로필 가져오기');
      logout();
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      const response = await fetch(`${config.apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      if (response.ok) {
        const data = await response.json();
        const { access_token, user: userData } = data;
        
        handleAuthSuccess(access_token, userData, '로그인');
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || '로그인에 실패했습니다.' };
      }
    } catch (error) {
      handleAuthError(error, '로그인');
      return { success: false, error: '네트워크 오류가 발생했습니다.' };
    }
  };

  const guestLogin = async () => {
    try {
      const response = await fetch(`${config.apiUrl}/auth/guest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const { access_token, user: userData } = data;
        
        handleAuthSuccess(access_token, userData, '게스트 로그인');
        return { success: true };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || '게스트 로그인에 실패했습니다.' };
      }
    } catch (error) {
      handleAuthError(error, '게스트 로그인');
      return { success: false, error: '네트워크 오류가 발생했습니다.' };
    }
  };

  const register = async (userData) => {
    try {
      const response = await fetch(`${config.apiUrl}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(userData)
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, message: data.message };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || '회원가입에 실패했습니다.' };
      }
    } catch (error) {
      handleAuthError(error, '회원가입');
      return { success: false, error: '네트워크 오류가 발생했습니다.' };
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
  };

  const changePassword = async (currentPassword, newPassword) => {
    try {
      const response = await fetch(`${config.apiUrl}/auth/change-password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ current_password: currentPassword, new_password: newPassword })
      });

      if (response.ok) {
        return { success: true, message: '비밀번호가 변경되었습니다.' };
      } else {
        const errorData = await response.json();
        return { success: false, error: errorData.error || '비밀번호가 변경에 실패했습니다.' };
      }
    } catch (error) {
      handleAuthError(error, '비밀번호 변경');
      return { success: false, error: '네트워크 오류가 발생했습니다.' };
    }
  };

  const value = {
    user,
    token,
    loading,
    login,
    guestLogin,
    register,
    logout,
    changePassword,
    isAuthenticated: !!token
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
