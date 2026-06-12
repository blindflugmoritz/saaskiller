import { apiClient } from './client';

export interface ApiKey {
	id: string;
	name: string;
	prefix: string;
	lastUsedAt: string | null;
	createdAt: string;
	isActive: boolean;
}

export interface ApiKeyCreated extends ApiKey {
	rawKey: string;
}

export const apiKeysApi = {
	listKeys(): Promise<ApiKey[]> {
		return apiClient.get('/api-keys/');
	},

	createKey(name: string): Promise<ApiKeyCreated> {
		return apiClient.post('/api-keys/', { name });
	},

	revokeKey(id: string): Promise<void> {
		return apiClient.delete(`/api-keys/${id}/`);
	},
};
