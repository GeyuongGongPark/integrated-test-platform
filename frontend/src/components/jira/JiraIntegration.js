import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '@tms/config';
import PromptModal from '../common/PromptModal';
import './JiraIntegration.css';

const JiraIntegration = ({ testId, testType, testName, testResult, errorMessage, setActiveTab }) => {
  const [jiraIssues, setJiraIssues] = useState([]);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIssue, setSelectedIssue] = useState(null);
  const [comments, setComments] = useState([]);
  const [showComments, setShowComments] = useState(false);
  const [loadingComments, setLoadingComments] = useState(false);
  const [showCommentPrompt, setShowCommentPrompt] = useState(false);
  const [commentIssueKey, setCommentIssueKey] = useState(null);

  // Jira 이슈 조회
  const fetchJiraIssues = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${config.apiUrl}/api/jira/issues`);
      
      if (response.data.success) {
        setJiraIssues(response.data.data.issues || []);
      }
    } catch (err) {
      console.error('Jira 이슈 조회 오류:', err);
      setError('Jira 이슈를 불러오는 중 오류가 발생했습니다.');
    } finally {
      setLoading(false);
    }
  };

  // Jira 이슈 생성
  const createJiraIssue = async (issueData) => {
    try {
      setLoading(true);
      const response = await axios.post(`${config.apiUrl}/api/jira/issues`, {
        ...issueData,
        test_case_id: testType === 'testcase' ? testId : null,
        automation_test_id: testType === 'automation' ? testId : null,
        performance_test_id: testType === 'performance' ? testId : null
      });
      
      if (response.data.success) {
        setShowCreateModal(false);
        fetchJiraIssues();
        alert('Jira 이슈가 성공적으로 생성되었습니다.');
      }
    } catch (err) {
      console.error('Jira 이슈 생성 오류:', err);
      alert('Jira 이슈 생성 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  // 자동 이슈 생성 (테스트 실패 시)
  const autoCreateIssue = async () => {
    try {
      setLoading(true);
      
      if (testResult && ['Fail', 'Error'].includes(testResult)) {
        const issueData = {
          summary: `테스트 실패: ${testName}`,
          description: `**테스트 정보**\n- 테스트명: ${testName}\n- 결과: ${testResult}\n\n**오류 정보**\n${errorMessage || '오류 정보 없음'}`,
          issue_type: 'Bug',
          priority: 'Medium',
          test_case_id: testType === 'testcase' ? testId : null,
          automation_test_id: testType === 'automation' ? testId : null,
          performance_test_id: testType === 'performance' ? testId : null
        };
        
        const response = await axios.post(`${config.apiUrl}/api/jira/issues`, issueData);
        
        if (response.data.success) {
          alert('테스트 실패로 인해 Jira 이슈가 자동 생성되었습니다.');
          fetchJiraIssues();
        }
      } else {
        alert('테스트가 성공했으므로 이슈를 생성하지 않습니다.');
      }
    } catch (err) {
      console.error('자동 이슈 생성 오류:', err);
      alert('자동 이슈 생성 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message));
    } finally {
      setLoading(false);
    }
  };

  // Jira 이슈 상태 업데이트
  const updateIssueStatus = async (issueKey, newStatus) => {
    try {
      const response = await axios.put(`${config.apiUrl}/api/jira/issues/${issueKey}`, {
        status: newStatus
      });
      
      if (response.data.success) {
        fetchJiraIssues();
        alert('이슈 상태가 업데이트되었습니다.');
      }
    } catch (err) {
      console.error('이슈 상태 업데이트 오류:', err);
      alert('이슈 상태 업데이트 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message));
    }
  };

  // Jira 이슈에 댓글 추가
  const addComment = async (issueKey, comment) => {
    try {
      const response = await axios.post(`${config.apiUrl}/api/jira/issues/${issueKey}/comments`, {
        body: comment,
        author_email: 'admin@example.com'
      });
      
      if (response.data.success) {
        alert('댓글이 추가되었습니다.');
        fetchJiraIssues(); // 댓글 추가 후 이슈 목록 새로고침
        // 댓글 모달이 열려있다면 댓글 목록도 새로고침
        if (showComments && selectedIssue) {
          fetchComments(selectedIssue.issue_key);
        }
      }
    } catch (err) {
      console.error('댓글 추가 오류:', err);
      alert('댓글 추가 중 오류가 발생했습니다: ' + (err.response?.data?.error || err.message));
    }
  };

  // 댓글 조회
  const fetchComments = async (issueKey) => {
    setLoadingComments(true);
    try {
      const response = await axios.get(`${config.apiUrl}/api/jira/issues/${issueKey}/comments`);
      if (response.data.success) {
        setComments(response.data.data || []);
      }
    } catch (err) {
      console.error('댓글 조회 오류:', err);
      setComments([]);
    } finally {
      setLoadingComments(false);
    }
  };

  // 댓글 모달 열기
  const showCommentsModal = (issue) => {
    setSelectedIssue(issue);
    setShowComments(true);
    fetchComments(issue.issue_key);
  };

  // 댓글 모달 닫기
  const closeCommentsModal = () => {
    setShowComments(false);
    setSelectedIssue(null);
    setComments([]);
  };

  useEffect(() => {
    if (testId && testType) {
      fetchJiraIssues();
    }
  }, [testId, testType]);

  return (
    <div className="jira-integration">
      <div className="jira-header">
        <h3>🔗 이슈 관리</h3>
        <div className="jira-actions">
          <button 
            className="btn btn-primary"
            onClick={() => setShowCreateModal(true)}
            disabled={loading}
          >
            ➕ 이슈 생성
          </button>
          {testResult && ['Fail', 'Error'].includes(testResult) && (
            <button 
              className="btn btn-warning"
              onClick={autoCreateIssue}
              disabled={loading}
            >
              🤖 자동 이슈 생성
            </button>
          )}
        </div>
      </div>
      
      {loading && (
        <div className="loading">로딩 중...</div>
      )}
      
      {error && (
        <div className="error">{error}</div>
      )}
      
      {/* Jira 이슈 목록 */}
      <div className="jira-issues">
        {jiraIssues.length === 0 ? (
          <div className="no-issues">
            <p>연결된 이슈가 없습니다.</p>
          </div>
        ) : (
          jiraIssues.map(issue => (
            <div key={issue.id} className="jira-issue">
              <div className="issue-info">
                <div className="issue-header">
                  <span className="issue-key">{issue.issue_key}</span>
                  <span className={`issue-status status-${issue.status.toLowerCase().replace(' ', '-')}`}>
                    {issue.status}
                  </span>
                </div>
                <div className="issue-summary">{issue.summary}</div>
                <div className="issue-meta">
                  <span className="issue-type">{issue.issue_type}</span>
                  <span className="issue-priority">{issue.priority}</span>
                  <span className="issue-created">
                    {new Date(issue.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>
              
              <div className="issue-actions">
                {/* 게스트는 상태 변경 불가 */}
                {user && (user.role === 'admin' || user.role === 'user') && (
                  <>
                    <select
                      className="status-select"
                      value={issue.status}
                      onChange={(e) => updateIssueStatus(issue.issue_key, e.target.value)}
                    >
                      <option value="To Do">To Do</option>
                      <option value="In Progress">In Progress</option>
                      <option value="Done">Done</option>
                    </select>
                    
                    <button 
                      className="btn btn-secondary btn-sm"
                      onClick={() => {
                        setCommentIssueKey(issue.issue_key);
                        setShowCommentPrompt(true);
                      }}
                    >
                      💬 댓글 추가
                    </button>
                  </>
                )}
                
                {/* 게스트는 읽기 전용 상태 표시 */}
                {user && user.role === 'guest' && (
                  <span className="status-readonly" style={{ 
                    padding: '4px 8px', 
                    backgroundColor: '#e9ecef', 
                    borderRadius: '4px',
                    fontSize: '12px',
                    marginRight: '8px'
                  }}>
                    상태: {issue.status}
                  </span>
                )}
                
                <button 
                  className="btn btn-primary btn-sm"
                  onClick={() => showCommentsModal(issue)}
                  title="댓글 보기"
                >
                  📝 댓글 보기
                </button>
                
                <button 
                  className="btn btn-info btn-sm"
                  onClick={() => {
                    // 이슈 탭으로 이동하는 함수 호출
                    if (setActiveTab) {
                      setActiveTab('jira');
                    }
                  }}
                  title="이슈 탭에서 상세보기"
                >
                  🔗 상세보기
                </button>
                
              </div>
            </div>
          ))
        )}
      </div>
      
      {/* 이슈 생성 모달 */}
      {showCreateModal && (
        <JiraIssueModal 
          onSubmit={createJiraIssue}
          onClose={() => setShowCreateModal(false)}
          testName={testName}
          testResult={testResult}
          errorMessage={errorMessage}
        />
      )}

      {/* 댓글 모달 */}
      {showComments && selectedIssue && (
        <CommentsModal 
          issue={selectedIssue}
          comments={comments}
          loading={loadingComments}
          onClose={closeCommentsModal}
          onAddComment={addComment}
        />
      )}
    </div>
  );
};

// Jira 이슈 생성 모달 컴포넌트
const JiraIssueModal = ({ onSubmit, onClose, testName, testResult, errorMessage }) => {
  const [issueData, setIssueData] = useState({
    summary: testName ? `테스트 실패: ${testName}` : '',
    description: testResult && errorMessage ? 
      `**테스트 정보**\n- 테스트명: ${testName}\n- 결과: ${testResult}\n\n**오류 정보**\n${errorMessage}` : '',
    issue_type: 'Bug',
    priority: 'Medium'
  });
  const [isClosing, setIsClosing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 모달이 열릴 때 배경 스크롤 방지
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    
    // ESC 키로 모달 닫기
    const handleEscape = (e) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    
    return () => {
      document.body.style.overflow = 'unset';
      document.removeEventListener('keydown', handleEscape);
    };
  }, [onClose]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!issueData.summary.trim()) {
      alert('이슈 요약을 입력해주세요.');
      return;
    }
    if (issueData.summary.length < 5) {
      alert('이슈 요약은 5자 이상 입력해주세요.');
      return;
    }
    
    setIsSubmitting(true);
    try {
      await onSubmit(issueData);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    setIsClosing(true);
    setTimeout(() => {
      onClose();
    }, 200);
  };

  const handleOverlayClick = (e) => {
    if (e.target === e.currentTarget) {
      handleClose();
    }
  };

  return (
    <div className={`jira-modal-overlay ${isClosing ? 'closing' : ''}`} onClick={handleOverlayClick}>
      <div className={`jira-modal ${isClosing ? 'closing' : ''}`}>
        <div className="jira-modal-header">
          <div className="jira-modal-title">
            <span className="jira-modal-icon">🔗</span>
            <h3>이슈 생성</h3>
          </div>
          <button className="jira-modal-close" onClick={handleClose} title="닫기">×</button>
        </div>
        
        <form onSubmit={handleSubmit} className="jira-modal-body">
          <div className="form-group">
            <label>이슈 요약 *</label>
            <input
              type="text"
              className={`form-control ${issueData.summary.length > 0 && issueData.summary.length < 5 ? 'error' : ''}`}
              value={issueData.summary}
              onChange={(e) => setIssueData({...issueData, summary: e.target.value})}
              placeholder="이슈 요약을 입력하세요 (5자 이상)"
              required
            />
            {issueData.summary.length > 0 && issueData.summary.length < 5 && (
              <div className="form-error">이슈 요약은 5자 이상 입력해주세요.</div>
            )}
          </div>
          
          <div className="form-group">
            <label>설명</label>
            <textarea
              className="form-control"
              value={issueData.description}
              onChange={(e) => setIssueData({...issueData, description: e.target.value})}
              placeholder="이슈 상세 설명을 입력하세요"
              rows="5"
            />
          </div>
          
          <div className="form-row">
            <div className="form-group">
              <label>이슈 타입</label>
              <select
                className="form-control"
                value={issueData.issue_type}
                onChange={(e) => setIssueData({...issueData, issue_type: e.target.value})}
              >
                <option value="Bug">🐛 Bug</option>
                <option value="Task">📋 Task</option>
                <option value="Story">📖 Story</option>
                <option value="Epic">🏗️ Epic</option>
              </select>
            </div>
            
            <div className="form-group">
              <label>우선순위</label>
              <select
                className="form-control"
                value={issueData.priority}
                onChange={(e) => setIssueData({...issueData, priority: e.target.value})}
              >
                <option value="Low">🟢 Low</option>
                <option value="Medium">🟡 Medium</option>
                <option value="High">🟠 High</option>
                <option value="Critical">🔴 Critical</option>
              </select>
            </div>
          </div>
        </form>
        
        <div className="jira-modal-actions">
          <button className="btn btn-secondary" onClick={handleClose}>
            취소
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleSubmit}
            disabled={!issueData.summary.trim() || isSubmitting}
          >
            {isSubmitting ? '생성 중...' : '생성'}
          </button>
        </div>
      </div>
    </div>
  );
};

// 댓글 모달 컴포넌트
const CommentsModal = ({ issue, comments, loading, onClose, onAddComment }) => {
  const [newComment, setNewComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleAddComment = async () => {
    if (!newComment.trim()) return;
    
    setIsSubmitting(true);
    try {
      await onAddComment(issue.issue_key, newComment);
      setNewComment('');
    } catch (err) {
      console.error('댓글 추가 오류:', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleAddComment();
    }
  };

  return (
    <div className="jira-modal-overlay">
      <div className="jira-modal comments-modal">
        <div className="jira-modal-header">
          <div className="jira-modal-title">
            <span className="jira-modal-icon">💬</span>
            <h3>{issue.issue_key} - 댓글</h3>
          </div>
          <button className="jira-modal-close" onClick={onClose} title="닫기">×</button>
        </div>
        
        <div className="jira-modal-body comments-body">
          {/* 댓글 목록 */}
          <div className="comments-list">
            {loading ? (
              <div className="loading">댓글을 불러오는 중...</div>
            ) : comments.length === 0 ? (
              <div className="no-comments">
                <p>아직 댓글이 없습니다.</p>
              </div>
            ) : (
              comments.map(comment => (
                <div key={comment.id} className="comment-item">
                  <div className="comment-header">
                    <span className="comment-author">{comment.author_email}</span>
                    <span className="comment-date">
                      {new Date(comment.created_at).toLocaleString()}
                    </span>
                  </div>
                  <div className="comment-body">
                    {comment.body}
                  </div>
                </div>
              ))
            )}
          </div>
          
          {/* 댓글 추가 */}
          <div className="comment-add">
            <textarea
              className="form-control"
              placeholder="댓글을 입력하세요..."
              value={newComment}
              onChange={(e) => setNewComment(e.target.value)}
              onKeyPress={handleKeyPress}
              rows="3"
            />
            <div className="comment-actions">
              <button 
                className="btn btn-primary btn-sm"
                onClick={handleAddComment}
                disabled={!newComment.trim() || isSubmitting}
              >
                {isSubmitting ? '추가 중...' : '댓글 추가'}
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* 댓글 입력 모달 */}
      <PromptModal
        isOpen={showCommentPrompt}
        onClose={() => {
          setShowCommentPrompt(false);
          setCommentIssueKey(null);
        }}
        title="댓글 추가"
        message="댓글을 입력하세요:"
        placeholder="댓글을 입력하세요..."
        onConfirm={(comment) => {
          if (comment && commentIssueKey) {
            addComment(commentIssueKey, comment);
          }
        }}
      />
    </div>
  );
};

export default JiraIntegration;
