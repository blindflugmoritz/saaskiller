<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { workspaceStore } from '$lib/stores/workspaces.svelte';
	import type { MemberRole } from '$lib/api/workspaces';

	const ROLE_OPTIONS: { value: MemberRole; label: string }[] = [
		{ value: 'owner', label: 'Owner' },
		{ value: 'admin', label: 'Admin' },
		{ value: 'member', label: 'Member' },
		{ value: 'viewer', label: 'Viewer' },
	];

	let inviteEmail = $state('');
	let inviteRole = $state<MemberRole>('member');
	let inviting = $state(false);
	let inviteError = $state<string | null>(null);
	let inviteSuccess = $state(false);

	let removingId = $state<string | null>(null);
	let confirmLeaveId = $state<string | null>(null);

	// The current user's membership in this workspace
	let myMembership = $derived(
		workspaceStore.members.find((m) => m.user === authStore.currentUser?.email) ?? null
	);
	let isAdminOrOwner = $derived(
		myMembership?.role === 'owner' || myMembership?.role === 'admin'
	);

	onMount(async () => {
		await authStore.fetchCurrentUser();
		if (!authStore.isAuthenticated) {
			goto('/auth/login');
			return;
		}
		const id = page.params.id!;
		await workspaceStore.selectWorkspace(id);
	});

	async function handleInvite() {
		if (!inviteEmail.trim()) return;
		inviting = true;
		inviteError = null;
		inviteSuccess = false;
		try {
			await workspaceStore.inviteMember(inviteEmail.trim(), inviteRole);
			inviteEmail = '';
			inviteRole = 'member';
			inviteSuccess = true;
			setTimeout(() => (inviteSuccess = false), 3000);
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string };
			inviteError = e.detail || e.message || 'Failed to send invitation.';
		} finally {
			inviting = false;
		}
	}

	async function handleRemove(membershipId: string) {
		removingId = membershipId;
		try {
			await workspaceStore.removeMember(membershipId);
			// If we removed ourselves, redirect
			if (membershipId === myMembership?.id) {
				goto('/dashboard/workspaces');
			}
		} finally {
			removingId = null;
			confirmLeaveId = null;
		}
	}

	async function handleRoleChange(membershipId: string, role: MemberRole) {
		await workspaceStore.updateMemberRole(membershipId, role);
	}
</script>

{#if authStore.isAuthenticated}
	<div class="min-h-screen flex flex-col">
		<header class="border-b border-[--color-border] px-6 py-4 flex items-center gap-4">
			<a href="/dashboard/workspaces" class="text-sm text-[--color-muted-foreground] hover:underline">← Workspaces</a>
			{#if workspaceStore.currentWorkspace}
				<h1 class="font-semibold text-lg">{workspaceStore.currentWorkspace.name}</h1>
				<span class="text-sm text-[--color-muted-foreground] capitalize">{workspaceStore.currentWorkspace.kind}</span>
			{:else}
				<h1 class="font-semibold text-lg">Workspace</h1>
			{/if}
		</header>

		<main class="flex-1 p-8">
			<div class="max-w-2xl mx-auto space-y-8">

				{#if workspaceStore.loading}
					<p class="text-sm text-[--color-muted-foreground]">Loading…</p>
				{:else if workspaceStore.error}
					<p class="text-sm text-[--color-destructive]">{workspaceStore.error}</p>
				{:else if workspaceStore.currentWorkspace}

					<!-- Workspace info -->
					<section class="space-y-1">
						<h2 class="text-lg font-medium">Details</h2>
						<p class="text-sm text-[--color-muted-foreground]">Owner: {workspaceStore.currentWorkspace.owner}</p>
						<p class="text-sm text-[--color-muted-foreground] capitalize">Type: {workspaceStore.currentWorkspace.kind}</p>
					</section>

					<!-- Members list -->
					<section class="space-y-3">
						<h2 class="text-lg font-medium">Members</h2>
						{#if workspaceStore.members.length === 0}
							<p class="text-sm text-[--color-muted-foreground]">No members yet.</p>
						{:else}
							<ul class="divide-y divide-[--color-border] border border-[--color-border] rounded-md overflow-hidden">
								{#each workspaceStore.members as member (member.id)}
									<li class="flex items-center justify-between px-4 py-3 gap-3">
										<span class="text-sm flex-1 min-w-0 truncate">{member.user}</span>

										{#if isAdminOrOwner && member.role !== 'owner'}
											<select
												value={member.role}
												onchange={(e) => handleRoleChange(member.id, (e.currentTarget as HTMLSelectElement).value as MemberRole)}
												class="border border-[--color-border] rounded px-2 py-1 text-xs bg-[--color-background]"
											>
												{#each ROLE_OPTIONS.filter((o) => o.value !== 'owner') as opt (opt.value)}
													<option value={opt.value}>{opt.label}</option>
												{/each}
											</select>
										{:else}
											<span class="text-xs text-[--color-muted-foreground] capitalize">{member.role}</span>
										{/if}

										{#if isAdminOrOwner && member.id !== myMembership?.id && member.role !== 'owner'}
											<!-- Remove other member -->
											<button
												onclick={() => handleRemove(member.id)}
												disabled={removingId === member.id}
												class="text-xs text-[--color-destructive] hover:underline disabled:opacity-50"
											>
												{removingId === member.id ? 'Removing…' : 'Remove'}
											</button>
										{:else if member.id === myMembership?.id && myMembership?.role !== 'owner'}
											<!-- Leave workspace -->
											{#if confirmLeaveId === member.id}
												<span class="text-xs flex items-center gap-1">
													<span>Sure?</span>
													<button
														onclick={() => handleRemove(member.id)}
														disabled={removingId === member.id}
														class="text-[--color-destructive] hover:underline disabled:opacity-50"
													>
														{removingId === member.id ? 'Leaving…' : 'Yes, leave'}
													</button>
													<button
														onclick={() => (confirmLeaveId = null)}
														class="text-[--color-muted-foreground] hover:underline"
													>
														Cancel
													</button>
												</span>
											{:else}
												<button
													onclick={() => (confirmLeaveId = member.id)}
													class="text-xs text-[--color-muted-foreground] hover:text-[--color-foreground] hover:underline"
												>
													Leave
												</button>
											{/if}
										{/if}
									</li>
								{/each}
							</ul>
						{/if}
					</section>

					<!-- Invite form (admin/owner only) -->
					{#if isAdminOrOwner}
						<section class="space-y-3">
							<h2 class="text-lg font-medium">Invite member</h2>
							<form
								onsubmit={(e) => { e.preventDefault(); handleInvite(); }}
								class="flex flex-col sm:flex-row gap-2"
							>
								<input
									type="email"
									bind:value={inviteEmail}
									placeholder="email@example.com"
									required
									class="flex-1 border border-[--color-border] rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[--color-ring]"
								/>
								<select
									bind:value={inviteRole}
									class="border border-[--color-border] rounded-md px-3 py-2 text-sm bg-[--color-background] focus:outline-none focus:ring-2 focus:ring-[--color-ring]"
								>
									{#each ROLE_OPTIONS.filter((o) => o.value !== 'owner') as opt (opt.value)}
										<option value={opt.value}>{opt.label}</option>
									{/each}
								</select>
								<button
									type="submit"
									disabled={inviting}
									class="bg-[--color-primary] text-[--color-primary-foreground] px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50 whitespace-nowrap"
								>
									{inviting ? 'Sending…' : 'Send invite'}
								</button>
							</form>
							{#if inviteError}
								<p class="text-sm text-[--color-destructive]">{inviteError}</p>
							{/if}
							{#if inviteSuccess}
								<p class="text-sm text-green-600">Invitation sent!</p>
							{/if}
						</section>
					{/if}

				{/if}
			</div>
		</main>
	</div>
{/if}
