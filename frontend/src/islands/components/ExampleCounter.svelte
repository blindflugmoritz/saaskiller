<script lang="ts">
	// === FEATURE: cms ===
	// Example island: a simple counter component.
	// Demonstrates: Svelte 5 runes, props from data-props JSON, optional API access.
	// Replace with real islands for your project.

	interface Props {
		start?: number;
		label?: string;
	}

	let { start = 0, label = 'Count' }: Props = $props();
	// count is intentionally seeded from start once. It is independent local state —
	// $derived would re-track start, which is wrong for a counter.
	const initialCount = start;
	let count = $state(initialCount);
</script>

<!-- === FEATURE: cms === -->
<div class="inline-flex items-center gap-3 rounded-lg border border-[--color-border] bg-[--color-background] px-4 py-2">
	<span class="text-sm text-[--color-muted-foreground]">{label}:</span>
	<button
		onclick={() => count--}
		class="rounded px-2 py-0.5 text-sm font-medium hover:bg-[--color-secondary] transition-colors"
		aria-label="Decrease"
	>−</button>
	<span class="w-8 text-center font-mono font-semibold tabular-nums">{count}</span>
	<button
		onclick={() => count++}
		class="rounded px-2 py-0.5 text-sm font-medium hover:bg-[--color-secondary] transition-colors"
		aria-label="Increase"
	>+</button>
</div>
<!-- === END FEATURE: cms === -->
