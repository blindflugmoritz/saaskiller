// === FEATURE: cms ===
// Island component registry.
// Add every Svelte component that can be used as an island here.
// Usage in feincms3 admin: set component name to the key below.
import type { Component } from 'svelte';
import ExampleCounter from './components/ExampleCounter.svelte';

// Map of island name → Svelte 5 component.
// Name must match the value of data-svelte-island="…" in the Django template.
export const registry: Record<string, Component> = {
	ExampleCounter,
};
// === END FEATURE: cms ===
