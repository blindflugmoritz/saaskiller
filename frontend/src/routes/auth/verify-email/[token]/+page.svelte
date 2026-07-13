<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	type Status = 'loading' | 'success' | 'expired' | 'error';
	let status = $state<Status>('loading');
	let errorMessage = $state('');
	let resendEmail = $state('');
	let resent = $state(false);

	onMount(async () => {
		const token = page.params.token!;
		const next = page.url.searchParams.get('next') ?? '/dashboard';
		try {
			await authStore.verifyEmail(token);
			status = 'success';
			goto(next);
		} catch (err: unknown) {
			const e = err as { expired?: boolean; detail?: string; error?: string };
			if (e.expired) {
				status = 'expired';
			} else {
				status = 'error';
				errorMessage = e.detail || e.error || 'Verification failed.';
			}
		}
	});

	async function handleResend() {
		if (!resendEmail) return;
		await authStore.resendVerification(resendEmail);
		resent = true;
	}
</script>

<div class="mx-auto w-full max-w-md">
	{#if status === 'loading'}
		<div class="flex items-center gap-3 border-2 border-border bg-background p-6">
			<span class="mk"><span class="mk-sq"></span></span>
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">Verifying…</p>
		</div>
	{:else if status === 'success'}
		<div class="border-2 border-border bg-background p-6">
			<span class="eyebrow">Verified</span>
			<div class="rule my-4"></div>
			<div class="flex items-center gap-3">
				<span class="mk"><span class="mk-ci bg-green"></span></span>
				<p class="font-display text-lg font-bold text-foreground">Email verified — redirecting…</p>
			</div>
		</div>
	{:else if status === 'expired'}
		<div class="border-2 border-border bg-background p-6">
			<span class="eyebrow">Link expired</span>
			<div class="rule my-4"></div>
			<h2 class="title font-display text-3xl font-black text-foreground">Request a new link</h2>
			<p class="mt-2 font-mono text-sm uppercase tracking-wider text-muted-foreground">
				This verification link is no longer valid.
			</p>
			{#if resent}
				<div class="mt-6 flex items-center gap-3 border-2 border-border p-4">
					<span class="mk"><span class="mk-sq bg-green"></span></span>
					<p class="font-mono text-sm uppercase tracking-wider text-foreground">New link sent!</p>
				</div>
			{:else}
				<div class="mt-6 space-y-3">
					<Label for="resend-email">Email</Label>
					<div class="flex gap-2">
						<Input
							id="resend-email"
							type="email"
							bind:value={resendEmail}
							placeholder="your@email.com"
							class="flex-1"
						/>
						<Button onclick={handleResend}>Resend</Button>
					</div>
				</div>
			{/if}
		</div>
	{:else}
		<div class="border-2 border-border bg-background p-6">
			<span class="eyebrow">Verification failed</span>
			<div class="rule my-4"></div>
			<div class="flex items-center gap-3">
				<span class="mk"><span class="mk-sq bg-red"></span></span>
				<h2 class="font-display text-2xl font-bold text-foreground">Something went wrong</h2>
			</div>
			<p class="mt-2 font-mono text-sm uppercase tracking-wider text-destructive">{errorMessage}</p>
			<div class="rule-thin my-4"></div>
			<Button variant="outline" href="/auth/signup">Back to signup</Button>
		</div>
	{/if}
</div>
