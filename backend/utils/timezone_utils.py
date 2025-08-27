from datetime import datetime, timezone, timedelta
import pytz

# KST 시간대 설정
KST = pytz.timezone('Asia/Seoul')

def get_kst_now():
    """현재 KST 시간을 반환합니다."""
    utc_now = datetime.now(timezone.utc)
    kst_now = utc_now.astimezone(KST)
    return kst_now

def get_kst_datetime(utc_datetime):
    """UTC 시간을 KST로 변환합니다."""
    if utc_datetime is None:
        return None
    
    if utc_datetime.tzinfo is None:
        # timezone 정보가 없는 경우 UTC로 가정
        utc_datetime = utc_datetime.replace(tzinfo=timezone.utc)
    
    return utc_datetime.astimezone(KST)

def format_kst_datetime(datetime_obj, format_str='%Y-%m-%d %H:%M:%S'):
    """KST 시간을 지정된 형식으로 포맷팅합니다."""
    if datetime_obj is None:
        return None
    
    kst_datetime = get_kst_datetime(datetime_obj)
    return kst_datetime.strftime(format_str)

def get_kst_isoformat(datetime_obj):
    """KST 시간을 ISO 형식으로 반환합니다."""
    if datetime_obj is None:
        return None
    
    kst_datetime = get_kst_datetime(datetime_obj)
    return kst_datetime.isoformat()

def get_kst_timestamp():
    """현재 KST 시간의 타임스탬프를 반환합니다."""
    return get_kst_now().timestamp()

def get_kst_date_string():
    """현재 KST 날짜를 문자열로 반환합니다 (YYYY-MM-DD)."""
    return get_kst_now().strftime('%Y-%m-%d')

def get_kst_datetime_string():
    """현재 KST 날짜시간을 문자열로 반환합니다 (YYYY-MM-DD HH:MM:SS)."""
    return get_kst_now().strftime('%Y-%m-%d %H:%M:%S')
