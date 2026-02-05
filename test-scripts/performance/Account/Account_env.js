import { getAccount, getAccountsByEnv, initializeDatabase } from './db.js';

/**
 * k6에서 돌기 쉬운 경량 계정 로더.
 * - __ENV(또는 process.env)에서 ACCOUNT/ENV/ROLE/BASE_URL/ACCOUNT_JSON을 읽어 동작
 * - ACCOUNT_JSON은 아래 형태의 문자열 JSON:
 *   {
 *     "myAccount": {
 *       "DEV": {
 *         "base_url": "https://dev.example.com",
 *         "master": { "id": "user", "password": "pw" }
 *       }
 *     }
 *   }
 */

// 1차: __ENV(k6) → 2차: process.env(Node) → 3차: .env(open)
const baseEnvSource =
    typeof __ENV !== 'undefined'
        ? __ENV
        : typeof process !== 'undefined' && process.env
        ? process.env
        : {};

function parseDotEnvString(raw) {
    if (!raw) return {};
    const lines = raw.split(/\r?\n/);
    const out = {};
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed || trimmed.startsWith('#')) continue;
        const idx = trimmed.indexOf('=');
        if (idx === -1) continue;
        const key = trimmed.slice(0, idx).trim();
        const value = trimmed.slice(idx + 1).trim();
        out[key] = value;
    }
    return out;
}

let envSource = { ...baseEnvSource };

// k6에서 __ENV가 없거나 ACCOUNT가 비어 있으면 .env를 open()으로 시도
if (!envSource.ACCOUNT) {
    // 1) k6 open
    try {
        if (typeof open === 'function') {
            const envText = open('./.env');
            const parsed = parseDotEnvString(envText);
            envSource = { ...envSource, ...parsed };
            if (parsed.ACCOUNT) {
                console.log('[Account_env] .env에서 ACCOUNT 로드 성공 (open)');
            }
        }
    } catch (error) {
        console.warn('[Account_env] .env 로드 건너뜀(open):', error.message);
    }

    // 2) Node 환경에서 require('fs') 가능 시 동기 로드
    if (!envSource.ACCOUNT) {
        try {
            // eslint-disable-next-line no-new-func
            const req = Function(
                'return typeof require !== "undefined" ? require : null;'
            )();
            const fs = req ? req('fs') : null;
            if (fs && typeof fs.readFileSync === 'function') {
                const envText = fs.readFileSync('./.env', 'utf-8');
                const parsed = parseDotEnvString(envText);
                envSource = { ...envSource, ...parsed };
                if (parsed.ACCOUNT) {
                    console.log('[Account_env] .env에서 ACCOUNT 로드 성공 (fs)');
                }
            }
        } catch (error) {
            console.warn('[Account_env] .env 로드 건너뜀(fs):', error.message);
        }
    }
}

function readEnv(name, fallback = undefined) {
    const value = envSource?.[name];
    return value !== undefined ? value : fallback;
}

function parseAccountJson(raw) {
    if (!raw) return {};
    try {
        return JSON.parse(raw);
    } catch (error) {
        console.error('[Account_env] ACCOUNT_JSON 파싱 실패:', error.message);
        return {};
    }
}

const accountStore = parseAccountJson(readEnv('ACCOUNT_JSON', ''));

/**
 * DB가 없더라도 k6 실행을 막지 않도록 초기화만 보장.
 */
function ensureDbInitialized() {
    try {
        initializeDatabase();
    } catch (error) {
        // k6 환경에선 DB 모듈이 없을 수 있으니 경고만 남김
        console.warn('[Account_env] DB 초기화 건너뜀:', error.message);
    }
}

function pickFromStore(store, key, env, role) {
    const envData = store?.[key]?.[env];
    if (!envData) return null;

    const baseUrl = envData.base_url || envData.baseUrl || null;
    const roleInfo = envData[role] || null;

    if (!roleInfo) {
        return { base_url: baseUrl, roleData: null };
    }

    const roleData = {
        id: roleInfo.id || roleInfo.user_id || null,
        password: roleInfo.password || null
    };

    return { base_url: baseUrl, roleData };
}

/**
 * accountKey/env/role 정보를 기반으로 계정 데이터를 반환.
 * - 반환값: { env, role, baseUrl, roleData, fullData }
 */
export function loadAccountEnv(accountKey = null, env = null, role = null) {
    ensureDbInitialized();

    const key = accountKey || readEnv('ACCOUNT', null);
    const selectedEnv = (env || readEnv('ENV', 'DEV')).toUpperCase();
    const selectedRole = role || readEnv('ROLE', 'master');

    if (!key) {
        throw new Error('ACCOUNT 환경변수가 필요합니다 (__ENV.ACCOUNT).');
    }

    // 1) ACCOUNT_JSON 기반 조회
    const fromStore = pickFromStore(accountStore, key, selectedEnv, selectedRole);

    // 2) DB 조회 (옵션). k6 환경에서 미사용이면 단순 null 반환됨.
    let accountFromDb = null;
    try {
        accountFromDb = getAccount(key, selectedEnv, selectedRole);
    } catch (error) {
        // k6에서는 DB 모듈이 없을 수 있으니 조용히 패스
        accountFromDb = null;
    }

    const baseUrl =
        fromStore?.base_url ||
        accountFromDb?.base_url ||
        readEnv('BASE_URL', null);

    const roleData =
        fromStore?.roleData || (accountFromDb
            ? { id: accountFromDb.user_id, password: accountFromDb.password }
            : {
                  id:
                      readEnv('USER_ID', null) ||
                      readEnv(`${selectedRole.toUpperCase()}_ID`, null),
                  password:
                      readEnv('PASSWORD', null) ||
                      readEnv(`${selectedRole.toUpperCase()}_PASSWORD`, null)
              });

    if (!baseUrl) {
        throw new Error(
            'base_url을 찾을 수 없습니다. __ENV.BASE_URL 또는 ACCOUNT_JSON을 설정하세요.'
        );
    }

    if (!roleData || !roleData.id || !roleData.password) {
        const accountsByEnv = (() => {
            try {
                return getAccountsByEnv(key, selectedEnv) || [];
            } catch (_e) {
                return [];
            }
        })();
        const availableRoles = accountsByEnv.map((a) => a.role).join(', ');
        throw new Error(
            `계정을 찾을 수 없습니다: ${key} - ${selectedEnv} - ${selectedRole}. ` +
                `사용 가능한 ROLE: ${availableRoles || '없음'}. ` +
                'ACCOUNT_JSON 또는 ROLE_ID/PASSWORD 환경변수를 확인하세요.'
        );
    }

    const fullData = {
        [selectedEnv]: {
            base_url: baseUrl,
            [selectedRole]: roleData
        }
    };

    return {
        env: selectedEnv,
        role: selectedRole,
        baseUrl,
        roleData,
        fullData
    };
}
