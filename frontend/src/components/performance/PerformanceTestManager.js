import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';
import './PerformanceTestManager.css';

// axios 기본 설정
axios.defaults.baseURL = config.apiUrl;

const PerformanceTestManager = () => {
    const [performanceTests, setPerformanceTests] = useState([]);
    const [newTest, setNewTest] = useState({
        name: '',
        description: '',
        k6_script_path: '',
        environment: 'prod',
        parameters: {}
    });
    const [editingTest, setEditingTest] = useState(null);
    const [showEditModal, setShowEditModal] = useState(false);
    const [testResults, setTestResults] = useState([]);
    const [executing, setExecuting] = useState(false);
    const [expandedTests, setExpandedTests] = useState(new Set());

    useEffect(() => {
        fetchPerformanceTests();
    }, []);

    const fetchPerformanceTests = async () => {
        try {
            const response = await axios.get('/performance-tests');
            setPerformanceTests(response.data);
        } catch (error) {
            console.error('성능 테스트 조회 오류:', error);
        }
    };

    const addPerformanceTest = async () => {
        try {
            await axios.post('/performance-tests', {
                name: newTest.name,
                description: newTest.description,
                k6_script_path: newTest.k6_script_path,
                environment: newTest.environment,
                parameters: newTest.parameters
            });
            fetchPerformanceTests();
            setNewTest({
                name: '',
                description: '',
                k6_script_path: '',
                environment: 'prod',
                parameters: {}
            });
        } catch (error) {
            console.error('성능 테스트 추가 오류:', error);
        }
    };

    const handleEditTest = async () => {
        if (!editingTest.name || !editingTest.k6_script_path) {
            alert('테스트명과 스크립트 경로를 입력해주세요.');
            return;
        }

        try {
            await axios.put(`/performance-tests/${editingTest.id}`, editingTest);
            alert('성능 테스트가 성공적으로 수정되었습니다.');
            setShowEditModal(false);
            setEditingTest(null);
            fetchPerformanceTests();
        } catch (err) {
            alert('성능 테스트 수정 중 오류가 발생했습니다: ' + err.response?.data?.error || err.message);
        }
    };

    const deletePerformanceTest = async (testId) => {
        if (!window.confirm('정말로 이 성능 테스트를 삭제하시겠습니까?')) {
            return;
        }
        
        try {
            await axios.delete(`/performance-tests/${testId}`);
            alert('성능 테스트가 성공적으로 삭제되었습니다.');
            fetchPerformanceTests();
        } catch (error) {
            alert('성능 테스트 삭제 중 오류가 발생했습니다: ' + error.response?.data?.error || error.message);
        }
    };

    const executePerformanceTest = async (testId) => {
        setExecuting(true);
        try {
            const response = await axios.post(`/performance-tests/${testId}/execute`, {
                environment_vars: {}
            });
            console.log('테스트 실행 결과:', response.data);
            fetchPerformanceTests();
        } catch (error) {
            console.error('성능 테스트 실행 오류:', error);
        } finally {
            setExecuting(false);
        }
    };

    const fetchTestResults = async (testId) => {
        try {
            const response = await axios.get(`/performance-tests/${testId}/results`);
            setTestResults(response.data);
        } catch (error) {
            console.error('테스트 결과 조회 오류:', error);
        }
    };

    // 성능 테스트 상세 토글 함수
    const toggleTestDetails = (testId) => {
        setExpandedTests(prev => {
            const newSet = new Set(prev);
            if (newSet.has(testId)) {
                newSet.delete(testId);
            } else {
                newSet.add(testId);
                // 상세보기가 열릴 때 결과를 가져옴
                fetchTestResults(testId);
            }
            return newSet;
        });
    };

    return (
        <div className="performance-test-manager">
            <div className="performance-header">
                <h1>Performance Test Manager</h1>
            </div>
            
            <div className="add-test-form">
                <h2>Add Performance Test</h2>
                <div className="form-row">
                    <div className="form-group">
                        <input 
                            type="text" 
                            placeholder="Test Name" 
                            value={newTest.name} 
                            onChange={(e) => setNewTest({ ...newTest, name: e.target.value })} 
                            className="form-control"
                        />
                    </div>
                    <div className="form-group">
                        <input 
                            type="text" 
                            placeholder="Description" 
                            value={newTest.description} 
                            onChange={(e) => setNewTest({ ...newTest, description: e.target.value })} 
                            className="form-control"
                        />
                    </div>
                </div>
                <div className="form-row">
                    <div className="form-group">
                        <input 
                            type="text" 
                            placeholder="k6 Script Path" 
                            value={newTest.k6_script_path} 
                            onChange={(e) => setNewTest({ ...newTest, k6_script_path: e.target.value })} 
                            className="form-control"
                        />
                    </div>
                    <div className="form-group">
                        <select 
                            value={newTest.environment} 
                            onChange={(e) => setNewTest({ ...newTest, environment: e.target.value })}
                            className="form-control"
                        >
                            <option value="prod">Production</option>
                            <option value="staging">Staging</option>
                            <option value="dev">Development</option>
                        </select>
                    </div>
                </div>
                <button 
                    onClick={addPerformanceTest}
                    className="btn btn-add"
                >
                    Add Performance Test
                </button>
            </div>

            <h2>Performance Tests</h2>
            <div className="test-list">
                {performanceTests.map(test => (
                    <div key={test.id} className={`test-item ${expandedTests.has(test.id) ? 'selected' : ''}`}>
                        <div className="test-info">
                            <div className="test-name">{test.name}</div>
                            <div className="test-description">{test.description}</div>
                            <div className="test-meta">
                                <span>Script: {test.k6_script_path}</span>
                                <span>Environment: {test.environment}</span>
                            </div>
                        </div>
                        <div className="test-actions">
                            <button 
                                onClick={() => executePerformanceTest(test.id)}
                                disabled={executing}
                                className="btn btn-automation btn-icon"
                                title="Execute Test"
                            >
                                {executing ? '⏳' : '▶️'}
                            </button>
                            <button 
                                onClick={() => toggleTestDetails(test.id)}
                                className="btn btn-details btn-icon"
                                title="상세보기"
                            >
                                {expandedTests.has(test.id) ? '📋' : '📄'}
                            </button>
                            <button 
                                onClick={() => {
                                    setEditingTest(test);
                                    setShowEditModal(true);
                                }}
                                className="btn btn-edit-icon btn-icon"
                                title="수정"
                            >
                                ✏️
                            </button>
                            <button 
                                onClick={() => deletePerformanceTest(test.id)}
                                className="btn btn-delete-icon btn-icon"
                                title="Delete Test"
                            >
                                ✕
                            </button>
                        </div>
                        
                        {/* 아코디언 형태의 상세보기 */}
                        {expandedTests.has(test.id) && (
                            <div className={`test-details expanded`}>
                                <div className="test-info">
                                    <p><strong>스크립트 경로:</strong> {test.script_path || '없음'}</p>
                                    <p><strong>환경:</strong> {test.environment || '없음'}</p>
                                    <p><strong>매개변수:</strong> {test.parameters ? JSON.stringify(JSON.parse(test.parameters), null, 2) : '없음'}</p>
                                    <p><strong>생성일:</strong> {new Date(test.created_at).toLocaleString()}</p>
                                    <p><strong>수정일:</strong> {new Date(test.updated_at).toLocaleString()}</p>
                                </div>
                                
                                {/* 테스트 결과 영역 */}
                                <div className="test-results">
                                    <h5>📊 테스트 실행 결과</h5>
                                    <table className="results-table">
                                        <thead>
                                            <tr>
                                                <th>실행 시간</th>
                                                <th>상태</th>
                                                <th>실행 시간</th>
                                                <th>환경</th>
                                                <th>실행자</th>
                                                <th>비고</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {testResults.map(result => (
                                                <tr key={result.id}>
                                                    <td>
                                                        {result.executed_at ? new Date(result.executed_at).toLocaleString() : 'N/A'}
                                                    </td>
                                                    <td>
                                                        <span className={`status-${result.result?.toLowerCase() || 'error'}`}>
                                                            {result.result || 'N/A'}
                                                        </span>
                                                    </td>
                                                    <td>
                                                        {result.execution_time ? `${result.execution_time}ms` : 'N/A'}
                                                    </td>
                                                    <td>{result.environment || 'N/A'}</td>
                                                    <td>{result.executed_by || 'N/A'}</td>
                                                    <td>
                                                        {result.notes ? (
                                                            <details>
                                                                <summary>결과 보기</summary>
                                                                <pre className="result-notes">{result.notes}</pre>
                                                            </details>
                                                        ) : 'N/A'}
                                                    </td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
            
            {/* 수정 모달 */}
            {showEditModal && editingTest && (
                <div className="modal-overlay fullscreen-modal">
                    <div className="modal fullscreen-modal-content">
                        <div className="modal-header">
                            <h3>성능 테스트 수정</h3>
                            <button 
                                className="modal-close"
                                onClick={() => setShowEditModal(false)}
                            >
                                ×
                            </button>
                        </div>
                        <div className="modal-body">
                            <div className="form-group">
                                <label>테스트명 *</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    value={editingTest.name}
                                    onChange={(e) => setEditingTest({...editingTest, name: e.target.value})}
                                    placeholder="테스트명을 입력하세요"
                                />
                            </div>
                            <div className="form-group">
                                <label>설명</label>
                                <textarea
                                    className="form-control"
                                    value={editingTest.description}
                                    onChange={(e) => setEditingTest({...editingTest, description: e.target.value})}
                                    placeholder="테스트 설명을 입력하세요"
                                    rows="3"
                                />
                            </div>
                            <div className="form-group">
                                <label>k6 스크립트 경로 *</label>
                                <input
                                    type="text"
                                    className="form-control"
                                    value={editingTest.k6_script_path}
                                    onChange={(e) => setEditingTest({...editingTest, k6_script_path: e.target.value})}
                                    placeholder="k6 스크립트 파일 경로를 입력하세요"
                                />
                            </div>
                            <div className="form-group">
                                <label>환경</label>
                                <select
                                    className="form-control"
                                    value={editingTest.environment}
                                    onChange={(e) => setEditingTest({...editingTest, environment: e.target.value})}
                                >
                                    <option value="prod">Production</option>
                                    <option value="staging">Staging</option>
                                    <option value="dev">Development</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label>매개변수 (JSON)</label>
                                <textarea
                                    className="form-control"
                                    value={editingTest.parameters ? JSON.stringify(editingTest.parameters, null, 2) : ''}
                                    onChange={(e) => {
                                        try {
                                            const params = e.target.value ? JSON.parse(e.target.value) : {};
                                            setEditingTest({...editingTest, parameters: params});
                                        } catch (err) {
                                            // JSON 파싱 오류 무시
                                        }
                                    }}
                                    placeholder='{"timeout": 30, "retries": 3}'
                                    rows="5"
                                />
                            </div>
                        </div>
                        <div className="modal-actions">
                            <button 
                                className="btn btn-cancel"
                                onClick={() => setShowEditModal(false)}
                            >
                                취소
                            </button>
                            <button 
                                className="btn btn-save"
                                onClick={handleEditTest}
                            >
                                수정
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PerformanceTestManager; 