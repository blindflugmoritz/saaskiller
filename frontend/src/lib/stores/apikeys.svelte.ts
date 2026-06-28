import { apiKeysApi, type ApiKey } from '$lib/api/apikeys';
import { apiError } from './utils';

class ApiKeysStore {
	keys = $state<ApiKey[]>([]);
	loading = $state(false);
	error = $state<string | null>(null);
	newKeyRaw = $state<string | null>(null);

	async fetchKeys() {
		this.loading = true;
		this.error = null;
		this.newKeyRaw = null;
		try {
			this.keys = await apiKeysApi.listKeys();
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to load API keys.');
		} finally {
			this.loading = false;
		}
	}

	async createKey(name: string) {
		this.loading = true;
		this.error = null;
		try {
			const created = await apiKeysApi.createKey(name);
			this.newKeyRaw = created.rawKey;
			// Add new key (without rawKey) to the list
			const { rawKey: _, ...keyRecord } = created;
			this.keys = [keyRecord, ...this.keys];
			return created;
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to create API key.');
			throw err;
		} finally {
			this.loading = false;
		}
	}

	async revokeKey(id: string) {
		this.loading = true;
		this.error = null;
		try {
			await apiKeysApi.revokeKey(id);
			this.keys = this.keys.filter((k) => k.id !== id);
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to revoke API key.');
			throw err;
		} finally {
			this.loading = false;
		}
	}

	reset() {
		this.keys = [];
		this.loading = false;
		this.error = null;
		this.newKeyRaw = null;
	}
}

export const apiKeysStore = new ApiKeysStore();
