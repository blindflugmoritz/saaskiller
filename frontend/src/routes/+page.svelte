<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
</script>

<main class="min-h-screen flex flex-col items-center justify-center p-8">
	<div class="max-w-lg text-center space-y-6">
		<h1 class="text-4xl font-bold tracking-tight">SaasKiller</h1>
		<p class="text-lg text-[--color-muted-foreground]">
			A forkable SaaS template. Django + SvelteKit. Ready to ship.
		</p>
		<div class="flex gap-4 justify-center">
			{#if authStore.isAuthenticated}
				<a
					href="/dashboard"
					class="bg-[--color-primary] text-[--color-primary-foreground] px-6 py-2 rounded-md font-medium hover:opacity-90"
				>
					Go to dashboard
				</a>
			{:else}
				<a
					href="/auth/signup"
					class="bg-[--color-primary] text-[--color-primary-foreground] px-6 py-2 rounded-md font-medium hover:opacity-90"
				>
					Get started
				</a>
				<a
					href="/auth/login"
					class="border border-[--color-border] px-6 py-2 rounded-md font-medium hover:bg-[--color-secondary]"
				>
					Log in
				</a>
			{/if}
		</div>
	</div>
</main>
