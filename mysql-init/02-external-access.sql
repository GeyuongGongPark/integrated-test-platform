-- root 사용자 비밀번호 설정 및 외부 접근 권한 부여
ALTER USER 'root'@'localhost' IDENTIFIED BY '1q2w#E$R';

-- 외부 접근을 위한 root 사용자 생성
CREATE USER IF NOT EXISTS 'root'@'%' IDENTIFIED BY '1q2w#E$R';
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 외부 접근을 위한 testuser 권한 설정
CREATE USER IF NOT EXISTS 'testuser'@'%' IDENTIFIED BY '1q2w#E$R';
GRANT ALL PRIVILEGES ON test_management.* TO 'testuser'@'%';

-- 권한 적용
FLUSH PRIVILEGES;
