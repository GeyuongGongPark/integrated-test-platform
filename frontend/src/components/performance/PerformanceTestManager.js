import React, { useState, useEffect } from 'react';
import axios from 'axios';

const PerformanceTestManager = () => {
    const [performanceTests, setPerformanceTests] = useState([]);
    const [newTest, setNewTest] = useState({
        name: '',
        description: '',
        k6_script_path: '',
        environment: 'prod',
        parameters: {}
    });
    const [selectedTest, setSelectedTest] = useState(null);
    const [testResults, setTestResults] = useState([]);
    const [executing, setExecuting] = useState(false);

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

    const deletePerformanceTest = async (testId) => {
        try {
            await axios.delete(`/performance-tests/${testId}`);
            fetchPerformanceTests();
        } catch (error) {
            console.error('성능 테스트 삭제 오류:', error);
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

    return (
        <div>
            <h1>Performance Test Manager</h1>
            
            <h2>Add Performance Test</h2>
            <div style={{ marginBottom: '20px' }}>
                <input 
                    type="text" 
                    placeholder="Test Name" 
                    value={newTest.name} 
                    onChange={(e) => setNewTest({ ...newTest, name: e.target.value })} 
                    style={{ marginRight: '10px', padding: '5px' }}
                />
                <input 
                    type="text" 
                    placeholder="Description" 
                    value={newTest.description} 
                    onChange={(e) => setNewTest({ ...newTest, description: e.target.value })} 
                    style={{ marginRight: '10px', padding: '5px' }}
                />
                <input 
                    type="text" 
                    placeholder="k6 Script Path" 
                    value={newTest.k6_script_path} 
                    onChange={(e) => setNewTest({ ...newTest, k6_script_path: e.target.value })} 
                    style={{ marginRight: '10px', padding: '5px' }}
                />
                <select 
                    value={newTest.environment} 
                    onChange={(e) => setNewTest({ ...newTest, environment: e.target.value })}
                    style={{ marginRight: '10px', padding: '5px' }}
                >
                    <option value="prod">Production</option>
                    <option value="staging">Staging</option>
                    <option value="dev">Development</option>
                </select>
                <button onClick={addPerformanceTest}>Add Performance Test</button>
            </div>

            <h2>Performance Tests</h2>
            <div style={{ marginBottom: '20px' }}>
                {performanceTests.map(test => (
                    <div key={test.id} style={{ 
                        border: '1px solid #ccc', 
                        padding: '10px', 
                        margin: '5px 0',
                        backgroundColor: selectedTest?.id === test.id ? '#f0f0f0' : 'white'
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <div>
                                <strong>{test.name}</strong><br/>
                                <small>Description: {test.description}</small><br/>
                                <small>Script: {test.k6_script_path}</small><br/>
                                <small>Environment: {test.environment}</small>
                            </div>
                            <div>
                                <button 
                                    onClick={() => executePerformanceTest(test.id)}
                                    disabled={executing}
                                    style={{ 
                                        padding: '5px 10px', 
                                        marginRight: '10px',
                                        backgroundColor: executing ? '#ccc' : '#007bff',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '3px'
                                    }}
                                >
                                    {executing ? 'Executing...' : 'Execute'}
                                </button>
                                <button 
                                    onClick={() => {
                                        setSelectedTest(test);
                                        fetchTestResults(test.id);
                                    }}
                                    style={{ 
                                        padding: '5px 10px', 
                                        marginRight: '10px',
                                        backgroundColor: '#28a745',
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '3px'
                                    }}
                                >
                                    View Results
                                </button>
                                <button 
                                    onClick={() => deletePerformanceTest(test.id)}
                                    style={{ 
                                        padding: '5px 10px', 
                                        backgroundColor: 'red', 
                                        color: 'white',
                                        border: 'none',
                                        borderRadius: '3px'
                                    }}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {selectedTest && (
                <div style={{ border: '2px solid #007bff', padding: '15px', borderRadius: '5px' }}>
                    <h3>Test Results for: {selectedTest.name}</h3>
                    
                    <div>
                        <h4>Previous Results</h4>
                        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                            <thead>
                                <tr style={{ backgroundColor: '#f8f9fa' }}>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Execution Time</th>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Status</th>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Avg Response Time</th>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Throughput</th>
                                    <th style={{ border: '1px solid #ddd', padding: '8px' }}>Error Rate</th>
                                </tr>
                            </thead>
                            <tbody>
                                {testResults.map(result => (
                                    <tr key={result.id}>
                                        <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                            {new Date(result.execution_time).toLocaleString()}
                                        </td>
                                        <td style={{ 
                                            border: '1px solid #ddd', 
                                            padding: '8px',
                                            backgroundColor: 
                                                result.status === 'Pass' ? '#d4edda' :
                                                result.status === 'Fail' ? '#f8d7da' : '#e2e3e5'
                                        }}>
                                            {result.status}
                                        </td>
                                        <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                            {result.response_time_avg ? `${result.response_time_avg}ms` : 'N/A'}
                                        </td>
                                        <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                            {result.throughput ? `${result.throughput}/s` : 'N/A'}
                                        </td>
                                        <td style={{ border: '1px solid #ddd', padding: '8px' }}>
                                            {result.error_rate ? `${(result.error_rate * 100).toFixed(2)}%` : 'N/A'}
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

export default PerformanceTestManager; 