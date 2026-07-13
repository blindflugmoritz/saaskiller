<!-- === FEATURE: stripe === -->
<script lang="ts">
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';
	// No logic needed — static cancellation page
</script>

<div class="flex flex-col items-center">
	<div class="w-full max-w-md">
		<p class="eyebrow">Billing</p>
		<h1 class="title font-display font-black text-4xl mb-6">Checkout cancelled</h1>
		<div class="rule mb-8"></div>

		<Card.Root class="border-2 border-border">
			<Card.Header>
				<div class="flex items-center gap-4">
					<span class="mk mk-sq shrink-0" aria-hidden="true"></span>
					<Card.Title class="font-display font-bold text-xl">No charge was made</Card.Title>
				</div>
				<Card.Description class="font-mono text-sm text-muted-foreground pt-2">
					You can try again whenever you're ready.
				</Card.Description>
			</Card.Header>
			<Card.Footer>
				<Button href="/dashboard/billing" variant="default" size="lg">Back to billing</Button>
			</Card.Footer>
		</Card.Root>
	</div>
</div>
