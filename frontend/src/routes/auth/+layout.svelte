<script lang="ts">
	const { children } = $props();
</script>

<!-- Swiss auth frame: paper ground, a hard-bordered card, top yellow rule. No
     rounding, no shadow — the border does the work. -->
<div class="flex min-h-screen items-center justify-center bg-secondary p-4">
	<div class="w-full max-w-md border-2 border-border bg-card">
		<div class="h-1.5 bg-yellow"></div>
		<div class="p-8">
			{@render children()}
		</div>
	</div>
</div>
