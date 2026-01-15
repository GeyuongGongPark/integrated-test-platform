import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { initializeDatabase, getAccount, getAccountsByEnv } from './db.js';

let dotenvLoaded = false;
let dbInitialized = false;

/**
 * Load .env once if dotenv is available.
 * dotenv가 없으면 조용히 패스 (컨테이너/배포 환경에서 이미 주입된 경우)
 */
async function _ensureDotenvLoaded() {
    if (dotenvLoaded) {
        return;
    }
    
    try {
        const dotenvModule = await import('dotenv');
        const dotenv = dotenvModule.default || dotenvModule;
        if (dotenv && typeof dotenv.config === 'function') {
            // 프로젝트 루트에서 .env 파일 찾기
            const __filename = fileURLToPath(import.meta.url);
            const __dirname = path.dirname(__filename);
            const root = path.resolve(__dirname, '..');
            const envPath = path.join(root, '.env');
            console.log('[Account_env] .env 파일 경로:', envPath);
            console.log('[Account_env] .env 파일 존재 여부:', fs.existsSync(envPath));
            
            const result = dotenv.config({ path: envPath });
            console.log('[Account_env] .env 파일 로드 결과:', result);
            if (result.error) {
                console.error('[Account_env] .env 파일 로드 실패:', result.error);
            } else if (result.parsed) {
                console.log('[Account_env] .env 파일에서 로드된 키:', Object.keys(result.parsed));
            }
        }
    } catch (error) {
        // dotenv가 없으면 조용히 패스 (컨테이너/배포 환경에서 이미 주입된 경우)
        console.log('[Account_env] dotenv 패키지가 없거나 로드 실패:', error.message);
    }
    
    dotenvLoaded = true;
    console.log('[Account_env] 환경변수 ACCOUNT:', process.env.ACCOUNT);
}

/**
 * 프로젝트 루트 기준 경로 추정: 현재 파일 기준 상위로 계산.
 * Account/Account_env.js → 프로젝트 루트는 상위 디렉토리
 */
function _workspaceRoot() {
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    return path.resolve(__dirname, '..');
}

/**
 * DB 초기화 (한 번만 실행)
 */
function _ensureDbInitialized() {
    if (!dbInitialized) {
        initializeDatabase();
        dbInitialized = true;
    }
}

/**
 * .env의 ACCOUNT 키(또는 인자로 받은 키)에 해당하는 Account/Account_JSON/<key>.json을 로드해
 * ENV(DEV/PROD)와 ROLE(master, approver 등)을 구분하여 해당하는 데이터만 환경변수로 주입합니다.
 *
 * - accountKey가 null/undefined이면 .env의 ACCOUNT를 사용
 * - env가 null/undefined이면 .env의 ENV를 사용 (기본값: DEV)
 * - role이 null/undefined이면 .env의 ROLE을 사용 (기본값: master)
 * - 선택된 ENV와 ROLE에 해당하는 데이터만 환경변수로 주입
 *
 * @param {string|null|undefined} accountKey - 계정 키 (선택사항)
 * @param {string|null|undefined} env - 환경 (DEV 또는 PROD, 선택사항)
 * @param {string|null|undefined} role - 역할 (master, approver, legal_advisor, legal, user, 선택사항)
 * @returns {Promise<Object>} 로드된 계정 데이터와 선택된 ENV/ROLE 정보
 */
export async function loadAccountEnv(accountKey = null, env = null, role = null) {
    await _ensureDotenvLoaded();
    _ensureDbInitialized();

    const key = accountKey || process.env.ACCOUNT;
    const selectedEnv = (env || process.env.ENV || 'DEV').toUpperCase();
    const selectedRole = role || process.env.ROLE || 'master';
    
    console.log('[Account_env] accountKey 인자:', accountKey);
    console.log('[Account_env] process.env.ACCOUNT:', process.env.ACCOUNT);
    console.log('[Account_env] 최종 사용할 key:', key);
    console.log('[Account_env] 선택된 ENV:', selectedEnv);
    console.log('[Account_env] 선택된 ROLE:', selectedRole);
    
    if (!key) {
        throw new Error('ACCOUNT 환경변수가 필요합니다 (.env 또는 인자).');
    }

    // DB에서 계정 정보 조회
    const account = await getAccount(key, selectedEnv, selectedRole);
    
    if (!account) {
        // DB에 없으면 사용 가능한 계정 키와 역할 목록 조회
        const accountsByEnv = await getAccountsByEnv(key, selectedEnv);
        const availableRoles = accountsByEnv.map(a => a.role).join(', ');
        
        throw new Error(
            `계정을 찾을 수 없습니다: ${key} - ${selectedEnv} - ${selectedRole}. ` +
            `사용 가능한 ROLE: ${availableRoles || '없음'}`
        );
    }

    console.log('[Account_env] DB에서 계정 정보 로드 성공');

    // base_url 환경변수 설정
    if (account.base_url && !('base_url' in process.env)) {
        process.env.base_url = account.base_url;
        console.log(`[Account_env] 환경변수 설정: base_url = ${account.base_url}`);
    }

    // ROLE의 id, password를 환경변수로 설정
    if (account.user_id) {
        const envKey = `${selectedRole.toUpperCase()}_ID`;
        if (!(envKey in process.env)) {
            process.env[envKey] = account.user_id;
            console.log(`[Account_env] 환경변수 설정: ${envKey} = ${account.user_id}`);
        }
    }

    if (account.password) {
        const envKey = `${selectedRole.toUpperCase()}_PASSWORD`;
        if (!(envKey in process.env)) {
            process.env[envKey] = account.password;
            console.log(`[Account_env] 환경변수 설정: ${envKey} = ***`);
        }
    }

    // ENV와 ROLE 정보도 환경변수로 설정
    if (!('ENV' in process.env)) {
        process.env.ENV = selectedEnv;
    }
    if (!('ROLE' in process.env)) {
        process.env.ROLE = selectedRole;
    }

    console.log('[Account_env] 계정 데이터 로드 완료');
    
    // 호환성을 위해 roleData 객체 생성
    const roleData = {
        id: account.user_id,
        password: account.password
    };

    // 전체 데이터 구조 (호환성 유지)
    const fullData = {
        [selectedEnv]: {
            base_url: account.base_url,
            [selectedRole]: roleData
        }
    };

    return {
        env: selectedEnv,
        role: selectedRole,
        baseUrl: account.base_url,
        roleData: roleData,
        fullData: fullData
    };
}

// 파일이 직접 실행될 때 테스트 실행
const currentFilePath = fileURLToPath(import.meta.url);
const executedFilePath = process.argv[1] ? path.resolve(process.argv[1]) : '';
const isDirectExecution = currentFilePath === executedFilePath || process.argv[1]?.includes('Account_env.js');

if (isDirectExecution) {
    console.log('[Account_env] 직접 실행 모드 감지');
    console.log('[Account_env] 현재 파일:', currentFilePath);
    console.log('[Account_env] 실행 파일:', executedFilePath);
    console.log('[Account_env] loadAccountEnv() 테스트 시작\n');
    
    loadAccountEnv()
        .then((data) => {
            console.log('\n[Account_env] 테스트 완료. 로드된 데이터:', JSON.stringify(data, null, 2));
        })
        .catch((error) => {
            console.error('\n[Account_env] 테스트 실패:', error.message);
            console.error('[Account_env] 에러 스택:', error.stack);
            process.exit(1);
        });
}
