<!-- === FEATURE: stripe === -->
<script lang="ts">
	// No logic needed — static cancellation page
</script>

<div class="min-h-screen flex items-center justify-center p-8">
	<div class="max-w-md w-full text-center space-y-6">
		<div class="flex justify-center">
			<div class="rounded-full bg-gray-100 p-4">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-8 w-8 text-gray-500"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="2"
				>
					<path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
				</svg>
			</div>
		</div>
		<div class="space-y-2">
			<h1 class="text-2xl font-semibold">Checkout cancelled</h1>
			<p class="text-[--color-muted-foreground]">No charge was made. You can try again whenever you're ready.</p>
		</div>
		<a
			href="/dashboard/billing"
			class="inline-flex items-center justify-center rounded-md border border-[--color-border] px-5 py-2.5 text-sm font-medium hover:bg-[--color-accent]"
		>
			Back to billing
		</a>
	</div>
</div>
