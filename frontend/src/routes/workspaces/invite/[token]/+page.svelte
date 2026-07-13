<script lang="ts">
	import { goto } from '$app/navigation';
	import { page } from '$app/state';
	import { onMount } from 'svelte';
	import { authStore } from '$lib/stores/auth.svelte';
	import { membersApi } from '$lib/api/workspaces';
	import { workspacesApi } from '$lib/api/workspaces';
	import { Button } from '$lib/components/ui/button';
	import * as Card from '$lib/components/ui/card';

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

<div class="min-h-screen flex items-center justify-center bg-background p-6">
	<div class="w-full max-w-md">

		{#if status === 'loading'}
			<Card.Root class="border-2 border-border">
				<Card.Content class="py-12 text-center">
					<div class="mk mk-sq mx-auto mb-6"></div>
					<p class="font-mono uppercase tracking-wider text-sm text-muted-foreground">
						Accepting invitation…
					</p>
				</Card.Content>
			</Card.Root>

		{:else if status === 'unauthenticated'}
			<Card.Root class="border-2 border-border">
				<Card.Header>
					<span class="eyebrow">Invitation</span>
					<Card.Title class="title font-display font-black text-3xl leading-none">
						Sign in to accept
					</Card.Title>
					<Card.Description class="font-mono text-sm text-muted-foreground">
						You need to be logged in to join a workspace.
					</Card.Description>
				</Card.Header>
				<div class="rule-thin mx-6"></div>
				<Card.Footer class="pt-6">
					<Button
						href="/auth/login?next={encodeURIComponent(page.url.pathname)}"
						size="lg"
						class="w-full"
					>
						Log in
					</Button>
				</Card.Footer>
			</Card.Root>

		{:else if status === 'success'}
			<Card.Root class="border-2 border-border">
				<Card.Header>
					<div class="mk mk-ci mb-4"></div>
					<span class="eyebrow">Joined</span>
					<Card.Title class="title font-display font-black text-3xl leading-none">
						{#if workspaceName}
							You've joined {workspaceName}
						{:else}
							You've joined the workspace
						{/if}
					</Card.Title>
					<Card.Description class="font-mono text-sm text-muted-foreground">
						You are now a member of this workspace.
					</Card.Description>
				</Card.Header>
				<div class="rule-thin mx-6"></div>
				<Card.Footer class="flex flex-col sm:flex-row gap-3 pt-6">
					{#if workspaceId}
						<Button href="/dashboard/workspaces/{workspaceId}" size="lg" class="w-full sm:flex-1">
							Go to workspace
						</Button>
					{/if}
					<Button href="/dashboard" variant="outline" size="lg" class="w-full sm:flex-1">
						Dashboard
					</Button>
				</Card.Footer>
			</Card.Root>

		{:else if status === 'error'}
			<Card.Root class="border-2 border-destructive">
				<Card.Header>
					<div class="mk mk-tr mb-4"></div>
					<span class="eyebrow">Error</span>
					<Card.Title class="title font-display font-black text-3xl leading-none text-destructive">
						Invitation failed
					</Card.Title>
					<Card.Description class="font-mono text-sm text-muted-foreground">
						{errorMessage}
					</Card.Description>
				</Card.Header>
				<div class="rule-thin mx-6"></div>
				<Card.Footer class="pt-6">
					<Button href="/dashboard" variant="outline" size="lg" class="w-full">
						Back to dashboard
					</Button>
				</Card.Footer>
			</Card.Root>
		{/if}

	</div>
</div>
