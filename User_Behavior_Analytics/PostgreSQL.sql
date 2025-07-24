# 1. PostgreSQL 설치 (Ubuntu 기준)
sudo apt install postgresql postgresql-contrib -y

# 2. postgres 계정으로 접속
sudo -u postgres psql

-- 3. 사용자 및 DB 생성
CREATE USER kafka_user WITH PASSWORD 'kafka123';
CREATE DATABASE gameevents OWNER kafka_user;

-- 4. DB에 접속
\c gameevents

-- 5. public 스키마에 권한 부여
GRANT USAGE ON SCHEMA public TO kafka_user;
GRANT CREATE ON SCHEMA public TO kafka_user;

-- 6. 모든 테이블에 대한 권한 부여 (이미 존재하는 테이블들)
GRANT ALL ON ALL TABLES IN SCHEMA public TO kafka_user;

-- 7. 앞으로 생성될 테이블에도 자동으로 권한 부여되게 설정
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL ON TABLES TO kafka_user;
