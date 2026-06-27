import { type BrowserContext, type Page } from '@playwright/test';
import { execSync } from 'child_process';
import { fileURLToPath } from 'url';
import { resolve, dirname } from 'path';

const __dirname = dirname(fileURLToPath(import.meta.url));
const BACKEND_DIR = resolve(__dirname, '../../../../../backend');

/**
 * Creates a JWT token pair via Django management command and injects it into
 * the browser context. No email flow, no magic link — fast and deterministic.
 */
export async function loginAsTestUser(context: BrowserContext): Promise<void> {
	const output = execSync(
		`cd ${BACKEND_DIR} && source venv/bin/activate && python manage.py create_test_token`,
		{ encoding: 'utf-8', shell: '/bin/bash' }
	).trim();

	const accessMatch = output.match(/ACCESS=(\S+)/);
	const refreshMatch = output.match(/REFRESH=(\S+)/);

	if (!accessMatch || !refreshMatch) {
		throw new Error(`create_test_token unexpected output: ${output}`);
	}

	await context.addInitScript(
		([a, r]: [string, string]) => {
			localStorage.setItem('accessToken', a);
			localStorage.setItem('refreshToken', r);
		},
		[accessMatch[1], refreshMatch[1]]
	);
}

export async function gotoApp(page: Page, path = '/dashboard'): Promise<void> {
	await page.goto(path, { waitUntil: 'domcontentloaded' });
}
