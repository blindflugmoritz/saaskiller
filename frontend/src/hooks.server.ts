// === FEATURE: sentry ===
import * as Sentry from '@sentry/sveltekit'
import { PUBLIC_SENTRY_DSN, PUBLIC_ENVIRONMENT } from '$env/static/public'
if (PUBLIC_SENTRY_DSN) {
	Sentry.init({ dsn: PUBLIC_SENTRY_DSN, tracesSampleRate: 0.1, environment: PUBLIC_ENVIRONMENT || 'development' })
}
export const handleError = Sentry.handleErrorWithSentry()
// === END FEATURE: sentry ===
