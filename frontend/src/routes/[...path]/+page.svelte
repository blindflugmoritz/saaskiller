<script lang="ts">
	// === FEATURE: cms ===
	import type { CmsPage } from './+page.server';

	const { data } = $props<{ data: { page: CmsPage } }>();
	const { page } = data;
	// === END FEATURE: cms ===
</script>

<!-- === FEATURE: cms === -->
<svelte:head>
	<title>{page.title}</title>
	{#if page.metaDescription}
		<meta name="description" content={page.metaDescription} />
	{/if}
</svelte:head>

<article class="max-w-3xl mx-auto px-6 py-12">
	<h1 class="text-3xl font-bold mb-8">{page.title}</h1>

	{#each page.regions.main as block}
		{#if block.type === 'richtext' && block.html}
			<div class="prose prose-neutral max-w-none mb-6">
				{@html block.html}
			</div>
		{:else if block.type === 'image' && block.url}
			<figure class="mb-6">
				<img
					src={block.url}
					alt={block.alt ?? block.caption ?? ''}
					class="w-full rounded-lg"
				/>
				{#if block.caption}
					<figcaption class="text-sm text-[--color-muted-foreground] mt-2 text-center">
						{block.caption}
					</figcaption>
				{/if}
			</figure>
		{:else if block.type === 'html' && block.html}
			<div class="mb-6">
				{@html block.html}
			</div>
		{/if}
	{/each}
</article>
<!-- === END FEATURE: cms === -->
