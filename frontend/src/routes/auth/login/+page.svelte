<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

	let email = $state('');
	let sent = $state(false);
	let loading = $state(false);
	let error = $state('');

	const GOOGLE_AUTH_URL = `${PUBLIC_API_URL.replace('/api', '')}/accounts/google/login/`;

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		error = '';
		try {
			await authStore.requestMagicLink(email);
			sent = true;
		} catch (err: unknown) {
			const e2 = err as { detail?: string };
			error = e2.detail || 'Something went wrong.';
		} finally {
			loading = false;
		}
	}
</script>

{#if sent}
	<div class="space-y-3">
		<span class="mk mk-sq"></span>
		<h2 class="font-display text-2xl font-bold">Check your email</h2>
		<p class="text-base text-muted-foreground">
			We sent a login link to <strong>{email}</strong>. It expires in 15 minutes.
		</p>
	</div>
{:else}
	<div class="space-y-6">
		<div class="space-y-2">
			<span class="eyebrow">Magic link</span>
			<h2 class="font-display text-3xl font-bold leading-none">Log in</h2>
		</div>

		<form onsubmit={handleSubmit} class="space-y-4">
			<div class="space-y-1.5">
				<Label for="email">Email</Label>
				<Input id="email" type="email" bind:value={email} required placeholder="you@example.com" />
			</div>
			{#if error}
				<p class="font-mono text-sm text-destructive">{error}</p>
			{/if}
			<Button type="submit" disabled={loading} class="w-full">
				{loading ? 'Sending…' : 'Send login link'}
			</Button>
		</form>

		<div class="flex items-center gap-3">
			<div class="h-0.5 flex-1 bg-border"></div>
			<span class="font-mono text-xs uppercase tracking-wider text-muted-foreground">or</span>
			<div class="h-0.5 flex-1 bg-border"></div>
		</div>

		<Button href={GOOGLE_AUTH_URL} variant="outline" class="w-full">
			<svg class="size-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
				<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
				<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
				<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
				<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
			</svg>
			Continue with Google
		</Button>

		<p class="text-center text-sm text-muted-foreground">
			No account? <a href="/auth/signup" class="font-medium text-foreground underline underline-offset-2">Sign up</a>
		</p>
	</div>
{/if}
