<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';

	let { children } = $props();

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) {
			goto('/auth/login');
		}
	});

	const nav = [
		{ href: '/dashboard', label: 'Overview' },
		{ href: '/dashboard/settings', label: 'Settings' }
	];

	async function handleLogout() {
		authStore.logout();
		goto('/auth/login');
	}
</script>

{#if authStore.authLoading}
	<!-- minimal loading state while auth resolves -->
{:else if authStore.isAuthenticated}
	<div class="min-h-screen bg-background text-foreground">
		<!-- Swiss dashboard header: black bar + yellow rule, brand, nav, logout. -->
		<header class="border-b-[6px] border-yellow bg-primary text-primary-foreground">
			<div class="mx-auto flex max-w-5xl items-baseline justify-between gap-4 px-6 py-4">
				<a href="/dashboard" class="font-display text-xl font-black uppercase tracking-wider">SaasKiller</a>
				<button
					onclick={handleLogout}
					class="font-mono text-xs uppercase tracking-wider text-primary-foreground hover:text-yellow"
				>
					Log out
				</button>
			</div>
			<nav class="mx-auto flex max-w-5xl gap-6 px-6 pb-3">
				{#each nav as item (item.href)}
					<a
						href={item.href}
						class="border-b-[3px] pb-1 font-mono text-xs uppercase tracking-wider transition-colors {page
							.url.pathname === item.href
							? 'border-yellow text-yellow'
							: 'border-transparent text-primary-foreground hover:text-yellow'}"
					>
						{item.label}
					</a>
				{/each}
			</nav>
		</header>

		<main class="mx-auto max-w-5xl px-6 py-12">
			{@render children()}
		</main>
	</div>
{/if}
