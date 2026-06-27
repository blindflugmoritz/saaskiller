import { vi, describe, it, expect, beforeEach } from 'vitest';

vi.mock('$lib/api/auth', () => ({
	authApi: {
		signup: vi.fn(),
		verifyEmail: vi.fn(),
		loginWithMagicLink: vi.fn(),
		requestMagicLink: vi.fn(),
		resendVerification: vi.fn(),
		getCurrentUser: vi.fn(),
		updateUser: vi.fn(),
		deleteAccount: vi.fn(),
	}
}));

vi.mock('$lib/utils/tokenStorage', () => ({
	tokenStorage: {
		getAccess: vi.fn(),
		getRefresh: vi.fn(),
		set: vi.fn(),
		clear: vi.fn(),
	}
}));

import { authApi } from '$lib/api/auth';
import { tokenStorage } from '$lib/utils/tokenStorage';
import { authStore } from './auth.svelte';

// Cast mocks for type-safe .mockResolvedValue / .mockRejectedValue access
const mockAuthApi = authApi as Record<string, ReturnType<typeof vi.fn>>;
const mockTokenStorage = tokenStorage as Record<string, ReturnType<typeof vi.fn>>;

const fakeUser = {
	id: 'user-1',
	email: 'test@example.com',
	languagePreference: 'en' as const,
	emailVerified: true,
	createdAt: '2024-01-01T00:00:00Z',
};

const fakeTokens = {
	access: 'access-token',
	refresh: 'refresh-token',
	user: fakeUser,
};

beforeEach(() => {
	vi.clearAllMocks();
	// Reset store state to a clean baseline using logout()
	authStore.logout();
});

// ---------------------------------------------------------------------------
// signup
// ---------------------------------------------------------------------------
describe('signup', () => {
	it('sets authLoading to false after a successful call', async () => {
		mockAuthApi.signup.mockResolvedValue({ message: 'Check your email' });

		await authStore.signup({ email: 'test@example.com' });

		expect(authStore.authLoading).toBe(false);
	});

	it('sets authError on failure and re-throws', async () => {
		const err = { detail: 'Email already registered.' };
		mockAuthApi.signup.mockRejectedValue(err);

		await expect(authStore.signup({ email: 'taken@example.com' })).rejects.toEqual(err);

		expect(authStore.authError).toBe('Email already registered.');
		expect(authStore.authLoading).toBe(false);
	});

	it('sets authError from message when detail is absent', async () => {
		const err = { message: 'Network error' };
		mockAuthApi.signup.mockRejectedValue(err);

		await expect(authStore.signup({ email: 'test@example.com' })).rejects.toEqual(err);

		expect(authStore.authError).toBe('Network error');
	});

	it('uses fallback message when error has no detail or message', async () => {
		mockAuthApi.signup.mockRejectedValue({});

		await expect(authStore.signup({ email: 'test@example.com' })).rejects.toBeTruthy();

		expect(authStore.authError).toBe('Signup failed.');
	});
});

// ---------------------------------------------------------------------------
// loginWithMagicLink
// ---------------------------------------------------------------------------
describe('loginWithMagicLink', () => {
	it('sets currentUser and calls tokenStorage.set on success', async () => {
		mockAuthApi.loginWithMagicLink.mockResolvedValue(fakeTokens);

		await authStore.loginWithMagicLink('magic-token');

		expect(authStore.currentUser).toEqual(fakeUser);
		expect(mockTokenStorage.set).toHaveBeenCalledWith(fakeTokens.access, fakeTokens.refresh);
	});

	it('sets isAuthenticated to true after login', async () => {
		mockAuthApi.loginWithMagicLink.mockResolvedValue(fakeTokens);

		await authStore.loginWithMagicLink('magic-token');

		expect(authStore.isAuthenticated).toBe(true);
	});

	it('sets authError on failure and keeps currentUser null', async () => {
		const err = { detail: 'Invalid or expired token.' };
		mockAuthApi.loginWithMagicLink.mockRejectedValue(err);

		await expect(authStore.loginWithMagicLink('bad-token')).rejects.toEqual(err);

		expect(authStore.authError).toBe('Invalid or expired token.');
		expect(authStore.currentUser).toBeNull();
		expect(authStore.isAuthenticated).toBe(false);
	});

	it('does not call tokenStorage.set on failure', async () => {
		mockAuthApi.loginWithMagicLink.mockRejectedValue({ detail: 'Expired.' });

		await expect(authStore.loginWithMagicLink('bad-token')).rejects.toBeTruthy();

		expect(mockTokenStorage.set).not.toHaveBeenCalled();
	});
});

// ---------------------------------------------------------------------------
// fetchCurrentUser
// ---------------------------------------------------------------------------
describe('fetchCurrentUser', () => {
	it('sets currentUser when a token exists in storage and API succeeds', async () => {
		mockTokenStorage.getAccess.mockReturnValue('stored-access-token');
		mockAuthApi.getCurrentUser.mockResolvedValue(fakeUser);

		await authStore.fetchCurrentUser();

		expect(authStore.currentUser).toEqual(fakeUser);
	});

	it('sets currentUser to null when no token is in storage', async () => {
		mockTokenStorage.getAccess.mockReturnValue(null);

		await authStore.fetchCurrentUser();

		expect(authStore.currentUser).toBeNull();
		expect(mockAuthApi.getCurrentUser).not.toHaveBeenCalled();
	});

	it('sets currentUser to null and clears storage when API throws', async () => {
		mockTokenStorage.getAccess.mockReturnValue('stored-access-token');
		mockAuthApi.getCurrentUser.mockRejectedValue(new Error('Unauthorized'));

		await authStore.fetchCurrentUser();

		expect(authStore.currentUser).toBeNull();
		expect(mockTokenStorage.clear).toHaveBeenCalled();
	});
});

// ---------------------------------------------------------------------------
// logout
// ---------------------------------------------------------------------------
describe('logout', () => {
	it('sets currentUser to null', async () => {
		// First log in
		mockAuthApi.loginWithMagicLink.mockResolvedValue(fakeTokens);
		await authStore.loginWithMagicLink('magic-token');
		expect(authStore.currentUser).not.toBeNull();

		authStore.logout();

		expect(authStore.currentUser).toBeNull();
	});

	it('calls tokenStorage.clear()', async () => {
		authStore.logout();

		expect(mockTokenStorage.clear).toHaveBeenCalled();
	});

	it('sets isAuthenticated to false', async () => {
		mockAuthApi.loginWithMagicLink.mockResolvedValue(fakeTokens);
		await authStore.loginWithMagicLink('magic-token');

		authStore.logout();

		expect(authStore.isAuthenticated).toBe(false);
	});
});

// ---------------------------------------------------------------------------
// deleteAccount
// ---------------------------------------------------------------------------
describe('deleteAccount', () => {
	it('clears currentUser and calls tokenStorage.clear() on success', async () => {
		// Start authenticated
		mockAuthApi.loginWithMagicLink.mockResolvedValue(fakeTokens);
		await authStore.loginWithMagicLink('magic-token');

		mockAuthApi.deleteAccount.mockResolvedValue(undefined);
		vi.clearAllMocks(); // clear previous tokenStorage.clear call from beforeEach logout

		await authStore.deleteAccount();

		expect(authStore.currentUser).toBeNull();
		expect(mockTokenStorage.clear).toHaveBeenCalled();
	});

	it('sets authError on failure and re-throws', async () => {
		const err = { detail: 'Cannot delete account.' };
		mockAuthApi.deleteAccount.mockRejectedValue(err);

		await expect(authStore.deleteAccount()).rejects.toEqual(err);

		expect(authStore.authError).toBe('Cannot delete account.');
	});

	it('sets authLoading to false after failure', async () => {
		mockAuthApi.deleteAccount.mockRejectedValue({ detail: 'Failed.' });

		await expect(authStore.deleteAccount()).rejects.toBeTruthy();

		expect(authStore.authLoading).toBe(false);
	});
});

// ---------------------------------------------------------------------------
// updateLanguagePreference
// ---------------------------------------------------------------------------
describe('updateLanguagePreference', () => {
	it('updates currentUser.languagePreference on success', async () => {
		// Start authenticated
		mockAuthApi.loginWithMagicLink.mockResolvedValue(fakeTokens);
		await authStore.loginWithMagicLink('magic-token');

		const updatedUser = { ...fakeUser, languagePreference: 'de' as const };
		mockAuthApi.updateUser.mockResolvedValue(updatedUser);

		await authStore.updateLanguagePreference('de');

		expect(authStore.currentUser?.languagePreference).toBe('de');
		expect(mockAuthApi.updateUser).toHaveBeenCalledWith({ languagePreference: 'de' });
	});

	it('sets authError on failure and re-throws', async () => {
		const err = { detail: 'Update failed on server.' };
		mockAuthApi.updateUser.mockRejectedValue(err);

		await expect(authStore.updateLanguagePreference('en')).rejects.toEqual(err);

		expect(authStore.authError).toBe('Update failed on server.');
	});
});
