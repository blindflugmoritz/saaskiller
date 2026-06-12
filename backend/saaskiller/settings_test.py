from .settings import *  # noqa: F401, F403

# Disable throttling for E2E tests — set very high rates so per-view throttle classes don't crash
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100000/hour',
    'signup': '100000/hour',
    'magic_link': '100000/hour',
    'login': '100000/hour',
    'resend_verification': '100000/hour',
}

# Ephemeral test database — deleted after test run
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}
