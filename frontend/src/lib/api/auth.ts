import { apiClient } from './client';

export interface User {
	id: string;
	email: string;
	languagePreference: 'de' | 'en';
	emailVerified: boolean;
	createdAt: string;
}

export interface AuthTokens {
	access: string;
	refresh: string;
	user: User;
}

export interface SignupResponse {
	user?: User;
	message: string;
	existing?: boolean;
}

export const authApi = {
	signup(data: { email: string; languagePreference?: string }): Promise<SignupResponse> {
		return apiClient.post('/auth/signup/', data);
	},

	verifyEmail(token: string): Promise<AuthTokens> {
		return apiClient.post(`/auth/verify-email/${token}/`, {});
	},

	resendVerification(email: string): Promise<{ message: string }> {
		return apiClient.post('/auth/resend-verification/', { email });
	},

	requestMagicLink(email: string): Promise<{ message: string }> {
		return apiClient.post('/auth/request-magic-link/', { email });
	},

	loginWithMagicLink(token: string): Promise<AuthTokens> {
		return apiClient.post('/auth/login/', { token });
	},

	getCurrentUser(): Promise<User> {
		return apiClient.get('/auth/me/');
	},

	updateUser(data: Partial<Pick<User, 'languagePreference'>>): Promise<User> {
		return apiClient.patch('/auth/me/', data);
	},

	deleteAccount(): Promise<void> {
		return apiClient.delete('/auth/me/delete/');
	},
};
