# 🔗 Jira 연동 구현 계획서

## 📋 개요

통합 테스트 플랫폼과 Atlassian Jira를 연동하여 테스트 결과를 자동으로 이슈로 생성하고, 개발 프로세스와의 연속성을 확보하는 시스템을 구축합니다.

## 🏗️ 아키텍처 설계

### 1.1 전체 시스템 구조

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Jira Cloud    │
│   (React)       │◄──►│   (Flask)       │◄──►│   (REST API)    │
│                 │    │                 │    │                 │
│ - 테스트 실행      │    │ - Jira Client   │    │ - 이슈 생성       │
│ - 결과 표시       │    │ - 웹훅 처리        │    │ - 상태 업데이트    │
│ - Jira 연동      │    │ - 동기화 엔진      │    │ - 댓글 추가       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 1.2 데이터 흐름

```
테스트 실행 → 결과 분석 → Jira 이슈 생성/업데이트 → 상태 동기화 → 대시보드 반영
```

## 🔧 백엔드 구현 방안

### 2.1 Jira API 클라이언트 설계

```python
# backend/utils/jira_client.py
class JiraClient:
    def __init__(self, server_url, username, api_token):
        self.server_url = server_url
        self.username = username
        self.api_token = api_token
        self.session = requests.Session()
        self.session.auth = (username, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def create_issue(self, project_key, summary, description, issue_type, **kwargs):
        """Jira 이슈 생성"""
        pass
    
    def update_issue(self, issue_key, **kwargs):
        """Jira 이슈 업데이트"""
        pass
    
    def add_comment(self, issue_key, comment):
        """Jira 이슈에 댓글 추가"""
        pass
    
    def get_issue(self, issue_key):
        """Jira 이슈 조회"""
        pass
    
    def search_issues(self, jql_query):
        """JQL을 사용한 이슈 검색"""
        pass
```

### 2.2 환경 변수 설정

```bash
# .env
JIRA_SERVER_URL=https://your-domain.atlassian.net
JIRA_USERNAME=your-email@domain.com
JIRA_API_TOKEN=your-api-token
JIRA_PROJECT_KEY=PROJECT
JIRA_DEFAULT_ISSUE_TYPE=Task
JIRA_WEBHOOK_SECRET=your-webhook-secret
```

### 2.3 Jira 연동 모델 설계

```python
# backend/models.py
class JiraIntegration(db.Model):
    __tablename__ = 'JiraIntegrations'
    id = db.Column(db.Integer, primary_key=True)
    test_case_id = db.Column(db.Integer, db.ForeignKey('TestCases.id'), nullable=True)
    automation_test_id = db.Column(db.Integer, db.ForeignKey('AutomationTests.id'), nullable=True)
    performance_test_id = db.Column(db.Integer, db.ForeignKey('PerformanceTests.id'), nullable=True)
    jira_issue_key = db.Column(db.String(20), nullable=False)  # PROJECT-123
    jira_issue_id = db.Column(db.String(50), nullable=False)  # 내부 ID
    jira_project_key = db.Column(db.String(20), nullable=False)
    issue_type = db.Column(db.String(50), nullable=False)  # Bug, Task, Story
    status = db.Column(db.String(50), nullable=False)  # To Do, In Progress, Done
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 관계 설정
    test_case = db.relationship('TestCase', backref='jira_integrations')
    automation_test = db.relationship('AutomationTest', backref='jira_integrations')
    performance_test = db.relationship('PerformanceTest', backref='jira_integrations')
```

## 🌐 API 엔드포인트 설계

### 3.1 Jira 연동 API

```python
# backend/routes/jira_integration.py
@jira_bp.route('/jira/issues', methods=['POST'])
def create_jira_issue():
    """테스트 결과를 기반으로 Jira 이슈 생성"""
    pass

@jira_bp.route('/jira/issues/<issue_key>', methods=['GET'])
def get_jira_issue(issue_key):
    """Jira 이슈 정보 조회"""
    pass

@jira_bp.route('/jira/issues/<issue_key>/update', methods=['PUT'])
def update_jira_issue(issue_key):
    """Jira 이슈 상태 업데이트"""
    pass

@jira_bp.route('/jira/sync', methods=['POST'])
def sync_jira_status():
    """Jira 상태와 테스트 상태 동기화"""
    pass

@jira_bp.route('/jira/webhook', methods=['POST'])
def jira_webhook():
    """Jira 웹훅 처리"""
    pass
```

### 3.2 테스트 실행 시 자동 연동

```python
# backend/routes/automation.py (수정)
@automation_bp.route('/<int:test_id>/execute', methods=['POST'])
def execute_automation_test(test_id):
    # 기존 테스트 실행 로직...
    
    # 테스트 실패 시 Jira 이슈 자동 생성
    if result.status == 'Failed':
        jira_client = JiraClient()
        issue = jira_client.create_issue(
            project_key=app.config['JIRA_PROJECT_KEY'],
            summary=f"자동화 테스트 실패: {test.name}",
            description=f"""
            **테스트 정보**
            - 테스트명: {test.name}
            - 설명: {test.description}
            - 환경: {test.environment}
            - 실행 시간: {execution_time}
            
            **실패 원인**
            {result.notes}
            """,
            issue_type='Bug'
        )
        
        # Jira 연동 정보 저장
        jira_integration = JiraIntegration(
            automation_test_id=test.id,
            jira_issue_key=issue['key'],
            jira_issue_id=issue['id'],
            jira_project_key=app.config['JIRA_PROJECT_KEY'],
            issue_type='Bug',
            status='To Do'
        )
        db.session.add(jira_integration)
        db.session.commit()
```

## 🎨 프론트엔드 구현 방안

### 4.1 Jira 연동 컴포넌트

```javascript
// frontend/src/components/jira/JiraIntegration.js
const JiraIntegration = ({ testId, testType, testResult }) => {
    const [jiraIssues, setJiraIssues] = useState([]);
    const [showCreateModal, setShowCreateModal] = useState(false);
    
    // Jira 이슈 조회
    const fetchJiraIssues = async () => {
        try {
            const response = await axios.get(`/jira/issues?test_id=${testId}&test_type=${testType}`);
            setJiraIssues(response.data);
        } catch (error) {
            console.error('Jira 이슈 조회 오류:', error);
        }
    };
    
    // Jira 이슈 생성
    const createJiraIssue = async (issueData) => {
        try {
            const response = await axios.post('/jira/issues', {
                test_id: testId,
                test_type: testType,
                ...issueData
            });
            setShowCreateModal(false);
            fetchJiraIssues();
        } catch (error) {
            console.error('Jira 이슈 생성 오류:', error);
        }
    };
    
    return (
        <div className="jira-integration">
            <div className="jira-header">
                <h3>🔗 Jira 연동</h3>
                <button 
                    className="btn btn-add"
                    onClick={() => setShowCreateModal(true)}
                >
                    ➕ Jira 이슈 생성
                </button>
            </div>
            
            {/* Jira 이슈 목록 */}
            <div className="jira-issues">
                {jiraIssues.map(issue => (
                    <div key={issue.id} className="jira-issue">
                        <div className="issue-info">
                            <span className="issue-key">{issue.jira_issue_key}</span>
                            <span className="issue-status">{issue.status}</span>
                        </div>
                        <div className="issue-actions">
                            <button 
                                className="btn btn-details"
                                onClick={() => window.open(`https://your-domain.atlassian.net/browse/${issue.jira_issue_key}`)}
                            >
                                🔗 Jira에서 보기
                            </button>
                        </div>
                    </div>
                ))}
            </div>
            
            {/* 이슈 생성 모달 */}
            {showCreateModal && (
                <JiraIssueModal 
                    onSubmit={createJiraIssue}
                    onClose={() => setShowCreateModal(false)}
                />
            )}
        </div>
    );
};
```

### 4.2 Jira 이슈 생성 모달

```javascript
// frontend/src/components/jira/JiraIssueModal.js
const JiraIssueModal = ({ onSubmit, onClose }) => {
    const [issueData, setIssueData] = useState({
        summary: '',
        description: '',
        issue_type: 'Bug',
        priority: 'Medium'
    });
    
    return (
        <div className="modal-overlay">
            <div className="modal">
                <div className="modal-header">
                    <h3>🔗 Jira 이슈 생성</h3>
                    <button className="modal-close" onClick={onClose}>×</button>
                </div>
                <div className="modal-body">
                    <div className="form-group">
                        <label>이슈 요약 *</label>
                        <input
                            type="text"
                            className="form-control"
                            value={issueData.summary}
                            onChange={(e) => setIssueData({...issueData, summary: e.target.value})}
                            placeholder="이슈 요약을 입력하세요"
                        />
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
                </div>
                <div className="modal-actions">
                    <button className="btn btn-cancel" onClick={onClose}>취소</button>
                    <button 
                        className="btn btn-save" 
                        onClick={() => onSubmit(issueData)}
                        disabled={!issueData.summary}
                    >
                        이슈 생성
                    </button>
                </div>
            </div>
        </div>
    );
};
```

## 🤖 자동화 및 웹훅 구현

### 5.1 테스트 실패 시 자동 이슈 생성

```python
# backend/utils/test_result_handler.py
class TestResultHandler:
    def __init__(self):
        self.jira_client = JiraClient()
    
    def handle_test_failure(self, test_result, test_info):
        """테스트 실패 시 자동으로 Jira 이슈 생성"""
        try:
            # 이슈 생성
            issue = self.jira_client.create_issue(
                project_key=app.config['JIRA_PROJECT_KEY'],
                summary=f"테스트 실패: {test_info['name']}",
                description=self._generate_failure_description(test_result, test_info),
                issue_type='Bug',
                priority=self._determine_priority(test_info)
            )
            
            # 연동 정보 저장
            self._save_integration_info(test_result, issue)
            
            return issue
        except Exception as e:
            logger.error(f"Jira 이슈 생성 실패: {e}")
            return None
    
    def _generate_failure_description(self, test_result, test_info):
        """실패 설명 생성"""
        return f"""
        **테스트 정보**
        - 테스트명: {test_info['name']}
        - 타입: {test_info['type']}
        - 환경: {test_info['environment']}
        - 실행 시간: {test_result.execution_time}
        
        **실패 원인**
        {test_result.notes}
        
        **재현 단계**
        1. {test_info['name']} 테스트 실행
        2. {test_info['environment']} 환경에서 실행
        3. 실패 발생
        
        **예상 결과**
        테스트 성공
        
        **실제 결과**
        {test_result.result}
        """
```

### 5.2 Jira 웹훅 처리

```python
# backend/routes/jira_webhook.py
@jira_bp.route('/webhook', methods=['POST'])
def jira_webhook():
    """Jira 웹훅 처리"""
    try:
        # 웹훅 검증
        if not verify_webhook_signature(request):
            return jsonify({'error': 'Invalid signature'}), 401
        
        data = request.json
        event_type = data.get('webhookEvent')
        
        if event_type == 'jira:issue_updated':
            handle_issue_update(data)
        elif event_type == 'jira:issue_created':
            handle_issue_created(data)
        elif event_type == 'jira:issue_deleted':
            handle_issue_deleted(data)
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"웹훅 처리 오류: {e}")
        return jsonify({'error': str(e)}), 500

def handle_issue_update(data):
    """이슈 업데이트 처리"""
    issue = data['issue']
    issue_key = issue['key']
    
    # 데이터베이스에서 연동 정보 조회
    integration = JiraIntegration.query.filter_by(
        jira_issue_key=issue_key
    ).first()
    
    if integration:
        # 상태 동기화
        integration.status = issue['fields']['status']['name']
        integration.updated_at = datetime.utcnow()
        db.session.commit()
        
        # 프론트엔드에 실시간 업데이트 알림 (WebSocket 또는 Server-Sent Events)
        notify_frontend_update(integration)
```

## 📊 대시보드 및 모니터링

### 6.1 Jira 연동 대시보드

```javascript
// frontend/src/components/dashboard/JiraDashboard.js
const JiraDashboard = () => {
    const [jiraStats, setJiraStats] = useState({
        totalIssues: 0,
        openIssues: 0,
        inProgressIssues: 0,
        resolvedIssues: 0
    });
    
    const [recentIssues, setRecentIssues] = useState([]);
    
    useEffect(() => {
        fetchJiraStats();
        fetchRecentIssues();
    }, []);
    
    return (
        <div className="jira-dashboard">
            <div className="stats-grid">
                <div className="stat-card">
                    <h3>📊 총 이슈</h3>
                    <div className="stat-number">{jiraStats.totalIssues}</div>
                </div>
                <div className="stat-card">
                    <h3>🟡 진행 중</h3>
                    <div className="stat-number">{jiraStats.inProgressIssues}</div>
                </div>
                <div className="stat-card">
                    <h3>🟢 해결됨</h3>
                    <div className="stat-number">{jiraStats.resolvedIssues}</div>
                </div>
            </div>
            
            <div className="recent-issues">
                <h3>🕒 최근 이슈</h3>
                {recentIssues.map(issue => (
                    <div key={issue.id} className="issue-item">
                        <span className="issue-key">{issue.jira_issue_key}</span>
                        <span className="issue-summary">{issue.summary}</span>
                        <span className={`issue-status status-${issue.status.toLowerCase()}`}>
                            {issue.status}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};
```

## 📅 구현 단계별 계획

### Phase 1: 기본 인프라 (1-2주)
1. Jira API 클라이언트 구현
2. 데이터베이스 모델 설계 및 마이그레이션
3. 기본 API 엔드포인트 구현
4. 환경 변수 및 설정 관리

### Phase 2: 핵심 기능 (2-3주)
1. 테스트 실패 시 자동 이슈 생성
2. Jira 이슈 조회 및 표시
3. 수동 이슈 생성 기능
4. 기본 연동 상태 관리

### Phase 3: 고급 기능 (2-3주)
1. 웹훅 처리 및 실시간 동기화
2. 이슈 상태 자동 업데이트
3. 우선순위 및 담당자 자동 할당
4. 대시보드 및 통계

### Phase 4: 최적화 및 확장 (1-2주)
1. 성능 최적화
2. 에러 처리 및 로깅
3. 사용자 권한 관리
4. API 문서화

## 🔒 기술적 고려사항

### 8.1 보안
- API 토큰 암호화 저장
- 웹훅 서명 검증
- 사용자 권한 검증

### 8.2 성능
- 비동기 처리 (Celery/Background Tasks)
- 캐싱 전략 (Redis)
- 배치 처리

### 8.3 확장성
- 마이크로서비스 아키텍처 고려
- 플러그인 시스템 설계
- 다중 Jira 인스턴스 지원

## 📝 참고 자료

- [Jira REST API 문서](https://developer.atlassian.com/cloud/jira/platform/rest/v3/)
- [Jira 웹훅 가이드](https://developer.atlassian.com/cloud/jira/platform/webhooks/)
- [Flask-JWT-Extended 문서](https://flask-jwt-extended.readthedocs.io/)
- [React 상태 관리 패턴](https://reactjs.org/docs/state-and-lifecycle.html)

---

**버전**: 1.0  
**상태**: 기획 단계
