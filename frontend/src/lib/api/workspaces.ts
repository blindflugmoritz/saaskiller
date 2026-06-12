import { apiClient } from './client';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export type WorkspaceKind = 'personal' | 'family' | 'school' | 'business';
export type MemberRole = 'owner' | 'admin' | 'member' | 'viewer';

export interface Workspace {
	id: string;
	name: string;
	kind: WorkspaceKind;
	owner: string; // email
	createdAt: string;
}

export interface Membership {
	id: string;
	workspace: string; // workspace id
	user: string; // email
	role: MemberRole;
	joinedAt: string;
}

export interface InvitationAcceptResult {
	detail: string;
	workspace: string; // workspace id
	role: MemberRole;
}

// ---------------------------------------------------------------------------
// WorkspacesApi
// ---------------------------------------------------------------------------

export const workspacesApi = {
	listWorkspaces(): Promise<Workspace[]> {
		return apiClient.get('/workspaces/');
	},

	createWorkspace(data: { name: string; kind: WorkspaceKind }): Promise<Workspace> {
		return apiClient.post('/workspaces/', data);
	},

	getWorkspace(id: string): Promise<Workspace> {
		return apiClient.get(`/workspaces/${id}/`);
	},

	updateWorkspace(id: string, data: Partial<Pick<Workspace, 'name' | 'kind'>>): Promise<Workspace> {
		return apiClient.patch(`/workspaces/${id}/`, data);
	},

	deleteWorkspace(id: string): Promise<void> {
		return apiClient.delete(`/workspaces/${id}/`);
	},
};

// ---------------------------------------------------------------------------
// MembersApi
// ---------------------------------------------------------------------------

export const membersApi = {
	listMembers(workspaceId: string): Promise<Membership[]> {
		return apiClient.get(`/workspaces/${workspaceId}/members/`);
	},

	updateRole(workspaceId: string, membershipId: string, role: MemberRole): Promise<Membership> {
		return apiClient.patch(`/workspaces/${workspaceId}/members/${membershipId}/`, { role });
	},

	removeMember(workspaceId: string, membershipId: string): Promise<void> {
		return apiClient.delete(`/workspaces/${workspaceId}/members/${membershipId}/remove/`);
	},

	inviteMember(
		workspaceId: string,
		email: string,
		role: MemberRole
	): Promise<{ detail: string; token: string }> {
		return apiClient.post(`/workspaces/${workspaceId}/invite/`, { email, role });
	},

	acceptInvitation(token: string): Promise<InvitationAcceptResult> {
		return apiClient.get(`/workspaces/invite/${token}/`);
	},
};
