<script lang="ts">
	import type { WithElementRef } from 'bits-ui';
	import type { HTMLAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils/cn';
	let { ref = $bindable(null), class: className, children, ...restProps }:
		WithElementRef<HTMLAttributes<HTMLHeadingElement>> = $props();
</script>
<h3 bind:this={ref} class={cn('font-display text-lg font-bold leading-tight', className)} {...restProps}>{@render children?.()}</h3>
