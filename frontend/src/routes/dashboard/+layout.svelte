<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';

	let { children } = $props();

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) {
			goto('/auth/login');
		}
	});
</script>

{#if authStore.authLoading}
	<!-- minimal loading state while auth resolves -->
{:else if authStore.isAuthenticated}
	{@render children()}
{/if}
