<!-- === FEATURE: stripe === -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { billingStore } from '$lib/stores/billing.svelte';

	onMount(async () => {
		await Promise.all([billingStore.fetchPlans(), billingStore.fetchSubscription()]);
	});

	function formatPrice(amountCents: number, currency: string): string {
		return new Intl.NumberFormat('en-US', {
			style: 'currency',
			currency: currency.toUpperCase(),
			minimumFractionDigits: 0,
		}).format(amountCents / 100);
	}

	function formatDate(isoString: string): string {
		return new Date(isoString).toLocaleDateString('en-US', {
			year: 'numeric',
			month: 'long',
			day: 'numeric',
		});
	}
</script>

<div class="min-h-screen flex flex-col">
	<!-- Header -->
	<header class="border-b border-[--color-border] px-6 py-4 flex items-center justify-between">
		<h1 class="font-semibold text-lg">Billing</h1>
		<a href="/dashboard" class="text-sm hover:underline">Back to dashboard</a>
	</header>

	<main class="flex-1 p-8">
		<div class="max-w-3xl mx-auto space-y-10">

			{#if billingStore.error}
				<div class="rounded-md bg-red-50 border border-red-200 px-4 py-3 text-sm text-red-700">
					{billingStore.error}
				</div>
			{/if}

			<!-- Current subscription -->
			<section>
				<h2 class="text-xl font-semibold mb-4">Current subscription</h2>
				{#if billingStore.loading && billingStore.subscription === null && billingStore.plans.length === 0}
					<p class="text-[--color-muted-foreground] text-sm">Loading...</p>
				{:else if billingStore.subscription}
					<div class="rounded-lg border border-[--color-border] p-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
						<div class="space-y-1">
							<p class="font-medium capitalize">{billingStore.subscription.status}</p>
							<p class="text-sm text-[--color-muted-foreground]">
								{billingStore.subscription.cancelAtPeriodEnd
									? 'Cancels on'
									: 'Renews on'} {formatDate(billingStore.subscription.currentPeriodEnd)}
							</p>
						</div>
						<button
							onclick={() => billingStore.openPortal()}
							disabled={billingStore.loading}
							class="self-start sm:self-auto inline-flex items-center justify-center rounded-md bg-[--color-primary] px-4 py-2 text-sm font-medium text-[--color-primary-foreground] hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed"
						>
							Manage subscription
						</button>
					</div>
				{:else}
					<p class="text-[--color-muted-foreground] text-sm">No active subscription.</p>
				{/if}
			</section>

			<!-- Plans -->
			<section>
				<h2 class="text-xl font-semibold mb-4">Available plans</h2>
				{#if billingStore.loading && billingStore.plans.length === 0}
					<p class="text-[--color-muted-foreground] text-sm">Loading plans...</p>
				{:else if billingStore.plans.length === 0}
					<p class="text-[--color-muted-foreground] text-sm">No plans available at this time.</p>
				{:else}
					<div class="grid gap-4 sm:grid-cols-2">
						{#each billingStore.plans.filter((p) => p.isActive) as plan (plan.id)}
							<div class="rounded-lg border border-[--color-border] p-5 flex flex-col gap-4">
								<div class="space-y-1">
									<h3 class="font-semibold text-base">{plan.name}</h3>
									<p class="text-2xl font-bold">
										{formatPrice(plan.amountCents, plan.currency)}
										<span class="text-sm font-normal text-[--color-muted-foreground]">/ {plan.interval}</span>
									</p>
								</div>
								<button
									onclick={() => billingStore.startCheckout(plan.stripePriceId)}
									disabled={billingStore.loading}
									class="mt-auto inline-flex items-center justify-center rounded-md border border-[--color-border] px-4 py-2 text-sm font-medium hover:bg-[--color-accent] disabled:opacity-50 disabled:cursor-not-allowed"
								>
									Upgrade
								</button>
							</div>
						{/each}
					</div>
				{/if}
			</section>

		</div>
	</main>
</div>
