import { defineConfig, devices } from '@playwright/test';

export default defineConfig({
	testDir: './tests',
	fullyParallel: false,
	forbidOnly: !!process.env.CI,
	retries: process.env.CI ? 2 : 1,
	workers: 1,
	reporter: 'line',
	use: {
		baseURL: 'http://localhost:5173',
		trace: 'on-first-retry',
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
});
