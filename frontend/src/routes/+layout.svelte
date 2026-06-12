<script lang="ts">
	import '../app.css';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	// === FEATURE: websockets ===
	import { notificationsStore } from '$lib/stores/notifications.svelte';
	import { tokenStorage } from '$lib/utils/tokenStorage';
	// === END FEATURE: websockets ===
	// === FEATURE: i18n ===
	import { ParaglideJS } from '@inlang/paraglide-sveltekit';
	import { i18n } from '$lib/i18n';
	// === END FEATURE: i18n ===

	const { children } = $props();

	onMount(() => {
		authStore.fetchCurrentUser();
	});

	// === FEATURE: websockets ===
	$effect(() => {
		if (authStore.isAuthenticated) {
			const token = tokenStorage.getAccess();
			if (token) {
				notificationsStore.connect(token);
			}
		} else {
			notificationsStore.disconnect();
		}
	});
	// === END FEATURE: websockets ===
</script>

<!-- === FEATURE: i18n === -->
<ParaglideJS {i18n}>
	{@render children()}
</ParaglideJS>
<!-- === END FEATURE: i18n === -->
