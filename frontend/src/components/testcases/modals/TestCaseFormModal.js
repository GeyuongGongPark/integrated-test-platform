import React, { useEffect, useState } from 'react';
import TestCaseModal from './TestCaseModal';

const TestCaseFormModal = ({ 
  isOpen, 
  onClose, 
  testCase = {}, 
  onChange, 
  onSubmit, 
  onCancel,
  users = [],
  isEdit = false,
  onAiGenerate,
  aiGenerating = false,
  aiError = ''
}) => {
  const [aiPrompt, setAiPrompt] = useState('');

  useEffect(() => {
    if (!isOpen) {
      setAiPrompt('');
    }
  }, [isOpen]);

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit();
  };

  const handleChange = (field, value) => {
    onChange({ ...testCase, [field]: value });
  };

  const formActions = (
    <>
      <button 
        className="testcase-btn testcase-btn-primary"
        onClick={handleSubmit}
      >
        {isEdit ? '수정' : '추가'}
      </button>
      <button 
        className="testcase-btn testcase-btn-secondary"
        onClick={onCancel}
      >
        취소
      </button>
    </>
  );

  return (
    <TestCaseModal
      isOpen={isOpen}
      onClose={onClose}
      title={isEdit ? '테스트 케이스 편집' : '새 테스트 케이스 추가'}
      actions={formActions}
      size="large"
    >
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>AI 프롬프트로 설계</label>
          <textarea
            value={aiPrompt}
            onChange={(e) => setAiPrompt(e.target.value)}
            placeholder="기능/시나리오를 입력하면 테스트 케이스 초안을 제안합니다."
            rows="3"
          />
          <div className="ai-actions">
            <button
              type="button"
              className="testcase-btn testcase-btn-primary"
              onClick={() => onAiGenerate && onAiGenerate(aiPrompt)}
              disabled={aiGenerating}
            >
              {aiGenerating ? '생성 중...' : 'AI로 채우기'}
            </button>
            {aiError && <p className="error-text">{aiError}</p>}
          </div>
        </div>

        <div className="form-group">
          <label>대분류 *</label>
          <input 
            type="text" 
            value={testCase.main_category || ''}
            onChange={(e) => handleChange('main_category', e.target.value)}
            placeholder="대분류를 입력하세요"
            required
          />
        </div>
        
        <div className="form-group">
          <label>중분류 *</label>
          <input 
            type="text" 
            value={testCase.sub_category || ''}
            onChange={(e) => handleChange('sub_category', e.target.value)}
            placeholder="중분류를 입력하세요"
            required
          />
        </div>
        
        <div className="form-group">
          <label>소분류 *</label>
          <input 
            type="text" 
            value={testCase.detail_category || ''}
            onChange={(e) => handleChange('detail_category', e.target.value)}
            placeholder="소분류를 입력하세요"
            required
          />
        </div>
        
        <div className="form-group">
          <label>사전조건</label>
          <textarea 
            value={testCase.pre_condition || ''}
            onChange={(e) => handleChange('pre_condition', e.target.value)}
            placeholder="사전조건을 입력하세요"
            rows="3"
          />
        </div>
        
        <div className="form-group">
          <label>기대결과</label>
          <textarea 
            value={testCase.expected_result || ''}
            onChange={(e) => handleChange('expected_result', e.target.value)}
            placeholder="기대결과를 입력하세요"
            rows="3"
          />
        </div>
        
        <div className="form-group">
          <label>결과 상태</label>
          <select 
            value={testCase.result_status || 'N/T'}
            onChange={(e) => handleChange('result_status', e.target.value)}
          >
            <option value="N/T">N/T (Not Tested)</option>
            <option value="Pass">Pass</option>
            <option value="Fail">Fail</option>
            <option value="N/A">N/A</option>
            <option value="Block">Block</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>비고</label>
          <textarea 
            value={testCase.remark || ''}
            onChange={(e) => handleChange('remark', e.target.value)}
            placeholder="비고를 입력하세요"
            rows="3"
          />
        </div>

        <div className="form-group">
          <label>테스트 단계 (JSON, 코드 없이 실행)</label>
          <textarea 
            value={testCase.test_steps || ''}
            onChange={(e) => handleChange('test_steps', e.target.value)}
            placeholder={'예: [{"action":"navigate","url":"/"},{"action":"fill","selector":"#id","value":"admin"},{"action":"click","selector":"button[type=submit]"}]'}
            rows="5"
          />
          <small className="form-hint">
            자동화 코드 경로 없이 실행 버튼으로 동작합니다. action: navigate, click, fill, type, press, waitForTimeout, assertText 등.
          </small>
        </div>
        
        <div className="form-group">
          <label>자동화 코드 경로</label>
          <input 
            type="text" 
            value={testCase.automation_code_path || ''}
            onChange={(e) => handleChange('automation_code_path', e.target.value)}
            placeholder="자동화 코드 파일 경로 (비워두면 위 테스트 단계만 사용)"
          />
        </div>
        
        <div className="form-group">
          <label>자동화 코드 타입</label>
          <select 
            value={testCase.automation_code_type || 'playwright'}
            onChange={(e) => handleChange('automation_code_type', e.target.value)}
          >
            <option value="playwright">Playwright</option>
            <option value="selenium">Selenium</option>
            <option value="k6">k6 (성능 테스트)</option>
          </select>
        </div>
        
        <div className="form-group">
          <label>담당자</label>
          <select 
            value={testCase.assignee_id || ''}
            onChange={(e) => handleChange('assignee_id', e.target.value ? Number(e.target.value) : null)}
          >
            <option value="">담당자를 선택하세요</option>
            {users.map(user => (
              <option key={user.id} value={user.id}>
                {user.username || user.first_name || user.email}
              </option>
            ))}
          </select>
        </div>
      </form>
    </TestCaseModal>
  );
};

export default TestCaseFormModal;
