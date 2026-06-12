<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	let showDeleteConfirm = $state(false);
	let saving = $state(false);
	let deleting = $state(false);
	let saved = $state(false);

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) goto('/auth/login');
	});

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
			await authStore.logout();
			goto('/');
		} finally {
			deleting = false;
		}
	}
</script>

{#if authStore.isAuthenticated}
	<div class="min-h-screen flex flex-col">
		<header class="border-b border-[--color-border] px-6 py-4 flex items-center gap-4">
			<a href="/dashboard" class="text-sm text-[--color-muted-foreground] hover:underline">← Dashboard</a>
			<h1 class="font-semibold text-lg">Settings</h1>
		</header>
		<main class="flex-1 p-8">
			<div class="max-w-lg mx-auto space-y-8">
				<!-- Account info -->
				<section class="space-y-2">
					<h2 class="text-lg font-medium">Account</h2>
					<p class="text-sm text-[--color-muted-foreground]">{authStore.currentUser?.email}</p>
				</section>

				<!-- Language -->
				<section class="space-y-3">
					<h2 class="text-lg font-medium">Language</h2>
					<div class="flex gap-2">
						{#each [['en', 'English'], ['de', 'Deutsch']] as [code, label]}
							<button
								onclick={() => saveLanguage(code as 'de' | 'en')}
								disabled={saving}
								class="px-4 py-2 rounded-md border text-sm font-medium transition-colors
									{authStore.currentUser?.languagePreference === code
										? 'bg-[--color-primary] text-[--color-primary-foreground] border-[--color-primary]'
										: 'border-[--color-border] hover:bg-[--color-secondary]'}"
							>
								{label}
							</button>
						{/each}
					</div>
					{#if saved}
						<p class="text-sm text-green-600">Saved!</p>
					{/if}
				</section>

				<!-- Danger zone -->
				<section class="space-y-3 border border-[--color-destructive] rounded-md p-4">
					<h2 class="text-lg font-medium text-[--color-destructive]">Danger zone</h2>
					{#if showDeleteConfirm}
						<p class="text-sm">Are you sure? This cannot be undone.</p>
						<div class="flex gap-2">
							<button
								onclick={deleteAccount}
								disabled={deleting}
								class="bg-[--color-destructive] text-[--color-destructive-foreground] px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
							>
								{deleting ? 'Deleting…' : 'Yes, delete my account'}
							</button>
							<button
								onclick={() => (showDeleteConfirm = false)}
								class="border border-[--color-border] px-4 py-2 rounded-md text-sm"
							>
								Cancel
							</button>
						</div>
					{:else}
						<button
							onclick={() => (showDeleteConfirm = true)}
							class="border border-[--color-destructive] text-[--color-destructive] px-4 py-2 rounded-md text-sm font-medium hover:bg-red-50"
						>
							Delete account
						</button>
					{/if}
				</section>
			</div>
		</main>
	</div>
{/if}
