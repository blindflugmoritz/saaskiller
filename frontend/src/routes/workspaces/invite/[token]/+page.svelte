<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { membersApi } from '$lib/api/workspaces';
	import { workspacesApi } from '$lib/api/workspaces';

	let status = $state<'loading' | 'success' | 'error' | 'unauthenticated'>('loading');
	let workspaceName = $state<string | null>(null);
	let errorMessage = $state<string | null>(null);
	let workspaceId = $state<string | null>(null);

	onMount(async () => {
		await authStore.fetchCurrentUser();

		if (!authStore.isAuthenticated) {
			status = 'unauthenticated';
			return;
		}

		const token = page.params.token!;
		try {
			const result = await membersApi.acceptInvitation(token);
			workspaceId = result.workspace;
			// Fetch workspace name to show a friendly message
			try {
				const ws = await workspacesApi.getWorkspace(result.workspace);
				workspaceName = ws.name;
			} catch {
				// If fetch fails, we still show success without the name
				workspaceName = null;
			}
			status = 'success';
		} catch (err: unknown) {
			const e = err as { detail?: string; message?: string; status?: number };
			errorMessage = e.detail || e.message || 'Invalid or expired invitation.';
			status = 'error';
		}
	});
</script>

<div class="min-h-screen flex items-center justify-center p-6">
	<div class="max-w-sm w-full text-center space-y-4">

		{#if status === 'loading'}
			<p class="text-[--color-muted-foreground]">Accepting invitation…</p>

		{:else if status === 'unauthenticated'}
			<h1 class="text-xl font-semibold">Sign in to accept this invitation</h1>
			<p class="text-sm text-[--color-muted-foreground]">
				You need to be logged in to join a workspace.
			</p>
			<a
				href="/auth/login?next={encodeURIComponent(page.url.pathname)}"
				class="inline-block bg-[--color-primary] text-[--color-primary-foreground] px-6 py-2 rounded-md text-sm font-medium"
			>
				Log in
			</a>

		{:else if status === 'success'}
			<div class="space-y-3">
				<div class="text-4xl">&#10003;</div>
				<h1 class="text-xl font-semibold">
					{#if workspaceName}
						You've joined {workspaceName}!
					{:else}
						You've joined the workspace!
					{/if}
				</h1>
				<p class="text-sm text-[--color-muted-foreground]">
					You are now a member of this workspace.
				</p>
				<div class="flex flex-col sm:flex-row gap-2 justify-center pt-2">
					{#if workspaceId}
						<a
							href="/dashboard/workspaces/{workspaceId}"
							class="bg-[--color-primary] text-[--color-primary-foreground] px-6 py-2 rounded-md text-sm font-medium"
						>
							Go to workspace
						</a>
					{/if}
					<a
						href="/dashboard"
						class="border border-[--color-border] px-6 py-2 rounded-md text-sm font-medium hover:bg-[--color-secondary]"
					>
						Dashboard
					</a>
				</div>
			</div>

		{:else if status === 'error'}
			<h1 class="text-xl font-semibold text-[--color-destructive]">Invitation failed</h1>
			<p class="text-sm text-[--color-muted-foreground]">{errorMessage}</p>
			<a
				href="/dashboard"
				class="inline-block border border-[--color-border] px-6 py-2 rounded-md text-sm font-medium hover:bg-[--color-secondary]"
			>
				Back to dashboard
			</a>
		{/if}

	</div>
</div>
