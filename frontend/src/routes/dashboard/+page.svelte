<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) {
			goto('/auth/login');
		}
	});
</script>

{#if authStore.isAuthenticated}
	<div class="min-h-screen flex flex-col">
		<!-- Header -->
		<header class="border-b border-[--color-border] px-6 py-4 flex items-center justify-between">
			<h1 class="font-semibold text-lg">Dashboard</h1>
			<div class="flex items-center gap-4">
				<span class="text-sm text-[--color-muted-foreground]">{authStore.currentUser?.email}</span>
				<a href="/dashboard/settings" class="text-sm hover:underline">Settings</a>
				<button
					onclick={() => { authStore.logout(); goto('/'); }}
					class="text-sm text-[--color-muted-foreground] hover:text-[--color-foreground]"
				>
					Log out
				</button>
			</div>
		</header>
		<!-- Main content -->
		<main class="flex-1 p-8">
			<div class="max-w-4xl mx-auto">
				<h2 class="text-2xl font-semibold mb-2">Welcome</h2>
				<p class="text-[--color-muted-foreground]">
					Your dashboard is empty. Add your product features here.
				</p>
			</div>
		</main>
	</div>
{/if}
