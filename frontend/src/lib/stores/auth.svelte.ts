import { authApi, type User } from '$lib/api/auth';
import { tokenStorage } from '$lib/utils/tokenStorage';

class AuthStore {
	currentUser = $state<User | null>(null);
	authLoading = $state(false);
	authError = $state<string | null>(null);
	isAuthenticated = $derived(this.currentUser !== null);

	async signup(data: { email: string; languagePreference?: string }) {
		this.authLoading = true;
		this.authError = null;
		try {
			return await authApi.signup(data);
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Signup failed.';
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	async verifyEmail(token: string) {
		this.authLoading = true;
		this.authError = null;
		try {
			const result = await authApi.verifyEmail(token);
			tokenStorage.set(result.access, result.refresh);
			this.currentUser = result.user;
			return result;
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Verification failed.';
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	async loginWithMagicLink(token: string) {
		this.authLoading = true;
		this.authError = null;
		try {
			const result = await authApi.loginWithMagicLink(token);
			tokenStorage.set(result.access, result.refresh);
			this.currentUser = result.user;
			return result;
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Login failed.';
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	async requestMagicLink(email: string) {
		this.authLoading = true;
		this.authError = null;
		try {
			return await authApi.requestMagicLink(email);
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Request failed.';
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	async resendVerification(email: string) {
		this.authLoading = true;
		this.authError = null;
		try {
			return await authApi.resendVerification(email);
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Request failed.';
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	async fetchCurrentUser() {
		if (typeof window === 'undefined') return;
		if (!tokenStorage.getAccess()) {
			this.currentUser = null;
			return;
		}
		try {
			this.currentUser = await authApi.getCurrentUser();
		} catch {
			this.currentUser = null;
			tokenStorage.clear();
		}
	}

	async updateLanguagePreference(lang: 'de' | 'en') {
		try {
			const updated = await authApi.updateUser({ languagePreference: lang });
			this.currentUser = updated;
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Update failed.';
			throw err;
		}
	}

	async deleteAccount() {
		this.authLoading = true;
		this.authError = null;
		try {
			await authApi.deleteAccount();
			this.currentUser = null;
			tokenStorage.clear();
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.authError = e.detail || e.message || 'Delete failed.';
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	logout() {
		this.currentUser = null;
		tokenStorage.clear();
	}
}

export const authStore = new AuthStore();
