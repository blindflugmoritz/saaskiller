<script lang="ts">
	import { onMount } from 'svelte';
	import { apiKeysStore } from '$lib/stores/apikeys.svelte';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { Badge } from '$lib/components/ui/badge';

	let newKeyName = $state('');
	let creating = $state(false);
	let createError = $state<string | null>(null);
	let confirmRevokeId = $state<string | null>(null);
	let copied = $state(false);

	onMount(async () => {
		await apiKeysStore.fetchKeys();
	});

	async function handleCreate() {
		const name = newKeyName.trim();
		if (!name) return;
		creating = true;
		createError = null;
		try {
			await apiKeysStore.createKey(name);
			newKeyName = '';
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			createError = e.detail || e.message || 'Failed to create key.';
		} finally {
			creating = false;
		}
	}

	async function handleRevoke(id: string) {
		confirmRevokeId = null;
		await apiKeysStore.revokeKey(id);
	}

	async function copyRawKey() {
		if (!apiKeysStore.newKeyRaw) return;
		await navigator.clipboard.writeText(apiKeysStore.newKeyRaw);
		copied = true;
		setTimeout(() => (copied = false), 2000);
	}

	function formatDate(iso: string | null) {
		if (!iso) return 'Never';
		return new Date(iso).toLocaleDateString(undefined, {
			year: 'numeric',
			month: 'short',
			day: 'numeric',
		});
	}
</script>

<div class="space-y-10">
	<div>
		<p class="eyebrow">Developer</p>
		<h1 class="title font-display font-black text-4xl md:text-5xl mt-2">API Keys</h1>
	</div>

	<div class="rule"></div>

	<!-- New key revealed -->
	{#if apiKeysStore.newKeyRaw}
		<div class="border-2 border-border bg-yellow p-5 space-y-3">
			<p class="font-mono uppercase tracking-wider text-sm font-bold text-black">
				Save this key — it won't be shown again.
			</p>
			<div class="flex items-center gap-2">
				<code class="flex-1 break-all border-2 border-border bg-background px-3 py-2 text-sm font-mono text-foreground">
					{apiKeysStore.newKeyRaw}
				</code>
				<Button variant="outline" size="sm" onclick={copyRawKey} class="shrink-0">
					{copied ? 'Copied!' : 'Copy'}
				</Button>
			</div>
		</div>
	{/if}

	<!-- Create key form -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk mk-sq"></span>
			<h2 class="font-display font-bold text-2xl">Create API key</h2>
		</div>
		<form
			onsubmit={(e) => { e.preventDefault(); handleCreate(); }}
			class="space-y-3"
		>
			<div class="space-y-2">
				<Label for="key-name" class="font-mono uppercase tracking-wider text-xs">Key name</Label>
				<div class="flex gap-2">
					<Input
						id="key-name"
						type="text"
						bind:value={newKeyName}
						placeholder="Key name (e.g. production, ci)"
						disabled={creating}
						class="flex-1"
					/>
					<Button type="submit" disabled={creating || !newKeyName.trim()}>
						{creating ? 'Creating…' : 'Create'}
					</Button>
				</div>
			</div>
		</form>
		{#if createError}
			<p class="font-mono text-sm text-destructive">{createError}</p>
		{/if}
	</section>

	<div class="rule-thin"></div>

	<!-- Key list -->
	<section class="space-y-4">
		<div class="flex items-center gap-3">
			<span class="mk mk-ci"></span>
			<h2 class="font-display font-bold text-2xl">Active keys</h2>
		</div>

		{#if apiKeysStore.loading && apiKeysStore.keys.length === 0}
			<p class="font-mono text-sm text-muted-foreground uppercase tracking-wider">Loading…</p>
		{:else if apiKeysStore.error}
			<p class="font-mono text-sm text-destructive">{apiKeysStore.error}</p>
		{:else if apiKeysStore.keys.length === 0}
			<p class="font-mono text-sm text-muted-foreground uppercase tracking-wider">No API keys yet.</p>
		{:else}
			<ul class="border-2 border-border divide-y-2 divide-border">
				{#each apiKeysStore.keys as key (key.id)}
					<li class="flex items-center gap-4 px-4 py-4">
						<div class="flex-1 min-w-0">
							<p class="font-display font-bold text-base truncate">{key.name}</p>
							<p class="text-xs text-muted-foreground font-mono mt-1">
								{key.prefix}…
							</p>
							<p class="text-xs text-muted-foreground font-mono uppercase tracking-wider mt-1">
								Created {formatDate(key.createdAt)}
								&middot;
								Last used {formatDate(key.lastUsedAt)}
							</p>
						</div>

						{#if confirmRevokeId === key.id}
							<div class="flex items-center gap-2 shrink-0">
								<span class="font-mono text-xs uppercase tracking-wider text-muted-foreground">Revoke?</span>
								<Button variant="destructive" size="sm" onclick={() => handleRevoke(key.id)}>
									Yes, revoke
								</Button>
								<Button variant="outline" size="sm" onclick={() => (confirmRevokeId = null)}>
									Cancel
								</Button>
							</div>
						{:else}
							<Button
								variant="outline"
								size="sm"
								onclick={() => (confirmRevokeId = key.id)}
								class="shrink-0 border-destructive text-destructive hover:bg-destructive hover:text-destructive-foreground"
							>
								Revoke
							</Button>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	</section>
</div>
