import { workspacesApi, membersApi, type Workspace, type Membership, type MemberRole } from '$lib/api/workspaces';
import { apiError } from './utils';

class WorkspaceStore {
	workspaces = $state<Workspace[]>([]);
	currentWorkspace = $state<Workspace | null>(null);
	members = $state<Membership[]>([]);
	loading = $state(false);
	error = $state<string | null>(null);

	// ---------------------------------------------------------------------------
	// Workspaces
	// ---------------------------------------------------------------------------

	async fetchWorkspaces(): Promise<void> {
		this.loading = true;
		this.error = null;
		try {
			this.workspaces = await workspacesApi.listWorkspaces();
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to load workspaces.');
		} finally {
			this.loading = false;
		}
	}

	async selectWorkspace(id: string): Promise<void> {
		this.loading = true;
		this.error = null;
		try {
			const [workspace, members] = await Promise.all([
				workspacesApi.getWorkspace(id),
				membersApi.listMembers(id),
			]);
			this.currentWorkspace = workspace;
			this.members = members;
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to load workspace.');
		} finally {
			this.loading = false;
		}
	}

	async createWorkspace(name: string, kind: Workspace['kind']): Promise<Workspace> {
		this.loading = true;
		this.error = null;
		try {
			const workspace = await workspacesApi.createWorkspace({ name, kind });
			this.workspaces = [...this.workspaces, workspace];
			return workspace;
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to create workspace.');
			throw err;
		} finally {
			this.loading = false;
		}
	}

	// ---------------------------------------------------------------------------
	// Members (operate on currentWorkspace)
	// ---------------------------------------------------------------------------

	async inviteMember(email: string, role: MemberRole): Promise<void> {
		if (!this.currentWorkspace) return;
		this.error = null;
		try {
			await membersApi.inviteMember(this.currentWorkspace.id, email, role);
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to send invitation.');
			throw err;
		}
	}

	async removeMember(membershipId: string): Promise<void> {
		if (!this.currentWorkspace) return;
		this.error = null;
		try {
			await membersApi.removeMember(this.currentWorkspace.id, membershipId);
			this.members = this.members.filter((m) => m.id !== membershipId);
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to remove member.');
			throw err;
		}
	}

	async updateMemberRole(membershipId: string, role: MemberRole): Promise<void> {
		if (!this.currentWorkspace) return;
		this.error = null;
		try {
			const updated = await membersApi.updateRole(this.currentWorkspace.id, membershipId, role);
			this.members = this.members.map((m) => (m.id === membershipId ? updated : m));
		} catch (err: unknown) {
			this.error = apiError(err, 'Failed to update role.');
			throw err;
		}
	}

	reset() {
		this.workspaces = [];
		this.currentWorkspace = null;
		this.members = [];
		this.loading = false;
		this.error = null;
	}
}

export const workspaceStore = new WorkspaceStore();
