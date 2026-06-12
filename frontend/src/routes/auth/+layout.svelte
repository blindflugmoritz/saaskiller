<script lang="ts">
	const { children } = $props();
</script>

<div class="min-h-screen flex items-center justify-center bg-[--color-secondary] p-4">
	<div class="w-full max-w-md bg-[--color-background] rounded-lg border border-[--color-border] shadow-sm p-8">
		{@render children()}
	</div>
</div>
