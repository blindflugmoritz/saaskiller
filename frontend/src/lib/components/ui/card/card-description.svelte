<script lang="ts">
	import type { WithElementRef } from 'bits-ui';
	import type { HTMLAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils/cn';
	let { ref = $bindable(null), class: className, children, ...restProps }:
		WithElementRef<HTMLAttributes<HTMLParagraphElement>> = $props();
</script>
<p bind:this={ref} class={cn('font-mono text-xs uppercase tracking-wide text-muted-foreground', className)} {...restProps}>{@render children?.()}</p>
