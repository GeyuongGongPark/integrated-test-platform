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

  // 토큰이 있으면 사용자 정보 가져오기
  useEffect(() => {
    console.log('🔄 useEffect 실행 - token:', token);
    if (token) {
      console.log('🔍 사용자 프로필 가져오기 시작');
      fetchUserProfile();
    } else {
      console.log('❌ 토큰이 없음, 로딩 완료');
      setLoading(false);
    }
  }, [token]);

  const fetchUserProfile = async () => {
    try {
      console.log('🔍 fetchUserProfile 시작 - token:', token ? '있음' : '없음');
      console.log('🔗 API URL:', `${config.apiUrl}/auth/profile`);
      
      const response = await fetch(`${config.apiUrl}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 프로필 응답 상태:', response.status, response.ok);

      if (response.ok) {
        const userData = await response.json();
        console.log('✅ 프로필 데이터 수신:', userData);
        setUser(userData);
      } else {
        console.log('❌ 프로필 요청 실패, 로그아웃 실행');
        // 토큰이 유효하지 않으면 제거
        logout();
      }
    } catch (error) {
      console.error('🚨 프로필 가져오기 실패:', error);
      logout();
    } finally {
      console.log('🏁 fetchUserProfile 완료, 로딩 상태 해제');
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    try {
      console.log('🔐 로그인 시도:', { username, password });
      console.log('🔗 API URL:', `${config.apiUrl}/auth/login`);
      
      const response = await fetch(`${config.apiUrl}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ username, password })
      });

      console.log('📡 응답 상태:', response.status, response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ 로그인 성공 데이터:', data);
        
        const { access_token, user: userData } = data;
        
        console.log('🎫 토큰 설정:', access_token ? '있음' : '없음');
        console.log('👤 사용자 데이터:', userData);
        
        setToken(access_token);
        setUser(userData);
        localStorage.setItem('token', access_token);
        
        console.log('💾 로컬 스토리지에 토큰 저장 완료');
        console.log('🔄 상태 업데이트 완료');
        
        return { success: true };
      } else {
        const errorData = await response.json();
        console.log('❌ 로그인 실패:', errorData);
        return { success: false, error: errorData.error || '로그인에 실패했습니다.' };
      }
    } catch (error) {
      console.error('🚨 로그인 오류:', error);
      return { success: false, error: '네트워크 오류가 발생했습니다.' };
    }
  };

  const guestLogin = async () => {
    try {
      console.log('🎭 게스트 로그인 시도');
      console.log('🔗 API URL:', `${config.apiUrl}/auth/guest`);
      
      const response = await fetch(`${config.apiUrl}/auth/guest`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        }
      });

      console.log('📡 게스트 응답 상태:', response.status, response.ok);
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ 게스트 로그인 성공 데이터:', data);
        
        const { access_token, user: userData } = data;
        
        console.log('🎫 게스트 토큰 설정:', access_token ? '있음' : '없음');
        console.log('👤 게스트 사용자 데이터:', userData);
        
        setToken(access_token);
        setUser(userData);
        localStorage.setItem('token', access_token);
        
        console.log('💾 게스트 토큰을 로컬 스토리지에 저장 완료');
        console.log('🔄 게스트 상태 업데이트 완료');
        
        return { success: true };
      } else {
        const errorData = await response.json();
        console.log('❌ 게스트 로그인 실패:', errorData);
        return { success: false, error: errorData.error || '게스트 로그인에 실패했습니다.' };
      }
    } catch (error) {
      console.error('🚨 게스트 로그인 오류:', error);
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
      console.error('회원가입 오류:', error);
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
      console.error('비밀번호 변경 오류:', error);
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
