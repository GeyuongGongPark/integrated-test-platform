import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import config from '../../config';
import './AutomationTestDetail.css';

// 자동화 테스트 실행 결과 컴포넌트
const AutomationTestResults = ({ testId }) => {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (testId) {
      fetchResults();
    }
  }, [testId, fetchResults]);

  const fetchResults = useCallback(async () => {
    try {
      setLoading(true);
      const response = await axios.get(`/automation-tests/${testId}/results`);
      setResults(response.data);
    } catch (err) {
      console.error('자동화 테스트 결과 조회 오류:', err);
    } finally {
      setLoading(false);
    }
  }, [testId]);

  if (loading) {
    return <div className="results-loading">실행 결과 로딩 중...</div>;
  }

  if (results.length === 0) {
    return <div className="no-results">실행 결과가 없습니다.</div>;
  }

  return (
    <div className="automation-results-container">
      {results.map((result, index) => (
        <div key={result.id} className={`result-item ${result.status.toLowerCase()}`}>
          <div className="result-header">
            <span className={`result-status ${result.status.toLowerCase()}`}>
              {result.status}
            </span>
            <span className="result-timestamp">
              {new Date(result.execution_start).toLocaleString()}
            </span>
          </div>
          {result.execution_duration && (
            <div className="result-duration">
              실행 시간: {result.execution_duration.toFixed(2)}초
            </div>
          )}
          {result.output && (
            <div className="result-output">
              <strong>출력:</strong> {result.output}
            </div>
          )}
          {result.error_message && (
            <div className="result-error">
              <strong>오류:</strong> {result.error_message}
            </div>
          )}
          {result.screenshot_path && (
            <div className="result-screenshot">
              <img 
                src={`${config.apiUrl}/screenshots/${result.screenshot_path}`}
                alt="실행 결과 스크린샷"
                className="result-screenshot-image"
              />
            </div>
          )}
          {result.notes && (
            <div className="result-notes">
              <strong>메모:</strong> {result.notes}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const AutomationTestDetail = ({ test, onClose, onRefresh }) => {
  const [loading, setLoading] = useState(false);
  const [executing, setExecuting] = useState(false);

  const handleExecuteTest = async () => {
    if (!window.confirm('이 자동화 테스트를 실행하시겠습니까?')) {
      return;
    }

    try {
      setExecuting(true);
      await axios.post(`/automation-tests/${test.id}/execute`);
      alert('자동화 테스트 실행이 완료되었습니다.');
      onRefresh(); // 목록 새로고침
    } catch (err) {
      alert('자동화 테스트 실행 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    } finally {
      setExecuting(false);
    }
  };

  const handleEditTest = () => {
    // 편집 모달 열기 로직 (부모 컴포넌트에서 처리)
    onClose(); // 상세 화면 닫기
  };

  const handleDeleteTest = async () => {
    if (!window.confirm('정말로 이 자동화 테스트를 삭제하시겠습니까?')) {
      return;
    }

    try {
      setLoading(true);
      await axios.delete(`/automation-tests/${test.id}`);
      alert('자동화 테스트가 성공적으로 삭제되었습니다.');
      onClose(); // 상세 화면 닫기
      onRefresh(); // 목록 새로고침
    } catch (err) {
      alert('자동화 테스트 삭제 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="automation-test-detail">
      <div className="detail-header">
        <h2>자동화 테스트 상세</h2>
        <button 
          className="btn btn-close"
          onClick={onClose}
        >
          ×
        </button>
      </div>

      <div className="detail-content">
        <div className="detail-section">
          <h3>기본 정보</h3>
          <div className="info-grid">
            <div className="info-item">
              <label>테스트명:</label>
              <span>{test.name}</span>
            </div>
            <div className="info-item">
              <label>설명:</label>
              <span>{test.description || '설명 없음'}</span>
            </div>
            <div className="info-item">
              <label>테스트 타입:</label>
              <span className="test-type-badge">{test.test_type}</span>
            </div>
            <div className="info-item">
              <label>환경:</label>
              <span className="environment-badge">{test.environment}</span>
            </div>
            <div className="info-item">
              <label>스크립트 경로:</label>
              <span className="script-path">{test.script_path}</span>
            </div>
            <div className="info-item">
              <label>생성일:</label>
              <span>{new Date(test.created_at).toLocaleString()}</span>
            </div>
            <div className="info-item">
              <label>수정일:</label>
              <span>{new Date(test.updated_at).toLocaleString()}</span>
            </div>
          </div>
        </div>

        {test.parameters && (
          <div className="detail-section">
            <h3>매개변수</h3>
            <div className="parameters-container">
              <pre className="parameters-json">{test.parameters}</pre>
            </div>
          </div>
        )}

        <div className="detail-section">
          <h3>실행 결과</h3>
          <AutomationTestResults testId={test.id} />
        </div>
      </div>

      <div className="detail-actions">
        <button 
          className="btn btn-automation"
          onClick={handleExecuteTest}
          disabled={executing}
          title="자동화 실행"
        >
          {executing ? '실행 중...' : '🤖'}
        </button>
        <button 
          className="btn btn-edit-icon"
          onClick={handleEditTest}
          title="수정"
        >
          ✏️
        </button>
        <button 
          className="btn btn-delete-icon"
          onClick={handleDeleteTest}
          disabled={loading}
          title="삭제"
        >
          ✕
        </button>
        <button 
          className="btn btn-cancel"
          onClick={onClose}
        >
          닫기
        </button>
      </div>
    </div>
  );
};

export default AutomationTestDetail; 