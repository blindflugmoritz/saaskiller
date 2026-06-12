import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Guard: skip entire suite if the module doesn't exist
let WebSocketClient: typeof import('./websocket').WebSocketClient;
try {
	const mod = await import('./websocket');
	WebSocketClient = mod.WebSocketClient;
} catch {
	describe.skip('WebSocketClient (module not found)', () => {});
}

// Minimal WebSocket mock
class MockWebSocket {
	static CONNECTING = 0;
	static OPEN = 1;
	static CLOSING = 2;
	static CLOSED = 3;

	url: string;
	readyState: number = MockWebSocket.OPEN;
	private listeners: Record<string, Array<(event: unknown) => void>> = {};

	constructor(url: string) {
		this.url = url;
	}

	addEventListener(type: string, handler: (event: unknown) => void): void {
		if (!this.listeners[type]) this.listeners[type] = [];
		this.listeners[type].push(handler);
	}

	removeEventListener(type: string, handler: (event: unknown) => void): void {
		if (this.listeners[type]) {
			this.listeners[type] = this.listeners[type].filter((h) => h !== handler);
		}
	}

	close(): void {
		this.readyState = MockWebSocket.CLOSED;
		this.emit('close', {});
	}

	emit(type: string, event: unknown): void {
		for (const handler of this.listeners[type] ?? []) {
			handler(event);
		}
	}

	send = vi.fn();
}

describe('WebSocketClient', () => {
	let mockSocketInstance: MockWebSocket;
	const MockWebSocketConstructor = vi.fn((url: string) => {
		mockSocketInstance = new MockWebSocket(url);
		return mockSocketInstance;
	});

	beforeEach(() => {
		MockWebSocketConstructor.mockClear();
		// Replace global WebSocket with the mock
		vi.stubGlobal('WebSocket', MockWebSocketConstructor);
	});

	afterEach(() => {
		vi.unstubAllGlobals();
	});

	describe('connect', () => {
		it('opens a WebSocket with the token appended as a query parameter', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/events/');
			client.connect('test-token-abc');

			expect(MockWebSocketConstructor).toHaveBeenCalledOnce();
			const calledUrl: string = MockWebSocketConstructor.mock.calls[0][0];
			expect(calledUrl).toContain('ws://localhost:8000/ws/events/');
			expect(calledUrl).toContain('token=test-token-abc');
		});

		it('uses & separator when the base URL already has query params', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/events/?room=1');
			client.connect('my-token');

			const calledUrl: string = MockWebSocketConstructor.mock.calls[0][0];
			expect(calledUrl).toBe('ws://localhost:8000/ws/events/?room=1&token=my-token');
		});

		it('uses ? separator when the base URL has no query params', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/events/');
			client.connect('my-token');

			const calledUrl: string = MockWebSocketConstructor.mock.calls[0][0];
			expect(calledUrl).toBe('ws://localhost:8000/ws/events/?token=my-token');
		});

		it('URL-encodes the token', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token with spaces & special=chars');

			const calledUrl: string = MockWebSocketConstructor.mock.calls[0][0];
			expect(calledUrl).toContain('token=token%20with%20spaces%20%26%20special%3Dchars');
		});
	});

	describe('onMessage', () => {
		it('calls the registered handler when a message is received', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-1');

			const handler = vi.fn();
			client.onMessage(handler);

			mockSocketInstance.emit('message', {
				data: JSON.stringify({ type: 'ping', payload: 'hello' }),
			});

			expect(handler).toHaveBeenCalledOnce();
			expect(handler).toHaveBeenCalledWith({ type: 'ping', payload: 'hello' });
		});

		it('passes raw string data when message is not valid JSON', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-1');

			const handler = vi.fn();
			client.onMessage(handler);

			mockSocketInstance.emit('message', { data: 'plain text message' });

			expect(handler).toHaveBeenCalledWith('plain text message');
		});

		it('calls multiple registered handlers', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-1');

			const handler1 = vi.fn();
			const handler2 = vi.fn();
			client.onMessage(handler1);
			client.onMessage(handler2);

			mockSocketInstance.emit('message', { data: JSON.stringify({ x: 1 }) });

			expect(handler1).toHaveBeenCalledOnce();
			expect(handler2).toHaveBeenCalledOnce();
		});
	});

	describe('reconnect on close', () => {
		beforeEach(() => {
			vi.useFakeTimers();
		});

		afterEach(() => {
			vi.useRealTimers();
		});

		it('schedules a reconnect when the socket closes unexpectedly', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-reconnect');

			// Simulate unexpected close (not via disconnect())
			mockSocketInstance.emit('close', {});

			// Before timer fires, no new socket yet
			expect(MockWebSocketConstructor).toHaveBeenCalledTimes(1);

			// Advance past the initial reconnect delay (1000 ms)
			vi.advanceTimersByTime(1000);

			expect(MockWebSocketConstructor).toHaveBeenCalledTimes(2);
			const secondUrl: string = MockWebSocketConstructor.mock.calls[1][0];
			expect(secondUrl).toContain('token=token-reconnect');
		});

		it('does not reconnect after explicit disconnect()', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-no-reconnect');

			client.disconnect();

			vi.advanceTimersByTime(5000);

			// Only the initial connect, no reconnect
			expect(MockWebSocketConstructor).toHaveBeenCalledTimes(1);
		});

		it('only schedules one reconnect timer when close fires', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-1');

			// Fire close twice quickly (edge case)
			mockSocketInstance.emit('close', {});
			mockSocketInstance.emit('close', {});

			vi.advanceTimersByTime(1000);

			// Should only have reconnected once (timer guard)
			expect(MockWebSocketConstructor).toHaveBeenCalledTimes(2);
		});
	});

	describe('disconnect', () => {
		it('closes the underlying socket', () => {
			const client = new WebSocketClient('ws://localhost:8000/ws/');
			client.connect('token-1');

			const closeSpy = vi.spyOn(mockSocketInstance, 'close');
			client.disconnect();

			expect(closeSpy).toHaveBeenCalledOnce();
		});
	});
});
