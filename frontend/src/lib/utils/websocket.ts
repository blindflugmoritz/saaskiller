// === FEATURE: websockets ===
type MessageHandler = (data: unknown) => void;

export class WebSocketClient {
	private url: string;
	private socket: WebSocket | null = null;
	private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
	private messageHandlers: MessageHandler[] = [];
	private reconnectDelay = 1000;
	private readonly maxReconnectDelay = 30000;
	private shouldReconnect = false;
	private currentToken: string | null = null;

	constructor(url: string) {
		this.url = url;
	}

	connect(token: string): void {
		this.currentToken = token;
		this.shouldReconnect = true;
		this.reconnectDelay = 1000;
		this.openSocket(token);
	}

	private openSocket(token: string): void {
		const separator = this.url.includes('?') ? '&' : '?';
		const fullUrl = `${this.url}${separator}token=${encodeURIComponent(token)}`;

		this.socket = new WebSocket(fullUrl);

		this.socket.addEventListener('message', (event: MessageEvent) => {
			let data: unknown;
			try {
				data = JSON.parse(event.data as string);
			} catch {
				data = event.data;
			}
			for (const handler of this.messageHandlers) {
				handler(data);
			}
		});

		this.socket.addEventListener('close', () => {
			this.socket = null;
			if (this.shouldReconnect && this.currentToken) {
				this.scheduleReconnect();
			}
		});

		this.socket.addEventListener('open', () => {
			this.reconnectDelay = 1000;
		});
	}

	private scheduleReconnect(): void {
		if (this.reconnectTimer !== null) return;
		this.reconnectTimer = setTimeout(() => {
			this.reconnectTimer = null;
			if (this.shouldReconnect && this.currentToken) {
				this.openSocket(this.currentToken);
				this.reconnectDelay = Math.min(this.reconnectDelay * 2, this.maxReconnectDelay);
			}
		}, this.reconnectDelay);
	}

	disconnect(): void {
		this.shouldReconnect = false;
		this.currentToken = null;
		if (this.reconnectTimer !== null) {
			clearTimeout(this.reconnectTimer);
			this.reconnectTimer = null;
		}
		if (this.socket) {
			this.socket.close();
			this.socket = null;
		}
	}

	onMessage(handler: MessageHandler): void {
		this.messageHandlers.push(handler);
	}
}
// === END FEATURE: websockets ===
