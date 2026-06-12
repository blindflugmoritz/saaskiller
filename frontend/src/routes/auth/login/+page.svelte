<script lang="ts">
	import { PUBLIC_API_URL } from '$env/static/public';
	import { authStore } from '$lib/stores/auth.svelte';

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

<div class="space-y-6">
	{#if sent}
		<div class="text-center space-y-2">
			<h2 class="text-2xl font-semibold">Check your email</h2>
			<p class="text-[--color-muted-foreground]">
				We sent a login link to <strong>{email}</strong>. It expires in 15 minutes.
			</p>
		</div>
	{:else}
		<div class="space-y-1">
			<h2 class="text-2xl font-semibold">Log in</h2>
			<p class="text-sm text-[--color-muted-foreground]">We'll send you a magic link.</p>
		</div>
		<form onsubmit={handleSubmit} class="space-y-4">
			<div class="space-y-1">
				<label for="email" class="text-sm font-medium">Email</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					required
					placeholder="you@example.com"
					class="w-full border border-[--color-border] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[--color-ring]"
				/>
			</div>
			{#if error}
				<p class="text-sm text-[--color-destructive]">{error}</p>
			{/if}
			<button
				type="submit"
				disabled={loading}
				class="w-full bg-[--color-primary] text-[--color-primary-foreground] py-2 rounded-md font-medium disabled:opacity-50"
			>
				{loading ? 'Sending…' : 'Send login link'}
			</button>
		</form>
		<div class="relative">
			<div class="absolute inset-0 flex items-center">
				<div class="w-full border-t border-[--color-border]"></div>
			</div>
			<div class="relative flex justify-center text-xs uppercase">
				<span class="bg-[--color-background] px-2 text-[--color-muted-foreground]">or</span>
			</div>
		</div>
		<a
			href={GOOGLE_AUTH_URL}
			class="flex items-center justify-center gap-2 w-full border border-[--color-border] py-2 rounded-md font-medium hover:bg-[--color-secondary] text-sm"
		>
			<svg class="w-4 h-4" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
				<path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
				<path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
				<path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
				<path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
			</svg>
			Continue with Google
		</a>
		<p class="text-center text-sm text-[--color-muted-foreground]">
			No account? <a href="/auth/signup" class="text-[--color-primary] hover:underline">Sign up</a>
		</p>
	{/if}
</div>
