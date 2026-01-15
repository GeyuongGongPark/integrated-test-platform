import mysql from 'mysql2/promise';
import dotenv from 'dotenv';
import path from 'path';
import { fileURLToPath } from 'url';
import fs from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * 프로젝트 루트 기준 경로 추정
 */
function _workspaceRoot() {
    return path.resolve(__dirname, '..');
}

/**
 * .env 파일 로드
 */
function _loadEnv() {
    const root = _workspaceRoot();
    const envPath = path.join(root, '.env');
    if (fs.existsSync(envPath)) {
        dotenv.config({ path: envPath });
    }
}

// 환경변수 로드
_loadEnv();

let poolInstance = null;

/**
 * MySQL 연결 풀 생성
 */
function _createConnectionPool() {
    const config = {
        host: process.env.DB_HOST || 'localhost',
        port: parseInt(process.env.DB_PORT || '3306'),
        user: process.env.DB_USER || 'root',
        password: process.env.DB_PASSWORD || '',
        database: process.env.DB_NAME || 'lfbz_accounts',
        waitForConnections: true,
        connectionLimit: 10,
        queueLimit: 0,
        enableKeepAlive: true,
        keepAliveInitialDelay: 0
    };

    console.log('[DB] MySQL 연결 설정:', {
        host: config.host,
        port: config.port,
        database: config.database,
        user: config.user
    });

    return mysql.createPool(config);
}

/**
 * DB 연결 풀 가져오기 (싱글톤)
 */
export function getDatabase() {
    if (!poolInstance) {
        poolInstance = _createConnectionPool();
    }
    return poolInstance;
}

/**
 * DB 초기화 (테이블 생성)
 */
export async function initializeDatabase() {
    const pool = getDatabase();
    
    try {
        // accounts 테이블 생성
        await pool.execute(`
            CREATE TABLE IF NOT EXISTS accounts (
                id INT AUTO_INCREMENT PRIMARY KEY,
                account_key VARCHAR(100) NOT NULL,
                env ENUM('DEV', 'PROD') NOT NULL,
                role VARCHAR(50) NOT NULL,
                base_url TEXT,
                user_id VARCHAR(255),
                password VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                UNIQUE KEY unique_account_env_role (account_key, env, role)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
        `);
        
        // 인덱스 생성
        await pool.execute(`
            CREATE INDEX IF NOT EXISTS idx_account_key_env ON accounts(account_key, env)
        `).catch(() => {
            // 인덱스가 이미 존재하면 무시
        });
        
        await pool.execute(`
            CREATE INDEX IF NOT EXISTS idx_account_key ON accounts(account_key)
        `).catch(() => {
            // 인덱스가 이미 존재하면 무시
        });
        
        console.log('[DB] 데이터베이스 초기화 완료');
    } catch (error) {
        console.error('[DB] 초기화 오류:', error.message);
        throw error;
    }
}

/**
 * 계정 정보 조회
 * @param {string} accountKey - 계정 키
 * @param {string} env - 환경 (DEV/PROD)
 * @param {string} role - 역할 (master, approver, legal_advisor, legal, user 등)
 * @returns {Promise<Object|null>} 계정 정보 또는 null
 */
export async function getAccount(accountKey, env, role) {
    const pool = getDatabase();
    
    try {
        const [rows] = await pool.execute(
            `SELECT * FROM accounts 
             WHERE account_key = ? AND env = ? AND role = ?`,
            [accountKey, env.toUpperCase(), role]
        );
        
        return rows.length > 0 ? rows[0] : null;
    } catch (error) {
        console.error('[DB] 계정 조회 오류:', error.message);
        throw error;
    }
}

/**
 * 계정 정보 저장
 * @param {string} accountKey - 계정 키
 * @param {string} env - 환경 (DEV/PROD)
 * @param {string} role - 역할
 * @param {Object} data - 계정 데이터 (base_url, user_id, password 등)
 */
export async function saveAccount(accountKey, env, role, data) {
    const pool = getDatabase();
    
    try {
        await pool.execute(
            `INSERT INTO accounts (account_key, env, role, base_url, user_id, password)
             VALUES (?, ?, ?, ?, ?, ?)
             ON DUPLICATE KEY UPDATE
                 base_url = VALUES(base_url),
                 user_id = VALUES(user_id),
                 password = VALUES(password),
                 updated_at = CURRENT_TIMESTAMP`,
            [
                accountKey,
                env.toUpperCase(),
                role,
                data.base_url || null,
                data.id || data.user_id || null,
                data.password || null
            ]
        );
    } catch (error) {
        console.error('[DB] 계정 저장 오류:', error.message);
        throw error;
    }
}

/**
 * 환경별 모든 계정 정보 조회
 * @param {string} accountKey - 계정 키
 * @param {string} env - 환경 (DEV/PROD)
 * @returns {Promise<Array>} 계정 정보 배열
 */
export async function getAccountsByEnv(accountKey, env) {
    const pool = getDatabase();
    
    try {
        const [rows] = await pool.execute(
            `SELECT * FROM accounts 
             WHERE account_key = ? AND env = ?
             ORDER BY role`,
            [accountKey, env.toUpperCase()]
        );
        
        return rows;
    } catch (error) {
        console.error('[DB] 계정 목록 조회 오류:', error.message);
        throw error;
    }
}

/**
 * 계정 키 목록 조회
 * @returns {Promise<Array>} 계정 키 배열
 */
export async function getAccountKeys() {
    const pool = getDatabase();
    
    try {
        const [rows] = await pool.execute(
            `SELECT DISTINCT account_key FROM accounts ORDER BY account_key`
        );
        
        return rows.map(row => row.account_key);
    } catch (error) {
        console.error('[DB] 계정 키 목록 조회 오류:', error.message);
        throw error;
    }
}

/**
 * DB 연결 종료
 */
export async function closeDatabase() {
    if (poolInstance) {
        await poolInstance.end();
        poolInstance = null;
        console.log('[DB] 데이터베이스 연결 종료');
    }
}
