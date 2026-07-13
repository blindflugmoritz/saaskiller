<!-- === FEATURE: stripe === -->
<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	// No logic needed — static confirmation page
</script>

<div class="mx-auto max-w-md">
	<Card.Root class="border-2 border-border">
		<Card.Header>
			<div class="mb-4 flex items-center gap-3">
				<span class="mk mk-sq"></span>
				<span class="mk mk-ci"></span>
				<span class="mk mk-tr"></span>
			</div>
			<p class="eyebrow">Payment confirmed</p>
			<Card.Title class="title font-display font-black text-3xl">Subscription activated</Card.Title>
			<Card.Description class="font-mono text-muted-foreground">
				Thank you. Your plan is now active.
			</Card.Description>
		</Card.Header>
		<Card.Content>
			<div class="rule-thin mb-6"></div>
			<div class="flex items-center gap-4 border-2 border-border bg-green p-4">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-8 w-8 shrink-0 text-background"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="3"
				>
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
				</svg>
				<p class="font-mono uppercase tracking-wider text-sm text-background">
					Everything is set up and ready to go.
				</p>
			</div>
		</Card.Content>
		<Card.Footer>
			<Button href="/dashboard" size="lg" class="w-full">Go to dashboard</Button>
		</Card.Footer>
	</Card.Root>
</div>
