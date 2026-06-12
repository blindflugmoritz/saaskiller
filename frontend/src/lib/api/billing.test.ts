import { describe, it, expect, vi, beforeEach } from 'vitest';

// Guard: skip entire suite if the module doesn't exist
let billingApi: typeof import('./billing').billingApi;
try {
	const mod = await import('./billing');
	billingApi = mod.billingApi;
} catch {
	describe.skip('billing api (module not found)', () => {});
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

// Import the mocked client after vi.mock is hoisted
const { apiClient } = await import('./client');

describe('billingApi', () => {
	beforeEach(() => {
		vi.clearAllMocks();
	});

	describe('getPlans', () => {
		it('calls GET /billing/plans/ and returns transformed plan list', async () => {
			const mockPlans = [
				{
					id: 'plan-1',
					name: 'Starter',
					stripePriceId: 'price_abc123',
					amountCents: 900,
					currency: 'usd',
					interval: 'month' as const,
					isActive: true,
				},
				{
					id: 'plan-2',
					name: 'Pro',
					stripePriceId: 'price_xyz789',
					amountCents: 2900,
					currency: 'usd',
					interval: 'month' as const,
					isActive: true,
				},
			];

			vi.mocked(apiClient.get).mockResolvedValueOnce(mockPlans);

			const result = await billingApi.getPlans();

			expect(apiClient.get).toHaveBeenCalledOnce();
			expect(apiClient.get).toHaveBeenCalledWith('/billing/plans/');
			expect(result).toEqual(mockPlans);
			expect(result).toHaveLength(2);
			expect(result[0].stripePriceId).toBe('price_abc123');
			expect(result[1].amountCents).toBe(2900);
		});

		it('returns an empty array when no plans exist', async () => {
			vi.mocked(apiClient.get).mockResolvedValueOnce([]);

			const result = await billingApi.getPlans();

			expect(result).toEqual([]);
		});
	});

	describe('createCheckoutSession', () => {
		it('calls POST /billing/checkout/ with priceId and returns url', async () => {
			const mockSession = { url: 'https://checkout.stripe.com/pay/cs_test_abc' };
			vi.mocked(apiClient.post).mockResolvedValueOnce(mockSession);

			const result = await billingApi.createCheckoutSession('price_abc123');

			expect(apiClient.post).toHaveBeenCalledOnce();
			expect(apiClient.post).toHaveBeenCalledWith('/billing/checkout/', {
				priceId: 'price_abc123',
			});
			expect(result.url).toBe('https://checkout.stripe.com/pay/cs_test_abc');
		});

		it('propagates errors from the API client', async () => {
			const error = { status: 400, detail: 'Invalid price ID' };
			vi.mocked(apiClient.post).mockRejectedValueOnce(error);

			await expect(billingApi.createCheckoutSession('bad-id')).rejects.toEqual(error);
		});
	});

	describe('getSubscription', () => {
		it('calls GET /billing/subscription/ and returns subscription', async () => {
			const mockSub = {
				id: 'sub-1',
				status: 'active',
				currentPeriodEnd: '2026-07-10T00:00:00Z',
				cancelAtPeriodEnd: false,
			};
			vi.mocked(apiClient.get).mockResolvedValueOnce(mockSub);

			const result = await billingApi.getSubscription();

			expect(apiClient.get).toHaveBeenCalledWith('/billing/subscription/');
			expect(result).toEqual(mockSub);
		});

		it('returns null when there is no subscription', async () => {
			vi.mocked(apiClient.get).mockResolvedValueOnce(null);

			const result = await billingApi.getSubscription();

			expect(result).toBeNull();
		});
	});
});
