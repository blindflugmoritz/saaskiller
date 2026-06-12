// === FEATURE: websockets ===
import { WebSocketClient } from '$lib/utils/websocket';
import { PUBLIC_API_URL } from '$env/static/public';

export interface Notification {
	id?: string;
	type?: string;
	message?: string;
	[key: string]: unknown;
}

const MAX_NOTIFICATIONS = 50;

function buildWsUrl(apiUrl: string): string {
	// Convert http(s):// to ws(s)://
	return apiUrl.replace(/^http/, 'ws') + '/ws/notifications/';
}

class NotificationsStore {
	notifications = $state<Notification[]>([]);
	connected = $state(false);

	private client: WebSocketClient | null = null;

	connect(token: string): void {
		if (this.client) {
			this.client.disconnect();
		}
		this.client = new WebSocketClient(buildWsUrl(PUBLIC_API_URL));
		this.client.onMessage((data) => {
			this.addNotification(data as Notification);
		});
		this.client.connect(token);
		this.connected = true;
	}

	disconnect(): void {
		if (this.client) {
			this.client.disconnect();
			this.client = null;
		}
		this.connected = false;
	}

	addNotification(msg: Notification): void {
		this.notifications = [msg, ...this.notifications].slice(0, MAX_NOTIFICATIONS);
	}

	clearAll(): void {
		this.notifications = [];
	}
}

export const notificationsStore = new NotificationsStore();
// === END FEATURE: websockets ===
