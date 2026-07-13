<script lang="ts">
	import type { WithElementRef } from 'bits-ui';
	import type { HTMLSelectAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils/cn';
	let { ref = $bindable(null), value = $bindable(), class: className, children, ...restProps }:
		WithElementRef<HTMLSelectAttributes> = $props();
</script>

<!-- Swiss native select: hard border, no rounding, mono. A drop-in for <select>. -->
<select
	bind:this={ref}
	bind:value
	class={cn('flex h-10 w-full rounded-none border-2 border-input bg-background px-3 py-2 text-base text-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)}
	{...restProps}
>
	{@render children?.()}
</select>
