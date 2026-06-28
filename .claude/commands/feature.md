You are helping open a new feature in SaasKiller. Your job is to gather requirements, create a GitHub issue, create a branch, and write **real failing tests** derived from the acceptance criteria — not placeholders.

## Step 1: Gather requirements

Ask the user these questions one by one (wait for each answer before asking the next):

1. **What should the feature do?** Describe from the user's perspective in 2-3 sentences.
2. **Acceptance criteria** — list 3-5 concrete, testable conditions that define "done". Be specific: "User can X", "System returns Y when Z", "Admin cannot do W".
3. **Which apps does it touch?** (users / workspaces / billing / apikeys / new app)
4. **Priority:** p0-now / p1-soon / p2-later
5. **Test levels needed:** pytest (backend) / vitest (frontend unit) / playwright @smoke (E2E) — choose all that apply

## Step 2: Create GitHub issue

```bash
gh issue create \
  --title "<feature title>" \
  --label "feature" \
  --label "<priority>" \
  --label "<scope>" \
  --body "## What

<description>

## Acceptance criteria

<acceptance criteria as checkboxes>

## Test plan
- [ ] Backend tests (pytest)
- [ ] Frontend unit tests (vitest)
- [ ] E2E smoke test (playwright @smoke)

## Scope
Apps: <apps>"
```

Save the issue number from the output (e.g. `#42`).

## Step 3: Create feature branch

```bash
git checkout -b feature/<issue-number>-<short-slug>
```

## Step 4: Read the codebase, then write real failing tests

**Before writing any test**, read the relevant existing code:
- The models for the affected apps (`backend/<app>/models.py`)
- The existing tests for that app (`backend/tests/test_<app>.py`)
- The existing views (`backend/<app>/views.py`)
- For frontend: the relevant store and API client (`frontend/src/lib/stores/<store>.svelte.ts`, `frontend/src/lib/api/<api>.ts`)

Use what you find to write tests that:
- Follow the exact same patterns and fixtures as existing tests in that file
- Are red because the **implementation is missing** — not because of `assert False`
- Cover each acceptance criterion with at least one test case
- Include the failure case as well as the happy path

**If pytest chosen** — add to `backend/tests/test_<app>.py`:

Each test must:
- Use the real API endpoint (e.g. `client.post("/api/workspaces/")`)
- Assert the correct HTTP status
- Assert the DB state changed (or didn't change) as expected
- Use fixtures from `conftest.py` (`user`, `auth_client`, `workspace`, etc.)

Example pattern (adapt to the actual feature):
```python
@pytest.mark.django_db
def test_<criterion_slug>(auth_client, <relevant_fixtures>):
    resp = auth_client.post("/api/<endpoint>/", {<payload>})
    assert resp.status_code == 201
    assert <Model>.objects.filter(<condition>).exists()

@pytest.mark.django_db  
def test_<criterion_slug>_forbidden(other_client, <relevant_fixtures>):
    resp = other_client.post("/api/<endpoint>/", {<payload>})
    assert resp.status_code == 403
```

**If vitest chosen** — add to the relevant test file next to the module:

Each test must:
- Mock only what's necessary (follow patterns in existing `*.test.ts` files)
- Call the real store method or API function
- Assert the state change, not just that a mock was called

**If playwright chosen** — add to `frontend/tests/e2e/<feature>.spec.ts`:

Each test must:
- Use `loginAsTestUser()` for authenticated flows
- Navigate to the real route
- Interact with real UI elements (fill, click)
- Assert the outcome is visible in the UI

```typescript
import { test, expect } from '@playwright/test';
import { loginAsTestUser, gotoApp } from './helpers/auth';

test('@smoke <feature> — <criterion>', async ({ browser }) => {
    const ctx = await browser.newContext();
    await loginAsTestUser(ctx);
    const page = await ctx.newPage();
    await gotoApp(page, '/<route>');
    // real interaction
    await page.getByRole('button', { name: '<action>' }).click();
    // real assertion
    await expect(page.getByText('<expected result>')).toBeVisible();
    await ctx.close();
});
```

## Step 5: Verify the tests are red

Run the tests to confirm they fail for the right reason (missing implementation, not syntax errors):

```bash
# Backend
cd backend && source venv/bin/activate && python -m pytest tests/test_<app>.py -v -k "<test_name>"

# Frontend unit
cd frontend && npm test -- --reporter=verbose

# E2E (only if servers running)
cd frontend && npx playwright test tests/e2e/<feature>.spec.ts
```

If a test fails due to a syntax error or import problem — fix it. It must fail because the feature doesn't exist yet.

## Step 6: Hand off

Report:
- GitHub issue URL
- Branch name  
- Which test files were modified
- Exactly which tests are now red and why (what's missing)
- Next step: implement following CLAUDE.md backend-first workflow (Model → Serializer → View → green → Frontend)
