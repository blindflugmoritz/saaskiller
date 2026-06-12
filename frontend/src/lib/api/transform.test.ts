import { describe, it, expect } from 'vitest';
import { toCamelCase, toSnakeCase, transformToCamelCase, transformToSnakeCase } from './transform';

describe('toCamelCase', () => {
	it('converts snake_case to camelCase', () => {
		expect(toCamelCase('language_preference')).toBe('languagePreference');
		expect(toCamelCase('email_verified')).toBe('emailVerified');
		expect(toCamelCase('created_at')).toBe('createdAt');
	});

	it('leaves already-camel untouched', () => {
		expect(toCamelCase('email')).toBe('email');
		expect(toCamelCase('createdAt')).toBe('createdAt');
	});
});

describe('toSnakeCase', () => {
	it('converts camelCase to snake_case', () => {
		expect(toSnakeCase('languagePreference')).toBe('language_preference');
		expect(toSnakeCase('emailVerified')).toBe('email_verified');
	});
});

describe('transformToCamelCase', () => {
	it('transforms object keys recursively', () => {
		const result = transformToCamelCase({
			email_verified: true,
			language_preference: 'en',
			nested_obj: { magic_link_token: null },
		});
		expect(result).toEqual({
			emailVerified: true,
			languagePreference: 'en',
			nestedObj: { magicLinkToken: null },
		});
	});

	it('handles arrays', () => {
		const result = transformToCamelCase([{ user_id: 1 }, { user_id: 2 }]);
		expect(result).toEqual([{ userId: 1 }, { userId: 2 }]);
	});

	it('handles null and undefined', () => {
		expect(transformToCamelCase(null)).toBeNull();
		expect(transformToCamelCase(undefined)).toBeUndefined();
	});
});

describe('transformToSnakeCase', () => {
	it('transforms object keys recursively', () => {
		const result = transformToSnakeCase({
			languagePreference: 'en',
			emailVerified: true,
		});
		expect(result).toEqual({
			language_preference: 'en',
			email_verified: true,
		});
	});
});
