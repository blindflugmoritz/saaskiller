import { test, expect } from '@playwright/test';
import { loginAsTestUser, gotoApp } from './helpers/auth';

test('@smoke dashboard loads without JS errors', async ({ browser }) => {
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

test('@smoke dashboard: settings page accessible', async ({ browser }) => {
	const ctx = await browser.newContext();
	await loginAsTestUser(ctx);
	const page = await ctx.newPage();

	await gotoApp(page, '/dashboard/settings');
	await expect(page).not.toHaveURL(/auth\/login/);
	await ctx.close();
});
