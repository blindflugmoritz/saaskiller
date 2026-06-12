<!-- === FEATURE: stripe === -->
<script lang="ts">
	// No logic needed — static confirmation page
</script>

<div class="min-h-screen flex items-center justify-center p-8">
	<div class="max-w-md w-full text-center space-y-6">
		<div class="flex justify-center">
			<div class="rounded-full bg-green-100 p-4">
				<svg
					xmlns="http://www.w3.org/2000/svg"
					class="h-8 w-8 text-green-600"
					fill="none"
					viewBox="0 0 24 24"
					stroke="currentColor"
					stroke-width="2"
				>
					<path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
				</svg>
			</div>
		</div>
		<div class="space-y-2">
			<h1 class="text-2xl font-semibold">Subscription activated!</h1>
			<p class="text-[--color-muted-foreground]">Thank you. Your plan is now active.</p>
		</div>
		<a
			href="/dashboard"
			class="inline-flex items-center justify-center rounded-md bg-[--color-primary] px-5 py-2.5 text-sm font-medium text-[--color-primary-foreground] hover:opacity-90"
		>
			Go to dashboard
		</a>
	</div>
</div>
