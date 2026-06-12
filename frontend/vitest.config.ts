import { defineConfig } from 'vitest/config';
import { svelte } from '@sveltejs/vite-plugin-svelte';
import { resolve } from 'path';

export default defineConfig({
	plugins: [svelte({ hot: !process.env.VITEST, configFile: false })],
	test: {
		environment: 'jsdom',
		globals: true,
		include: ['src/**/*.test.ts'],
		setupFiles: ['./src/test/setup.ts'],
		alias: {
			$lib: resolve(__dirname, 'src/lib'),
			$app: resolve(__dirname, 'src/test/mocks/app'),
			'$env/static/public': resolve(__dirname, 'src/test/mocks/env/static/public'),
		},
	},
});
