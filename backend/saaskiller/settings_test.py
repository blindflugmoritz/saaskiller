from .settings import *  # noqa: F401, F403

REST_FRAMEWORK['DEFAULT_THROTTLE_CLASSES'] = []
REST_FRAMEWORK['DEFAULT_THROTTLE_RATES'] = {
    'anon': '100000/hour',
    'signup': '100000/hour',
    'magic_link': '100000/hour',
    'login': '100000/hour',
    'resend_verification': '100000/hour',
    'verify_email': '100000/hour',
    'user': '100000/hour',
}

PASSWORD_HASHERS = ['django.contrib.auth.hashers.MD5PasswordHasher']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db_test.sqlite3',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

Q_CLUSTER = {'sync': True, 'name': 'test'}

DEBUG = True
