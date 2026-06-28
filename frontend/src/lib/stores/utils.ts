export function apiError(err: unknown, fallback: string): string {
    if (!err || typeof err !== 'object') return fallback;
    const e = err as Record<string, unknown>;
    // DRF detail string
    if (typeof e.detail === 'string') return e.detail;
    // DRF field-level errors: { email: ['This field is required.'] }
    for (const key of Object.keys(e)) {
        if (key === 'status') continue;
        const val = e[key];
        if (Array.isArray(val) && val.length > 0 && typeof val[0] === 'string') {
            return `${key}: ${val[0]}`;
        }
        if (typeof val === 'string' && val.length > 0 && key !== 'detail') return val;
    }
    // Network errors (TypeError: Failed to fetch) have a .message
    if ('message' in e && typeof e.message === 'string') {
        return 'Network error — please check your connection.';
    }
    return fallback;
}
