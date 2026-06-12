<script lang="ts">
	import { page } from '$app/stores';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	type Status = 'loading' | 'success' | 'expired' | 'error';
	let status = $state<Status>('loading');
	let errorMessage = $state('');
	let resendEmail = $state('');
	let resent = $state(false);

	onMount(async () => {
		const token = $page.params.token;
		try {
			await authStore.verifyEmail(token);
			status = 'success';
			setTimeout(() => goto('/dashboard'), 1000);
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

<div class="text-center space-y-4">
	{#if status === 'loading'}
		<p class="text-[--color-muted-foreground]">Verifying…</p>
	{:else if status === 'success'}
		<p class="text-green-600 font-medium">✓ Email verified! Redirecting…</p>
	{:else if status === 'expired'}
		<h2 class="text-xl font-semibold">Link expired</h2>
		<p class="text-[--color-muted-foreground]">Request a new verification link.</p>
		{#if resent}
			<p class="text-green-600 text-sm">New link sent!</p>
		{:else}
			<div class="flex gap-2">
				<input
					type="email"
					bind:value={resendEmail}
					placeholder="your@email.com"
					class="flex-1 border border-[--color-border] rounded-md px-3 py-2 text-sm"
				/>
				<button
					onclick={handleResend}
					class="bg-[--color-primary] text-white px-4 py-2 rounded-md text-sm font-medium"
				>
					Resend
				</button>
			</div>
		{/if}
	{:else}
		<h2 class="text-xl font-semibold">Verification failed</h2>
		<p class="text-[--color-muted-foreground]">{errorMessage}</p>
		<a href="/auth/signup" class="text-[--color-primary] hover:underline text-sm">Back to signup</a>
	{/if}
</div>
