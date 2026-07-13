<script lang="ts">
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { workspaceStore } from '$lib/stores/workspaces.svelte';
	import type { WorkspaceKind } from '$lib/api/workspaces';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { NativeSelect } from '$lib/components/ui/select';
	import { Badge } from '$lib/components/ui/badge';
	import * as Card from '$lib/components/ui/card';

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
	<div class="space-y-10">
		<div>
			<p class="eyebrow">Workspaces</p>
			<h1 class="title font-display font-black text-4xl md:text-5xl mt-2">Your workspaces</h1>
		</div>

		<div class="rule"></div>

		{#if workspaceStore.error}
			<p class="font-mono text-sm text-destructive">{workspaceStore.error}</p>
		{/if}

		<!-- Workspace list -->
		{#if workspaceStore.loading}
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">Loading…</p>
		{:else if workspaceStore.workspaces.length === 0}
			<div class="border-2 border-border p-8 flex items-start gap-4">
				<span class="mk mk-sq shrink-0 mt-1"></span>
				<p class="text-muted-foreground">You don't belong to any workspaces yet.</p>
			</div>
		{:else}
			<ul class="border-2 border-border">
				{#each workspaceStore.workspaces as ws, i (ws.id)}
					<li class={i > 0 ? 'border-t-2 border-border' : ''}>
						<a
							href="/dashboard/workspaces/{ws.id}"
							class="flex items-center justify-between px-5 py-4 transition-colors hover:bg-primary hover:text-primary-foreground group"
						>
							<div class="flex items-center gap-4">
								<span class="font-display font-bold text-lg">{ws.name}</span>
								<Badge variant="outline" class="uppercase tracking-wider">{ws.kind}</Badge>
							</div>
							<span class="font-mono text-lg" aria-hidden="true">→</span>
						</a>
					</li>
				{/each}
			</ul>
		{/if}

		<div class="rule-thin"></div>

		<!-- Create workspace -->
		{#if showForm}
			<Card.Root class="border-2 border-border rounded-none">
				<Card.Header>
					<p class="eyebrow">Create</p>
					<Card.Title class="font-display font-bold text-2xl">New workspace</Card.Title>
				</Card.Header>
				<Card.Content>
					<form
						onsubmit={(e) => { e.preventDefault(); handleCreate(); }}
						class="space-y-6"
					>
						<div class="space-y-2">
							<Label for="ws-name" class="font-mono uppercase tracking-wider text-xs">Name</Label>
							<Input
								id="ws-name"
								type="text"
								bind:value={newName}
								placeholder="My Workspace"
								required
							/>
						</div>

						<div class="space-y-2">
							<Label for="ws-kind" class="font-mono uppercase tracking-wider text-xs">Type</Label>
							<NativeSelect id="ws-kind" bind:value={newKind}>
								{#each KIND_OPTIONS as opt (opt.value)}
									<option value={opt.value}>{opt.label}</option>
								{/each}
							</NativeSelect>
						</div>

						{#if createError}
							<p class="font-mono text-sm text-destructive">{createError}</p>
						{/if}

						<div class="flex gap-3 pt-2">
							<Button type="submit" disabled={creating}>
								{creating ? 'Creating…' : 'Create workspace'}
							</Button>
							<Button
								type="button"
								variant="outline"
								onclick={() => { showForm = false; createError = null; }}
							>
								Cancel
							</Button>
						</div>
					</form>
				</Card.Content>
			</Card.Root>
		{:else}
			<Button variant="outline" onclick={() => (showForm = true)}>+ New workspace</Button>
		{/if}
	</div>
{/if}
