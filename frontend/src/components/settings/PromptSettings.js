import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '@tms/config';
import { useAuth } from '@tms/contexts/AuthContext';
import './PromptSettings.css';

axios.defaults.baseURL = config.apiUrl;

const PromptSettings = () => {
  const { user, token } = useAuth();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    }
  }, [token]);

  useEffect(() => {
    fetchPrompt();
  }, []);

  const fetchPrompt = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await axios.get('/settings/tc-prompt');
      setContent(res.data.content || '');
    } catch (err) {
      setError(err.response?.data?.error || '프롬프트를 불러오는 중 오류가 발생했습니다.');
      setContent('');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (user?.role !== 'admin') {
      setError('관리자만 저장할 수 있습니다.');
      return;
    }
    try {
      setSaving(true);
      setError(null);
      setMessage(null);
      await axios.put('/settings/tc-prompt', { content: content.trim() });
      setMessage('저장되었습니다.');
      setTimeout(() => setMessage(null), 3000);
    } catch (err) {
      setError(err.response?.data?.error || '저장 중 오류가 발생했습니다.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="prompt-settings-container">
        <div className="prompt-settings-loading">프롬프트 설정을 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="prompt-settings-container">
      <div className="prompt-settings-header">
        <h2>🤖 AI 테스트케이스 기본 프롬프트</h2>
        <p className="prompt-settings-desc">
          AI를 활용한 TC 작성 시 사용할 기본 프롬프트를 설정합니다. 아래 형식은 공용 단위 테스트케이스 생성용 구조 중심 프롬프트 예시입니다.
        </p>
      </div>

      <div className="prompt-settings-content">
        <div className="prompt-settings-section">
          <h3>프롬프트 내용</h3>
          <p className="prompt-format-hint">
            /context.global, /tc.rules, /tc.priority, /tc.columns, /tc.input 섹션 및 샘플 출력 형식을 유지한 채 수정하세요.
          </p>
          <textarea
            className="prompt-textarea"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="기본 프롬프트 내용을 입력하세요..."
            rows={28}
            spellCheck={false}
          />
          <div className="prompt-settings-actions">
            {user?.role === 'admin' && (
              <button
                type="button"
                className="prompt-settings-btn-save"
                onClick={handleSave}
                disabled={saving}
              >
                {saving ? '저장 중...' : '저장'}
              </button>
            )}
            <button
              type="button"
              className="prompt-settings-btn-reload"
              onClick={fetchPrompt}
              disabled={loading}
            >
              다시 불러오기
            </button>
          </div>
          {message && <p className="prompt-settings-message">{message}</p>}
          {error && <p className="prompt-settings-error">{error}</p>}
        </div>
      </div>
    </div>
  );
};

export default PromptSettings;
