<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';

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

<div class="space-y-8">
	{#if sent}
		<div class="space-y-4">
			<div class="mk"><span class="mk-sq"></span></div>
			<p class="eyebrow">Check your email</p>
			<h2 class="title font-display font-black text-4xl">You're in the loop</h2>
			<div class="rule"></div>
			<p class="text-muted-foreground">
				{#if isExisting}
					We sent a login link to <strong class="text-foreground font-mono">{email}</strong>.
				{:else}
					We sent a verification link to <strong class="text-foreground font-mono">{email}</strong>.
				{/if}
			</p>
		</div>
	{:else}
		<div class="space-y-4">
			<div class="mk"><span class="mk-ci"></span></div>
			<p class="eyebrow">Get started</p>
			<h2 class="title font-display font-black text-4xl">Create account</h2>
			<div class="rule"></div>
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">
				Enter your email to get started.
			</p>
		</div>
		<form onsubmit={handleSubmit} class="space-y-6">
			<div class="space-y-2">
				<Label for="email" class="font-mono uppercase tracking-wider text-xs">Email</Label>
				<Input
					id="email"
					type="email"
					bind:value={email}
					required
					placeholder="you@example.com"
				/>
			</div>
			{#if error}
				<p class="border-2 border-destructive bg-destructive/10 px-3 py-2 font-mono text-sm text-destructive">
					{error}
				</p>
			{/if}
			<Button type="submit" disabled={loading} size="lg" class="w-full">
				{loading ? 'Sending…' : 'Continue with email'}
			</Button>
		</form>
		<div class="rule-thin"></div>
		<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">
			Already have an account?
			<a href="/auth/login" class="text-primary underline underline-offset-4 hover:no-underline">Log in</a>
		</p>
	{/if}
</div>
