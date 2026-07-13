<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';

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

<div class="mx-auto w-full max-w-md space-y-6">
	{#if status === 'loading'}
		<div class="border-2 border-border bg-background p-8 text-center space-y-4">
			<div class="mk mk-ci mx-auto"></div>
			<p class="eyebrow justify-center">Magic link</p>
			<p class="font-mono uppercase tracking-wider text-sm text-muted-foreground">
				Logging you in…
			</p>
		</div>
	{:else if status === 'success'}
		<div class="border-2 border-border bg-background p-8 text-center space-y-4">
			<div class="mk mk-sq mx-auto"></div>
			<p class="eyebrow justify-center">Success</p>
			<p class="font-display font-bold text-2xl text-green">Logged in</p>
			<p class="font-mono uppercase tracking-wider text-sm text-muted-foreground">
				Redirecting…
			</p>
		</div>
	{:else}
		<div class="border-2 border-border bg-background p-8 text-center space-y-6">
			<div class="mk mk-tr mx-auto"></div>
			<p class="eyebrow justify-center">Error</p>
			<h2 class="title font-display font-black text-3xl text-foreground">
				Link expired or invalid
			</h2>
			<div class="rule-thin"></div>
			<p class="text-muted-foreground">{errorMessage}</p>
			<Button href="/auth/login" variant="default" size="lg" class="w-full">
				Request a new link
			</Button>
		</div>
	{/if}
</div>
