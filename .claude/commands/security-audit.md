Run a security audit of the SaasKiller codebase. Check each area and report findings:

**Authentication & Authorization**
- Are all non-public API views protected with `IsAuthenticated` or a custom permission?
- Is JWT used correctly (no session auth bypass)?
- Are magic link tokens single-use and expiring?

**Input Validation**
- Do all write endpoints use serializer validation before touching the DB?
- Any raw SQL or `.format()` in queries (SQL injection risk)?

**Secrets & Config**
- Does `settings.py` read all secrets from env vars?
- Is `DEBUG` safe (defaults to False or reads from env)?
- Is `SECRET_KEY` never hardcoded?

**HTTPS & Cookies**
- Are `SECURE_PROXY_SSL_HEADER`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE` set when `DEBUG=False`?

**Dependencies**
- Run `pip list --outdated` in backend — flag any packages with known CVEs if possible.

**Frontend**
- Is user input ever rendered as raw HTML (XSS risk)?
- Are API errors sanitized before display?

Report a table: Area | Finding | Severity (low/medium/high) | Fix.
