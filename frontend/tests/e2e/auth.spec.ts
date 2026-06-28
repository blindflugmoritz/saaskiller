import { test, expect } from '@playwright/test';
import { loginAsTestUser, gotoApp } from './helpers/auth';

// Unauthenticated guards

test('@smoke unauthenticated: /dashboard redirects to login', async ({ page }) => {
	await page.goto('/dashboard', { waitUntil: 'domcontentloaded' });
	await page.waitForURL('**/auth/login', { timeout: 5000 });
	await expect(page).toHaveURL(/auth\/login/);
});

test('@smoke login page: shows email form and Google button', async ({ page }) => {
	await page.goto('/auth/login');
	await expect(page.getByRole('heading', { name: 'Log in' })).toBeVisible();
	await expect(page.getByRole('link', { name: /Continue with Google/ })).toBeVisible();
});

test('@smoke signup page: shows email form', async ({ page }) => {
	await page.goto('/auth/signup');
	await expect(page.getByRole('heading', { name: 'Create account' })).toBeVisible();
	await expect(page.getByLabel('Email')).toBeVisible();
});

// Authenticated state via test token

test('@smoke authenticated: /dashboard accessible without redirect', async ({ browser }) => {
	const ctx = await browser.newContext();
	await loginAsTestUser(ctx);
	const page = await ctx.newPage();
	await gotoApp(page, '/dashboard');

	await expect(page).not.toHaveURL(/auth\/login/);
	await ctx.close();
});

test('authenticated: no console errors on dashboard load', async ({ browser }) => {
	const ctx = await browser.newContext();
	await loginAsTestUser(ctx);
	const page = await ctx.newPage();

	const errors: string[] = [];
	page.on('pageerror', (e) => errors.push(e.message));

	await gotoApp(page, '/dashboard');
	await page.waitForTimeout(1000);

	expect(errors.filter((e) => !e.includes('favicon'))).toHaveLength(0);
	await ctx.close();
});

// Magic link form flow (no actual email sent — just verifies UI response)

test('login: submitting email shows check-your-email state', async ({ page }) => {
	await page.goto('/auth/login');
	await page.waitForLoadState('networkidle');
	const responsePromise = page.waitForResponse(
		(resp) => resp.url().includes('/api/auth/request-magic-link/'),
		{ timeout: 15000 }
	);
	await page.getByLabel('Email').fill(`test-${Date.now()}@example.com`);
	await page.getByRole('button', { name: 'Send login link' }).click();
	await responsePromise;
	await expect(page.getByText('Check your email')).toBeVisible();
});

test('signup: submitting email shows check-your-email state', async ({ page }) => {
	await page.goto('/auth/signup');
	await page.waitForLoadState('networkidle');
	const responsePromise = page.waitForResponse(
		(resp) => resp.url().includes('/api/auth/signup/'),
		{ timeout: 15000 }
	);
	await page.getByLabel('Email').fill(`test-${Date.now()}@example.com`);
	await page.getByRole('button', { name: 'Continue with email' }).click();
	await responsePromise;
	await expect(page.getByText('Check your email')).toBeVisible();
});

// ── Authenticated flow ────────────────────────────────────────────────────────

test('@smoke authenticated: dashboard shows user email', async ({ browser }) => {
	const ctx = await browser.newContext();
	await loginAsTestUser(ctx);
	const page = await ctx.newPage();

	await gotoApp(page, '/dashboard');
	// Wait for auth to resolve — dashboard renders email only after fetchCurrentUser()
	await expect(page.getByText('e2e-test@saaskiller.local')).toBeVisible({ timeout: 8000 });
	await ctx.close();
});

test('@smoke logout: clears session and redirects to root', async ({ browser }) => {
	const ctx = await browser.newContext();
	await loginAsTestUser(ctx);
	const page = await ctx.newPage();

	await gotoApp(page, '/dashboard');
	// Wait until dashboard is fully rendered before clicking logout
	await expect(page.getByRole('button', { name: 'Log out' })).toBeVisible({ timeout: 8000 });
	await page.getByRole('button', { name: 'Log out' }).click();

	// Should land on root (or login) — not dashboard
	await page.waitForURL((url) => !url.pathname.startsWith('/dashboard'), { timeout: 5000 });
	await expect(page).not.toHaveURL(/dashboard/);
	await ctx.close();
});

test('@smoke logout: dashboard inaccessible after logout', async ({ browser }) => {
	const ctx = await browser.newContext();
	await loginAsTestUser(ctx);
	const page = await ctx.newPage();

	await gotoApp(page, '/dashboard');
	await expect(page.getByRole('button', { name: 'Log out' })).toBeVisible({ timeout: 8000 });
	await page.getByRole('button', { name: 'Log out' }).click();
	await page.waitForURL((url) => !url.pathname.startsWith('/dashboard'), { timeout: 5000 });

	// Open a fresh context (no injected tokens) and verify dashboard redirects to login
	const freshCtx = await browser.newContext();
	const freshPage = await freshCtx.newPage();
	await freshPage.goto('/dashboard', { waitUntil: 'domcontentloaded' });
	await freshPage.waitForURL('**/auth/login', { timeout: 8000 });
	await expect(freshPage).toHaveURL(/auth\/login/);
	await freshCtx.close();
	await ctx.close();
});
