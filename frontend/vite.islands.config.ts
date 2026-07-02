// === FEATURE: cms ===
// Separate Vite build for Svelte islands (Django-rendered CMS pages).
// NOT SvelteKit — plain @sveltejs/vite-plugin-svelte so we own the entry point.
// Output → backend/static/islands/ ; served by whitenoise after collectstatic.
import { svelte } from '@sveltejs/vite-plugin-svelte';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
	plugins: [
		tailwindcss(),
		svelte({
			compilerOptions: {
				runes: true,
			},
		}),
	],
	resolve: {
		alias: {
			$lib: resolve('./src/lib'),
		},
	},
	build: {
		outDir: '../backend/static/islands',
		emptyOutDir: true,
		// manifest: true allows Django's templatetag to read the hashed asset paths.
		manifest: true,
		rollupOptions: {
			input: {
				islands: resolve('./src/islands/entry.ts'),
			},
			output: {
				// Stable entry name so the Django templatetag always finds "islands.js";
				// whitenoise's ManifestStaticFilesStorage handles cache-busting from there.
				entryFileNames: 'islands.js',
				chunkFileNames: 'chunks/[name]-[hash].js',
				assetFileNames: 'islands[extname]',
			},
		},
	},
});
// === END FEATURE: cms ===
