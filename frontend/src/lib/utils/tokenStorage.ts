const ACCESS_KEY = 'sk_access_token';
const REFRESH_KEY = 'sk_refresh_token';

function isBrowser(): boolean {
	return typeof window !== 'undefined';
}

export const tokenStorage = {
	getAccess(): string | null {
		if (!isBrowser()) return null;
		return localStorage.getItem(ACCESS_KEY);
	},

	getRefresh(): string | null {
		if (!isBrowser()) return null;
		return localStorage.getItem(REFRESH_KEY);
	},

	set(access: string, refresh?: string): void {
		if (!isBrowser()) return;
		localStorage.setItem(ACCESS_KEY, access);
		if (refresh !== undefined) {
			localStorage.setItem(REFRESH_KEY, refresh);
		}
	},

	clear(): void {
		if (!isBrowser()) return;
		localStorage.removeItem(ACCESS_KEY);
		localStorage.removeItem(REFRESH_KEY);
	},
};
