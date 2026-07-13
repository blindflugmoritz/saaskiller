<script lang="ts">
	import { authStore } from '$lib/stores/auth.svelte';
	import { Button } from '$lib/components/ui/button';
	import { SiteHeader } from '$lib/components/ui/site-header';
</script>

<!-- Swiss/poster landing: reusable SiteHeader, mono eyebrow, big Helvetica
     display title, geometric markers, shadcn buttons. -->
<div class="min-h-screen bg-background text-foreground">
	<SiteHeader brand="SaasKiller" chip="Django · SvelteKit" />

	<main class="mx-auto max-w-5xl px-6 py-20">
		<span class="eyebrow">Forkable SaaS template</span>
		<h1 class="title mt-4 text-5xl md:text-7xl">Ship the product,<br />not the boilerplate.</h1>
		<p class="mt-6 max-w-[60ch] text-xl leading-relaxed">
			Auth, billing, teams, tasks and deploy — already wired. Fork it, strip what
			you don't need, and build the thing you actually care about.
		</p>

		<div class="mt-8 flex flex-wrap gap-4">
			{#if authStore.isAuthenticated}
				<Button href="/dashboard" size="lg">Go to dashboard →</Button>
			{:else}
				<Button href="/auth/signup" size="lg">Get started</Button>
				<Button href="/auth/login" variant="secondary" size="lg">Log in</Button>
			{/if}
		</div>

		<hr class="rule my-14" />

		<div class="grid gap-8 sm:grid-cols-3">
			<div class="flex flex-col gap-3">
				<span class="mk mk-sq"></span>
				<h2 class="font-display text-xl font-bold">Backend-first</h2>
				<p class="text-base leading-relaxed">Django 5 + DRF + JWT. Models, serializers, views, tests.</p>
			</div>
			<div class="flex flex-col gap-3">
				<span class="mk mk-ci"></span>
				<h2 class="font-display text-xl font-bold">Svelte 5 runes</h2>
				<p class="text-base leading-relaxed">Class-based stores, camelCase at the boundary, Tailwind 4.</p>
			</div>
			<div class="flex flex-col gap-3">
				<span class="mk mk-tr"></span>
				<h2 class="font-display text-xl font-bold">One command</h2>
				<p class="text-base leading-relaxed">remote_setup.sh with a config file — no retyping the answers.</p>
			</div>
		</div>
	</main>
</div>
