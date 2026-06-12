import { test, expect } from '@playwright/test';

// E2E tests require both backend (port 8000) and frontend (port 5173) running.
// Use: make test-all (starts servers automatically)

test.describe('Landing page', () => {
	test('shows get started and log in links', async ({ page }) => {
		await page.goto('/');
		await expect(page.getByRole('link', { name: 'Get started' })).toBeVisible();
		await expect(page.getByRole('link', { name: 'Log in' })).toBeVisible();
	});
});

test.describe('Signup flow', () => {
	test('shows email form on signup page', async ({ page }) => {
		await page.goto('/auth/signup');
		await expect(page.getByRole('heading', { name: 'Create account' })).toBeVisible();
		await expect(page.getByLabel('Email')).toBeVisible();
	});

	test('submitting valid email shows check-your-email state', async ({ page }) => {
		await page.goto('/auth/signup');
		await page.waitForLoadState('networkidle');
		// Set up response watcher before triggering the action
		const responsePromise = page.waitForResponse(
			resp => resp.url().includes('/api/auth/signup/'),
			{ timeout: 15000 }
		);
		await page.getByLabel('Email').fill(`test-${Date.now()}@example.com`);
		await page.getByRole('button', { name: 'Continue with email' }).click();
		await responsePromise;
		await expect(page.getByText('Check your email')).toBeVisible();
	});
});

test.describe('Login flow', () => {
	test('shows magic link form and Google button', async ({ page }) => {
		await page.goto('/auth/login');
		await expect(page.getByRole('heading', { name: 'Log in' })).toBeVisible();
		await expect(page.getByRole('link', { name: /Continue with Google/ })).toBeVisible();
	});

	test('submitting email shows check-your-email state', async ({ page }) => {
		await page.goto('/auth/login');
		await page.waitForLoadState('networkidle');
		// Set up response watcher before triggering the action
		const responsePromise = page.waitForResponse(
			resp => resp.url().includes('/api/auth/request-magic-link/'),
			{ timeout: 15000 }
		);
		await page.getByLabel('Email').fill(`test-${Date.now()}@example.com`);
		await page.getByRole('button', { name: 'Send login link' }).click();
		await responsePromise;
		await expect(page.getByText('Check your email')).toBeVisible();
	});
});

test.describe('Auth guard', () => {
	test('dashboard redirects to login when not authenticated', async ({ page }) => {
		await page.goto('/dashboard');
		// Should redirect to login (localStorage is empty in new context)
		await page.waitForURL('**/auth/login', { timeout: 5000 });
		await expect(page).toHaveURL(/auth\/login/);
	});
});
