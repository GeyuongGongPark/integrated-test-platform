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

  // 헬퍼 함수들
  const log = (message, data = null) => {
    if (data) {
      console.log(message, data);
    } else {
      console.log(message);
    }
  };

  const handleAuthSuccess = (access_token, userData, source = 'login') => {
    log(`✅ ${source} 성공 데이터:`, { access_token: !!access_token, user: userData });
    log(`🎫 ${source} 토큰 설정:`, access_token ? '있음' : '없음');
    log(`🔑 실제 토큰 값 (첫 50자):`, access_token ? access_token.substring(0, 50) + '...' : 'null');
    log(`👤 ${source} 사용자 데이터:`, userData);
    
    log(`💾 토큰 저장 시작...`);
    setToken(access_token);
    setUser(userData);
    localStorage.setItem('token', access_token);
    
    log(`💾 ${source} 토큰을 로컬 스토리지에 저장 완료`);
    log(`🔄 ${source} 상태 업데이트 완료`);
  };

  const handleAuthError = (error, source = '요청') => {
    console.error(`🚨 ${source} 오류:`, error);
  };

  // 토큰 만료 체크 함수
  const isTokenExpired = (token) => {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]));
      const currentTime = Math.floor(Date.now() / 1000);
      const expirationTime = payload.exp;
      
      log('⏰ 토큰 만료 시간 체크:', {
        currentTime: new Date(currentTime * 1000).toISOString(),
        expirationTime: new Date(expirationTime * 1000).toISOString(),
        isExpired: currentTime >= expirationTime
      });
      
      return currentTime >= expirationTime;
    } catch (error) {
      log('🚨 토큰 만료 시간 체크 오류:', error);
      return true; // 파싱 오류 시 만료된 것으로 간주
    }
  };

  // 토큰이 있으면 사용자 정보 가져오기
  useEffect(() => {
    log('🔄 useEffect 실행 - token:', token);
    log('🏪 localStorage token:', localStorage.getItem('token') ? '있음' : '없음');
    
    if (token) {
      // 토큰 만료 시간 체크
      if (isTokenExpired(token)) {
        log('⏰ 토큰 만료됨 - 자동 로그아웃');
        logout();
        return;
      }
      
      log('🔍 사용자 프로필 가져오기 시작');
      fetchUserProfile();
    } else {
      log('❌ 토큰이 없음, 로딩 완료');
      setLoading(false);
    }
  }, [token]);

  // 주기적 토큰 만료 체크 (5분마다)
  useEffect(() => {
    if (!token) return;
    
    const checkTokenExpiry = () => {
      if (isTokenExpired(token)) {
        log('⏰ 주기적 체크에서 토큰 만료 발견 - 자동 로그아웃');
        logout();
      }
    };
    
    const interval = setInterval(checkTokenExpiry, 5 * 60 * 1000); // 5분마다
    
    return () => clearInterval(interval);
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      log('🔍 fetchUserProfile 시작 - token:', token ? '있음' : '없음');
      log('🎫 실제 토큰 값:', token ? token.substring(0, 50) + '...' : 'null');
      log('🏪 localStorage에서 직접 확인:', localStorage.getItem('token') ? localStorage.getItem('token').substring(0, 50) + '...' : 'null');
      log('🔗 API URL:', `${config.apiUrl}/auth/profile`);
      
      const authHeader = `Bearer ${token}`;
      log('🔐 Authorization 헤더:', authHeader.substring(0, 60) + '...');
      
      const response = await fetch(`${config.apiUrl}/auth/profile`, {
        headers: {
          'Authorization': authHeader,
          'Content-Type': 'application/json'
        }
      });

      log('📡 프로필 응답 상태:', response.status, response.ok);

      if (response.ok) {
        const userData = await response.json();
        log('✅ 프로필 데이터 수신:', userData);
        log('🕐 last_login 값:', userData.last_login);
        log('📅 created_at 값:', userData.created_at);
        setUser(userData);
      } else {
        log('❌ 프로필 요청 실패, 로그아웃 실행');
        // 토큰이 유효하지 않으면 제거
        logout();
      }
    } catch (error) {
      handleAuthError(error, '프로필 가져오기');
      logout();
    } finally {
      log('🏁 fetchUserProfile 완료, 로딩 상태 해제');
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      log('🔐 로그인 시도:', { username, password });
      log('🔗 API URL:', `${config.apiUrl}/auth/login`);
      
      const response = await fetch(`${config.apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      log('📡 응답 상태:', response.status, response.ok);
      
      if (response.ok) {
        const data = await response.json();
        const { access_token, user: userData } = data;
        
        log('📥 로그인 응답에서 받은 사용자 데이터:', userData);
        log('🕐 last_login 값:', userData.last_login);
        
        handleAuthSuccess(access_token, userData, '로그인');
        return { success: true };
      } else {
        const errorData = await response.json();
        log('❌ 로그인 실패:', errorData);
        return { success: false, error: errorData.error || '로그인에 실패했습니다.' };
      }
    } catch (error) {
      handleAuthError(error, '로그인');
      return { success: false, error: '네트워크 오류가 발생했습니다.' };
    }
  };

  const guestLogin = async () => {
    try {
      log('🎭 게스트 로그인 시도');
      log('🔗 API URL:', `${config.apiUrl}/auth/guest`);
      
      const response = await fetch(`${config.apiUrl}/auth/guest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      log('📡 게스트 응답 상태:', response.status, response.ok);
      
      if (response.ok) {
        const data = await response.json();
        const { access_token, user: userData } = data;
        
        handleAuthSuccess(access_token, userData, '게스트 로그인');
        return { success: true };
      } else {
        const errorData = await response.json();
        log('❌ 게스트 로그인 실패:', errorData);
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
