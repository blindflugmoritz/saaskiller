import { describe, it, expect, vi, beforeEach } from 'vitest';

// Mock the SvelteKit env module before importing client
vi.mock('$env/static/public', () => ({ PUBLIC_API_URL: 'http://localhost:8000/api' }));

// Mock tokenStorage
vi.mock('$lib/utils/tokenStorage', () => ({
	tokenStorage: {
		getAccess: vi.fn(),
		getRefresh: vi.fn(),
		set: vi.fn(),
		clear: vi.fn(),
	},
}));

import { tokenStorage } from '$lib/utils/tokenStorage';
import { apiClient } from './client';

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

function jsonResponse(data: unknown, status = 200) {
	return new Response(JSON.stringify(data), {
		status,
		headers: { 'Content-Type': 'application/json' },
	});
}

beforeEach(() => {
	vi.clearAllMocks();
	vi.mocked(tokenStorage.getAccess).mockReturnValue(null);
	vi.mocked(tokenStorage.getRefresh).mockReturnValue(null);
});

describe('ApiClient — JWT injection', () => {
	it('adds Authorization header when access token exists', async () => {
		vi.mocked(tokenStorage.getAccess).mockReturnValue('my-access-token');
		mockFetch.mockResolvedValueOnce(jsonResponse({ id: 1 }));

		await apiClient.get('/users/me/');

		const [, options] = mockFetch.mock.calls[0];
		expect((options.headers as Record<string, string>)['Authorization']).toBe('Bearer my-access-token');
	});

	it('sends no Authorization header when no token', async () => {
		mockFetch.mockResolvedValueOnce(jsonResponse({ id: 1 }));

		await apiClient.get('/users/me/');

		const [, options] = mockFetch.mock.calls[0];
		expect((options.headers as Record<string, string>)['Authorization']).toBeUndefined();
	});
});

describe('ApiClient — snake↔camel transform', () => {
	it('transforms response keys to camelCase', async () => {
		mockFetch.mockResolvedValueOnce(jsonResponse({ first_name: 'Ada', created_at: '2024-01-01' }));

		const result = await apiClient.get<Record<string, unknown>>('/users/me/');

		expect(result).toEqual({ firstName: 'Ada', createdAt: '2024-01-01' });
	});

	it('transforms request body to snake_case', async () => {
		mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));

		await apiClient.post('/users/me/', { firstName: 'Ada', languagePreference: 'de' });

		const [, options] = mockFetch.mock.calls[0];
		const body = JSON.parse(options.body as string);
		expect(body).toEqual({ first_name: 'Ada', language_preference: 'de' });
	});

	it('handles nested objects in response', async () => {
		mockFetch.mockResolvedValueOnce(jsonResponse({ user_profile: { display_name: 'Ada' } }));

		const result = await apiClient.get<Record<string, unknown>>('/me/');

		expect(result).toEqual({ userProfile: { displayName: 'Ada' } });
	});
});

describe('ApiClient — 401 auto-refresh', () => {
	it('retries with new token after 401', async () => {
		vi.mocked(tokenStorage.getAccess).mockReturnValue('expired-token');
		vi.mocked(tokenStorage.getRefresh).mockReturnValue('valid-refresh');

		// First call: 401, second call (refresh): new token + rotated refresh, third call (retry): success
		mockFetch
			.mockResolvedValueOnce(new Response('', { status: 401 }))
			.mockResolvedValueOnce(jsonResponse({ access: 'new-access-token', refresh: 'new-refresh-token' }))
			.mockResolvedValueOnce(jsonResponse({ id: 1 }));

		const result = await apiClient.get<{ id: number }>('/protected/');

		expect(tokenStorage.set).toHaveBeenCalledWith('new-access-token', 'new-refresh-token');
		expect(result).toEqual({ id: 1 });
		expect(mockFetch).toHaveBeenCalledTimes(3);
	});

	it('throws after 401 when no refresh token available', async () => {
		vi.mocked(tokenStorage.getAccess).mockReturnValue('expired-token');
		vi.mocked(tokenStorage.getRefresh).mockReturnValue(null);

		mockFetch.mockResolvedValueOnce(new Response('', { status: 401 }));

		await expect(apiClient.get('/protected/')).rejects.toMatchObject({ status: 401 });
	});

	it('clears tokens when refresh request fails', async () => {
		vi.mocked(tokenStorage.getAccess).mockReturnValue('expired-token');
		vi.mocked(tokenStorage.getRefresh).mockReturnValue('bad-refresh');

		mockFetch
			.mockResolvedValueOnce(new Response('', { status: 401 }))
			.mockResolvedValueOnce(new Response('', { status: 401 })); // refresh also fails

		await expect(apiClient.get('/protected/')).rejects.toMatchObject({ status: 401 });
		expect(tokenStorage.clear).toHaveBeenCalled();
	});
});

describe('ApiClient — HTTP methods', () => {
	it('handles 204 No Content (returns undefined)', async () => {
		mockFetch.mockResolvedValueOnce(new Response(null, { status: 204 }));

		const result = await apiClient.delete('/users/me/');

		expect(result).toBeUndefined();
	});

	it('throws structured error on non-ok response', async () => {
		mockFetch.mockResolvedValueOnce(jsonResponse({ detail: 'Not found.' }, 404));

		await expect(apiClient.get('/missing/')).rejects.toMatchObject({
			status: 404,
			detail: 'Not found.',
		});
	});

	it('sends correct method for patch', async () => {
		mockFetch.mockResolvedValueOnce(jsonResponse({ ok: true }));

		await apiClient.patch('/users/me/', { firstName: 'Ada' });

		const [, options] = mockFetch.mock.calls[0];
		expect(options.method).toBe('PATCH');
	});
});
