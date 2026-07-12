<script lang="ts" module>
	import type { WithElementRef } from 'bits-ui';
	import type { HTMLAnchorAttributes } from 'svelte/elements';
	import { type VariantProps, tv } from 'tailwind-variants';

	// Swiss badge: mono uppercase, hard 2px border, no rounding.
	export const badgeVariants = tv({
		base: 'inline-flex items-center gap-1.5 rounded-none border-2 px-2 py-0.5 font-mono text-[10.5px] font-medium uppercase tracking-wider',
		variants: {
			variant: {
				default: 'border-primary bg-primary text-primary-foreground',
				secondary: 'border-input bg-secondary text-secondary-foreground',
				destructive: 'border-destructive bg-destructive text-destructive-foreground',
				outline: 'border-input bg-background text-foreground'
			}
		},
		defaultVariants: { variant: 'default' }
	});

	export type BadgeVariant = VariantProps<typeof badgeVariants>['variant'];
</script>

<script lang="ts">
	import { cn } from '$lib/utils/cn';

	let {
		ref = $bindable(null),
		class: className,
		variant = 'default',
		href = undefined,
		children,
		...restProps
	}: WithElementRef<HTMLAnchorAttributes> & { variant?: BadgeVariant } = $props();
</script>

<svelte:element
	this={href ? 'a' : 'span'}
	bind:this={ref}
	{href}
	class={cn(badgeVariants({ variant }), className)}
	{...restProps}
>
	{@render children?.()}
</svelte:element>
