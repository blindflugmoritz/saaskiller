// === FEATURE: stripe ===
import { apiClient } from './client';

export interface Plan {
	id: string;
	name: string;
	stripePriceId: string;
	amountCents: number;
	currency: string;
	interval: 'month' | 'year';
	isActive: boolean;
}

export interface Subscription {
	id: string;
	status: string;
	currentPeriodEnd: string;
	cancelAtPeriodEnd: boolean;
}

export interface CheckoutSession {
	url: string;
}

export interface PortalSession {
	url: string;
}

export const billingApi = {
	getPlans(): Promise<Plan[]> {
		return apiClient.get('/billing/plans/');
	},

	getSubscription(): Promise<Subscription | null> {
		return apiClient.get('/billing/subscription/');
	},

	createCheckoutSession(priceId: string): Promise<CheckoutSession> {
		return apiClient.post('/billing/checkout/', { priceId });
	},

	createPortalSession(): Promise<PortalSession> {
		return apiClient.post('/billing/portal/');
	},
};
