import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './tests/e2e',
	fullyParallel: true,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 0,
	reporter: 'list',
	use: {
		baseURL: process.env.E2E_BASE_URL ?? 'http://localhost:5175',
		trace: 'on-first-retry',
		screenshot: 'only-on-failure',
		actionTimeout: 10000,
	},
	timeout: 30000,
	expect: {
		timeout: 10000,
	},
	projects: [
		{
			name: 'chromium',
			use: { ...devices['Desktop Chrome'] },
		},
	],
	// Run against staging: E2E_BASE_URL=https://myapp-staging-frontend.deploio.app npm run test:e2e:smoke
});
