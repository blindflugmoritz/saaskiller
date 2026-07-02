// === FEATURE: cms ===
// Islands entry point — scans the Django-rendered HTML for island containers
// and mounts the corresponding Svelte 5 components into them.
//
// Usage in Django templates (via feincms3 IslandPlugin or any HTML block):
//   <div data-svelte-island="ExampleCounter" data-props='{"start": 5}'></div>
import './islands.css';
import { mount } from 'svelte';
import { registry } from './registry';

function mountIslands() {
	const containers = document.querySelectorAll<HTMLElement>('[data-svelte-island]');
	containers.forEach((el) => {
		const name = el.dataset.svelteIsland;
		if (!name) return;

		const Component = registry[name];
		if (!Component) {
			console.warn(`[islands] Unknown island: "${name}". Add it to registry.ts.`);
			return;
		}

		let props: Record<string, unknown> = {};
		try {
			if (el.dataset.props) {
				props = JSON.parse(el.dataset.props);
			}
		} catch (e) {
			console.warn(`[islands] Invalid props JSON for "${name}":`, e);
		}

		// Clear placeholder content, then mount the Svelte component
		el.innerHTML = '';
		mount(Component, { target: el, props });
	});
}

// Mount after DOM is ready
if (document.readyState === 'loading') {
	document.addEventListener('DOMContentLoaded', mountIslands);
} else {
	mountIslands();
}
// === END FEATURE: cms ===
