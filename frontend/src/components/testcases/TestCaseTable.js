import React from 'react';
// import { formatUTCToKST } from '../../utils/dateUtils';
import './TestCaseTable.css';

const TestCaseTable = ({
  testCases = [],
  selectedTestCases = [],
  onSelectTestCase,
  onSelectAll,
  onStatusChange,
  onAssigneeChange,
  onEdit,
  onDelete,
  onExecute,
  onViewDetails,
  users = [],
  user,
  sortBy,
  sortOrder,
  onSort
}) => {
  const handleSort = (column) => {
    if (onSort) {
      onSort(column);
    }
  };

  const renderSortIcon = (column) => {
    if (sortBy === column) {
      return sortOrder === 'asc' ? '↑' : '↓';
    }
    return '';
  };

  return (
    <div className="testcase-table-container">
      <table className="testcase-table">
        <thead>
          <tr>
            <th className="checkbox-column">
              <input 
                type="checkbox"
                checked={selectedTestCases.length === testCases.length && testCases.length > 0}
                onChange={onSelectAll}
              />
            </th>
            <th 
              className="no-column sortable" 
              onClick={() => handleSort('id')}
              style={{ cursor: 'pointer' }}
            >
              No {renderSortIcon('id')}
            </th>
            <th 
              className="summary-column sortable" 
              onClick={() => handleSort('name')}
              style={{ cursor: 'pointer' }}
            >
              요약 {renderSortIcon('name')}
            </th>
            <th 
              className="status-column sortable" 
              onClick={() => handleSort('status')}
              style={{ cursor: 'pointer' }}
            >
              상태 {renderSortIcon('status')}
            </th>
            <th 
              className="assignee-column sortable" 
              onClick={() => handleSort('assignee')}
              style={{ cursor: 'pointer' }}
            >
              담당자 {renderSortIcon('assignee')}
            </th>
            <th 
              className="creator-column sortable" 
              onClick={() => handleSort('creator')}
              style={{ cursor: 'pointer' }}
            >
              작성자 {renderSortIcon('creator')}
            </th>
            <th className="actions-column">동작</th>
          </tr>
        </thead>
        <tbody>
          {testCases.map((testCase, index) => (
            <tr key={testCase.id} className="testcase-table-row">
              <td className="checkbox-column">
                <input 
                  type="checkbox"
                  checked={selectedTestCases.includes(testCase.id)}
                  onChange={() => onSelectTestCase(testCase.id)}
                />
              </td>
              <td className="no-column">{index + 1}</td>
              <td className="summary-column">
                <div className="testcase-summary">
                  <div className="testcase-title">
                    {testCase.main_category && testCase.sub_category && testCase.detail_category 
                      ? `${testCase.main_category} > ${testCase.sub_category} > ${testCase.detail_category}`
                      : testCase.expected_result || '제목 없음'
                    }
                  </div>
                  <div className="testcase-meta">
                    <span className="environment-badge">{testCase.environment || 'dev'}</span>
                    {testCase.automation_code_path && (
                      <span className="automation-badge">자동화</span>
                    )}
                  </div>
                </div>
              </td>
              <td className="status-column">
                <div className="status-section">
                  <span className={`status-badge ${(testCase.result_status || 'N/A').toLowerCase().replace('/', '-')}`}>
                    {testCase.result_status || 'N/A'}
                  </span>
                  <select
                    className="status-select"
                    value={testCase.result_status}
                    onChange={(e) => onStatusChange(testCase.id, e.target.value)}
                  >
                    <option value="N/T">N/T</option>
                    <option value="Pass">Pass</option>
                    <option value="Fail">Fail</option>
                    <option value="N/A">N/A</option>
                    <option value="Block">Block</option>
                  </select>
                </div>
              </td>
              <td className="assignee-column">
                <div className="assignee-section">
                  <span className="assignee-badge">
                    👤 {testCase.assignee_name || '없음'}
                  </span>
                  <select
                    className="assignee-select"
                    value={testCase.assignee_id || ''}
                    onChange={(e) => onAssigneeChange(testCase.id, e.target.value)}
                  >
                    <option value="">담당자 변경</option>
                    {users && users.length > 0 ? (
                      users.map(user => (
                        <option key={user.id} value={user.id}>
                          {user.username || user.name || 'Unknown'}
                        </option>
                      ))
                    ) : (
                      <option value="" disabled>사용자 목록 로딩 중...</option>
                    )}
                  </select>
                </div>
              </td>
              <td className="creator-column">
                <span className="creator-badge">
                  👤 {testCase.creator_name || '없음'}
                </span>
              </td>
              <td className="actions-column">
                <div className="action-buttons">
                  {/* 자동화 실행 버튼 */}
                  {testCase.automation_code_path && (
                    <button 
                      className="testcase-btn testcase-btn-automation testcase-btn-icon"
                      onClick={() => onExecute(testCase.id)}
                      title="자동화 실행"
                    >
                      🤖
                    </button>
                  )}
                  {/* 상세보기 버튼 */}
                  <button 
                    className="testcase-btn testcase-btn-details testcase-btn-icon"
                    onClick={() => onViewDetails(testCase)}
                    title="상세보기"
                  >
                    📄
                  </button>
                  {/* 수정 버튼 */}
                  {user && (user.role === 'admin' || user.role === 'user') && (
                    <button 
                      className="testcase-btn testcase-btn-edit testcase-btn-icon"
                      onClick={() => onEdit(testCase)}
                      title="수정"
                    >
                      ✏️
                    </button>
                  )}
                  {/* 삭제 버튼 */}
                  {user && user.role === 'admin' && (
                    <button 
                      className="testcase-btn testcase-btn-delete testcase-btn-icon"
                      onClick={() => onDelete(testCase.id)}
                      title="삭제"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default TestCaseTable;
