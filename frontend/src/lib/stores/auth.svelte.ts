import { authApi, type User } from '$lib/api/auth';
import { tokenStorage } from '$lib/utils/tokenStorage';
import { apiError } from './utils';

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
			this.authError = apiError(err, 'Signup failed.');
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
			this.authError = apiError(err, 'Verification failed.');
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
			this.authError = apiError(err, 'Login failed.');
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
			this.authError = apiError(err, 'Request failed.');
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
			this.authError = apiError(err, 'Request failed.');
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
		this.authLoading = true;
		try {
			this.currentUser = await authApi.getCurrentUser();
		} catch {
			this.currentUser = null;
			tokenStorage.clear();
		} finally {
			this.authLoading = false;
		}
	}

	async updateLanguagePreference(lang: 'de' | 'en') {
		try {
			const updated = await authApi.updateUser({ languagePreference: lang });
			this.currentUser = updated;
		} catch (err: unknown) {
			this.authError = apiError(err, 'Update failed.');
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
			this.authError = apiError(err, 'Delete failed.');
			throw err;
		} finally {
			this.authLoading = false;
		}
	}

	logout() {
		this.currentUser = null;
		this.authError = null;
		tokenStorage.clear();
		// Reset all stores to prevent cross-account data leakage
		// Imported lazily to avoid circular deps at module init time
		import('./apikeys.svelte').then((m) => m.apiKeysStore.reset());
		import('./billing.svelte').then((m) => m.billingStore.reset());
		import('./workspaces.svelte').then((m) => m.workspaceStore.reset());
		import('./notifications.svelte').then((m) => m.notificationsStore.disconnect());
	}
}

export const authStore = new AuthStore();
