import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { initializeDatabase, saveAccount, closeDatabase } from './db.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * 프로젝트 루트 기준 경로 추정
 */
function _workspaceRoot() {
    return path.resolve(__dirname, '..');
}

/**
 * JSON 파일에서 계정 데이터 로드
 */
function loadJsonFile(filePath) {
    if (!fs.existsSync(filePath)) {
        console.warn(`[마이그레이션] 파일을 찾을 수 없습니다: ${filePath}`);
        return null;
    }
    
    try {
        const fileContent = fs.readFileSync(filePath, 'utf-8').trim();
        
        // 빈 파일 체크
        if (!fileContent) {
            console.warn(`[마이그레이션] 파일이 비어있습니다: ${filePath}`);
            return null;
        }
        
        const data = JSON.parse(fileContent);
        
        // 유효한 객체인지 확인
        if (typeof data !== 'object' || data === null) {
            console.warn(`[마이그레이션] 유효하지 않은 JSON 형식입니다: ${filePath}`);
            return null;
        }
        
        return data;
    } catch (error) {
        console.warn(`[마이그레이션] JSON 파싱 오류 (${filePath}): ${error.message}`);
        return null;
    }
}

/**
 * JSON 데이터를 DB로 마이그레이션
 */
async function migrateJsonToDb(accountKey, jsonData) {
    console.log(`[마이그레이션] ${accountKey} 계정 데이터 마이그레이션 시작...`);
    
    let count = 0;
    
    // DEV와 PROD 환경 순회
    for (const [env, envData] of Object.entries(jsonData)) {
        if (env !== 'DEV' && env !== 'PROD') {
            continue;
        }
        
        const baseUrl = envData.base_url || null;
        
        // 각 역할(role) 순회
        for (const [role, roleData] of Object.entries(envData)) {
            if (role === 'base_url' || typeof roleData !== 'object') {
                continue;
            }
            
            if (roleData.id && roleData.password) {
                await saveAccount(accountKey, env, role, {
                    base_url: baseUrl,
                    id: roleData.id,
                    password: roleData.password
                });
                count++;
                console.log(`[마이그레이션] ✓ ${accountKey} - ${env} - ${role}`);
            }
        }
    }
    
    console.log(`[마이그레이션] ${accountKey} 완료: ${count}개 계정 저장됨\n`);
    return count;
}

/**
 * Account_JSON 디렉토리의 모든 JSON 파일 마이그레이션
 */
async function migrateAllJsonFiles() {
    const root = _workspaceRoot();
    const jsonDir = path.join(root, 'Account', 'Account_JSON');
    
    if (!fs.existsSync(jsonDir)) {
        console.error(`[마이그레이션] 디렉토리를 찾을 수 없습니다: ${jsonDir}`);
        return;
    }
    
    const files = fs.readdirSync(jsonDir).filter(file => file.endsWith('.json'));
    
    if (files.length === 0) {
        console.log('[마이그레이션] 마이그레이션할 JSON 파일이 없습니다.');
        return;
    }
    
    console.log(`[마이그레이션] ${files.length}개 JSON 파일 발견\n`);
    
    let totalCount = 0;
    
    for (const file of files) {
        const accountKey = path.basename(file, '.json');
        const filePath = path.join(jsonDir, file);
        
        try {
            const jsonData = loadJsonFile(filePath);
            
            if (jsonData) {
                const count = await migrateJsonToDb(accountKey, jsonData);
                totalCount += count;
            } else {
                console.log(`[마이그레이션] ${accountKey} 스킵 (파일이 비어있거나 유효하지 않음)`);
            }
        } catch (error) {
            console.error(`[마이그레이션] ${accountKey} 처리 중 오류: ${error.message}`);
            console.error(`[마이그레이션] 파일 경로: ${filePath}`);
        }
    }
    
    console.log(`[마이그레이션] 전체 마이그레이션 완료: 총 ${totalCount}개 계정 저장됨`);
}

/**
 * Samsung 계정 JSON 파일 마이그레이션
 */
async function migrateSamsungJson() {
    const root = _workspaceRoot();
    const samsungJsonPath = path.join(root, 'Base_Code', 'samsung', 'beta', 'account', 'samsung.json');
    
    if (!fs.existsSync(samsungJsonPath)) {
        console.warn(`[마이그레이션] Samsung JSON 파일을 찾을 수 없습니다: ${samsungJsonPath}`);
        return;
    }
    
    try {
        const jsonData = loadJsonFile(samsungJsonPath);
        if (jsonData) {
            await migrateJsonToDb('samsung', jsonData);
        }
    } catch (error) {
        console.error(`[마이그레이션] Samsung 계정 처리 중 오류: ${error.message}`);
    }
}

/**
 * Harim 계정 JSON 파일 마이그레이션
 */
async function migrateHarimJson() {
    const root = _workspaceRoot();
    const harimJsonPath = path.join(root, 'harim', 'harim_account_all.json');
    
    if (!fs.existsSync(harimJsonPath)) {
        console.warn(`[마이그레이션] Harim JSON 파일을 찾을 수 없습니다: ${harimJsonPath}`);
        return;
    }
    
    try {
        const jsonData = loadJsonFile(harimJsonPath);
        if (jsonData) {
            // harim_account_all.json 구조에 따라 처리
            // 필요시 구조에 맞게 수정
            await migrateJsonToDb('harim', jsonData);
        }
    } catch (error) {
        console.error(`[마이그레이션] Harim 계정 처리 중 오류: ${error.message}`);
    }
}

/**
 * 메인 실행 함수
 */
async function main() {
    console.log('[마이그레이션] JSON → DB 마이그레이션 시작\n');
    
    try {
        // DB 초기화
        await initializeDatabase();
        
        // Account_JSON 디렉토리의 모든 파일 마이그레이션
        await migrateAllJsonFiles();
        
        // Samsung 계정 마이그레이션
        await migrateSamsungJson();
        
        // Harim 계정 마이그레이션
        await migrateHarimJson();
        
        console.log('\n[마이그레이션] 모든 마이그레이션 작업 완료!');
    } catch (error) {
        console.error('[마이그레이션] 오류 발생:', error);
        throw error;
    } finally {
        await closeDatabase();
    }
}

// 직접 실행 시 마이그레이션 수행
const isDirectExecution = import.meta.url === `file://${path.resolve(process.argv[1])}` || 
                          process.argv[1]?.includes('migrate_json_to_db.js');

if (isDirectExecution) {
    main().catch(error => {
        console.error(error);
        process.exit(1);
    });
}

export { migrateAllJsonFiles, migrateSamsungJson, migrateHarimJson };

