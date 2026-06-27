Scaffold a new Django app in SaasKiller. Ask the user for the app name (singular, snake_case, e.g. `invoice`).

Then do the following:

1. Run `cd backend && python manage.py startapp <name>`
2. Add `'<name>'` to `INSTALLED_APPS` in `backend/saaskiller/settings.py`
3. Create `backend/<name>/serializers.py` with a placeholder comment
4. Create `backend/<name>/urls.py` with an empty `urlpatterns = []`
5. Include the new urls in `backend/saaskiller/urls.py`: `path('api/<name>/', include('<name>.urls'))`
6. Create `backend/tests/test_<name>.py` with the standard fixture imports (they come from conftest.py — no need to redefine them) and one placeholder test: `def test_placeholder(): pass`
7. Run `make test-be` to verify everything still passes

Report what was created and remind the user to: write their model, run `make makemigrations`, then `make migrate`.
