## What

<!-- Describe what this PR changes. Be specific. -->

## Why

<!-- Explain why this change is needed. -->

Closes #...

## Test plan

- [ ] `make test-be` passes
- [ ] `make test-fe` passes
- [ ] `npm run test:e2e:smoke` passes
- [ ] Tested in browser manually
- [ ] No `.env` secrets committed
- [ ] No missing migrations (`python manage.py migrate --check`)

## Architecture checklist

- [ ] snake↔camelCase transform only in `client.ts`, not elsewhere
- [ ] No store state mutated from components
- [ ] Svelte 5 runes used (`$state`, `$derived`, `$effect`) — no `writable()`
- [ ] New Django views have explicit `permission_classes`
