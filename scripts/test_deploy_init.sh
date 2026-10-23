#!/usr/bin/env bash
# test_deploy_init.sh — dry run of setup.sh + the generated deploy-init.sh
# against a FAKE nctl that only records its calls. Nothing touches deplo.io.
#
# Usage: bash scripts/test_deploy_init.sh [--keep]
#   --keep   leave the scratch dir (generated projects + call logs) in place
#
# Cases (see SETUP_CONFIG.md "Database on deplo.io"):
#   A  staging + production, db = shared (default)
#   B  only one environment → named production, db = shared
#   C  staging + production, db = server:<existing server>
#   D  db = dedicated
#   plus failure paths: quota, "already exists", missing server
#
# Runs on macOS (setup.sh uses BSD `sed -i ''`) with bash ≥ 4. Only tracked
# files are copied — `git add` new files before running.

set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
KEEP=false
[[ "${1:-}" == "--keep" ]] && KEEP=true

WORK="$(mktemp -d "${TMPDIR:-/tmp}/deploy-init-test.XXXXXX")"
$KEEP || trap 'rm -rf "$WORK"' EXIT
mkdir -p "$WORK/bin" "$WORK/home"

FAILS=0
pass() { echo "  ✓ $1"; }
fail() { echo "  ✗ $1"; FAILS=$((FAILS + 1)); }

# ── Fake nctl ────────────────────────────────────────────────────────────────
# Records every call in $NCTL_LOG. FAKE_NCTL_FAIL (a regex over the arguments)
# makes matching calls fail with FAKE_NCTL_FAIL_MSG on stderr.
cat > "$WORK/bin/nctl" << 'NCTL'
#!/usr/bin/env bash
echo "nctl $*" >> "$NCTL_LOG"
if [[ -n "${FAKE_NCTL_FAIL:-}" && "$*" =~ $FAKE_NCTL_FAIL ]]; then
  echo "${FAKE_NCTL_FAIL_MSG:-Error: simulated failure}" >&2
  exit 1
fi
case "$1 $2" in
  "auth whoami")          echo "fake-user@example.com" ;;
  "get projects")         printf 'PROJECT\nn10687\n' ;;
  "get postgresdatabase") echo "postgres://u7k2q9:secret@$3.n10687.db.postgres.nineapis.ch/u7k2q9?sslmode=require" ;;
  "get postgres")         echo "postgres://dbadmin:secret@$3.n10687.db.nineapis.ch/postgres?sslmode=require" ;;
  "get app")              printf 'kind: Application\nstatus:\n  atProvider:\n    cnameTarget: %s.74abc12.deploio.app\n' "$3" ;;
  "get apiserviceaccount") printf 'client_id: fake-id\nclient_secret: fake-secret\n' ;;
esac
exit 0
NCTL
chmod +x "$WORK/bin/nctl"

# ── Helpers ──────────────────────────────────────────────────────────────────

# make_project NAME CONFIG_BODY → runs setup.sh on a fresh copy of the template
make_project() {
  local name="$1" body="$2" dir="$WORK/$1"
  mkdir -p "$dir"
  (cd "$ROOT" && git ls-files -z | xargs -0 tar cf -) | (cd "$dir" && tar xf -)
  printf '%s\n' "$body" > "$dir/setup.config.ini"
  # Fake HOME: no portman registration, no feedloop copy, no global git config.
  (cd "$dir" && HOME="$WORK/home" \
     GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t \
     bash setup.sh "$name" --config setup.config.ini --non-interactive > "$WORK/$name.setup.log" 2>&1) \
    || { fail "$name: setup.sh failed (see $WORK/$name.setup.log)"; tail -20 "$WORK/$name.setup.log"; return 1; }
}

# run_init NAME LABEL [ENV=VAL…] → runs deploy-init.sh with the fake nctl;
# sets RC and leaves the call log in $WORK/LABEL.calls
run_init() {
  local name="$1" label="$2"; shift 2
  : > "$WORK/$label.calls"
  (cd "$WORK/$name" && env "$@" PATH="$WORK/bin:$PATH" NCTL_LOG="$WORK/$label.calls" \
     GITHUB_PAT=github_pat_FAKE bash deploy-init.sh < /dev/null > "$WORK/$label.out" 2>&1)
  RC=$?
}

calls()    { grep -v -E '^nctl (auth|get projects)' "$WORK/$1.calls" | sed -E 's/--git-password="?[^ ]+"?/--git-password=***/; s/SECRET_KEY=[0-9a-f]+/SECRET_KEY=***/g'; }
has()      { grep -qE -- "$2" "$WORK/$1.calls"; }
expect()   { if has "$1" "$2"; then pass "$3"; else fail "$3   (no call matching: $2)"; fi; }
expect_no(){ if has "$1" "$2"; then fail "$3   (unexpected: $(grep -E -- "$2" "$WORK/$1.calls" | head -1))"; else pass "$3"; fi; }
out_has()  { if grep -qE -- "$2" "$WORK/$1.out"; then pass "$3"; else fail "$3   (output lacks: $2)"; fi; }

BASE_FEATURES="
workspaces=true
cms=true
stripe=true
websockets=true
s3=true
i18n=true
sentry=true
apikeys=true
github_oauth=true
mobile=true
feedloop=false
hosting=deploio
github_org=blindflugstudios"

# Stripping every feature is slow; the cases keep features on except tasks,
# which changes deploy-init.sh (worker jobs).

# ── A: staging + production, shared (default — `db` omitted) ─────────────────
echo "Case A — staging + production, db = shared (default)"
make_project casea "$BASE_FEATURES
tasks=true
staging=true
production=true
domain=casea.ch" && {
  run_init casea A
  [[ $RC == 0 ]] && pass "deploy-init.sh exit 0" || { fail "deploy-init.sh exit $RC"; tail -5 "$WORK/A.out"; }
  expect    A '^nctl create postgresdatabase casea-staging-db .*--location=nine-cz42 --wait'    "shared DB staging"
  expect    A '^nctl create postgresdatabase casea-production-db .*--location=nine-cz42 --wait' "shared DB production"
  expect_no A '^nctl create postgres '                                         "no dedicated server"
  expect    A 'DATABASE_URL=postgres://u7k2q9:secret@casea-staging-db\.n10687\.db\.postgres\.nineapis\.ch/u7k2q9\?sslmode=require' \
                                                                             "staging DATABASE_URL unchanged"
  expect_no A 'DATABASE_URL=postgres://[^ ]*/u7k2q9/'                          "nothing appended to connection string"
  expect    A '^nctl update app casea-staging-backend .*--worker-job-name=qcluster' "worker job"
  expect    A 'create app casea-production-backend .*bootstrap_database\.py && python manage\.py collectstatic' "release runs bootstrap before migrate"
  grep -q '^ENV=${1:-staging}$' "$WORK/casea/deploy.sh" && pass "deploy.sh default = staging" || fail "deploy.sh default != staging"
  expect    A 'FRONTEND_URL=https://casea-staging-frontend\.74abc12\.deploio\.app '   "staging FRONTEND_URL has project hash"
  expect    A 'CORS_ALLOWED_ORIGINS=https://casea-staging-frontend\.74abc12\.deploio\.app ' "staging CORS has project hash"
  expect    A 'PUBLIC_API_URL=https://casea-staging-backend\.74abc12\.deploio\.app/api ' "staging PUBLIC_API_URL has project hash"
  expect_no A '[a-z]-(frontend|backend)\.deploio\.app'                          "no hash-less deploio.app host"
  out_has   A 'CNAME  casea-production-frontend\.74abc12\.deploio\.app'        "DNS CNAME target has project hash"
  grep -q '^DEPLOIO_HASH=74abc12$' "$WORK/casea/.env" && pass "DEPLOIO_HASH written to .env" || fail "DEPLOIO_HASH missing in .env"
}

# ── B: one environment → production ──────────────────────────────────────────
echo "Case B — only one environment (configured as staging) → production"
make_project caseb "$BASE_FEATURES
tasks=false
staging=true
production=false
db=shared" && {
  run_init caseb B
  [[ $RC == 0 ]] && pass "deploy-init.sh exit 0" || { fail "deploy-init.sh exit $RC"; tail -5 "$WORK/B.out"; }
  expect_no B 'caseb-staging'                                                  "no staging resources"
  expect    B '^nctl create app caseb-production-backend '                    "production backend"
  expect    B '^nctl create postgresdatabase caseb-production-db '            "shared DB production"
  expect_no B '^nctl create postgres '                                         "no dedicated server"
  expect    B 'FRONTEND_URL=https://caseb-production-frontend\.74abc12\.deploio\.app ' "production FRONTEND_URL has project hash (no domain)"
  grep -q '^ENV=${1:-production}$' "$WORK/caseb/deploy.sh" && pass "deploy.sh default = production" || fail "deploy.sh default != production"
  (cd "$WORK/caseb" && bash deploy.sh staging >/dev/null 2>&1) && fail "deploy.sh accepts 'staging'" || pass "deploy.sh rejects 'staging'"
  [[ ! -f "$WORK/caseb/.github/workflows/deploy-staging.yml" ]] && pass "staging workflow removed" || fail "staging workflow still present"
}

# ── C: existing dedicated server ─────────────────────────────────────────────
echo "Case C — staging + production on existing server albula-pg"
make_project casec-app "$BASE_FEATURES
tasks=false
staging=true
production=true
db=server:albula-pg" && {
  run_init casec-app C
  [[ $RC == 0 ]] && pass "deploy-init.sh exit 0" || { fail "deploy-init.sh exit $RC"; tail -5 "$WORK/C.out"; }
  expect_no C '^nctl create postgres'                                          "creates no server and no shared DB"
  expect    C '^nctl get postgres albula-pg .*--print-connection-string'      "reads existing server"
  expect    C 'DATABASE_URL=postgres://dbadmin:secret@albula-pg\.n10687\.db\.nineapis\.ch/casec_app_staging\?sslmode=require' \
                                                                             "staging DB = casec_app_staging"
  expect    C 'DATABASE_URL=postgres://dbadmin:secret@albula-pg\.n10687\.db\.nineapis\.ch/casec_app_production\?sslmode=require' \
                                                                             "production DB = casec_app_production"
}

# ── D: dedicated ─────────────────────────────────────────────────────────────
echo "Case D — db = dedicated"
make_project cased "$BASE_FEATURES
tasks=false
staging=true
production=true
db=dedicated" && {
  run_init cased D
  [[ $RC == 0 ]] && pass "deploy-init.sh exit 0" || { fail "deploy-init.sh exit $RC"; tail -5 "$WORK/D.out"; }
  [[ $(grep -cE '^nctl create postgres ' "$WORK/D.calls") == 1 ]] && pass "exactly one server for the project" || fail "server count != 1"
  expect    D '^nctl create postgres cased-db '                               "server cased-db"
  expect    D 'DATABASE_URL=postgres://dbadmin:secret@cased-db\.[^ ]*/cased_production\?sslmode=require' "production DB on it"
  out_has   D 'CHF 104'                                                        "cost warning"
}

# ── Failure paths (reuse case A) ─────────────────────────────────────────────
if [[ -d "$WORK/casea" ]]; then
  echo "Failure — quota on postgresdatabase"
  run_init casea Q FAKE_NCTL_FAIL='create postgresdatabase' \
    FAKE_NCTL_FAIL_MSG='Error: admission webhook denied the request: quota exceeded for postgresdatabases'
  [[ $RC != 0 ]] && pass "exit $RC (non-zero)" || fail "exit 0 despite quota error"
  out_has   Q 'Kontingent bei Nine erhöhen lassen oder .*DB_MODE=server'      "quota hint"
  expect_no Q '^nctl create app'                                               "no apps without a database"
  if grep -q 'Already exists\|existiert schon' "$WORK/Q.out"; then fail "quota reported as 'exists'"; else pass "not reported as 'exists'"; fi

  echo "Failure — rerun, resources already exist"
  run_init casea X FAKE_NCTL_FAIL='^create ' FAKE_NCTL_FAIL_MSG='Error: apps.deplo.io "x" already exists'
  [[ $RC == 0 ]] && pass "exit 0" || { fail "exit $RC"; tail -5 "$WORK/X.out"; }
  out_has   X 'existiert schon'                                                "reported as existing"

  echo "Failure — project hash unreadable"
  run_init casea H FAKE_NCTL_FAIL='^get app ' DEPLOIO_HASH_VERSUCHE=1
  [[ $RC != 0 ]] && pass "exit $RC (non-zero)" || fail "exit 0 without project hash"
  out_has   H 'Projekt-Hash nicht lesbar'                                      "missing hash detected"
  expect_no H '--env=FRONTEND_URL'                                             "no env vars with dead hostnames"

  echo "Failure — empty connection string"
  run_init casea E FAKE_NCTL_FAIL='get postgresdatabase casea-staging-db'
  [[ $RC != 0 ]] && pass "exit $RC (non-zero)" || fail "exit 0 with empty DATABASE_URL"
  out_has   E 'DATABASE_URL \(staging\) ist leer'                              "empty URL detected"
fi

if [[ -d "$WORK/casec-app" ]]; then
  echo "Failure — server does not exist"
  run_init casec-app M FAKE_NCTL_FAIL='get postgres albula-pg'
  [[ $RC != 0 ]] && pass "exit $RC (non-zero)" || fail "exit 0 with missing server"
  out_has   M "Postgres-Server 'albula-pg' nicht gefunden"                     "missing server detected"
  expect_no M '^nctl create'                                                   "nothing created"
fi

# ── Call logs (for review / PR description) ──────────────────────────────────
if $KEEP || [[ -n "${SHOW_CALLS:-}" ]]; then
  for label in A B C D; do
    [[ -f "$WORK/$label.calls" ]] || continue
    echo ""; echo "── nctl calls, case $label ──"; calls "$label"
  done
fi

echo ""
$KEEP && echo "Scratch dir kept: $WORK"
if [[ $FAILS == 0 ]]; then echo "All checks passed."; else echo "$FAILS check(s) failed."; exit 1; fi
