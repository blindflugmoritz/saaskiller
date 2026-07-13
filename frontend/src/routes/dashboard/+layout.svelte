<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { authStore } from '$lib/stores/auth.svelte';
	import { Sidebar, type SidebarNavItem } from '$lib/components/ui/sidebar';

	let { children } = $props();

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) {
			goto('/auth/login');
		}
	});

	const nav: SidebarNavItem[] = [
		{ href: '/dashboard', label: 'Overview', marker: 'sq' },
		{ href: '/dashboard/settings', label: 'Settings', marker: 'ci' }
	];

	function handleLogout() {
		authStore.logout();
		goto('/auth/login');
	}
</script>

{#if authStore.authLoading}
	<!-- minimal loading state while auth resolves -->
{:else if authStore.isAuthenticated}
	<!-- Swiss dashboard shell: fixed sidebar (nav + user footer) beside content. -->
	<div class="flex min-h-screen bg-background text-foreground">
		<Sidebar items={nav} pathname={page.url.pathname}>
			{#snippet footer()}
				<div class="flex flex-col gap-2">
					<span class="truncate font-mono text-[11px] uppercase tracking-wider text-primary-foreground">
						{authStore.currentUser?.email ?? ''}
					</span>
					<button
						onclick={handleLogout}
						class="text-left font-mono text-xs uppercase tracking-wider text-primary-foreground hover:text-yellow"
					>
						Log out →
					</button>
				</div>
			{/snippet}
		</Sidebar>

		<main class="min-w-0 flex-1 px-6 py-12 md:px-10">
			<div class="mx-auto max-w-4xl">
				{@render children()}
			</div>
		</main>
	</div>
{/if}
