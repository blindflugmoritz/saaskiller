<script lang="ts" module>
	export type SidebarNavItem = {
		href: string;
		label: string;
		/** one of the three Swiss markers */
		marker?: 'sq' | 'ci' | 'tr';
	};
</script>

<script lang="ts">
	import { cn } from '$lib/utils/cn';
	import type { Snippet } from 'svelte';

	let {
		brand = 'SaasKiller',
		brandHref = '/dashboard',
		items = [],
		pathname = '',
		footer,
		class: className
	}: {
		brand?: string;
		brandHref?: string;
		items?: SidebarNavItem[];
		pathname?: string;
		footer?: Snippet;
		class?: string;
	} = $props();

	// Mobile: the sidebar is a slide-in panel toggled by a hamburger.
	let open = $state(false);
</script>

<!-- Mobile top bar with a hamburger — only shown below md. -->
<div class="flex items-center justify-between border-b-[6px] border-yellow bg-primary px-5 py-3 text-primary-foreground md:hidden">
	<a href={brandHref} class="font-display text-lg font-black uppercase tracking-wider">{brand}</a>
	<button
		type="button"
		aria-label="Toggle navigation"
		aria-expanded={open}
		onclick={() => (open = !open)}
		class="font-mono text-xs uppercase tracking-wider hover:text-yellow"
	>
		{open ? 'Close' : 'Menu'}
	</button>
</div>

<!-- Mobile scrim -->
{#if open}
	<button
		type="button"
		aria-label="Close navigation"
		style="background: color-mix(in srgb, var(--ink) 40%, transparent);"
		class="fixed inset-0 z-30 md:hidden"
		onclick={() => (open = false)}
	></button>
{/if}

<aside
	class={cn(
		'flex w-64 shrink-0 flex-col border-r-2 border-border bg-primary text-primary-foreground',
		// desktop: static column; mobile: fixed slide-in
		'fixed inset-y-0 left-0 z-40 -translate-x-full transition-transform md:static md:translate-x-0',
		open && 'translate-x-0',
		className
	)}
>
	<!-- brand + yellow rule -->
	<div class="border-b-[6px] border-yellow px-5 py-5">
		<a href={brandHref} class="font-display text-xl font-black uppercase tracking-wider">{brand}</a>
	</div>

	<!-- nav -->
	<nav class="flex flex-1 flex-col gap-0.5 p-3" aria-label="Sidebar">
		{#each items as item (item.href)}
			{@const active = pathname === item.href}
			<a
				href={item.href}
				aria-current={active ? 'page' : undefined}
				onclick={() => (open = false)}
				class={cn(
					'flex items-center gap-3 border-l-[3px] px-3 py-2.5 font-mono text-xs uppercase tracking-wider transition-colors',
					active
						? 'border-yellow bg-ink text-yellow'
						: 'border-transparent text-primary-foreground hover:border-yellow hover:text-yellow'
				)}
			>
				{#if item.marker === 'sq'}
					<span class="mk mk-sq size-3 shrink-0" aria-hidden="true"></span>
				{:else if item.marker === 'ci'}
					<span class="mk mk-ci size-3 shrink-0" aria-hidden="true"></span>
				{:else if item.marker === 'tr'}
					<span class="mk mk-tr shrink-0" aria-hidden="true"></span>
				{/if}
				{item.label}
			</a>
		{/each}
	</nav>

	<!-- footer (user / logout) -->
	{#if footer}
		<div class="border-t-2 border-border p-3">
			{@render footer()}
		</div>
	{/if}
</aside>
