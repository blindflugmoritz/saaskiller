<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';

	let email = $state('');
	let sent = $state(false);
	let isExisting = $state(false);
	let loading = $state(false);
	let error = $state('');

	async function handleSubmit(e: SubmitEvent) {
		e.preventDefault();
		loading = true;
		error = '';
		try {
			const result = await authStore.signup({ email, languagePreference: 'en' });
			isExisting = result.existing ?? false;
			sent = true;
		} catch (err: unknown) {
			const e2 = err as { detail?: string; email?: string[] };
			error = e2.detail || e2.email?.[0] || 'Something went wrong.';
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
				{#if isExisting}
					We sent a login link to <strong>{email}</strong>.
				{:else}
					We sent a verification link to <strong>{email}</strong>.
				{/if}
			</p>
		</div>
	{:else}
		<div class="space-y-1">
			<h2 class="text-2xl font-semibold">Create account</h2>
			<p class="text-sm text-[--color-muted-foreground]">Enter your email to get started.</p>
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
				{loading ? 'Sending…' : 'Continue with email'}
			</button>
		</form>
		<p class="text-center text-sm text-[--color-muted-foreground]">
			Already have an account? <a href="/auth/login" class="text-[--color-primary] hover:underline">Log in</a>
		</p>
	{/if}
</div>
