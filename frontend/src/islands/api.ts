// === FEATURE: cms ===
// Minimal API client for Svelte islands (used in Django-rendered CMS pages).
// Cannot use the SvelteKit apiClient ($env/static/public alias not available here).
// The API base URL is passed via a <meta name="api-url"> tag in the Django template.

const ACCESS_KEY = 'sk_access_token';
const REFRESH_KEY = 'sk_refresh_token';

function getTokens() {
	return {
		access: localStorage.getItem(ACCESS_KEY),
		refresh: localStorage.getItem(REFRESH_KEY),
	};
}

function setTokens(access: string, refresh?: string) {
	localStorage.setItem(ACCESS_KEY, access);
	if (refresh) localStorage.setItem(REFRESH_KEY, refresh);
}

function clearTokens() {
	localStorage.removeItem(ACCESS_KEY);
	localStorage.removeItem(REFRESH_KEY);
}

function getApiBase(): string {
	const meta = document.querySelector<HTMLMetaElement>('meta[name="api-url"]');
	return meta?.content ?? '/api';
}

let refreshPromise: Promise<string | null> | null = null;

async function doRefresh(base: string): Promise<string | null> {
	const { refresh } = getTokens();
	if (!refresh) return null;
	try {
		const resp = await fetch(`${base}/auth/refresh/`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ refresh }),
		});
		if (!resp.ok) { clearTokens(); return null; }
		const data = await resp.json();
		setTokens(data.access, data.refresh ?? refresh);
		return data.access;
	} catch {
		clearTokens();
		return null;
	}
}

export async function apiRequest<T>(path: string, options: RequestInit = {}): Promise<T> {
	const base = getApiBase();
	const { access, refresh } = getTokens();

	const headers: Record<string, string> = {
		'Content-Type': 'application/json',
		...(options.headers as Record<string, string>),
	};
	if (access) headers['Authorization'] = `Bearer ${access}`;

	let response = await fetch(`${base}${path}`, { ...options, headers });

	if (response.status === 401 && refresh) {
		if (!refreshPromise) {
			refreshPromise = doRefresh(base).finally(() => { refreshPromise = null; });
		}
		const newToken = await refreshPromise;
		if (newToken) {
			headers['Authorization'] = `Bearer ${newToken}`;
			response = await fetch(`${base}${path}`, { ...options, headers });
		}
	}

	if (!response.ok) {
		let err: Record<string, unknown> = {};
		try { err = await response.json(); } catch { /* ignore */ }
		throw { status: response.status, ...err };
	}
	if (response.status === 204) return undefined as T;
	return response.json() as Promise<T>;
}
// === END FEATURE: cms ===
