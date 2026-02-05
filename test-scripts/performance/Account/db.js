// k6 호환을 위해 Node 내장 모듈과 mysql 의존성을 제거한 경량 인메모리 스토어.
// 필요 시 xk6-sql 등을 별도로 구성하면 여기 로직을 교체할 수 있도록 최소 API만 유지.

const memoryStore = [];

export function initializeDatabase() {
    // k6에서는 별도 초기화 필요 없음. Playwright/Node 환경에서도 side-effect 없음.
    return true;
}

export function getAccount(accountKey, env, role) {
    return (
        memoryStore.find(
            (row) =>
                row.account_key === accountKey &&
                row.env === env.toUpperCase() &&
                row.role === role
        ) || null
    );
}

export function saveAccount(accountKey, env, role, data) {
    const existingIndex = memoryStore.findIndex(
        (row) =>
            row.account_key === accountKey &&
            row.env === env.toUpperCase() &&
            row.role === role
    );

    const row = {
        account_key: accountKey,
        env: env.toUpperCase(),
        role,
        base_url: data.base_url || null,
        user_id: data.id || data.user_id || null,
        password: data.password || null
    };

    if (existingIndex >= 0) {
        memoryStore[existingIndex] = row;
    } else {
        memoryStore.push(row);
    }
}

export function getAccountsByEnv(accountKey, env) {
    return memoryStore
        .filter(
            (row) =>
                row.account_key === accountKey && row.env === env.toUpperCase()
        )
        .sort((a, b) => a.role.localeCompare(b.role));
}

export function getAccountKeys() {
    const keys = new Set(memoryStore.map((row) => row.account_key));
    return Array.from(keys).sort();
}

export function closeDatabase() {
    // 인메모리 스토어이므로 별도 종료 필요 없음
    return true;
}
