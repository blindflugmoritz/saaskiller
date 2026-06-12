export function toCamelCase(str: string): string {
	return str.replace(/_([a-z])/g, (_, letter) => letter.toUpperCase());
}

export function toSnakeCase(str: string): string {
	return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}

export function transformToCamelCase(obj: unknown): unknown {
	if (obj === null || obj === undefined) return obj;
	if (Array.isArray(obj)) return obj.map(transformToCamelCase);
	if (typeof obj === 'object') {
		return Object.fromEntries(
			Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
				toCamelCase(k),
				transformToCamelCase(v),
			])
		);
	}
	return obj;
}

export function transformToSnakeCase(obj: unknown): unknown {
	if (obj === null || obj === undefined) return obj;
	if (Array.isArray(obj)) return obj.map(transformToSnakeCase);
	if (typeof obj === 'object') {
		return Object.fromEntries(
			Object.entries(obj as Record<string, unknown>).map(([k, v]) => [
				toSnakeCase(k),
				transformToSnakeCase(v),
			])
		);
	}
	return obj;
}
