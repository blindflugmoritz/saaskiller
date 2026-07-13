<script lang="ts">
	import type { WithElementRef } from 'bits-ui';
	import type { HTMLTextareaAttributes } from 'svelte/elements';
	import { cn } from '$lib/utils/cn';
	let { ref = $bindable(null), value = $bindable(), class: className, ...restProps }:
		WithElementRef<HTMLTextareaAttributes> = $props();
</script>

<!-- Swiss textarea: hard 2px border, no rounding, blue focus ring. -->
<textarea
	bind:this={ref}
	bind:value
	class={cn('flex min-h-[80px] w-full rounded-none border-2 border-input bg-background px-3 py-2 text-base text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-[3px] focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', className)}
	{...restProps}
></textarea>
