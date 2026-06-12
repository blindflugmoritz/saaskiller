import { describe, it, expect, beforeEach } from 'vitest';
import { tokenStorage } from './tokenStorage';

describe('tokenStorage', () => {
	beforeEach(() => {
		localStorage.clear();
	});

	it('returns null when no token stored', () => {
		expect(tokenStorage.getAccess()).toBeNull();
		expect(tokenStorage.getRefresh()).toBeNull();
	});

	it('stores and retrieves access token', () => {
		tokenStorage.set('acc-123');
		expect(tokenStorage.getAccess()).toBe('acc-123');
	});

	it('stores both tokens when refresh provided', () => {
		tokenStorage.set('acc-123', 'ref-456');
		expect(tokenStorage.getAccess()).toBe('acc-123');
		expect(tokenStorage.getRefresh()).toBe('ref-456');
	});

	it('does not overwrite refresh when not provided', () => {
		tokenStorage.set('acc-1', 'ref-1');
		tokenStorage.set('acc-2');
		expect(tokenStorage.getRefresh()).toBe('ref-1');
	});

	it('clears both tokens', () => {
		tokenStorage.set('acc-123', 'ref-456');
		tokenStorage.clear();
		expect(tokenStorage.getAccess()).toBeNull();
		expect(tokenStorage.getRefresh()).toBeNull();
	});
});
