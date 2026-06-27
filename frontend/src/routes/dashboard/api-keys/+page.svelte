<script lang="ts">
	import { onMount } from 'svelte';
	import { apiKeysStore } from '$lib/stores/apikeys.svelte';

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

<div class="min-h-screen flex flex-col">
	<header class="border-b border-[--color-border] px-6 py-4 flex items-center gap-4">
		<a href="/dashboard" class="text-sm text-[--color-muted-foreground] hover:underline">
			← Dashboard
		</a>
		<h1 class="font-semibold text-lg">API Keys</h1>
	</header>

	<main class="flex-1 p-8">
		<div class="max-w-2xl mx-auto space-y-8">

			<!-- New key revealed -->
			{#if apiKeysStore.newKeyRaw}
				<div class="rounded-md border border-amber-300 bg-amber-50 p-4 space-y-3">
					<p class="text-sm font-medium text-amber-800">
						Save this key — it won't be shown again.
					</p>
					<div class="flex items-center gap-2">
						<code class="flex-1 break-all rounded bg-white border border-amber-200 px-3 py-2 text-sm font-mono text-amber-900">
							{apiKeysStore.newKeyRaw}
						</code>
						<button
							onclick={copyRawKey}
							class="shrink-0 px-3 py-2 rounded-md border border-amber-300 text-sm font-medium text-amber-800 hover:bg-amber-100 transition-colors"
						>
							{copied ? 'Copied!' : 'Copy'}
						</button>
					</div>
				</div>
			{/if}

			<!-- Create key form -->
			<section class="space-y-3">
				<h2 class="text-lg font-medium">Create API key</h2>
				<form
					onsubmit={(e) => { e.preventDefault(); handleCreate(); }}
					class="flex gap-2"
				>
					<input
						type="text"
						bind:value={newKeyName}
						placeholder="Key name (e.g. production, ci)"
						disabled={creating}
						class="flex-1 rounded-md border border-[--color-border] bg-[--color-background] px-3 py-2 text-sm placeholder:text-[--color-muted-foreground] focus:outline-none focus:ring-2 focus:ring-[--color-ring] disabled:opacity-50"
					/>
					<button
						type="submit"
						disabled={creating || !newKeyName.trim()}
						class="px-4 py-2 rounded-md bg-[--color-primary] text-[--color-primary-foreground] text-sm font-medium hover:opacity-90 disabled:opacity-50 transition-opacity"
					>
						{creating ? 'Creating…' : 'Create'}
					</button>
				</form>
				{#if createError}
					<p class="text-sm text-[--color-destructive]">{createError}</p>
				{/if}
			</section>

			<!-- Key list -->
			<section class="space-y-3">
				<h2 class="text-lg font-medium">Active keys</h2>

				{#if apiKeysStore.loading && apiKeysStore.keys.length === 0}
					<p class="text-sm text-[--color-muted-foreground]">Loading…</p>
				{:else if apiKeysStore.error}
					<p class="text-sm text-[--color-destructive]">{apiKeysStore.error}</p>
				{:else if apiKeysStore.keys.length === 0}
					<p class="text-sm text-[--color-muted-foreground]">No API keys yet.</p>
				{:else}
					<ul class="divide-y divide-[--color-border] rounded-md border border-[--color-border]">
						{#each apiKeysStore.keys as key (key.id)}
							<li class="flex items-center gap-4 px-4 py-3">
								<div class="flex-1 min-w-0">
									<p class="text-sm font-medium truncate">{key.name}</p>
									<p class="text-xs text-[--color-muted-foreground] font-mono mt-0.5">
										{key.prefix}…
									</p>
									<p class="text-xs text-[--color-muted-foreground] mt-0.5">
										Created {formatDate(key.createdAt)}
										&middot;
										Last used {formatDate(key.lastUsedAt)}
									</p>
								</div>

								{#if confirmRevokeId === key.id}
									<div class="flex items-center gap-2 shrink-0">
										<span class="text-xs text-[--color-muted-foreground]">Revoke?</span>
										<button
											onclick={() => handleRevoke(key.id)}
											class="px-3 py-1.5 rounded-md bg-[--color-destructive] text-[--color-destructive-foreground] text-xs font-medium hover:opacity-90"
										>
											Yes, revoke
										</button>
										<button
											onclick={() => (confirmRevokeId = null)}
											class="px-3 py-1.5 rounded-md border border-[--color-border] text-xs"
										>
											Cancel
										</button>
									</div>
								{:else}
									<button
										onclick={() => (confirmRevokeId = key.id)}
										class="shrink-0 px-3 py-1.5 rounded-md border border-[--color-destructive] text-[--color-destructive] text-xs font-medium hover:bg-red-50 transition-colors"
									>
										Revoke
									</button>
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
			</section>

		</div>
	</main>
</div>
