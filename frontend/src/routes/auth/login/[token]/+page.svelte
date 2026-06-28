<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	type Status = 'loading' | 'success' | 'error';
	let status = $state<Status>('loading');
	let errorMessage = $state('');

	onMount(async () => {
		const token = page.params.token!;
		const next = page.url.searchParams.get('next') ?? '/dashboard';
		try {
			await authStore.loginWithMagicLink(token);
			status = 'success';
			goto(next);
		} catch (err: unknown) {
			const e = err as { detail?: string; error?: string };
			status = 'error';
			errorMessage = e.detail || e.error || 'Invalid or expired link.';
		}
	});
</script>

<div class="text-center space-y-4">
	{#if status === 'loading'}
		<p class="text-[--color-muted-foreground]">Logging you in…</p>
	{:else if status === 'success'}
		<p class="text-green-600 font-medium">✓ Logged in! Redirecting…</p>
	{:else}
		<h2 class="text-xl font-semibold">Link expired or invalid</h2>
		<p class="text-[--color-muted-foreground]">{errorMessage}</p>
		<a href="/auth/login" class="text-[--color-primary] hover:underline text-sm">Request a new link</a>
	{/if}
</div>
