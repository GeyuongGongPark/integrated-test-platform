// src/TestCaseApp.js
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import config from '../../config';

// axios 기본 설정
axios.defaults.baseURL = config.apiUrl;

const TestCaseApp = () => {
    const [projects, setProjects] = useState([]);
    const [testCases, setTestCases] = useState([]);
    const [newCase, setNewCase] = useState({
        project_id: '',
        main_category: '',
        sub_category: '',
        detail_category: '',
        pre_condition: '',
        description: '', // 기대 결과를 설명으로 사용
        result_status: 'N/T',
        remark: ''
    });
    const [selectedTestCase, setSelectedTestCase] = useState(null);
    const [testResults, setTestResults] = useState([]);
    const [newResult, setNewResult] = useState({ result: 'N/T', notes: '' });

    useEffect(() => {
        fetchProjects();
        fetchTestCases();
    }, []);

    const fetchProjects = async () => {
        try {
            const response = await axios.get('/projects'); // API 경로 수정
            setProjects(response.data);
        } catch (error) {
            console.error('프로젝트 조회 오류:', error);
        }
    };

    const fetchTestCases = async () => {
        try {
            const response = await axios.get('/testcases'); // API 경로 수정
            setTestCases(response.data);
        } catch (error) {
            console.error('테스트 케이스 조회 오류:', error);
        }
    };

    const addTestCase = async () => {
        console.log("Adding Test Case:", newCase); // 요청 데이터 확인
        try {
            await axios.post('/testcases', {
                project_id: newCase.project_id,
                main_category: newCase.main_category,
                sub_category: newCase.sub_category,
                detail_category: newCase.detail_category,
                pre_condition: newCase.pre_condition,
                description: newCase.description, // 기대 결과를 설명으로 사용
                result_status: newCase.result_status,
                remark: newCase.remark
            });
            fetchTestCases(); // 테스트 케이스 목록 새로 고침
            setNewCase({
                project_id: '',
                main_category: '',
                sub_category: '',
                detail_category: '',
                pre_condition: '',
                description: '', // 초기화
                result_status: 'N/T',
                remark: ''
            });
        } catch (error) {
            console.error('테스트 케이스 추가 오류:', error);
        }
    };

    const deleteTestCase = async (testCaseId) => {
        try {
            await axios.delete(`/testcases/${testCaseId}`); // API 경로 수정
            fetchTestCases(); // 테스트 케이스 목록 새로 고침
        } catch (error) {
            console.error('테스트 케이스 삭제 오류:', error);
        }
    };

    const fetchTestResults = async (testCaseId) => {
        try {
            const response = await axios.get(`/testresults/${testCaseId}`); // API 경로 수정
            setTestResults(response.data);
        } catch (error) {
            console.error('테스트 결과 조회 오류:', error);
        }
    };

    const addTestResult = async () => {
        if (!selectedTestCase) return;

        try {
            await axios.post('/testresults', {
                test_case_id: selectedTestCase.id,
                result: newResult.result,
                notes: newResult.notes
            }); // API 경로 수정
            fetchTestResults(selectedTestCase.id);
            setNewResult({ result: 'N/T', notes: '' });
            fetchTestCases(); // 테스트 케이스 상태 업데이트
        } catch (error) {
            console.error('테스트 결과 추가 오류:', error);
        }
    };

    const updateTestCaseStatus = async (testCaseId, status) => {
        try {
            await axios.put(`/testcases/${testCaseId}/status`, { status }); // API 경로 수정
            fetchTestCases();
        } catch (error) {
            console.error('테스트 케이스 상태 업데이트 오류:', error);
        }
    };

    return (
        <div>
            <h1>Test Case Manager</h1>
            
            <h2>Add Test Case</h2>
            <select 
                value={newCase.project_id} 
                onChange={(e) => setNewCase({ ...newCase, project_id: e.target.value })}
            >
                <option value="">Select Project</option>
                {projects.map(project => (
                    <option key={project.id} value={project.id}>{project.name}</option>
                ))}
            </select>
            <input 
                type="text" 
                placeholder="Main Category" 
                value={newCase.main_category} 
                onChange={(e) => setNewCase({ ...newCase, main_category: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Sub Category" 
                value={newCase.sub_category} 
                onChange={(e) => setNewCase({ ...newCase, sub_category: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Detail Category" 
                value={newCase.detail_category} 
                onChange={(e) => setNewCase({ ...newCase, detail_category: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Pre Condition" 
                value={newCase.pre_condition} 
                onChange={(e) => setNewCase({ ...newCase, pre_condition: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Description (Expected Result)" 
                value={newCase.description} 
                onChange={(e) => setNewCase({ ...newCase, description: e.target.value })} 
            />
            <input 
                type="text" 
                placeholder="Remark" 
                value={newCase.remark} 
                onChange={(e) => setNewCase({ ...newCase, remark: e.target.value })} 
            />
            <button onClick={addTestCase}>Add Test Case</button>

            <h2>Test Cases</h2>
            <div style={{ marginBottom: '20px' }}>
                {testCases.map(testCase => (
                    <div key={testCase.id} style={{ 
                        border: '1px solid #ccc', 
                        padding: '10px', 
                        margin: '5px 0',
                        backgroundColor: selectedTestCase?.id === testCase.id ? '#f0f0f0' : 'white'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <strong>{testCase.main_category} - {testCase.sub_category} - {testCase.detail_category}</strong><br/>
                                <small>Description: {testCase.description}</small>
                            </div>
                            <div>
                                <select 
                                    value={testCase.result_status} 
                                    onChange={(e) => updateTestCaseStatus(testCase.id, e.target.value)}
                                    style={{ marginRight: '10px' }}
                                >
                                    <option value="N/T">N/T</option>
                                    <option value="Pass">Pass</option>
                                    <option value="Fail">Fail</option>
                                    <option value="N/A">N/A</option>
                                    <option value="Block">Block</option>
                                </select>
                                <button 
                                    onClick={() => {
                                        setSelectedTestCase(testCase);
                                        fetchTestResults(testCase.id);
                                    }}
                                    style={{ padding: '5px 10px' }}
                                >
                                    View Results
                                </button>
                                <button 
                                    onClick={() => deleteTestCase(testCase.id)} // 삭제 버튼 클릭 시 삭제 함수 호출
                                    style={{ padding: '5px 10px', marginLeft: '10px', backgroundColor: 'red', color: 'white' }}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {selectedTestCase && (
                <div style={{ border: '2px solid #007bff', padding: '15px', borderRadius: '5px' }}>
                    <h3>Test Results for: {selectedTestCase.description}</h3>
                    
                    <div style={{ marginBottom: '15px' }}>
                        <h4>Add New Result</h4>
                        <select 
                            value={newResult.result} 
                            onChange={(e) => setNewResult({ ...newResult, result: e.target.value })}
                            style={{ marginRight: '10px', padding: '5px' }}
                        >
                            <option value="N/T">N/T</option>
                            <option value="Pass">Pass</option>
                            <option value="Fail">Fail</option>
                            <option value="N/A">N/A</option>
                            <option value="Block">Block</option>
                        </select>
                        <input 
                            type="text" 
                            placeholder="Notes" 
                            value={newResult.notes} 
                            onChange={(e) => setNewResult({ ...newResult, notes: e.target.value })}
                            style={{ marginRight: '10px', padding: '5px', width: '200px' }}
                        />
                        <button onClick={addTestResult}>Add Result</button>
                    </div>

                    <div>
                        <h4>Previous Results</h4>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ backgroundColor: '#f8f9fa' }}>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Result</th>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Date</th>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Notes</th>
                                </tr>
                            </thead>
                            <tbody>
                                {testResults.map(result => (
                                    <tr key={result.id}>
                                        <td style={{ 
                                            border: '1px solid #ddd', 
                                            padding: '8px',
                                            backgroundColor: 
                                                result.result === 'Pass' ? '#d4edda' :
                                                result.result === 'Fail' ? '#f8d7da' :
                                                result.result === 'Block' ? '#fff3cd' : '#e2e3e5'
                                        }}>
                                            {result.result}
                                        </td>
                                        <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                            {new Date(result.executed_at).toLocaleString()}
                                        </td>
                                        <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                            {result.notes}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TestCaseApp;
