// === FEATURE: stripe ===
import { billingApi, type Plan, type Subscription } from '$lib/api/billing';

class BillingStore {
	plans = $state<Plan[]>([]);
	subscription = $state<Subscription | null>(null);
	loading = $state(false);
	error = $state<string | null>(null);

	async fetchPlans() {
		this.loading = true;
		this.error = null;
		try {
			this.plans = await billingApi.getPlans();
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.error = e.detail || e.message || 'Failed to load plans.';
		} finally {
			this.loading = false;
		}
	}

	async fetchSubscription() {
		this.loading = true;
		this.error = null;
		try {
			this.subscription = await billingApi.getSubscription();
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string; status?: number };
			// 404 means no subscription — treat as null, not an error
			if ((err as { status?: number }).status === 404) {
				this.subscription = null;
			} else {
				this.error = e.detail || e.message || 'Failed to load subscription.';
			}
		} finally {
			this.loading = false;
		}
	}

	async startCheckout(priceId: string) {
		this.loading = true;
		this.error = null;
		try {
			const session = await billingApi.createCheckoutSession(priceId);
			window.location.href = session.url;
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.error = e.detail || e.message || 'Failed to start checkout.';
			this.loading = false;
		}
	}

	async openPortal() {
		this.loading = true;
		this.error = null;
		try {
			const session = await billingApi.createPortalSession();
			window.location.href = session.url;
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			this.error = e.detail || e.message || 'Failed to open billing portal.';
			this.loading = false;
		}
	}
}

export const billingStore = new BillingStore();
