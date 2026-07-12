<script lang="ts">
	import type { WithElementRef } from 'bits-ui';
	import type { HTMLAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils/cn';
	let { ref = $bindable(null), class: className, children, ...restProps }:
		WithElementRef<HTMLAttributes<HTMLDivElement>> = $props();
</script>

<!-- Swiss card: hard 2px ink border, no rounding, no shadow. -->
<div bind:this={ref} class={cn('rounded-none border-2 border-border bg-card text-card-foreground', className)} {...restProps}>
	{@render children?.()}
</div>
