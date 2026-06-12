import { PUBLIC_API_URL } from '$env/static/public';
import { transformToCamelCase, transformToSnakeCase } from './transform';
import { tokenStorage } from '$lib/utils/tokenStorage';

export interface ApiError {
	status: number;
	detail?: string;
	[key: string]: unknown;
}

class ApiClient {
	private baseUrl: string;

	constructor(baseUrl: string) {
		this.baseUrl = baseUrl;
	}

	private async refreshToken(): Promise<string | null> {
		const refresh = tokenStorage.getRefresh();
		if (!refresh) return null;
		try {
			const resp = await fetch(`${this.baseUrl}/auth/refresh/`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ refresh }),
			});
			if (!resp.ok) {
				tokenStorage.clear();
				return null;
			}
			const data = await resp.json();
			tokenStorage.set(data.access);
			return data.access;
		} catch {
			tokenStorage.clear();
			return null;
		}
	}

	async request<T>(path: string, options: RequestInit = {}): Promise<T> {
		const url = `${this.baseUrl}${path}`;
		const token = tokenStorage.getAccess();

		const headers: Record<string, string> = {
			'Content-Type': 'application/json',
			...(options.headers as Record<string, string>),
		};
		if (token) {
			headers['Authorization'] = `Bearer ${token}`;
		}

		// Transform outgoing body to snake_case
		if (options.body && typeof options.body === 'string') {
			try {
				const parsed = JSON.parse(options.body);
				options = { ...options, body: JSON.stringify(transformToSnakeCase(parsed)) };
			} catch {
				// Keep original body if not valid JSON
			}
		}

		let response = await fetch(url, { ...options, headers });

		// Auto-refresh on 401
		if (response.status === 401 && token) {
			const newToken = await this.refreshToken();
			if (newToken) {
				headers['Authorization'] = `Bearer ${newToken}`;
				response = await fetch(url, { ...options, headers });
			}
		}

		if (!response.ok) {
			let errorData: Record<string, unknown> = {};
			try {
				errorData = await response.json();
			} catch {
				// ignore
			}
			throw { status: response.status, ...errorData } as ApiError;
		}

		if (response.status === 204) return undefined as T;

		const data = await response.json();
		return transformToCamelCase(data) as T;
	}

	get<T>(path: string): Promise<T> {
		return this.request<T>(path, { method: 'GET' });
	}

	post<T>(path: string, data?: unknown): Promise<T> {
		return this.request<T>(path, {
			method: 'POST',
			body: data !== undefined ? JSON.stringify(data) : undefined,
		});
	}

	put<T>(path: string, data?: unknown): Promise<T> {
		return this.request<T>(path, {
			method: 'PUT',
			body: data !== undefined ? JSON.stringify(data) : undefined,
		});
	}

	patch<T>(path: string, data?: unknown): Promise<T> {
		return this.request<T>(path, {
			method: 'PATCH',
			body: data !== undefined ? JSON.stringify(data) : undefined,
		});
	}

	delete<T>(path: string): Promise<T> {
		return this.request<T>(path, { method: 'DELETE' });
	}
}

export const apiClient = new ApiClient(PUBLIC_API_URL);
