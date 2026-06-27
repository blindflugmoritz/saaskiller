You are helping implement a new feature in SaasKiller following the backend-first TDD workflow.

Ask the user: "What feature are you building? Describe what it should do in 2-3 sentences."

Then guide through these steps in order, stopping at each for confirmation:

1. **Model** — design the Django model(s). Show the fields and explain choices.
2. **Serializer** — write DRF serializer(s).
3. **View + URL** — write the view(s) and wire up urls.py.
4. **Backend test** — write pytest tests (red first). Run `make test-be` and confirm red.
5. **Implementation** — write the code to make tests green. Run `make test-be` again.
6. **Frontend store** — extend or create a Svelte store for the new data.
7. **Frontend component** — build the UI component/page.
8. **Frontend test** — write Vitest test. Run `make test-fe`.
9. **E2E test** — write a Playwright test tagged `@smoke` if it's a critical path.

Follow architecture rules: Svelte 5 runes, snake↔camel at API boundary only, class-based stores, no store mutation from components.
