<script lang="ts" module>
	export type SiteHeaderNavItem = {
		href: string;
		label: string;
	};
</script>

<script lang="ts">
	import { cn } from '$lib/utils/cn';
	import type { Snippet } from 'svelte';

	let {
		brand = 'SaasKiller',
		brandHref = '/',
		nav = [],
		pathname = '',
		/** small yellow chip shown at the right of the brand row (e.g. "Beta") */
		chip = undefined,
		/** rule colour under the header: yellow (default), red, or blue */
		accent = 'yellow',
		/** optional actions rendered at the right of the brand row (buttons, links) */
		actions,
		class: className
	}: {
		brand?: string;
		brandHref?: string;
		nav?: SiteHeaderNavItem[];
		pathname?: string;
		chip?: string;
		accent?: 'yellow' | 'red' | 'blue';
		actions?: Snippet;
		class?: string;
	} = $props();

	const accentBorder = $derived(
		{ yellow: 'border-yellow', red: 'border-red', blue: 'border-blue' }[accent]
	);
</script>

<!-- Swiss site header: black bar, brand + optional chip/actions, mono nav row,
     coloured rule underneath. Reusable across tools, CMS shells, landing. -->
<header class={cn('border-b-[6px] bg-primary text-primary-foreground', accentBorder, className)}>
	<div class="mx-auto flex max-w-5xl items-baseline justify-between gap-4 px-6 py-4">
		<a href={brandHref} class="font-display text-xl font-black uppercase tracking-wider md:text-2xl">
			{brand}
		</a>
		<div class="flex items-center gap-3">
			{#if chip}
				<span class="bg-yellow px-2.5 py-1 font-mono text-[11px] uppercase tracking-wider text-ink">
					{chip}
				</span>
			{/if}
			{@render actions?.()}
		</div>
	</div>

	{#if nav.length}
		<nav class="mx-auto flex max-w-5xl flex-wrap gap-x-6 gap-y-1 px-6 pb-3" aria-label="Primary">
			{#each nav as item (item.href)}
				{@const active = pathname === item.href}
				<a
					href={item.href}
					aria-current={active ? 'page' : undefined}
					class={cn(
						'border-b-[3px] pb-1 font-mono text-xs uppercase tracking-wider transition-colors',
						active
							? 'border-yellow text-yellow'
							: 'border-transparent text-primary-foreground hover:text-yellow'
					)}
				>
					{item.label}
				</a>
			{/each}
		</nav>
	{/if}
</header>
