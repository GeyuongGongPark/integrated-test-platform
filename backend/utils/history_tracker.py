from models import db, TestCaseHistory
from datetime import datetime
from utils.logger import get_logger

logger = get_logger(__name__)

def track_test_case_change(test_case_id, field_name, old_value, new_value, changed_by, change_type='update'):
    """테스트 케이스 변경 히스토리 추적"""
    try:
        # 값이 실제로 변경되었는지 확인
        if old_value != new_value:
            history = TestCaseHistory(
                test_case_id=test_case_id,
                field_name=field_name,
                old_value=str(old_value) if old_value is not None else None,
                new_value=str(new_value) if new_value is not None else None,
                changed_by=changed_by,
                change_type=change_type,
                changed_at=datetime.utcnow()
            )
            
            db.session.add(history)
            db.session.commit()
            
            logger.info(f"테스트 케이스 {test_case_id} {field_name} 필드 변경 추적: {old_value} -> {new_value}")
            
    except Exception as e:
        logger.error(f"히스토리 추적 실패: {str(e)}")
        db.session.rollback()

def track_test_case_creation(test_case_id, test_case_data, created_by):
    """테스트 케이스 생성 히스토리 추적"""
    try:
        for field_name, value in test_case_data.items():
            if value is not None and value != '':
                history = TestCaseHistory(
                    test_case_id=test_case_id,
                    field_name=field_name,
                    old_value=None,
                    new_value=str(value),
                    changed_by=created_by,
                    change_type='create',
                    changed_at=datetime.utcnow()
                )
                db.session.add(history)
        
        db.session.commit()
        logger.info(f"테스트 케이스 {test_case_id} 생성 히스토리 추적 완료")
        
    except Exception as e:
        logger.error(f"생성 히스토리 추적 실패: {str(e)}")
        db.session.rollback()

def track_test_case_deletion(test_case_id, deleted_by):
    """테스트 케이스 삭제 히스토리 추적"""
    try:
        history = TestCaseHistory(
            test_case_id=test_case_id,
            field_name='deleted',
            old_value='active',
            new_value='deleted',
            changed_by=deleted_by,
            change_type='delete',
            changed_at=datetime.utcnow()
        )
        
        db.session.add(history)
        db.session.commit()
        
        logger.info(f"테스트 케이스 {test_case_id} 삭제 히스토리 추적 완료")
        
    except Exception as e:
        logger.error(f"삭제 히스토리 추적 실패: {str(e)}")
        db.session.rollback()

def get_test_case_history(test_case_id):
    """테스트 케이스 변경 히스토리 조회"""
    try:
        history = TestCaseHistory.query.filter_by(test_case_id=test_case_id)\
            .order_by(TestCaseHistory.changed_at.desc()).all()
        return history
    except Exception as e:
        logger.error(f"히스토리 조회 실패: {str(e)}")
        return []

def get_user_changes(user_id, limit=50):
    """사용자별 변경 히스토리 조회"""
    try:
        history = TestCaseHistory.query.filter_by(changed_by=user_id)\
            .order_by(TestCaseHistory.changed_at.desc())\
            .limit(limit).all()
        return history
    except Exception as e:
        logger.error(f"사용자 변경 히스토리 조회 실패: {str(e)}")
        return []
