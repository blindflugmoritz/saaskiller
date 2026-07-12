<script lang="ts">
	import { Label as LabelPrimitive } from 'bits-ui';
	import { cn } from '$lib/utils/cn';

	let {
		ref = $bindable(null),
		class: className,
		...restProps
	}: LabelPrimitive.RootProps = $props();
</script>

<!-- Swiss label: mono uppercase, letter-spaced. -->
<LabelPrimitive.Root
	bind:ref
	class={cn(
		'font-mono text-xs font-medium uppercase tracking-wider leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70',
		className
	)}
	{...restProps}
/>
