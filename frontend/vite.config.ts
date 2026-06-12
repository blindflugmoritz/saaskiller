import { sveltekit } from '@sveltejs/kit/vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
// === FEATURE: i18n ===
import { paraglide } from '@inlang/paraglide-sveltekit/vite';
// === END FEATURE: i18n ===

export default defineConfig({
	plugins: [
		tailwindcss(),
		// === FEATURE: i18n ===
		paraglide({ project: './project.inlang', outdir: './src/lib/paraglide' }),
		// === END FEATURE: i18n ===
		sveltekit(),
	],
});
