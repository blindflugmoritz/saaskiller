<!-- === FEATURE: stripe === -->
<script lang="ts">
	import { onMount } from 'svelte';
	import { billingStore } from '$lib/stores/billing.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Badge } from '$lib/components/ui/badge';
	import * as Card from '$lib/components/ui/card';

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

<div class="space-y-12">
	<div>
		<p class="eyebrow">Account</p>
		<h1 class="title font-display font-black">Billing</h1>
	</div>

	{#if billingStore.error}
		<div class="border-2 border-destructive bg-destructive/10 px-4 py-3 font-mono text-sm text-destructive">
			{billingStore.error}
		</div>
	{/if}

	<!-- Current subscription -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk"><span class="mk-sq"></span></span>
			<h2 class="font-display text-2xl font-bold">Current subscription</h2>
		</div>
		<div class="rule-thin"></div>

		{#if billingStore.loading && billingStore.subscription === null && billingStore.plans.length === 0}
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">Loading...</p>
		{:else if billingStore.subscription}
			<Card.Root class="rounded-none border-2 border-border">
				<Card.Content class="flex flex-col gap-4 p-6 sm:flex-row sm:items-center sm:justify-between">
					<div class="space-y-2">
						<Badge variant="default" class="rounded-none uppercase tracking-wider">
							{billingStore.subscription.status}
						</Badge>
						<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">
							{billingStore.subscription.cancelAtPeriodEnd
								? 'Cancels on'
								: 'Renews on'} {formatDate(billingStore.subscription.currentPeriodEnd)}
						</p>
					</div>
					<Button
						variant="default"
						onclick={() => billingStore.openPortal()}
						disabled={billingStore.loading}
						class="self-start sm:self-auto"
					>
						Manage subscription
					</Button>
				</Card.Content>
			</Card.Root>
		{:else}
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">No active subscription.</p>
		{/if}
	</section>

	<!-- Plans -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk"><span class="mk-ci"></span></span>
			<h2 class="font-display text-2xl font-bold">Available plans</h2>
		</div>
		<div class="rule-thin"></div>

		{#if billingStore.loading && billingStore.plans.length === 0}
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">Loading plans...</p>
		{:else if billingStore.plans.length === 0}
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">No plans available at this time.</p>
		{:else}
			<div class="grid gap-4 sm:grid-cols-2">
				{#each billingStore.plans.filter((p) => p.isActive) as plan (plan.id)}
					<Card.Root class="flex flex-col rounded-none border-2 border-border">
						<Card.Header>
							<Card.Title class="font-display text-lg font-bold">{plan.name}</Card.Title>
							<p class="mt-2 font-display text-3xl font-black">
								{formatPrice(plan.amountCents, plan.currency)}
								<span class="font-mono text-sm font-normal uppercase tracking-wider text-muted-foreground">/ {plan.interval}</span>
							</p>
						</Card.Header>
						<Card.Footer class="mt-auto">
							<Button
								variant="outline"
								onclick={() => billingStore.startCheckout(plan.stripePriceId)}
								disabled={billingStore.loading}
								class="w-full"
							>
								Upgrade
							</Button>
						</Card.Footer>
					</Card.Root>
				{/each}
			</div>
		{/if}
	</section>
</div>
