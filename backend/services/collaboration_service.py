"""
협업 및 워크플로우 서비스
댓글, 멘션, 워크플로우 관리
"""
from models import db, Comment, Mention, Workflow, WorkflowStep, WorkflowState, User, TestCase
from utils.timezone_utils import get_kst_now
from utils.logger import get_logger
from services.notification_service import notification_service
import json
import re

logger = get_logger(__name__)

class CollaborationService:
    """협업 서비스"""
    
    def create_comment(self, entity_type, entity_id, content, author_id, parent_comment_id=None):
        """
        댓글 생성
        
        Args:
            entity_type: 엔티티 타입 ('test_case', 'test_result', etc.)
            entity_id: 엔티티 ID
            content: 댓글 내용
            author_id: 작성자 ID
            parent_comment_id: 부모 댓글 ID (대댓글인 경우)
        
        Returns:
            Comment: 생성된 댓글
        """
        try:
            comment = Comment(
                entity_type=entity_type,
                entity_id=entity_id,
                content=content,
                author_id=author_id,
                parent_comment_id=parent_comment_id
            )
            
            db.session.add(comment)
            db.session.commit()
            
            # 멘션 추출 및 생성 (작성자는 제외)
            self._extract_and_create_mentions(comment, content, author_id)
            
            logger.info(f"댓글 생성 완료: {entity_type}:{entity_id} by User {author_id}")
            return comment
            
        except Exception as e:
            logger.error(f"댓글 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def _extract_and_create_mentions(self, comment, content, author_id):
        """댓글 내용에서 멘션 추출 및 생성 (본인 멘션도 포함)"""
        try:
            logger.info(f"🔍 멘션 추출 시작: Comment {comment.id}, Content: {content[:100]}..., Author: {author_id}")
            
            # @username 형식의 멘션 찾기
            mention_pattern = r'@(\w+)'
            mentions = re.findall(mention_pattern, content)
            
            logger.info(f"🔍 발견된 멘션 패턴: {mentions}")
            
            if not mentions:
                logger.info("⏭️ 멘션 패턴이 발견되지 않음")
                return
            
            for username in mentions:
                logger.info(f"🔍 멘션 처리 중: @{username}")
                
                # 사용자 찾기 (대소문자 구분 없이)
                user = User.query.filter(
                    db.func.lower(User.username) == db.func.lower(username)
                ).first()
                
                if not user:
                    logger.warning(f"⚠️ 사용자를 찾을 수 없음: @{username}")
                    continue
                
                logger.info(f"✅ 사용자 발견: User {user.id} ({user.username})")
                
                # 멘션 레코드 생성
                mention = Mention(
                    entity_type=comment.entity_type,
                    entity_id=comment.entity_id,
                    mentioned_user_id=user.id,
                    comment_id=comment.id
                )
                db.session.add(mention)
                logger.info(f"✅ 멘션 레코드 추가: Mention for User {user.id}")
                
                # 멘션 알림 전송 (본인인 경우에도 전송)
                logger.info(f"🔔 멘션 알림 생성 시도: User {user.id}, Comment {comment.id}, Entity {comment.entity_type}:{comment.entity_id}, Author {author_id}")
                try:
                    notification = notification_service.create_notification(
                        user_id=user.id,
                        notification_type='mention',
                        title='멘션 알림',
                        message=f"댓글에서 멘션되었습니다: {comment.content[:50]}...",
                        related_test_case_id=comment.entity_id if comment.entity_type == 'test_case' else None,
                        priority='medium'
                    )
                    logger.info(f"✅ 멘션 알림 생성 성공: Notification ID {notification.id if notification else 'None'}")
                except Exception as e:
                    logger.error(f"❌ 멘션 알림 생성 실패: {str(e)}", exc_info=True)
                    # 알림 생성 실패해도 멘션 레코드는 저장
            
            db.session.commit()
            logger.info(f"✅ 멘션 추출 완료: Comment {comment.id}")
            
        except Exception as e:
            logger.error(f"❌ 멘션 추출 오류: {str(e)}", exc_info=True)
            db.session.rollback()
    
    def update_comment(self, comment_id, content, user_id):
        """댓글 수정"""
        try:
            comment = Comment.query.get(comment_id)
            if not comment:
                raise ValueError(f"댓글을 찾을 수 없습니다: {comment_id}")
            
            # 권한 확인 (작성자만 수정 가능)
            if comment.author_id != user_id:
                raise PermissionError("댓글을 수정할 권한이 없습니다")
            
            comment.content = content
            comment.is_edited = True
            db.session.commit()
            
            logger.info(f"댓글 수정 완료: {comment_id}")
            return comment
            
        except Exception as e:
            logger.error(f"댓글 수정 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def delete_comment(self, comment_id, user_id):
        """댓글 삭제 (소프트 삭제)"""
        try:
            comment = Comment.query.get(comment_id)
            if not comment:
                raise ValueError(f"댓글을 찾을 수 없습니다: {comment_id}")
            
            # 권한 확인 (작성자만 삭제 가능)
            if comment.author_id != user_id:
                raise PermissionError("댓글을 삭제할 권한이 없습니다")
            
            comment.is_deleted = True
            comment.content = "[삭제된 댓글입니다]"
            db.session.commit()
            
            logger.info(f"댓글 삭제 완료: {comment_id}")
            return comment
            
        except Exception as e:
            logger.error(f"댓글 삭제 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def get_comments(self, entity_type, entity_id, include_deleted=False):
        """엔티티의 댓글 목록 조회"""
        try:
            from sqlalchemy.orm import joinedload
            
            query = Comment.query.options(joinedload(Comment.author)).filter_by(
                entity_type=entity_type,
                entity_id=entity_id,
                parent_comment_id=None  # 부모 댓글만 조회
            )
            
            if not include_deleted:
                query = query.filter_by(is_deleted=False)
            
            comments = query.order_by(Comment.created_at.asc()).all()
            
            # 대댓글 포함하여 반환
            result = []
            for comment in comments:
                comment_dict = comment.to_dict()
                # 대댓글 추가 (author 관계도 함께 로드)
                replies = Comment.query.options(joinedload(Comment.author)).filter_by(
                    parent_comment_id=comment.id,
                    is_deleted=False
                ).order_by(Comment.created_at.asc()).all()
                comment_dict['replies'] = [r.to_dict() for r in replies]
                result.append(comment_dict)
            
            return result
            
        except Exception as e:
            logger.error(f"댓글 목록 조회 오류: {str(e)}")
            return []
    
    def get_user_mentions(self, user_id, is_read=None):
        """사용자의 멘션 목록 조회"""
        try:
            query = Mention.query.filter_by(mentioned_user_id=user_id)
            
            if is_read is not None:
                query = query.filter_by(is_read=is_read)
            
            mentions = query.order_by(Mention.created_at.desc()).all()
            return [m.to_dict() for m in mentions]
            
        except Exception as e:
            logger.error(f"멘션 목록 조회 오류: {str(e)}")
            return []
    
    def mark_mention_as_read(self, mention_id, user_id):
        """멘션 읽음 처리"""
        try:
            mention = Mention.query.get(mention_id)
            if not mention:
                raise ValueError(f"멘션을 찾을 수 없습니다: {mention_id}")
            
            if mention.mentioned_user_id != user_id:
                raise PermissionError("이 멘션을 읽음 처리할 권한이 없습니다")
            
            mention.is_read = True
            db.session.commit()
            
            return mention
            
        except Exception as e:
            logger.error(f"멘션 읽음 처리 오류: {str(e)}")
            db.session.rollback()
            raise

class WorkflowService:
    """워크플로우 서비스"""
    
    def create_workflow(self, name, workflow_type, initial_status, steps, created_by, project_id=None, description=None):
        """
        워크플로우 생성
        
        Args:
            name: 워크플로우 이름
            workflow_type: 워크플로우 타입
            initial_status: 초기 상태
            steps: 단계 목록 (list of dict)
            created_by: 생성자 ID
            project_id: 프로젝트 ID (선택적)
            description: 설명
        
        Returns:
            Workflow: 생성된 워크플로우
        """
        try:
            workflow = Workflow(
                name=name,
                description=description,
                workflow_type=workflow_type,
                initial_status=initial_status,
                project_id=project_id,
                created_by=created_by
            )
            
            db.session.add(workflow)
            db.session.flush()  # workflow.id를 얻기 위해
            
            # 단계 추가
            for order, step_data in enumerate(steps, 1):
                step = WorkflowStep(
                    workflow_id=workflow.id,
                    name=step_data['name'],
                    display_name=step_data.get('display_name', step_data['name']),
                    description=step_data.get('description'),
                    order=order,
                    allowed_roles=json.dumps(step_data.get('allowed_roles', [])),
                    allowed_user_ids=json.dumps(step_data.get('allowed_user_ids', [])),
                    next_steps=json.dumps(step_data.get('next_steps', [])),
                    auto_transition_condition=json.dumps(step_data.get('auto_transition_condition')) if step_data.get('auto_transition_condition') else None
                )
                db.session.add(step)
            
            db.session.commit()
            
            logger.info(f"워크플로우 생성 완료: {name} (ID: {workflow.id})")
            return workflow
            
        except Exception as e:
            logger.error(f"워크플로우 생성 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def apply_workflow_to_entity(self, entity_type, entity_id, workflow_id):
        """엔티티에 워크플로우 적용"""
        try:
            workflow = Workflow.query.get(workflow_id)
            if not workflow:
                raise ValueError(f"워크플로우를 찾을 수 없습니다: {workflow_id}")
            
            # 초기 단계 찾기
            initial_step = WorkflowStep.query.filter_by(
                workflow_id=workflow_id,
                name=workflow.initial_status
            ).first()
            
            if not initial_step:
                raise ValueError(f"초기 단계를 찾을 수 없습니다: {workflow.initial_status}")
            
            # 기존 상태 확인
            existing_state = WorkflowState.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            ).first()
            
            if existing_state:
                # 기존 상태 업데이트
                existing_state.workflow_id = workflow_id
                existing_state.current_step_id = initial_step.id
                existing_state.current_status = workflow.initial_status
            else:
                # 새 상태 생성
                state = WorkflowState(
                    entity_type=entity_type,
                    entity_id=entity_id,
                    workflow_id=workflow_id,
                    current_step_id=initial_step.id,
                    current_status=workflow.initial_status
                )
                db.session.add(state)
            
            db.session.commit()
            
            logger.info(f"워크플로우 적용 완료: {entity_type}:{entity_id} -> {workflow.name}")
            return existing_state if existing_state else state
            
        except Exception as e:
            logger.error(f"워크플로우 적용 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def transition_workflow_state(self, entity_type, entity_id, next_status, user_id, user_role=None):
        """
        워크플로우 상태 전환
        
        Args:
            entity_type: 엔티티 타입
            entity_id: 엔티티 ID
            next_status: 다음 상태
            user_id: 전환을 요청한 사용자 ID
            user_role: 사용자 역할 (선택적)
        
        Returns:
            WorkflowState: 업데이트된 상태
        """
        try:
            state = WorkflowState.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            ).first()
            
            if not state:
                raise ValueError(f"워크플로우 상태를 찾을 수 없습니다: {entity_type}:{entity_id}")
            
            current_step = state.current_step
            if not current_step:
                raise ValueError("현재 단계를 찾을 수 없습니다")
            
            # 다음 단계 확인
            next_steps = json.loads(current_step.next_steps) if current_step.next_steps else []
            if next_status not in next_steps:
                raise ValueError(f"'{next_status}'로 전환할 수 없습니다. 가능한 다음 단계: {next_steps}")
            
            # 권한 확인
            allowed_roles = json.loads(current_step.allowed_roles) if current_step.allowed_roles else []
            allowed_user_ids = json.loads(current_step.allowed_user_ids) if current_step.allowed_user_ids else []
            
            has_permission = False
            if user_role and user_role in allowed_roles:
                has_permission = True
            elif user_id in allowed_user_ids:
                has_permission = True
            
            if not has_permission:
                raise PermissionError("워크플로우 상태를 전환할 권한이 없습니다")
            
            # 다음 단계 찾기
            next_step = WorkflowStep.query.filter_by(
                workflow_id=state.workflow_id,
                name=next_status
            ).first()
            
            if not next_step:
                raise ValueError(f"다음 단계를 찾을 수 없습니다: {next_status}")
            
            # 상태 업데이트
            state.previous_status = state.current_status
            state.current_status = next_status
            state.current_step_id = next_step.id
            state.changed_by = user_id
            state.updated_at = get_kst_now()
            
            db.session.commit()
            
            logger.info(f"워크플로우 상태 전환 완료: {entity_type}:{entity_id} {state.previous_status} -> {next_status}")
            return state
            
        except Exception as e:
            logger.error(f"워크플로우 상태 전환 오류: {str(e)}")
            db.session.rollback()
            raise
    
    def get_entity_workflow_state(self, entity_type, entity_id):
        """엔티티의 워크플로우 상태 조회"""
        try:
            state = WorkflowState.query.filter_by(
                entity_type=entity_type,
                entity_id=entity_id
            ).first()
            
            if state:
                return state.to_dict()
            return None
            
        except Exception as e:
            logger.error(f"워크플로우 상태 조회 오류: {str(e)}")
            return None

# 전역 서비스 인스턴스
collaboration_service = CollaborationService()
workflow_service = WorkflowService()

