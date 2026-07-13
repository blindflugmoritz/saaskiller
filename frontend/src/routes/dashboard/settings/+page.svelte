<script lang="ts">
	import { goto } from '$app/navigation';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';

	let showDeleteConfirm = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let saved = $state(false);

	async function saveLanguage(lang: 'de' | 'en') {
		saving = true;
		saved = false;
		try {
			await authStore.updateLanguagePreference(lang);
			saved = true;
			setTimeout(() => (saved = false), 2000);
		} finally {
			saving = false;
		}
	}

	async function deleteAccount() {
		deleting = true;
		try {
			await authStore.deleteAccount();
			goto('/');
		} finally {
			deleting = false;
		}
	}
</script>

<div class="space-y-12">
	<div>
		<p class="eyebrow">Preferences</p>
		<h1 class="title font-display font-black text-5xl mt-4">Settings</h1>
	</div>

	<div class="rule"></div>

	<!-- Account info -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk"><span class="mk-sq"></span></span>
			<h2 class="font-display font-bold text-2xl">Account</h2>
		</div>
		<Card.Root class="border-2 border-border rounded-none">
			<Card.Content class="py-6">
				<p class="font-mono uppercase tracking-wider text-xs text-muted-foreground">Email</p>
				<p class="text-lg mt-1">{authStore.currentUser?.email}</p>
			</Card.Content>
		</Card.Root>
	</section>

	<!-- Language -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk"><span class="mk-ci"></span></span>
			<h2 class="font-display font-bold text-2xl">Language</h2>
		</div>
		<div class="flex gap-3">
			{#each [['en', 'English'], ['de', 'Deutsch']] as [code, label]}
				<Button
					variant={authStore.currentUser?.languagePreference === code ? 'default' : 'outline'}
					onclick={() => saveLanguage(code as 'de' | 'en')}
					disabled={saving}
				>
					{label}
				</Button>
			{/each}
		</div>
		{#if saved}
			<p class="font-mono uppercase tracking-wider text-sm text-green">Saved!</p>
		{/if}
	</section>

	<div class="rule-thin"></div>

	<!-- Danger zone -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk"><span class="mk-tr"></span></span>
			<h2 class="font-display font-bold text-2xl text-destructive">Danger zone</h2>
		</div>
		<Card.Root class="border-2 border-destructive rounded-none">
			<Card.Content class="py-6 space-y-4">
				{#if showDeleteConfirm}
					<p class="text-sm">Are you sure? This cannot be undone.</p>
					<div class="flex gap-3">
						<Button variant="destructive" onclick={deleteAccount} disabled={deleting}>
							{deleting ? 'Deleting…' : 'Yes, delete my account'}
						</Button>
						<Button variant="outline" onclick={() => (showDeleteConfirm = false)}>
							Cancel
						</Button>
					</div>
				{:else}
					<Button variant="outline" onclick={() => (showDeleteConfirm = true)}>
						Delete account
					</Button>
				{/if}
			</Card.Content>
		</Card.Root>
	</section>
</div>
