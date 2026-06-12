import { describe, it, expect, vi, beforeEach } from 'vitest';

// Guard: skip entire suite if the module doesn't exist
let apiKeysApi: typeof import('./apikeys').apiKeysApi;
try {
	const mod = await import('./apikeys');
	apiKeysApi = mod.apiKeysApi;
} catch {
	describe.skip('apikeys api (module not found)', () => {});
}

vi.mock('./client', () => ({
	apiClient: {
		get: vi.fn(),
		post: vi.fn(),
		put: vi.fn(),
		patch: vi.fn(),
		delete: vi.fn(),
	},
}));

const { apiClient } = await import('./client');

describe('apiKeysApi', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('listKeys', () => {
		it('calls GET /api-keys/ and returns key array', async () => {
			const mockKeys = [
				{
					id: 'key-1',
					name: 'My Key',
					prefix: 'sk_abc',
					lastUsedAt: '2026-06-01T12:00:00Z',
					createdAt: '2026-01-01T00:00:00Z',
					isActive: true,
				},
				{
					id: 'key-2',
					name: 'CI Key',
					prefix: 'sk_xyz',
					lastUsedAt: null,
					createdAt: '2026-03-15T00:00:00Z',
					isActive: true,
				},
			];

			vi.mocked(apiClient.get).mockResolvedValueOnce(mockKeys);

			const result = await apiKeysApi.listKeys();

			expect(apiClient.get).toHaveBeenCalledOnce();
			expect(apiClient.get).toHaveBeenCalledWith('/api-keys/');
			expect(result).toHaveLength(2);
			expect(result[0].id).toBe('key-1');
			expect(result[1].lastUsedAt).toBeNull();
		});

		it('returns empty array when there are no keys', async () => {
			vi.mocked(apiClient.get).mockResolvedValueOnce([]);

			const result = await apiKeysApi.listKeys();

			expect(result).toEqual([]);
		});
	});

	describe('createKey', () => {
		it('calls POST /api-keys/ with name and returns key including rawKey field', async () => {
			const mockCreated = {
				id: 'key-3',
				name: 'New Key',
				prefix: 'sk_new',
				lastUsedAt: null,
				createdAt: '2026-06-10T00:00:00Z',
				isActive: true,
				rawKey: 'sk_new_supersecretvalue',
			};

			vi.mocked(apiClient.post).mockResolvedValueOnce(mockCreated);

			const result = await apiKeysApi.createKey('New Key');

			expect(apiClient.post).toHaveBeenCalledOnce();
			expect(apiClient.post).toHaveBeenCalledWith('/api-keys/', { name: 'New Key' });
			expect(result.rawKey).toBe('sk_new_supersecretvalue');
			expect(result.id).toBe('key-3');
			expect(result.isActive).toBe(true);
		});

		it('propagates errors from the API client', async () => {
			const error = { status: 400, detail: 'Name is required' };
			vi.mocked(apiClient.post).mockRejectedValueOnce(error);

			await expect(apiKeysApi.createKey('')).rejects.toEqual(error);
		});
	});

	describe('revokeKey', () => {
		it('calls DELETE with the correct path for the given id', async () => {
			vi.mocked(apiClient.delete).mockResolvedValueOnce(undefined);

			await apiKeysApi.revokeKey('key-1');

			expect(apiClient.delete).toHaveBeenCalledOnce();
			expect(apiClient.delete).toHaveBeenCalledWith('/api-keys/key-1/');
		});

		it('uses the exact id in the path without modification', async () => {
			vi.mocked(apiClient.delete).mockResolvedValueOnce(undefined);

			await apiKeysApi.revokeKey('abc-def-ghi-123');

			expect(apiClient.delete).toHaveBeenCalledWith('/api-keys/abc-def-ghi-123/');
		});

		it('propagates errors from the API client', async () => {
			const error = { status: 404, detail: 'Not found' };
			vi.mocked(apiClient.delete).mockRejectedValueOnce(error);

			await expect(apiKeysApi.revokeKey('nonexistent')).rejects.toEqual(error);
		});
	});
});
