# 멘션 기능 사용 가이드

## 개요

멘션 기능은 댓글 시스템에서 특정 사용자를 언급하여 알림을 보낼 수 있는 기능입니다. `@username` 형식으로 사용자를 멘션하면 해당 사용자에게 자동으로 알림이 전송됩니다.

## 사용 방법

### 1. 댓글 작성 시 멘션

댓글 내용에 `@username` 형식을 사용하여 사용자를 멘션할 수 있습니다.

**예시:**
```
@admin 이 테스트 케이스를 확인해주세요.
@user1 @user2 이 부분에 대해 의견을 주시면 감사하겠습니다.
```

### 2. API 사용법

#### 댓글 생성 (멘션 포함)

```javascript
// POST /api/collaboration/comments
const response = await axios.post('/api/collaboration/comments', {
  entity_type: 'test_case',  // 'test_case', 'test_result' 등
  entity_id: 123,
  content: '@admin 이 테스트 케이스를 검토해주세요.',
  parent_comment_id: null  // 대댓글인 경우 부모 댓글 ID
}, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

#### 멘션 목록 조회

```javascript
// GET /api/collaboration/mentions
// 읽지 않은 멘션만 조회
const unreadMentions = await axios.get('/api/collaboration/mentions?is_read=false', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

// 모든 멘션 조회
const allMentions = await axios.get('/api/collaboration/mentions', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

#### 멘션 읽음 처리

```javascript
// POST /api/collaboration/mentions/{mention_id}/read
const response = await axios.post(`/api/collaboration/mentions/${mentionId}/read`, {}, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 동작 원리

1. **멘션 추출**: 댓글 생성 시 `@username` 패턴을 자동으로 감지합니다.
2. **사용자 확인**: 멘션된 username이 실제 사용자인지 확인합니다.
3. **멘션 생성**: `Mentions` 테이블에 멘션 기록을 생성합니다.
4. **알림 전송**: 멘션된 사용자에게 자동으로 알림을 전송합니다.

## 멘션 형식

- **기본 형식**: `@username`
- **여러 멘션**: 한 댓글에 여러 사용자를 멘션할 수 있습니다.
  - 예: `@user1 @user2 이 부분 확인 부탁드립니다.`
- **대소문자**: username은 대소문자를 구분하지 않습니다.

## 멘션 응답 형식

### 멘션 목록 응답 예시

```json
[
  {
    "id": 1,
    "entity_type": "test_case",
    "entity_id": 123,
    "mentioned_user_id": 5,
    "mentioned_user_name": "admin",
    "comment_id": 10,
    "is_read": false,
    "created_at": "2025-12-08T10:30:00"
  }
]
```

## 주의사항

1. **사용자명 확인**: 멘션할 사용자의 정확한 username을 사용해야 합니다.
2. **존재하지 않는 사용자**: 존재하지 않는 username을 멘션하면 무시됩니다.
3. **알림 설정**: 사용자가 알림을 받으려면 알림 설정이 활성화되어 있어야 합니다.

## 프론트엔드 통합 예시

### React 컴포넌트 예시

```javascript
import React, { useState } from 'react';
import axios from 'axios';

function CommentForm({ entityType, entityId, onCommentAdded }) {
  const [content, setContent] = useState('');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const response = await axios.post('/api/collaboration/comments', {
        entity_type: entityType,
        entity_id: entityId,
        content: content
      });
      
      // 멘션이 포함된 경우 자동으로 알림이 전송됨
      alert('댓글이 작성되었습니다.');
      setContent('');
      onCommentAdded();
    } catch (error) {
      alert('댓글 작성 중 오류가 발생했습니다.');
    }
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="@username 형식으로 멘션할 수 있습니다"
      />
      <button type="submit">댓글 작성</button>
    </form>
  );
}
```

### 멘션 목록 표시 예시

```javascript
import React, { useEffect, useState } from 'react';
import axios from 'axios';

function MentionList() {
  const [mentions, setMentions] = useState([]);
  
  useEffect(() => {
    fetchMentions();
  }, []);
  
  const fetchMentions = async () => {
    try {
      const response = await axios.get('/api/collaboration/mentions?is_read=false');
      setMentions(response.data);
    } catch (error) {
      console.error('멘션 조회 오류:', error);
    }
  };
  
  const markAsRead = async (mentionId) => {
    try {
      await axios.post(`/api/collaboration/mentions/${mentionId}/read`);
      fetchMentions(); // 목록 새로고침
    } catch (error) {
      console.error('읽음 처리 오류:', error);
    }
  };
  
  return (
    <div>
      <h3>멘션 알림 ({mentions.length})</h3>
      {mentions.map(mention => (
        <div key={mention.id} onClick={() => markAsRead(mention.id)}>
          <p>@{mention.mentioned_user_name}님이 멘션했습니다</p>
          <p>{mention.entity_type} #{mention.entity_id}</p>
          {!mention.is_read && <span>새 알림</span>}
        </div>
      ))}
    </div>
  );
}
```

## API 엔드포인트 요약

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/collaboration/mentions` | 멘션 목록 조회 |
| POST | `/api/collaboration/mentions/{id}/read` | 멘션 읽음 처리 |
| POST | `/api/collaboration/comments` | 댓글 생성 (멘션 포함) |

## 관련 기능

- **댓글 시스템**: 멘션은 댓글 시스템과 통합되어 있습니다.
- **알림 시스템**: 멘션 시 자동으로 알림이 전송됩니다.
- **워크플로우**: 멘션과 함께 워크플로우 상태 전환도 가능합니다.

## 참고

- 멘션 기능은 `backend/services/collaboration_service.py`에서 구현되어 있습니다.
- 멘션 모델은 `backend/models.py`의 `Mention` 클래스에 정의되어 있습니다.
- API 라우트는 `backend/routes/collaboration.py`에 정의되어 있습니다.

