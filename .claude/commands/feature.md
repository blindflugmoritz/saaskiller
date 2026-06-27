You are helping open a new feature in SaasKiller. You will gather requirements, create a GitHub issue, create a feature branch, and scaffold failing tests — then hand off to the developer.

## Step 1: Gather requirements

Ask the user these questions one by one (wait for each answer):

1. **What should the feature do?** Describe from the user's perspective in 2-3 sentences.
2. **Acceptance criteria** — list 3-5 testable conditions that define "done". Each becomes a test.
3. **Which apps does it touch?** (users / workspaces / billing / apikeys / new app)
4. **Priority:** p0-now / p1-soon / p2-later
5. **Test levels needed:** pytest (backend) / vitest (frontend unit) / playwright @smoke (E2E) — choose all that apply

## Step 2: Create GitHub issue

Run this command (fill in the values from Step 1):
```bash
gh issue create \
  --title "<feature title>" \
  --label "feature,<priority>,<scope>" \
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

Example: `feature/42-workspace-invites`

## Step 4: Scaffold failing tests

Create placeholder test files for each chosen test level. These must FAIL initially (red) — that is the starting point for TDD.

**If pytest chosen** — add to `backend/tests/test_<app>.py`:
```python
@pytest.mark.django_db
def test_<feature_slug>_placeholder():
    # TODO: implement — <acceptance criterion 1>
    assert False, "not implemented yet"
```

**If vitest chosen** — create `frontend/src/lib/<feature>/index.test.ts`:
```typescript
import { describe, it, expect } from 'vitest';

describe('<Feature name>', () => {
  it.todo('<acceptance criterion 1>');
  it.todo('<acceptance criterion 2>');
});
```

**If playwright chosen** — add to `frontend/tests/e2e/<feature>.spec.ts`:
```typescript
import { test, expect } from '@playwright/test';
import { loginAsTestUser, gotoApp } from './helpers/auth';

test('@smoke <feature name> — <acceptance criterion 1>', async ({ browser }) => {
  const ctx = await browser.newContext();
  await loginAsTestUser(ctx);
  const page = await ctx.newPage();
  await gotoApp(page, '/dashboard');
  // TODO: implement
  expect(false).toBe(true); // red
  await ctx.close();
});
```

## Step 5: Hand off

Report:
- GitHub issue URL
- Branch name
- Which test files were created / modified
- Next step: follow the TDD workflow in CLAUDE.md (Model → Serializer → View → green tests → Frontend)
