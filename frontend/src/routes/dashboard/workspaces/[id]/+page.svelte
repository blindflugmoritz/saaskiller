<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { workspaceStore } from '$lib/stores/workspaces.svelte';
	import type { MemberRole } from '$lib/api/workspaces';
	import { Button } from '$lib/components/ui/button';
	import { Input } from '$lib/components/ui/input';
	import { Label } from '$lib/components/ui/label';
	import { NativeSelect } from '$lib/components/ui/select';
	import { Badge } from '$lib/components/ui/badge';
	import * as Card from '$lib/components/ui/card';

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
	<div class="space-y-10">
		<!-- Page heading -->
		<div class="space-y-4">
			<a
				href="/dashboard/workspaces"
				class="font-mono text-xs uppercase tracking-wider text-muted-foreground hover:text-foreground"
			>
				← Workspaces
			</a>
			<div class="flex items-baseline gap-4 flex-wrap">
				<h1 class="title font-display font-black">
					{workspaceStore.currentWorkspace?.name ?? 'Workspace'}
				</h1>
				{#if workspaceStore.currentWorkspace}
					<Badge variant="outline" class="font-mono uppercase tracking-wider"
						>{workspaceStore.currentWorkspace.kind}</Badge
					>
				{/if}
			</div>
			<div class="rule"></div>
		</div>

		{#if workspaceStore.loading}
			<p class="font-mono text-sm uppercase tracking-wider text-muted-foreground">Loading…</p>
		{:else if workspaceStore.error}
			<p class="text-sm text-destructive">{workspaceStore.error}</p>
		{:else if workspaceStore.currentWorkspace}
			<!-- Workspace info -->
			<section class="space-y-3">
				<div class="eyebrow">Details</div>
				<dl class="space-y-2 text-sm">
					<div class="flex gap-3">
						<dt class="font-mono uppercase tracking-wider text-muted-foreground w-20">Owner</dt>
						<dd class="text-foreground">{workspaceStore.currentWorkspace.owner}</dd>
					</div>
					<div class="flex gap-3">
						<dt class="font-mono uppercase tracking-wider text-muted-foreground w-20">Type</dt>
						<dd class="text-foreground capitalize">{workspaceStore.currentWorkspace.kind}</dd>
					</div>
				</dl>
			</section>

			<!-- Members list -->
			<section class="space-y-4">
				<div class="eyebrow">Members</div>
				{#if workspaceStore.members.length === 0}
					<p class="text-sm text-muted-foreground">No members yet.</p>
				{:else}
					<ul class="border-2 border-border divide-y-2 divide-border">
						{#each workspaceStore.members as member (member.id)}
							<li class="flex items-center justify-between px-4 py-3 gap-3">
								<span class="text-sm flex-1 min-w-0 truncate">{member.user}</span>

								{#if isAdminOrOwner && member.role !== 'owner'}
									<NativeSelect
										class="w-auto text-xs"
										value={member.role}
										onchange={(e) =>
											handleRoleChange(
												member.id,
												(e.currentTarget as HTMLSelectElement).value as MemberRole
											)}
									>
										{#each ROLE_OPTIONS.filter((o) => o.value !== 'owner') as opt (opt.value)}
											<option value={opt.value}>{opt.label}</option>
										{/each}
									</NativeSelect>
								{:else}
									<Badge variant="secondary" class="font-mono uppercase tracking-wider"
										>{member.role}</Badge
									>
								{/if}

								{#if isAdminOrOwner && member.id !== myMembership?.id && member.role !== 'owner'}
									<!-- Remove other member -->
									<Button
										variant="ghost"
										size="sm"
										onclick={() => handleRemove(member.id)}
										disabled={removingId === member.id}
										class="text-destructive hover:text-destructive"
									>
										{removingId === member.id ? 'Removing…' : 'Remove'}
									</Button>
								{:else if member.id === myMembership?.id && myMembership?.role !== 'owner'}
									<!-- Leave workspace -->
									{#if confirmLeaveId === member.id}
										<span class="flex items-center gap-1">
											<span class="font-mono text-xs uppercase tracking-wider text-muted-foreground"
												>Sure?</span
											>
											<Button
												variant="ghost"
												size="sm"
												onclick={() => handleRemove(member.id)}
												disabled={removingId === member.id}
												class="text-destructive hover:text-destructive"
											>
												{removingId === member.id ? 'Leaving…' : 'Yes, leave'}
											</Button>
											<Button
												variant="ghost"
												size="sm"
												onclick={() => (confirmLeaveId = null)}
											>
												Cancel
											</Button>
										</span>
									{:else}
										<Button
											variant="ghost"
											size="sm"
											onclick={() => (confirmLeaveId = member.id)}
										>
											Leave
										</Button>
									{/if}
								{/if}
							</li>
						{/each}
					</ul>
				{/if}
			</section>

			<!-- Invite form (admin/owner only) -->
			{#if isAdminOrOwner}
				<Card.Root>
					<Card.Header>
						<div class="eyebrow">Invite</div>
						<Card.Title class="font-display font-bold">Invite member</Card.Title>
						<Card.Description>Add someone to this workspace by email.</Card.Description>
					</Card.Header>
					<Card.Content>
						<form
							onsubmit={(e) => {
								e.preventDefault();
								handleInvite();
							}}
							class="flex flex-col sm:flex-row gap-3 sm:items-end"
						>
							<div class="flex-1 space-y-2">
								<Label for="invite-email">Email</Label>
								<Input
									id="invite-email"
									type="email"
									bind:value={inviteEmail}
									placeholder="email@example.com"
									required
								/>
							</div>
							<div class="space-y-2">
								<Label for="invite-role">Role</Label>
								<NativeSelect id="invite-role" bind:value={inviteRole} class="sm:w-40">
									{#each ROLE_OPTIONS.filter((o) => o.value !== 'owner') as opt (opt.value)}
										<option value={opt.value}>{opt.label}</option>
									{/each}
								</NativeSelect>
							</div>
							<Button type="submit" disabled={inviting} class="whitespace-nowrap">
								{inviting ? 'Sending…' : 'Send invite'}
							</Button>
						</form>
						{#if inviteError}
							<p class="mt-3 text-sm text-destructive">{inviteError}</p>
						{/if}
						{#if inviteSuccess}
							<p class="mt-3 font-mono text-sm uppercase tracking-wider text-green">
								Invitation sent!
							</p>
						{/if}
					</Card.Content>
				</Card.Root>
			{/if}
		{/if}
	</div>
{/if}
