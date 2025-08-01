import React, { useState, useEffect } from 'react';
import axios from 'axios';

const UnifiedDashboard = () => {
    const [testCases, setTestCases] = useState([]);
    const [performanceTests, setPerformanceTests] = useState([]);
    const [testExecutions, setTestExecutions] = useState([]);
    const [stats, setStats] = useState({
        totalTestCases: 0,
        totalPerformanceTests: 0,
        passedTests: 0,
        failedTests: 0,
        runningTests: 0
    });

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [testCasesRes, performanceTestsRes, executionsRes] = await Promise.all([
                axios.get('/testcases'),
                axios.get('/performance-tests'),
                axios.get('/test-executions')
            ]);

            setTestCases(testCasesRes.data);
            setPerformanceTests(performanceTestsRes.data);
            setTestExecutions(executionsRes.data);

            // 통계 계산
            const totalTestCases = testCasesRes.data.length;
            const totalPerformanceTests = performanceTestsRes.data.length;
            
            const passedTests = testCasesRes.data.filter(tc => tc.result_status === 'Pass').length;
            const failedTests = testCasesRes.data.filter(tc => tc.result_status === 'Fail').length;
            const runningTests = executionsRes.data.filter(exec => exec.status === 'Running').length;

            setStats({
                totalTestCases,
                totalPerformanceTests,
                passedTests,
                failedTests,
                runningTests
            });
        } catch (error) {
            console.error('대시보드 데이터 조회 오류:', error);
        }
    };

    const getStatusColor = (status) => {
        switch (status) {
            case 'Pass': return '#d4edda';
            case 'Fail': return '#f8d7da';
            case 'Running': return '#fff3cd';
            case 'N/T': return '#e2e3e5';
            default: return '#e2e3e5';
        }
    };

    return (
        <div>
            <h1>Unified Test Dashboard</h1>
            
            {/* 통계 카드 */}
            <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                <div style={{ 
                    border: '1px solid #ddd', 
                    padding: '20px', 
                    borderRadius: '8px',
                    backgroundColor: '#f8f9fa',
                    flex: 1
                }}>
                    <h3>Test Cases</h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#007bff' }}>
                        {stats.totalTestCases}
                    </div>
                    <small>Total Test Cases</small>
                </div>
                
                <div style={{ 
                    border: '1px solid #ddd', 
                    padding: '20px', 
                    borderRadius: '8px',
                    backgroundColor: '#f8f9fa',
                    flex: 1
                }}>
                    <h3>Performance Tests</h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                        {stats.totalPerformanceTests}
                    </div>
                    <small>Total Performance Tests</small>
                </div>
                
                <div style={{ 
                    border: '1px solid #ddd', 
                    padding: '20px', 
                    borderRadius: '8px',
                    backgroundColor: '#f8f9fa',
                    flex: 1
                }}>
                    <h3>Passed Tests</h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#28a745' }}>
                        {stats.passedTests}
                    </div>
                    <small>Successfully Passed</small>
                </div>
                
                <div style={{ 
                    border: '1px solid #ddd', 
                    padding: '20px', 
                    borderRadius: '8px',
                    backgroundColor: '#f8f9fa',
                    flex: 1
                }}>
                    <h3>Failed Tests</h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#dc3545' }}>
                        {stats.failedTests}
                    </div>
                    <small>Tests Failed</small>
                </div>
                
                <div style={{ 
                    border: '1px solid #ddd', 
                    padding: '20px', 
                    borderRadius: '8px',
                    backgroundColor: '#f8f9fa',
                    flex: 1
                }}>
                    <h3>Running Tests</h3>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ffc107' }}>
                        {stats.runningTests}
                    </div>
                    <small>Currently Running</small>
                </div>
            </div>

            {/* 최근 테스트 케이스 */}
            <div style={{ marginBottom: '30px' }}>
                <h2>Recent Test Cases</h2>
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {testCases.slice(0, 5).map(testCase => (
                        <div key={testCase.id} style={{ 
                            border: '1px solid #ddd', 
                            padding: '10px', 
                            margin: '5px 0',
                            borderRadius: '5px',
                            backgroundColor: getStatusColor(testCase.result_status)
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <strong>{testCase.main_category} - {testCase.sub_category}</strong><br/>
                                    <small>{testCase.description}</small><br/>
                                    <small>Created: {new Date(testCase.created_at).toLocaleDateString()}</small>
                                </div>
                                <div style={{ 
                                    padding: '5px 10px', 
                                    borderRadius: '3px',
                                    backgroundColor: testCase.result_status === 'Pass' ? '#28a745' : 
                                                   testCase.result_status === 'Fail' ? '#dc3545' : '#6c757d',
                                    color: 'white',
                                    fontWeight: 'bold'
                                }}>
                                    {testCase.result_status}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 최근 성능 테스트 */}
            <div style={{ marginBottom: '30px' }}>
                <h2>Recent Performance Tests</h2>
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {performanceTests.slice(0, 5).map(test => (
                        <div key={test.id} style={{ 
                            border: '1px solid #ddd', 
                            padding: '10px', 
                            margin: '5px 0',
                            borderRadius: '5px',
                            backgroundColor: '#f8f9fa'
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <strong>{test.name}</strong><br/>
                                    <small>{test.description}</small><br/>
                                    <small>Script: {test.k6_script_path}</small><br/>
                                    <small>Environment: {test.environment}</small>
                                </div>
                                <div>
                                    <button 
                                        onClick={() => {
                                            // 성능 테스트 실행 로직
                                            console.log('Execute performance test:', test.id);
                                        }}
                                        style={{ 
                                            padding: '5px 10px', 
                                            backgroundColor: '#007bff',
                                            color: 'white',
                                            border: 'none',
                                            borderRadius: '3px',
                                            marginRight: '10px'
                                        }}
                                    >
                                        Execute
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            {/* 최근 테스트 실행 */}
            <div>
                <h2>Recent Test Executions</h2>
                <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
                    {testExecutions.slice(0, 10).map(execution => (
                        <div key={execution.id} style={{ 
                            border: '1px solid #ddd', 
                            padding: '10px', 
                            margin: '5px 0',
                            borderRadius: '5px',
                            backgroundColor: getStatusColor(execution.status)
                        }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <strong>Execution #{execution.id}</strong><br/>
                                    <small>Type: {execution.test_type}</small><br/>
                                    <small>Started: {new Date(execution.execution_start).toLocaleString()}</small>
                                    {execution.execution_end && (
                                        <small><br/>Ended: {new Date(execution.execution_end).toLocaleString()}</small>
                                    )}
                                </div>
                                <div style={{ 
                                    padding: '5px 10px', 
                                    borderRadius: '3px',
                                    backgroundColor: execution.status === 'Pass' ? '#28a745' : 
                                                   execution.status === 'Fail' ? '#dc3545' : 
                                                   execution.status === 'Running' ? '#ffc107' : '#6c757d',
                                    color: 'white',
                                    fontWeight: 'bold'
                                }}>
                                    {execution.status}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default UnifiedDashboard; 