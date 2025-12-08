"""
응답 압축 유틸리티
"""
import gzip
from flask import Response
from utils.logger import get_logger

logger = get_logger(__name__)

def compress_response(response):
    """
    Flask 응답 압축
    
    Args:
        response: Flask Response 객체
    
    Returns:
        Response: 압축된 응답
    """
    try:
        # JSON 응답만 압축
        if response.content_type and 'application/json' in response.content_type:
            data = response.get_data()
            
            # 작은 응답은 압축하지 않음 (오버헤드)
            if len(data) < 1024:  # 1KB 미만
                return response
            
            # gzip 압축
            compressed_data = gzip.compress(data)
            
            # 압축된 응답 생성
            compressed_response = Response(
                compressed_data,
                status=response.status_code,
                mimetype=response.content_type,
                headers={
                    'Content-Encoding': 'gzip',
                    'Content-Length': str(len(compressed_data))
                }
            )
            
            # 원본 헤더 복사
            for header, value in response.headers:
                if header not in ['Content-Length', 'Content-Encoding']:
                    compressed_response.headers[header] = value
            
            return compressed_response
        
        return response
        
    except Exception as e:
        logger.error(f"응답 압축 오류: {str(e)}")
        return response

