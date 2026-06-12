<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { workspaceStore } from '$lib/stores/workspaces.svelte';
	import type { WorkspaceKind } from '$lib/api/workspaces';

	const KIND_OPTIONS: { value: WorkspaceKind; label: string }[] = [
		{ value: 'personal', label: 'Personal' },
		{ value: 'family', label: 'Family' },
		{ value: 'school', label: 'School' },
		{ value: 'business', label: 'Business' },
	];

	let newName = $state('');
	let newKind = $state<WorkspaceKind>('personal');
	let creating = $state(false);
	let createError = $state<string | null>(null);
	let showForm = $state(false);

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) {
			goto('/auth/login');
			return;
		}
		await workspaceStore.fetchWorkspaces();
	});

	async function handleCreate() {
		if (!newName.trim()) return;
		creating = true;
		createError = null;
		try {
			const ws = await workspaceStore.createWorkspace(newName.trim(), newKind);
			newName = '';
			newKind = 'personal';
			showForm = false;
			goto(`/dashboard/workspaces/${ws.id}`);
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			createError = e.detail || e.message || 'Failed to create workspace.';
		} finally {
			creating = false;
		}
	}
</script>

{#if authStore.isAuthenticated}
	<div class="min-h-screen flex flex-col">
		<header class="border-b border-[--color-border] px-6 py-4 flex items-center gap-4">
			<a href="/dashboard" class="text-sm text-[--color-muted-foreground] hover:underline">← Dashboard</a>
			<h1 class="font-semibold text-lg">Workspaces</h1>
		</header>

		<main class="flex-1 p-8">
			<div class="max-w-2xl mx-auto space-y-6">

				{#if workspaceStore.error}
					<p class="text-sm text-[--color-destructive]">{workspaceStore.error}</p>
				{/if}

				<!-- Workspace list -->
				{#if workspaceStore.loading}
					<p class="text-sm text-[--color-muted-foreground]">Loading…</p>
				{:else if workspaceStore.workspaces.length === 0}
					<p class="text-sm text-[--color-muted-foreground]">You don't belong to any workspaces yet.</p>
				{:else}
					<ul class="divide-y divide-[--color-border] border border-[--color-border] rounded-md overflow-hidden">
						{#each workspaceStore.workspaces as ws (ws.id)}
							<li>
								<a
									href="/dashboard/workspaces/{ws.id}"
									class="flex items-center justify-between px-4 py-3 hover:bg-[--color-secondary] transition-colors"
								>
									<div>
										<span class="font-medium">{ws.name}</span>
										<span class="ml-2 text-xs text-[--color-muted-foreground] capitalize">{ws.kind}</span>
									</div>
									<span class="text-xs text-[--color-muted-foreground]">→</span>
								</a>
							</li>
						{/each}
					</ul>
				{/if}

				<!-- Create workspace -->
				{#if showForm}
					<form
						onsubmit={(e) => { e.preventDefault(); handleCreate(); }}
						class="border border-[--color-border] rounded-md p-4 space-y-4"
					>
						<h2 class="font-medium">New workspace</h2>

						<div class="space-y-1">
							<label for="ws-name" class="text-sm font-medium">Name</label>
							<input
								id="ws-name"
								type="text"
								bind:value={newName}
								placeholder="My Workspace"
								required
								class="w-full border border-[--color-border] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[--color-ring]"
							/>
						</div>

						<div class="space-y-1">
							<label for="ws-kind" class="text-sm font-medium">Type</label>
							<select
								id="ws-kind"
								bind:value={newKind}
								class="w-full border border-[--color-border] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[--color-ring] bg-[--color-background]"
							>
								{#each KIND_OPTIONS as opt (opt.value)}
									<option value={opt.value}>{opt.label}</option>
								{/each}
							</select>
						</div>

						{#if createError}
							<p class="text-sm text-[--color-destructive]">{createError}</p>
						{/if}

						<div class="flex gap-2">
							<button
								type="submit"
								disabled={creating}
								class="bg-[--color-primary] text-[--color-primary-foreground] px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
							>
								{creating ? 'Creating…' : 'Create workspace'}
							</button>
							<button
								type="button"
								onclick={() => { showForm = false; createError = null; }}
								class="border border-[--color-border] px-4 py-2 rounded-md text-sm"
							>
								Cancel
							</button>
						</div>
					</form>
				{:else}
					<button
						onclick={() => (showForm = true)}
						class="border border-[--color-border] px-4 py-2 rounded-md text-sm font-medium hover:bg-[--color-secondary] transition-colors"
					>
						+ New workspace
					</button>
				{/if}

			</div>
		</main>
	</div>
{/if}
